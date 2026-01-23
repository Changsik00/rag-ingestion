import logging
from typing import Annotated, Literal, TypedDict

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
    messages: Annotated[list[AnyMessage], add_messages]
    intent: str
    tool_output: str
    context_data: dict  # For passing RAG details (chunks, graph) to UI
    filters: dict | None  # For RAG filtering


class AdminAgent:
    def __init__(self, rag_service: RAGService, ingestion_service: IngestionService):
        self.rag_service = rag_service
        self.ingestion_service = ingestion_service
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash-exp", temperature=0, google_api_key=get_settings().GEMINI_API_KEY
        )
        # Default workflow (No HITL)
        self.workflow = self._build_graph()

    def _build_graph(self, interrupt_before: list[str] | None = None):
        workflow = StateGraph(AdminState)

        workflow.add_node("router", self.router_node)
        workflow.add_node("ingest", self.ingest_node)
        workflow.add_node("search", self.search_node)

        workflow.set_entry_point("router")

        workflow.add_conditional_edges("router", self.route_logic, {"ingest": "ingest", "search": "search"})

        workflow.add_edge("ingest", "search")  # Ingest finishes -> Go to Search (Summary)
        workflow.add_edge("search", END)  # Search finishes and returns answer

        # Checkpointer is handled by RAGService, but AdminAgent itself 
        # can also have one if we want HITL at this top level.
        # For now, we mainly want to pass HITL signals down to RAG.
        from app.interfaces.api.dependencies import get_checkpointer
        return workflow.compile(checkpointer=get_checkpointer(), interrupt_before=interrupt_before)

    def route_logic(self, state: AdminState) -> Literal["ingest", "search"]:
        return state["intent"]

    def router_node(self, state: AdminState) -> dict:
        messages = state["messages"]
        last_user_msg = messages[-1].content if messages else ""

        # Simple Logic + LLM Verification
        # If explicit URL is present, prefer ingest unless instructed otherwise

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

        logger.info(f"Router Decision: {intent} for input: {last_user_msg[:50]}...")

        if "ingest" in intent:
            intent = "ingest"
        else:
            intent = "search"

        logger.info(f"Router Decision: {intent} for input: {last_user_msg[:50]}...")
        return {"intent": intent}

    def ingest_node(self, state: AdminState) -> dict:
        messages = state["messages"]
        last_user_msg = messages[-1].content

        # Extract URL (Simple extraction for now, or use LLM)
        # For robustness, let's use a regex or simple split, but since we are agentic,
        # we can assume the tool can handle it or we extract it.
        # Let's simple split for now, assuming URL is in the text.
        import re

        url_pattern = r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"
        urls = re.findall(url_pattern, last_user_msg)

        if not urls:
            return {
                "messages": [AIMessage(content="URL을 찾을 수 없습니다. 올바른 URL을 입력해주세요.")],
                "tool_output": "No URL found",
            }

        target_url = urls[0]  # Pick first one

        # Call Service (Blocking for MVP)
        job = self.ingestion_service.create_job(target_url)

        # Process synchronously (or use run_in_executor if blocking loop)
        # self.ingestion_service.process_job(job.job_id) -> This is sync implementation?
        # Checked code: process_job is sync.
        # But we are in async context (Admin Agent runs in Streamlit async loop?)
        # AdminAgent methods are sync here but called by LangGraph.
        # LangGraph runs sync if nodes are sync.

        try:
            # Run Ingestion
            # Note: process_job might be blocking heavy IO.
            self.ingestion_service.process_job(job.job_id)

            # Reload job for status
            updated_job = self.ingestion_service.job_repository.get_job(job.job_id)

            if updated_job.status == JobStatus.COMPLETED:
                msg = f"✅ 수집 완료: {target_url}\n\n이제 내용을 요약해드릴게요..."
                # Pass doc_id to filters for immediate searching of THIS document
                if updated_job.docs_ids and len(updated_job.docs_ids) > 0:
                    doc_id = str(updated_job.docs_ids[0])
                    return {"messages": [AIMessage(content=msg)], "tool_output": msg, "filters": {"doc_id": doc_id}}
            else:
                msg = f"❌ 수집 실패: {updated_job.error_message}"

        except Exception as e:
            msg = f"❌ 오류 발생: {str(e)}"

        return {"messages": [AIMessage(content=msg)], "tool_output": msg}

    async def search_node(self, state: AdminState) -> dict:
        # Define as async if we want to call async service
        messages = state["messages"]
        last_user_msg = messages[-1].content

        # Prepare context (excluding last)
        history = [
            {"role": m.type, "content": m.content}
            for m in messages[:-1]
            if m.type in ["human", "ai", "user", "assistant"]
        ]

        filters = state.get("filters")
        # [Spec 034] Pass thread_id from state if present
        thread_id = state.get("thread_id") 
        
        result = await self.rag_service.retrieve_and_generate(
            last_user_msg, 
            history, 
            filters=filters,
            thread_id=thread_id
        )

        context_data = {
            "rewritten_query": result.rewritten_query,
            "vector_chunks": result.vector_chunks,
            "keyword_chunks": result.keyword_chunks,
            "graph_data": result.graph_data,
            "full_context": result.full_context,
            "user_intent": result.user_intent,  # Spec 032
        }

        return {
            "messages": [AIMessage(content=result.answer)],
            "tool_output": "Search Completed",
            "context_data": context_data,
        }


# Helper to expose nodes for testing if needed
def router_node(state: AdminState):
    # This is a bit tricky since it needs 'self'.
    # For testing, we might need to mock the agent or use the class.
    pass
