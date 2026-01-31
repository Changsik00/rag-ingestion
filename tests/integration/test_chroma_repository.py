from uuid import uuid4

import pytest
from chromadb.utils import embedding_functions

from app.domain.value_objects.chunk import Chunk
from app.infrastructure.repositories.chroma import ChromaVectorRepository

pytestmark = pytest.mark.skip(reason="Requires infrastructure setup - see specs/integration-test-improvement.md")



# Mock Embedding Function for Deterministic Tests
class MockEmbeddingFunction(embedding_functions.EmbeddingFunction):
    def __call__(self, input: list[str]) -> list[list[float]]:
        # Simple deterministic mapping for test strings
        # Query: "query" -> [1.0, 0.0]
        # Doc A: "exact" -> [1.0, 0.0]  (Sim=1.0)
        # Doc B: "similar" -> [0.9, 0.1] (Sim~0.9)
        # Doc C: "diverse" -> [0.5, 0.8] (Sim~0.5)

        embeddings = []
        for text in input:
            if text == "query":
                embeddings.append([1.0, 0.0])
            elif text == "exact":
                embeddings.append([1.0, 0.0])
            elif text == "similar":
                embeddings.append([0.9, 0.1])
            elif text == "diverse":
                embeddings.append([0.5, 0.8])  # Orthogonal-ish to [1,0]
            else:
                embeddings.append([0.1, 0.1])
        return embeddings


@pytest.fixture
def chroma_repo_mmr():
    # Setup Chroma with Mock Embedding
    repo = ChromaVectorRepository()
    # Replace collection with one using Mock EF
    client = repo.client
    # Delete if exists to clean state
    try:
        client.delete_collection("test_mmr")
    except Exception:
        pass

    mock_ef = MockEmbeddingFunction()
    repo.collection = client.create_collection(name="test_mmr", embedding_function=mock_ef)
    yield repo
    try:
        client.delete_collection("test_mmr")
    except Exception:
        pass


@pytest.mark.integration
def test_chroma_mmr_diversity(chroma_repo_mmr):
    """
    Scenario: Verify MMR returns diverse results compared to kNN
    1. Save 3 chunks: Exact, Similar (redundant), Diverse.
    2. kNN search (limit 2) should return Exact + Similar.
    3. MMR search (limit 2) should return Exact + Diverse.
    """
    # 1. Setup Data
    doc_id = str(uuid4())
    chunks = [
        Chunk(id=str(uuid4()), content="exact", parent_id=doc_id, index=0, metadata={"type": "A"}),
        Chunk(id=str(uuid4()), content="similar", parent_id=doc_id, index=1, metadata={"type": "B"}),
        Chunk(id=str(uuid4()), content="diverse", parent_id=doc_id, index=2, metadata={"type": "C"}),
    ]
    chroma_repo_mmr.save_chunks(chunks)

    # 2. kNN Search (Standard)
    # Chroma standard search is kNN
    knn_results = chroma_repo_mmr.search("query", limit=2)
    knn_content = [c.content for c in knn_results]

    # Expect Exact and Similar (Top 2 similarity)
    assert "exact" in knn_content
    assert "similar" in knn_content
    assert "diverse" not in knn_content

    # 3. MMR Search (TDD: Method not implemented yet)
    if hasattr(chroma_repo_mmr, "search_mmr"):
        mmr_results = chroma_repo_mmr.search_mmr("query", limit=2, diversity=0.8)  # High diversity penalty
        mmr_content = [c.content for c in mmr_results]

        # Expect Exact and Diverse (Similar penalized for being too close to Exact)
        assert "exact" in mmr_content
        assert "diverse" in mmr_content, "MMR should pick diverse result over similar one"
        assert "similar" not in mmr_content
    else:
        pytest.fail("search_mmr not implemented yet")
