"""
RAG Service - LangGraph 기반으로 전환.

Spec 033: LangGraph State Management
기존 함수 기반 로직을 LangGraph Orchestration으로 변경하여
의사결정 과정을 State로 관리합니다.
"""

import logging
from dataclasses import dataclass

from langgraph.graph.state import CompiledStateGraph
from pydantic import Field

from app.domain.value_objects.chunk import Chunk
from app.domain.value_objects.intent import UserIntent
from app.infrastructure.monitoring.langfuse_helper import get_langfuse_handler

logger = logging.getLogger(__name__)


@dataclass
class RAGResult:
    """RAG Pipeline 실행 결과"""

    answer: str
    rewritten_query: str
    vector_chunks: list[Chunk]
    keyword_chunks: list[Chunk]
    graph_data: list[dict]
    full_context: str
    citations: list[dict] = Field(default_factory=list)
    user_intent: UserIntent | None = None
    rerank_log: list[dict] = Field(default_factory=list)
    trace_id: str | None = None
    trace_url: str | None = None


class RAG:
    """
    LangGraph 기반 RAG Orchestrator.

    Spec 033에서 기존 함수 기반 로직을 Graph 기반으로 전환했습니다.
    모든 비즈니스 로직은 RAGNodes로 분리되었고,
    이 서비스는 Graph를 실행하고 결과를 변환하는 역할만 합니다.
    """

    def __init__(self, graph: CompiledStateGraph):
        """
        Args:
            graph: 컴파일된 RAG Graph (RAGGraphBuilder.build() 결과)
        """
        self.graph = graph

    async def retrieve_and_generate(
        self,
        query: str,
        history: list[dict],
        filters: dict | None = None,
        thread_id: str | None = None,
        retrieval_config: dict | None = None,
    ) -> RAGResult:
        """
        RAG Pipeline 실행: Intent → Rewrite → Hybrid Search → Generate.

        Args:
            query: 사용자 질문
            history: 대화 이력
            filters: 수동 필터 (Optional)
            thread_id: Checkpointer Thread ID (Optional)
            retrieval_config: Advanced Settings (Optional)

        Returns:
            RAGResult: 최종 답변 및 중간 결과
        """
        # Initial State 구성
        initial_state = {
            "query": query,
            "history": history,
            "manual_filters": filters,
            # Initialize empty fields
            "user_intent": None,
            "rewritten_query": None,
            "auto_filters": None,
            "final_filters": None,
            "vector_chunks": [],
            "keyword_chunks": [],
            "graph_data": [],
            "full_context": "",
            "final_answer": "",
        }

        # Config 설정 (Thread ID가 있으면 Checkpointer 사용)
        config = {"configurable": {"thread_id": thread_id}} if thread_id else {"configurable": {}}

        # [Spec 064] Observability (LangFuse)
        langfuse_handler = get_langfuse_handler(
            trace_name="RAG Pipeline Interaction",
            # user_id can be added if auth is implemented
        )
        if langfuse_handler:
            config["callbacks"] = [langfuse_handler]

        # Spec 055: Inject retrieval_config
        if retrieval_config:
            config["configurable"]["retrieval_config"] = retrieval_config

        # Graph 실행
        result_state = await self.graph.ainvoke(initial_state, config=config)

        # State → RAGResult 변환
        return self._state_to_result(result_state, langfuse_handler)

    def _state_to_result(self, state: dict, langfuse_handler: object | None = None) -> RAGResult:
        """
        RAGGraphState를 RAGResult로 변환.

        Args:
            state: Graph 실행 후 최종 State

        Returns:
            RAGResult: API Response 형식
        """
        return RAGResult(
            answer=state.get("final_answer", ""),
            rewritten_query=state.get("rewritten_query", state["query"]),
            vector_chunks=state.get("vector_chunks", []),
            keyword_chunks=state.get("keyword_chunks", []),
            graph_data=state.get("graph_data", []),
            full_context=state.get("full_context", ""),
            citations=state.get("citations", []),
            user_intent=state.get("user_intent"),
            rerank_log=state.get("rerank_log", []),
            trace_id=langfuse_handler.get_trace_id() if langfuse_handler else None,
            trace_url=langfuse_handler.get_trace_url() if langfuse_handler else None,
        )
