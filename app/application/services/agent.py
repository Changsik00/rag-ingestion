import logging
import re
from typing import TYPE_CHECKING, Annotated, Any, Literal, TypedDict

from langchain_core.messages import AIMessage, AnyMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableConfig
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import END, StateGraph, add_messages

from app.application.services.rag import RAG
from app.core.config import get_settings
from app.domain.entities.job import JobStatus

if TYPE_CHECKING:
    from app.application.services.ingestion import Ingestion
    from app.domain.services.discovery_service import DiscoveryService

logger = logging.getLogger(__name__)


class AgentState(TypedDict):
    """Admin Agent의 상태를 정의하는 TypedDict"""

    messages: Annotated[list[AnyMessage], add_messages]
    intent: Annotated[str, lambda x, y: y]
    tool_output: Annotated[str, lambda x, y: y]
    context_data: Annotated[dict, lambda x, y: y]  # RAG 상세 정보 (chunks, graph) 전달용 - 매번 초기화
    rerank_log: Annotated[list[dict], lambda x, y: y]  # Spec 066: Rerank Trace 저장용 - 매번 초기화
    filters: Annotated[dict | None, lambda x, y: y]  # RAG 필터링용
    thread_id: str | None  # Thread ID (Spec 034)
    hitl_enabled: bool  # HITL Toggle Status
    # Spec 045: Interactive Refinement
    draft_content: Annotated[str | None, lambda x, y: y]
    is_clarification: Annotated[bool, lambda x, y: y]
    missing_slots: Annotated[list[str], lambda x, y: y]
    # Spec 078-B: Interactive Discovery
    discovered_urls: Annotated[list[dict] | None, lambda x, y: y]  # Search results for review
    original_discovery_topic: Annotated[str | None, lambda x, y: y]


