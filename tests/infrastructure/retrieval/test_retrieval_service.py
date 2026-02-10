from unittest.mock import MagicMock

import pytest

from app.domain.value_objects.chunk import Chunk
from app.infrastructure.retrieval.service import RetrievalService


@pytest.fixture
def mock_repos():
    # Use standard MagicMocks for sync calls inside asyncio.to_thread
    neo4j_doc = MagicMock()
    neo4j_graph = MagicMock()
    chroma = MagicMock()
    return neo4j_doc, neo4j_graph, chroma

@pytest.fixture
def retrieval_service(mock_repos):
    neo4j_doc, neo4j_graph, chroma = mock_repos
    return RetrievalService(neo4j_doc, neo4j_graph, chroma)

@pytest.mark.asyncio
async def test_hybrid_search(retrieval_service, mock_repos):
    neo4j_doc, neo4j_graph, chroma = mock_repos

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
