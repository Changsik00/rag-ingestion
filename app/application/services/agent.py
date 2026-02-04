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

logger = logging.getLogger(__name__)


class AgentState(TypedDict):
    """Admin Agent의 상태를 정의하는 TypedDict"""

    messages: Annotated[list[AnyMessage], add_messages]
    intent: str
    tool_output: str
    context_data: dict  # RAG 상세 정보 (chunks, graph) 전달용
    filters: dict | None  # RAG 필터링용
    thread_id: str | None  # Thread ID (Spec 034)
    hitl_enabled: bool  # HITL Toggle Status
    # Spec 045: Interactive Refinement
    draft_content: str | None
    is_clarification: bool
    missing_slots: list[str]


class ConversationalRAGAgent:
    """
    RAG Playground 및 관리자용 Orchestration Agent.
    수집(Ingest)과 검색(Search) 의도를 구분하여 처리합니다.
    """

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

    def __init__(self, rag_service: "RAG", ingestion_service: "Ingestion"):
        self.rag_service = rag_service
        self.ingestion_service = ingestion_service
        self.llm = ChatGoogleGenerativeAI(
            model=get_settings().GEMINI_MODEL_NAME, temperature=0, google_api_key=get_settings().GEMINI_API_KEY
        )

    def build_workflow(self, checkpointer: Any = None, interrupt_before: list[str] | None = None):
        """LangGraph 워크플로우를 빌드하고 컴파일합니다."""
        workflow = StateGraph(AgentState)

        workflow.add_node("router", self.router_node)
        workflow.add_node("ingest", self.ingest_node)
        workflow.add_node("search", self.search_node)
        workflow.add_node("human_review", self.human_review_node)
        workflow.add_node("clarify", self.clarify_node)  # Spec 045

        workflow.set_entry_point("router")

        workflow.add_conditional_edges(
            "router",
            self.route_logic,
            {
                "ingest": "ingest",
                "search": "search",
                "clarify": "clarify",  # Spec 045
            },
        )

        workflow.add_edge("ingest", "search")  # 수집 완료 후 요약을 위해 검색 노드로 이동

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

    def route_logic(self, state: AgentState) -> Literal["ingest", "search", "clarify"]:
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
            1. If 'url' is missing, ask the user to provide the URL to ingest or summarize.
            2. If 'topic' is missing, ask the user what topic they want to search for.
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

    async def router_node(self, state: AgentState) -> dict:
        messages = state["messages"]
        last_user_msg = messages[-1].content if messages else ""

        # 의도 분류 프롬프트 (Spec 045: Clarify 추가)
        prompt = ChatPromptTemplate.from_template(
            """
            Analyze the user's input and determine the intent.

            check for missing critical information:
            - If intent is 'ingest', a URL is REQUIRED. If URL is missing, return 'clarify'.
            - If intent is 'search', a specific topic/question is REQUIRED. However, if the user asks to "summarize this" or "explain this" (referring to context/history), classify as 'search'.

            Options:
            - 'ingest': The user wants to read, learn, scrape, or ingest a URL. (e.g. "Read this link", "Ingest https://...")
            - 'search': The user is asking a specific question, discussing a topic, or asking for a summary of the context. (e.g. "What is RAG?", "Who is Elon Musk?", "일론 머스크가 누구야?", "이거 요약해줘")
            - 'clarify': The input is ambiguous or missing required arguments. (e.g. "Do it", "help me", "알려줘")

            Input: {input}

            Return ONLY 'ingest', 'search', or 'clarify'.
            """
        )
        prompt_val = prompt.invoke({"input": last_user_msg})
        response = await self.llm.ainvoke(prompt_val)

        if hasattr(response, "content"):
            intent = self._extract_text_content(response.content).strip().lower()
        else:
            intent = str(response).strip().lower()

        if "ingest" in intent:
            intent = "ingest"
        elif "search" in intent:
            intent = "search"
        else:
            intent = "clarify"

        # Basic slot filling check (fallback if LLM misses it)
        missing_slots = []
        if intent == "ingest":
            url_pattern = r"http[s]?://"
            if not re.search(url_pattern, last_user_msg):
                intent = "clarify"
                missing_slots.append("url")

        return {"intent": intent, "missing_slots": missing_slots}

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