class ConversationalRAGAgent:
    """
    RAG Playground 및 관리자용 Orchestration Agent.
    수집(Ingest)과 검색(Search) 의도를 구분하여 처리합니다.
    """

    def __init__(
        self,
        rag_service: "RAG",
        ingestion_service: "Ingestion",
        discovery_service: "DiscoveryService"
    ):
        self.rag_service = rag_service
        self.ingestion_service = ingestion_service
        self.discovery_service = discovery_service
        self.llm = ChatGoogleGenerativeAI(
            model=get_settings().GEMINI_MODEL_NAME, temperature=0, google_api_key=get_settings().GEMINI_API_KEY
        )

    def _extract_text_content(self, content: Any) -> str:
        """
        Gemini 3.0 Multimodal Response Parsing Helper.
        - List[Part] 형태에서 Text Part만 추출하여 결합합니다.
        - Non-text objects (images, blobs) are skipped.
        """
        if isinstance(content, str):
            return content

        if isinstance(content, list):
            text_parts = []
            for part in content:
                # Check for 'text' attribute (LangChain MessageContent or similar)
                if hasattr(part, "text"):
                    text_parts.append(part.text)
                elif isinstance(part, str):
                    text_parts.append(part)
                elif isinstance(part, dict) and "text" in part:
                    text_parts.append(part["text"])
                # Ignore other types (e.g. dicts without text, blobs) to prevent chaotic noise
            return "".join(text_parts)

        return str(content)

    def build_workflow(self, checkpointer: Any = None, interrupt_before: list[str] | None = None):
        """LangGraph 워크플로우를 빌드하고 컴파일합니다."""
        workflow = StateGraph(AgentState)

        workflow.add_node("router", self.router_node)
        workflow.add_node("ingest", self.ingest_node)
        workflow.add_node("search", self.search_node)
        workflow.add_node("discovery", self.discovery_node)  # Spec 078
        workflow.add_node("human_review", self.human_review_node)
        workflow.add_node("clarify", self.clarify_node)  # Spec 045

        workflow.set_entry_point("router")

        workflow.add_conditional_edges(
            "router",
            self.route_logic,
            {
                "ingest": "ingest",
                "search": "search",
                "discovery": "discovery",  # Spec 078
                "ingest_selection": "ingest_selection",  # Spec 078-B
                "clarify": "clarify",  # Spec 045
            },
        )
        
        workflow.add_node("ingest_selection", self.ingest_selection_node)

        workflow.add_edge("ingest", "search")  # 수집 완료 후 요약을 위해 검색 노드로 이동
        # Discovery now pauses for user input (Review)
        workflow.add_edge("discovery", END)
        # Selection -> Ingest -> Search
        workflow.add_edge("ingest_selection", "search")

        # Conditional Edge after Search: Check HITL
        def route_after_search(state: AgentState):
            if state.get("hitl_enabled"):
                return "human_review"
            return END

        workflow.add_conditional_edges("search", route_after_search, {"human_review": "human_review", END: END})

        # Feedback Loop Logic
        def route_after_review(state: AgentState):
            messages = state.get("messages", [])
            if messages and isinstance(messages[-1], HumanMessage):
                logger.info("🔄 Feedback detected, looping back to router.")
                return "router"
            return END

        workflow.add_conditional_edges("human_review", route_after_review, {"router": "router", END: END})

        # Clarification Loop Logic
        # 사용자가 답변을 주면 router로 다시 보냄
        workflow.add_edge("clarify", END)

        # Default interrupt if checkpointer is provided
        if checkpointer and not interrupt_before:
            # Spec 045: Clarify node also requires user input (interrupt)
            # But technically, we interrupt AFTER clarify node prints the question
            # So the user sees the question and the graph stops at END.
            # Next user input restarts from 'router' (if configured correctly via thread)
            # OR we loop back to END and wait for new input which restarts graph.
            # Actually standard generic chat pattern: Node -> Output -> END -> User Input -> Router.
            # However, for HITL 'human_review' we specifically pause BEFORE it or AFTER it?
            # Existing logic: interrupt_before=["human_review"] means we stop BEFORE entering human_review?
            # No, user said "human_review" node is pass-through.
            # Let's stick to existing pattern: interrupt_before=["human_review"]
            # For clarification, we don't strictly need interrupt logic if we output question and go to END.
            # User input will trigger next run starting at 'router'.
            interrupt_before = ["human_review"]

        return workflow.compile(checkpointer=checkpointer, interrupt_before=interrupt_before)

    def route_logic(self, state: AgentState) -> Literal["ingest", "search", "discovery", "ingest_selection", "clarify"]:
        return state["intent"]

    def human_review_node(self, state: AgentState) -> dict:
        """HITL Review Node (Pass-through)"""
        return {"tool_output": "Human Review Completed"}

    async def clarify_node(self, state: AgentState) -> dict:
        """사용자에게 역질문을 하는 노드 (LLM 기반 다국어 지원)"""
        missing_slots = state.get("missing_slots", [])
        messages = state.get("messages", [])
        last_user_msg = messages[-1].content if messages else ""

        prompt = ChatPromptTemplate.from_template(
            """
            You are a helpful assistant. The user's intent is ambiguous or missing critical information.
            Your task is to ask a clarifying question to get the missing information.

            Missing Information: {missing_slots}
            User Input: {input}

            Guidelines:
            1. If 'url' is missing for ingestion, ask the user to provide the URL.
            2. If 'topic' is missing for discovery/search, ask the user what topic they want to research.
            3. If specific slots are not clear, politely ask for clarification.
            4. **IMPORTANT**: Respond in the SAME LANGUAGE as the User Input.

            Clarifying Question:
            """
        )

        formatted_prompt = prompt.invoke({"missing_slots": ", ".join(missing_slots), "input": last_user_msg})
        response = await self.llm.ainvoke(formatted_prompt)

        # Handle Gemini 3.0 content list
        # Handle Gemini 3.0 content list
        if hasattr(response, "content"):
            response.content = self._extract_text_content(response.content)

        return {"messages": [response], "is_clarification": True, "tool_output": "Clarification Requested"}

        return {"intent": intent, "missing_slots": missing_slots}

    async def router_node(self, state: AgentState) -> dict:
        messages = state["messages"]
        last_user_msg = messages[-1].content if messages else ""

        # Spec 078-B: Check for Discovery URL Selection context
        discovered_urls = state.get("discovered_urls")
        if discovered_urls:
            # Check if user input is a selection (numbers, 'all', '전부')
            if self._is_selection(last_user_msg):
                return {"intent": "ingest_selection"}
            
            # If user changes topic or asks something else, we clear context?
            # For now, let standard routing handle it, but maybe clear discovered_urls if intent changes?
            # We'll rely on next node to decide.

        # 의도 분류 프롬프트 (Spec 045: Clarify 추가)
        prompt = ChatPromptTemplate.from_template(
            """
            Analyze the user's input and determine the intent.

            check for missing critical information:
            - If intent is 'ingest', a URL is REQUIRED. If URL is missing, return 'clarify'.
            - If intent is 'search', a specific topic/question is REQUIRED. However, if the user asks to "summarize this" or "explain this" (referring to context/history), classify as 'search'.

            options:
            - 'ingest': The user wants to read, learn, scrape, or ingest a SPECIFIC URL. (e.g. "Read this link", "Ingest https://...")
            - 'discovery': The user wants to RESEARCH a topic, find new information, or crawl the web automatically WITHOUT a specific URL. (e.g. "Research Agentic RAG", "Find papers about LLMs", "조사해줘", "찾아줘")
            - 'search': The user is asking a specific question, discussing a topic, or asking for a summary of the context. (e.g. "What is RAG?", "이거 요약해줘")
            - 'clarify': The input is ambiguous or missing required arguments. (e.g. "Do it", "help me", "알려줘")

            Input: {input}

            Return ONLY 'ingest', 'discovery', 'search', or 'clarify'.
            """
        )
        prompt_val = prompt.invoke({"input": last_user_msg})
        response = await self.llm.ainvoke(prompt_val)

        if hasattr(response, "content"):
            intent = self._extract_text_content(response.content).strip().lower()
        else:
            intent = str(response).strip().lower()

        logger.info(f"Router LLM Decision: {intent} (Input: {last_user_msg})")

        # Fallback / Force logic
        if "ingest" in intent:
            intent = "ingest"
        elif "discovery" in intent:
            intent = "discovery"
        elif "search" in intent:
            intent = "search"
        else:
            intent = "clarify"

        # Explicit Keyword Override (Korean)
        if "조사" in last_user_msg or "찾아줘" in last_user_msg or "research" in last_user_msg.lower():
             # Only if not a URL ingest request
            if "http" not in last_user_msg:
                 logger.info(f"Router Keyword Override: Force 'discovery' for input '{last_user_msg}'")
                 intent = "discovery"

        # Basic slot filling check (fallback if LLM misses it)
        missing_slots = []
        if intent == "ingest":
            url_pattern = r"http[s]?://"
            if not re.search(url_pattern, last_user_msg):
                intent = "clarify"
                missing_slots.append("url")
        elif intent == "discovery":
            if len(last_user_msg.strip()) < 2:
                intent = "clarify"
                missing_slots.append("topic")
            # Clear previous discovery context if new discovery started
            return {"intent": intent, "missing_slots": missing_slots, "discovered_urls": None}

        return {"intent": intent, "missing_slots": missing_slots}

    def _is_selection(self, text: str) -> bool:
        """Check if text is likely a selection (e.g. '1', '1, 3', 'all', '전부', '네')"""
        clean = text.strip().lower()
        # "all", "전부", "다"
        if clean in ["all", "전부", "다", "모두"]:
            return True
        # "yes", "네", "응" (Treat as all or top 1? Maybe just return True and let handler decide)
        if clean in ["yes", "y", "네", "응", "어"]:
            return True
        # Number patterns: "1", "1, 2", "1번 3번", "1 2"
        if re.search(r"\d", clean):
            return True
        return False

    def ingest_node(self, state: AgentState) -> dict:
        messages = state["messages"]
        last_user_msg = messages[-1].content

        # URL 추출
        url_pattern = r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"
        urls = re.findall(url_pattern, last_user_msg)

        if not urls:
            return {
                "messages": [AIMessage(content="URL을 찾을 수 없습니다. 올바른 URL을 입력해주세요.")],
                "tool_output": "No URL found",
            }

        target_url = urls[0]

        try:
            # 수집 작업 생성 및 실행 (동기 처리)
            job = self.ingestion_service.create_job(target_url)
            self.ingestion_service.process_job(job.job_id)
            updated_job = self.ingestion_service.job_repository.get_job(job.job_id)

            if updated_job.status == JobStatus.COMPLETED:
                msg = f"✅ 수집 완료: {target_url}\n\n이제 내용을 요약해드릴게요..."
                if updated_job.docs_ids:
                    doc_id = str(updated_job.docs_ids[0])
                    return {"messages": [AIMessage(content=msg)], "tool_output": msg, "filters": {"doc_id": doc_id}}
            else:
                msg = f"❌ 수집 실패: {updated_job.error_message}"

        except Exception as e:
            msg = f"❌ 오류 발생: {str(e)}"

        return {"messages": [AIMessage(content=msg)], "tool_output": msg}

    async def discovery_node(self, state: AgentState) -> dict:
        """Autonomous Discovery Node (Spec 078-B: Interactive)"""
        messages = state["messages"]
        last_user_msg = messages[-1].content

        topic = last_user_msg
        # Clean topic if it was an explicit command like "Research X"
        # For now, just use the whole message.

        try:
            # Step 1: Search only (No Ingestion)
            # Spec 078-B: Fetch 5 results for user review
            search_results = await self.discovery_service.search_topic(topic, max_results=5)

            if search_results:
                # Format results for user
                msg_lines = [f"🔍 '{topic}'에 대해 다음 {len(search_results)}개의 문서를 발견했습니다. 수집할 항목을 선택해주세요.\n"]
                for idx, res in enumerate(search_results, 1):
                    msg_lines.append(f"{idx}. [{res['title']}]({res['link']})")
                
                msg_lines.append("\n예: '1번, 3번', '전부', '1 2'")
                msg = "\n".join(msg_lines)
                
                return {
                    "messages": [AIMessage(content=msg)],
                    "tool_output": msg,
                    "discovered_urls": search_results,
                    "original_discovery_topic": topic
                }
            else:
                msg = f"⚠️ '{topic}'에 대한 유의미한 정보를 찾지 못했습니다."
                return {"messages": [AIMessage(content=msg)], "tool_output": msg}

        except Exception as e:
            msg = f"❌ 탐색 중 오류 발생: {str(e)}"
            return {"messages": [AIMessage(content=msg)], "tool_output": msg}

    async def ingest_selection_node(self, state: AgentState) -> dict:
        """Process user selection and trigger ingestion (Spec 078-B)"""
        messages = state["messages"]
        last_user_msg = messages[-1].content
        discovered_urls = state.get("discovered_urls", [])

        if not discovered_urls:
            return {
                "messages": [AIMessage(content="선택할 수 있는 검색 결과가 없습니다. 다시 검색해주세요.")],
                "tool_output": "No discovered URLs context"
            }

        selected_urls = []
        clean_msg = last_user_msg.strip().lower()

        # Parse Selection
        if any(w in clean_msg for w in ["all", "전부", "다", "모두"]):
            selected_urls = [res["link"] for res in discovered_urls]
        else:
            # Extract numbers
            indices = [int(n) for n in re.findall(r"\d+", clean_msg)]
            # Validate indices (1-based to 0-based)
            valid_indices = [i-1 for i in indices if 1 <= i <= len(discovered_urls)]
            selected_urls = [discovered_urls[i]["link"] for i in valid_indices]

        if not selected_urls:
            return {
                "messages": [AIMessage(content="올바른 번호를 선택해주세요.")],
                "tool_output": "Invalid selection"
            }

        # Trigger Ingestion for selected URLs
        try:
            job_ids = []
            msg = f"✅ {len(selected_urls)}개의 문서 수집을 시작합니다...\n"
            
            # Using create_job/process_job for each URL. 
            # Note: For multiple URLs, this might be slow if synchronous.
            # Ideally, we should fire them asynchronously or use a batch API.
            # But IngestionService seems to handle one by one. 
            # Let's do it sequentially for safety or use gather if possible.
            # Here we just iterate.
            
            for url in selected_urls:
                job = self.ingestion_service.create_job(url)
                # We can fire and forget process_job if we want async, 
                # but if we want to search immediately, we might need to wait or rely on background.
                # The prompt implies we wait or at least start it.
                # self.ingestion_service.process_job(job.job_id) -> This is sync/blocking?
                # In previous code "ingest_node" it was blocking.
                self.ingestion_service.process_job(job.job_id)
                job_ids.append(job.job_id)

            msg += f"작업 ID: {', '.join(job_ids)}\n\n내용을 요약합니다..."
            
            # Clear discovery context after selection
            return {
                "messages": [AIMessage(content=msg)],
                "tool_output": msg,
                "discovered_urls": None,  # Context Cleared
                "original_discovery_topic": None
            }

        except Exception as e:
            msg = f"❌ 수집 중 오류 발생: {str(e)}"
            return {"messages": [AIMessage(content=msg)], "tool_output": msg}

    async def search_node(self, state: AgentState, config: RunnableConfig) -> dict:
        messages = state["messages"]
        last_user_msg = messages[-1].content

        # 대화 이력 구성
        history = [
            {"role": m.type, "content": m.content}
            for m in messages[:-1]
            if m.type in ["human", "ai", "user", "assistant"]
        ]

        filters = state.get("filters")
        thread_id = state.get("thread_id")

        # Spec 055: Advanced Settings Propagation
        retrieval_config = config.get("configurable", {}).get("retrieval_config")

        # Spec 040 Fix: AdminAgent와 RAGService가 동일한 Checkpointer/ThreadID를 공유하면 상태 충돌 발생.
        # 따라서 RAGService 호출 시에는 별도의 namespace를 적용한 thread_id를 전달함.
        rag_thread_id = f"rag-{thread_id}" if thread_id else None

        # RAG 검색 및 생성 실행
        result = await self.rag_service.retrieve_and_generate(
            last_user_msg, history, filters=filters, thread_id=rag_thread_id, retrieval_config=retrieval_config
        )

        context_data = {
            "rewritten_query": result.rewritten_query,
            "vector_chunks": result.vector_chunks,
            "keyword_chunks": result.keyword_chunks,
            "graph_data": result.graph_data,
            "full_context": result.full_context,
            "user_intent": result.user_intent,
        }

        return {
            "messages": [AIMessage(content=result.answer)],
            "tool_output": "Search Completed",
            "context_data": context_data,
            "rerank_log": result.rerank_log,  # Spec 066: Propagate rerank_log to AgentState
        }

    async def ask(
        self,
        thread_id: str,
        message: str,
        filters: dict | None = None,
        hitl_enabled: bool = False,
        retrieval_config: dict | None = None,
        checkpointer: Any = None,
    ) -> dict[str, Any]:
        """
        사용자 질문을 처리하고 답변을 생성합니다. (LangGraph 실행 캡슐화)
        """
        # Config 설정
        config = {"configurable": {"thread_id": thread_id, "retrieval_config": retrieval_config or {}}}

        # Workflow 빌드 및 실행
        workflow = self.build_workflow(checkpointer=checkpointer)

        input_state = {
            "messages": [{"role": "user", "content": message}],
            "filters": filters,
            "thread_id": thread_id,
            "hitl_enabled": hitl_enabled,
        }

        result = await workflow.ainvoke(input_state, config=config)

        # 상태 및 Next Steps 확인
        next_steps = []
        status = "completed"

        if checkpointer:
            snapshot = await workflow.aget_state(config)
            next_steps = snapshot.next
            if next_steps:
                status = "paused"

        return {
            "result": result,
            "status": status,
            "next_steps": next_steps,
        }

    async def resume(
        self,
        thread_id: str,
        user_input: str | None,
        checkpointer: Any = None,
    ) -> dict[str, Any]:
        """
        중단된 세션(HITL)을 재개합니다.
        """
        config = {"configurable": {"thread_id": thread_id}}
        workflow = self.build_workflow(checkpointer=checkpointer)

        if user_input and user_input != "Approved":
            from langchain_core.messages import HumanMessage

            feedback_msg = HumanMessage(content=user_input)
            await workflow.aupdate_state(config, {"messages": [feedback_msg]})
            result = await workflow.ainvoke(None, config=config)
        else:
            result = await workflow.ainvoke(None, config=config)

        # 상태 및 Next Steps 확인
        next_steps = []
        status = "completed"

        if checkpointer:
            snapshot = await workflow.aget_state(config)
            next_steps = snapshot.next
            if next_steps:
                status = "paused"

        return {
            "result": result,
            "status": status,
            "next_steps": next_steps,
        }
