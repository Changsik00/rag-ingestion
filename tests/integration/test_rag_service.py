from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from app.application.services.rag import RAG
from app.domain.entities.chunk import Chunk
from app.domain.value_objects.intent import IntentType, UserIntent


@pytest.mark.asyncio
async def test_rag_service_orchestration():
    """
    Scenario: Verify RAG orchestration flow with LangGraph.

    Spec 033: RAG가 Graph 기반으로 리팩토링되어,
    Graph가 반환한 State를 RAGResult로 변환하는지 검증합니다.

    Given: Mock Graph가 완전한 RAGGraphState를 반환
    When: RAG.retrieve_and_generate() 호출
    Then: State가 RAGResult로 올바르게 변환됨
    """
    # Given: Mock Graph 생성
    mock_graph = MagicMock()

    # Mock ainvoke: 완전한 RAGGraphState 반환
    chunk_v = Chunk(
        id=uuid4(), content="Vector Content", parent_id="doc-1", index=0, metadata={"source": "wiki", "title": "V"}
    )
    chunk_k = Chunk(
        id=uuid4(), content="Keyword Content", parent_id="doc-1", index=0, metadata={"source": "news", "title": "K"}
    )

    mock_result_state = {
        "query": "Original Query",
        "history": [],
        "manual_filters": None,
        "user_intent": UserIntent(
            intent=IntentType.GENERAL_QUERY, targets=[], reasoning="General question for testing"
        ),
        "rewritten_query": "Rewritten Query",
        "auto_filters": None,
        "final_filters": None,
        "vector_chunks": [chunk_v],
        "keyword_chunks": [chunk_k],
        "graph_data": [{"source": "Elon", "relationship": "FOUNDED", "target": "Tesla"}],
        "full_context": "Mock context with Vector Content, Keyword Content, and Elon FOUNDED Tesla",
        "final_answer": "Final Answer",
    }

    mock_graph.ainvoke = AsyncMock(return_value=mock_result_state)

    # When: RAG 생성 및 실행
    service = RAG(graph=mock_graph)

    history = []
    response = await service.retrieve_and_generate("Original Query", history)

    # Then: Verification
    # 1. Graph가 올바른 initial_state로 호출되었는지 확인
    mock_graph.ainvoke.assert_called_once()
    call_args = mock_graph.ainvoke.call_args
    initial_state = call_args[0][0]

    assert initial_state["query"] == "Original Query"
    assert initial_state["history"] == []
    assert initial_state["manual_filters"] is None

    # 2. State → RAGResult 변환 확인
    assert response.answer == "Final Answer"
    assert response.rewritten_query == "Rewritten Query"
    assert len(response.vector_chunks) == 1
    assert len(response.keyword_chunks) == 1
    assert len(response.graph_data) == 1
    assert response.user_intent.intent == IntentType.GENERAL_QUERY
    assert response.full_context == "Mock context with Vector Content, Keyword Content, and Elon FOUNDED Tesla"
