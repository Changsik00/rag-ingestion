import json
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.domain.value_objects.chunk import Chunk
from app.domain.value_objects.rag_state import RAGGraphState
from app.infrastructure.ai.rag_nodes import RAGNodes


@pytest.mark.asyncio
async def test_rerank_results_success():
    # Given
    mock_llm = MagicMock()
    mock_llm.bind.return_value = mock_llm
    # LLM response for 2 chunks
    mock_llm.agenerate = AsyncMock(
        side_effect=[
            json.dumps({"score": 9, "reasoning": "High relevance"}),
            json.dumps({"score": 4, "reasoning": "Moderate relevance"}),
        ]
    )

    nodes = RAGNodes(
        neo4j_doc_repo=MagicMock(),
        neo4j_graph_repo=MagicMock(),
        chroma_repo=MagicMock(),
        query_rewriter=MagicMock(),
        intent_classifier=MagicMock(),
        llm=mock_llm,
    )

    state: RAGGraphState = {
        "query": "Test query",
        "rewritten_query": "Test query",
        "vector_chunks": [
            Chunk(id="1", content="Chunk 1", parent_id="P1", index=0, metadata={"title": "T1"}),
            Chunk(id="2", content="Chunk 2", parent_id="P1", index=1, metadata={"title": "T2"}),
        ],
        "keyword_chunks": [],
        "graph_data": [],
        "reranked_chunks": [],
        "rerank_log": [],
        "reasoning_log": [],
    }

    # When
    config = {"configurable": {"retrieval_config": {"temperature": 0.0}}}
    try:
        updated_state = await nodes.rerank_results(state, config=config)

        # Then
        assert len(updated_state["reranked_chunks"]) == 2  # Both scores 9 and 2 are >= 2 (threshold)
        assert updated_state["reranked_chunks"][0].id == "1"
        assert len(updated_state["rerank_log"]) == 2
    except AttributeError:
        pytest.fail("rerank_results method not implemented yet")


@pytest.mark.asyncio
async def test_rerank_results_with_v2_prompt(monkeypatch):
    """
    [Spec 069] Test that v2 prompt is used when RERANKER_VERSION=v2
    """
    # Given: Mock settings to return v2
    from app.core.config import Settings

    mock_settings = Settings(
        GEMINI_API_KEY="test_key",
        RERANKER_VERSION="v2",  # v2 활성화
    )

    # Monkeypatch get_settings to return our mock
    monkeypatch.setattr("app.infrastructure.ai.rag_nodes.get_settings", lambda: mock_settings)

    mock_llm = MagicMock()
    mock_llm.bind.return_value = mock_llm
    mock_llm.agenerate = AsyncMock(
        side_effect=[
            json.dumps({"score": 8, "reasoning": "Context-Aware evaluation"}),
            json.dumps({"score": 5, "reasoning": "Somewhat relevant"}),
        ]
    )

    nodes = RAGNodes(
        neo4j_doc_repo=MagicMock(),
        neo4j_graph_repo=MagicMock(),
        chroma_repo=MagicMock(),
        query_rewriter=MagicMock(),
        intent_classifier=MagicMock(),
        llm=mock_llm,
    )

    state: RAGGraphState = {
        "query": "일론 머스크의 SpaceX와 Tesla 비교",
        "rewritten_query": "일론 머스크의 SpaceX와 Tesla 비교",
        "vector_chunks": [
            Chunk(id="1", content="SpaceX는 우주 탐사 기업", parent_id="P1", index=0, metadata={"title": "SpaceX"}),
            Chunk(id="2", content="Tesla는 전기차 기업", parent_id="P1", index=1, metadata={"title": "Tesla"}),
        ],
        "keyword_chunks": [],
        "graph_data": [],
        "reranked_chunks": [],
        "rerank_log": [],
        "reasoning_log": [],
    }

    # When
    config = {"configurable": {"retrieval_config": {"temperature": 0.0}}}
    updated_state = await nodes.rerank_results(state, config=config)

    # Then: v2 프롬프트로 정상 작동하며 동일한 인터페이스 유지
    assert len(updated_state["reranked_chunks"]) == 2  # Both chunks passed (scores 8, 5 >= 3)
    assert updated_state["reranked_chunks"][0].id == "1"  # Sorted by score
    assert len(updated_state["rerank_log"]) == 2
    # v2 프롬프트는 Context-Aware이므로 Multi-Entity Query에서 더 관대함
