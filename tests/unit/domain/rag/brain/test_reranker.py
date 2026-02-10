import pytest
from unittest.mock import AsyncMock, MagicMock
from app.domain.rag.brain.reranker import Reranker
from app.domain.value_objects.chunk import Chunk

@pytest.fixture
def mock_deps():
    llm = MagicMock()  # Changed to MagicMock because we mock bind() 
    neo4j_doc = MagicMock()
    return llm, neo4j_doc

@pytest.fixture
def reranker(mock_deps):
    return Reranker(*mock_deps)

@pytest.mark.asyncio
async def test_rerank_pointwise(reranker, mock_deps, caplog):
    llm, neo4j_doc = mock_deps
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
    
    # Mock _get_rerank_score directly
    async def mock_get_score(*args, **kwargs):
        return {"score": 5, "reasoning": "good"}
    
    reranker._get_rerank_score = AsyncMock(side_effect=mock_get_score)
    
    # Execute
    reranked, logs = await reranker.rerank("query", [chunk], strategy="pointwise")

    # Verify
    assert len(logs) == 1
    assert logs[0]["status"] == "passed"
    assert len(reranked) == 1
    assert reranked[0].metadata["rerank_score"] == 5
