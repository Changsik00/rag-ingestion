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
            json.dumps({"score": 2, "reasoning": "Low relevance"}),
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
