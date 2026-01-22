import pytest
from uuid import uuid4
from datetime import datetime
from unittest.mock import MagicMock, AsyncMock

from app.domain.entities.document import Document
from app.domain.entities.chunk import Chunk
from app.domain.services.rag_service import RAGService
from app.infrastructure.storage.composite import CompositeStorage
from app.infrastructure.storage.neo4j_document_repository import Neo4jStorage
from app.infrastructure.storage.chroma import ChromaStorage

@pytest.fixture
def mock_deps():
    neo4j_doc_repo = MagicMock(spec=Neo4jStorage)
    neo4j_graph_repo = MagicMock()
    chroma_repo = MagicMock(spec=ChromaStorage)
    # CompositeStorage wraps neo4j and chroma
    composite_storage = CompositeStorage(neo4j_doc_repo, chroma_repo)
    
    query_rewriter = MagicMock()
    llm = MagicMock()
    
    return {
        "neo4j_doc": neo4j_doc_repo,
        "chroma": chroma_repo,
        "composite": composite_storage,
        "rewriter": query_rewriter,
        "llm": llm,
        "neo4j_graph": neo4j_graph_repo
    }

@pytest.mark.asyncio
async def test_scenario_1_homonym_isolation(mock_deps):
    """
    Scenario 1: The "Homonym" Test (Isolation)
    - Source A: Apple Tech
    - Source B: Apple Fruit
    - Filter: Source A -> Should only retrieve Tech content
    """
    deps = mock_deps
    service = RAGService(
        neo4j_doc_repo=deps["neo4j_doc"],
        neo4j_graph_repo=deps["neo4j_graph"], # Service might use composite or separate repos depending on impl
        chroma_repo=deps["chroma"],
        query_rewriter=deps["rewriter"],
        llm=deps["llm"]
    )
    
    # Mock Data
    doc_a_id = "doc-tech"
    doc_b_id = "doc-fruit"
    
    chunk_tech = Chunk(id=uuid4(), content="iPhone MacBook Steve Jobs", parent_id=doc_a_id, index=0, metadata={"source": "wiki_tech"})
    chunk_fruit = Chunk(id=uuid4(), content="Red Delicious Vitamin C", parent_id=doc_b_id, index=0, metadata={"source": "wiki_fruit"})

    # Setup Mocks to simulate Filtering Behavior (This is what we expect the Repo to do)
    # If filter is doc_a, return chunk_tech. If doc_b, return chunk_fruit.
    
    def search_side_effect(query, limit=5, filters=None):
        if not filters:
            return [chunk_tech, chunk_fruit]
        
        target_ids = filters.get("doc_id")
        if isinstance(target_ids, str):
            target_ids = [target_ids]
            
        results = []
        if doc_a_id in target_ids:
            results.append(chunk_tech)
        if doc_b_id in target_ids:
            results.append(chunk_fruit)
        return results

    # We are mocking the CompositeStorage behavior which delegates to Neo4j/Chroma
    # Since RAGService uses repositories directly (currently), we check if it passes filters correctly
    
    # Update: RAGService likely calls search on repositories.
    # We need to ensure RAGService accepts filters and passes them down.
    
    # 1. Filter: Source A
    await service.retrieve_and_generate("Apple Features", filters={"doc_id": doc_a_id})
    
    # Verify Repos were called with filters
    # Note: RAGService currently calls both neo4j and chroma
    deps["neo4j_doc"].search.assert_called()
    call_kwargs = deps["neo4j_doc"].search.call_args.kwargs
    assert call_kwargs.get("filters") == {"doc_id": doc_a_id}
    
    deps["chroma"].search_mmr.assert_called()
    # Check if search_mmr receives filters. Depending on impl, might be kwargs or pos arg.
    # Let's assume interface update: search_mmr(query, filters=...)
    chroma_kwargs = deps["chroma"].search_mmr.call_args.kwargs
    assert chroma_kwargs.get("filters") == {"doc_id": doc_a_id}


@pytest.mark.asyncio
async def test_scenario_2_context_switch_priority(mock_deps):
    """
    Scenario 2: The "Context Switch" Test (System Priority)
    - History: Steve Jobs (Tech)
    - Action: Switch Filter to Fruit
    - Query: Apple Features
    - Expectation: System enforces Fruit filter despite Tech history
    """
    deps = mock_deps
    service = RAGService(
        neo4j_doc_repo=deps["neo4j_doc"],
        neo4j_graph_repo=deps["neo4j_graph"],
        chroma_repo=deps["chroma"],
        query_rewriter=deps["rewriter"],
        llm=deps["llm"]
    )

    doc_fruit_id = "doc-fruit"
    
    # History context (Tech)
    history = [
        {"role": "user", "content": "Who is Steve Jobs?"},
        {"role": "assistant", "content": "He founded Apple."}
    ]
    
    # Switch Filter to Fruit
    await service.retrieve_and_generate("Apple Features", history=history, filters={"doc_id": doc_fruit_id})
    
    # Verify Filter is passed despite history
    deps["neo4j_doc"].search.assert_called()
    assert deps["neo4j_doc"].search.call_args.kwargs.get("filters") == {"doc_id": doc_fruit_id}


@pytest.mark.asyncio
async def test_scenario_3_source_injection_purity(mock_deps):
    """
    Scenario 3: The "Source Injection & Purity" Test
    - History: Tech context
    - Action: Inject Source C (Keyboard) & Filter to C
    - Expectation: Strict isolation to C
    """
    deps = mock_deps
    service = RAGService(
        neo4j_doc_repo=deps["neo4j_doc"],
        neo4j_graph_repo=deps["neo4j_graph"],
        chroma_repo=deps["chroma"],
        query_rewriter=deps["rewriter"],
        llm=deps["llm"]
    )
    
    doc_c_id = "doc-keyboard"
    
    # History context (Tech)
    history = [
        {"role": "user", "content": "Tell me about iPhone"},
        {"role": "assistant", "content": "It's a smartphone."}
    ]
    
    # New Query with new Source Filter
    await service.retrieve_and_generate("Summarize this", history=history, filters={"doc_id": doc_c_id})
    
    # Verify Repos called ONLY with Source C filter
    deps["neo4j_doc"].search.assert_called()
    filter_arg = deps["neo4j_doc"].search.call_args.kwargs.get("filters")
    assert filter_arg == {"doc_id": doc_c_id}
