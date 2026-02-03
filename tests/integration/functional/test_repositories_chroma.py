from uuid import uuid4

import pytest
from chromadb.utils import embedding_functions

from app.domain.value_objects.chunk import Chunk
from app.infrastructure.repositories.chroma import ChromaVectorRepository


# Mock Embedding Function for Deterministic Tests
class MockEmbeddingFunction(embedding_functions.EmbeddingFunction):
    def __init__(self):
        # Standard __init__ for ChromaDB EmbeddingFunction compatibility
        pass

    def __call__(self, input: list[str]) -> list[list[float]]:
        embeddings = []
        for text in input:
            if text == "query":
                embeddings.append([1.0, 0.0])
            elif text == "exact":
                embeddings.append([1.0, 0.0])
            elif text == "similar":
                embeddings.append([0.9, 0.1])
            elif text == "diverse":
                embeddings.append([0.5, 0.8])
            else:
                embeddings.append([0.1, 0.1])
        return embeddings

@pytest.fixture
def chroma_repo_mmr():
    # Given: Chroma repository with mock embedding function
    repo = ChromaVectorRepository()
    client = repo.client
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
def test_chroma_mmr_diversity_logic(chroma_repo_mmr):
    """
    Scenario: MMR (Maximal Marginal Relevance) should prioritize diversity
    over pure similarity to avoid redundant result sets.
    """
    # Given: Chunks with varying similarity (Exact, Similar, Diverse)
    doc_id = str(uuid4())
    chunks = [
        Chunk(id=str(uuid4()), content="exact", parent_id=doc_id, index=0, metadata={"type": "A"}),
        Chunk(id=str(uuid4()), content="similar", parent_id=doc_id, index=1, metadata={"type": "B"}),
        Chunk(id=str(uuid4()), content="diverse", parent_id=doc_id, index=2, metadata={"type": "C"}),
    ]
    chroma_repo_mmr.save_chunks(chunks)

    # When: Performing standard kNN search
    knn_results = chroma_repo_mmr.search("query", limit=2)
    knn_content = [c.content for c in knn_results]

    # Then: Returns Exact and Similar (The two most similar ones)
    assert "exact" in knn_content
    assert "similar" in knn_content
    assert "diverse" not in knn_content

    # When: Performing MMR search with high diversity penalty
    mmr_results = chroma_repo_mmr.search_mmr("query", limit=2, diversity=0.8)
    mmr_content = [c.content for c in mmr_results]

    # Then: Returns Exact and Diverse (Penalizing the redundant Similar result)
    assert "exact" in mmr_content
    assert "diverse" in mmr_content
    assert "similar" not in mmr_content
