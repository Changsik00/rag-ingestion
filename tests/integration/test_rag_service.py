from unittest.mock import MagicMock
from uuid import uuid4

import pytest

from app.domain.entities.chunk import Chunk
from app.domain.services.rag_service import RAGService


@pytest.fixture
def mock_deps():
    neo4j_doc_repo = MagicMock()
    neo4j_graph_repo = MagicMock()
    chroma_repo = MagicMock()
    query_rewriter = MagicMock()
    llm = MagicMock()

    return {
        "neo4j_doc": neo4j_doc_repo,
        "neo4j_graph": neo4j_graph_repo,
        "chroma": chroma_repo,
        "rewriter": query_rewriter,
        "llm": llm,
    }


@pytest.mark.asyncio
async def test_rag_service_orchestration(mock_deps):
    """
    Scenario: Verify RAGService orchestration flow.
    1. Rewrite Query.
    2. Search Hybrid (Vector MMR + Keyword).
    3. Search Graph (SubGraph).
    4. Format Context & Generate Answer.
    """
    deps = mock_deps
    service = RAGService(
        neo4j_doc_repo=deps["neo4j_doc"],
        neo4j_graph_repo=deps["neo4j_graph"],
        chroma_repo=deps["chroma"],
        query_rewriter=deps["rewriter"],
        llm=deps["llm"],
    )

    # Setup Mocks
    # 1. Rewrite
    deps["rewriter"].rewrite.return_value = "Rewritten Query"

    # 2. Vector Search (MMR)
    chunk_v = Chunk(
        id=uuid4(), content="Vector Content", parent_id="doc-1", index=0, metadata={"source": "wiki", "title": "V"}
    )
    deps["chroma"].search_mmr.return_value = [chunk_v]

    # 3. Keyword Search
    chunk_k = Chunk(
        id=uuid4(), content="Keyword Content", parent_id="doc-1", index=0, metadata={"source": "news", "title": "K"}
    )
    deps["neo4j_doc"].search.return_value = [chunk_k]

    # 4. Graph Search
    deps["neo4j_graph"].get_subgraph.return_value = [{"source": "Elon", "relationship": "FOUNDED", "target": "Tesla"}]

    # 5. LLM Generation
    deps["llm"].generate.return_value = "Final Answer"

    # Execution
    history = []
    response = await service.retrieve_and_generate("Original Query", history)

    # Verification
    # 1. Check Rewrite
    deps["rewriter"].rewrite.assert_called_with("Original Query", history)

    # 2. Check Parallel Search (Sequential is fine for MVP, but inputs must be from rewritten query)
    deps["chroma"].search_mmr.assert_called()
    assert deps["chroma"].search_mmr.call_args[0][0] == "Rewritten Query"

    deps["neo4j_doc"].search.assert_called()
    assert deps["neo4j_doc"].search.call_args[0][0] == "Rewritten Query"

    # 3. Check Graph Context
    # Check if context passed to LLM includes Graph Facts
    call_args = deps["llm"].generate.call_args
    assert call_args is not None
    prompt_sent = str(call_args)  # Simple check
    assert "Vector Content" in prompt_sent
    assert "Keyword Content" in prompt_sent
    assert "Elon" in prompt_sent and "FOUNDED" in prompt_sent and "Tesla" in prompt_sent

    # 4. Check Result
    assert response.answer == "Final Answer"

    # 5. Check Debug Info
    assert response.rewritten_query == "Rewritten Query"
    assert len(response.vector_chunks) == 1
    assert len(response.keyword_chunks) == 1
    assert len(response.graph_data) == 1
