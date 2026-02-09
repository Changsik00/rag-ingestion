import pytest
from unittest.mock import AsyncMock, MagicMock
from app.infrastructure.rag.retrieval.service import RetrievalService
from app.domain.value_objects.chunk import Chunk

@pytest.fixture
def mock_repos():
    # Use standard MagicMocks for sync calls inside asyncio.to_thread
    neo4j_doc = MagicMock()
    neo4j_graph = MagicMock()
    chroma = MagicMock()
    llm = AsyncMock()
    return neo4j_doc, neo4j_graph, chroma, llm

@pytest.fixture
def retrieval_service(mock_repos):
    neo4j_doc, neo4j_graph, chroma, llm = mock_repos
    return RetrievalService(neo4j_doc, neo4j_graph, chroma, llm)

@pytest.mark.asyncio
async def test_hybrid_search(retrieval_service, mock_repos):
    neo4j_doc, neo4j_graph, chroma, llm = mock_repos
    
    # Setup mocks
    chunk = Chunk(
        id="1", 
        content="test", 
        parent_id="d1", 
        index=0, 
        metadata={"source": "test"}
    )
    # These are sync methods called in threads
    chroma.search_mmr.return_value = [chunk]
    neo4j_doc.search.return_value = [chunk]
    neo4j_graph.get_subgraph.return_value = [{"id": "1", "name": "test"}]
    neo4j_graph.find_shortest_path.return_value = []
    
    # Execute
    v_res, k_res, g_res = await retrieval_service.hybrid_search(
        "query", filters=None, strategy="hybrid"
    )
    
    # Verify
    assert len(v_res) == 1
    assert len(k_res) == 1
    assert len(g_res) == 1
    assert v_res[0].id == "1"

@pytest.mark.asyncio
async def test_rerank_pointwise(retrieval_service, mock_repos, caplog):
    neo4j_doc, neo4j_graph, chroma, llm = mock_repos
    import logging
    caplog.set_level(logging.DEBUG)
    
    # Setup
    chunk = Chunk(
        id="1", 
        content="test", 
        parent_id="d1", 
        index=0, 
        metadata={"source": "test"}
    )
    
    # Mock _get_rerank_score directly to avoid complex LLM mocking
    # This ensures we test the filtering logic in rerank(), not the LLM interaction detail
    async def mock_get_score(*args, **kwargs):
        return {"score": 5, "reasoning": "good"}
    
    retrieval_service._get_rerank_score = AsyncMock(side_effect=mock_get_score)
    
    # Execute
    reranked, logs = await retrieval_service.rerank("query", [chunk], strategy="pointwise")


    # Print logs for debugging
    for record in caplog.records:
        print(f"LOG: {record.levelname} - {record.message}")

    # Verify
    assert len(logs) == 1
    assert logs[0]["status"] == "passed"
    assert len(reranked) == 1
    assert reranked[0].metadata["rerank_score"] == 5
