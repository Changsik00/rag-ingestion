import logging
import re
from typing import Annotated, Any, Literal, TypedDict

from langchain_core.messages import AIMessage, AnyMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import END, StateGraph, add_messages

from app.core.config import get_settings
from app.domain.entities.job import JobStatus
from app.domain.services.rag_service import RAGService
from app.use_cases.ingestion import IngestionService

logger = logging.getLogger(__name__)


class AdminState(TypedDict):
    """Admin Agent의 상태를 정의하는 TypedDict"""

    messages: Annotated[list[AnyMessage], add_messages]
    intent: str
    tool_output: str
    context_data: dict  # RAG 상세 정보 (chunks, graph) 전달용
    filters: dict | None  # RAG 필터링용
    thread_id: str | None  # Thread ID (Spec 034)
    hitl_enabled: bool  # HITL Toggle Status


class AdminAgent:
    """
    RAG Playground 및 관리자용 Orchestration Agent.
    수집(Ingest)과 검색(Search) 의도를 구분하여 처리합니다.
    """

    def __init__(self, rag_service: RAGService, ingestion_service: IngestionService):
        self.rag_service = rag_service
        self.ingestion_service = ingestion_service
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash-exp", temperature=0, google_api_key=get_settings().GEMINI_API_KEY
        )

    def build_workflow(self, checkpointer: Any = None, interrupt_before: list[str] | None = None):
        """LangGraph 워크플로우를 빌드하고 컴파일합니다."""
        workflow = StateGraph(AdminState)

        workflow.add_node("router", self.router_node)
        workflow.add_node("ingest", self.ingest_node)
        workflow.add_node("search", self.search_node)
        workflow.add_node("human_review", self.human_review_node)

        workflow.set_entry_point("router")

        workflow.add_conditional_edges("router", self.route_logic, {"ingest": "ingest", "search": "search"})

        workflow.add_edge("ingest", "search")  # 수집 완료 후 요약을 위해 검색 노드로 이동
        
        # Conditional Edge after Search: Check HITL
        def route_after_search(state: AdminState):
            if state.get("hitl_enabled"):
                return "human_review"
            return END

        workflow.add_conditional_edges("search", route_after_search, {"human_review": "human_review", END: END})
        workflow.add_edge("human_review", END)

        # Default interrupt if checkpointer is provided
        if checkpointer and not interrupt_before:
            interrupt_before = ["human_review"]

        return workflow.compile(checkpointer=checkpointer, interrupt_before=interrupt_before)

    def route_logic(self, state: AdminState) -> Literal["ingest", "search"]:
        return state["intent"]

    def human_review_node(self, state: AdminState) -> dict:
        """HITL Review Node (Pass-through)"""
        return {"tool_output": "Human Review Completed"}

    def router_node(self, state: AdminState) -> dict:
        messages = state["messages"]
        last_user_msg = messages[-1].content if messages else ""

        # 의도 분류 프롬프트
        prompt = ChatPromptTemplate.from_template(
            """
            Analyze the user's input and determine the intent.

            Options:
            - 'ingest': The user wants to read, learn, scrape, or ingest a URL. (e.g. "Read this link", "Ingest https://...")
            - 'search': The user is asking a question or chatting. (e.g. "What is RAG?", "Summarize the doc")

            Input: {input}

            Return ONLY 'ingest' or 'search'.
            """
        )
        prompt_val = prompt.invoke({"input": last_user_msg})
        response = self.llm.invoke(prompt_val)

        if hasattr(response, "content"):
            intent = response.content.strip().lower()
        else:
            intent = str(response).strip().lower()

        if "ingest" in intent:
            intent = "ingest"
        else:
            intent = "search"

        return {"intent": intent}

    def ingest_node(self, state: AdminState) -> dict:
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

    async def search_node(self, state: AdminState) -> dict:
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

        # RAG 검색 및 생성 실행
        result = await self.rag_service.retrieve_and_generate(
            last_user_msg, history, filters=filters, thread_id=thread_id
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
