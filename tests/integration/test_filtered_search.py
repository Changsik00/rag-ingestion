from uuid import uuid4

import pytest

from app.domain.entities.document import Document
from app.domain.value_objects.chunk import Chunk
from app.infrastructure.repositories.chroma import ChromaVectorRepository
from app.infrastructure.repositories.composite import CompositeDocumentRepository
from app.infrastructure.repositories.neo4j_document_repository import Neo4jDocumentRepository
from app.interfaces.api.dependencies import get_neo4j_driver

# pytestmark = pytest.mark.skip(reason="Requires infrastructure setup - see specs/integration-test-improvement.md")


@pytest.fixture(scope="module")
def stored_data():
    """
    Set up two distinct documents:
    1. Doc A (Tech): Apple Inc. related content.
    2. Doc B (Fruit): Apple Fruit related content.
    """
    driver = get_neo4j_driver()
    neo4j_repo = Neo4jDocumentRepository(driver)
    chroma_repo = ChromaVectorRepository()
    composite_repo = CompositeDocumentRepository(neo4j_repo, chroma_repo)

    # Document A: Apple (Tech)
    doc_a_id = str(uuid4())
    doc_a = Document(
        id=doc_a_id,
        content="Apple Inc. designs, manufactures, and markets smartphones, personal computers, tablets, wearables, and accessories.",
        metadata={"title": "Apple (Tech)", "source_id": "tech_wiki"},
    )
    chunks_a = [
        Chunk(
            id=str(uuid4()),
            content="Apple generally releases a new iPhone every September.",
            parent_id=doc_a_id,
            index=0,
            metadata={"source": "tech_wiki"},
        ),
        Chunk(
            id=str(uuid4()),
            content="macOS is the operating system for Apple's Mac computers.",
            parent_id=doc_a_id,
            index=1,
            metadata={"source": "tech_wiki"},
        ),
    ]

    # Document B: Apple (Fruit)
    doc_b_id = str(uuid4())
    doc_b = Document(
        id=doc_b_id,
        content="An apple is a round, edible fruit produced by an apple tree (Malus spp.).",
        metadata={"title": "Apple (Fruit)", "source_id": "fruit_wiki"},
    )
    chunks_b = [
        Chunk(
            id=str(uuid4()),
            content="Apples are generally red, green, or yellow in color.",
            parent_id=doc_b_id,
            index=0,
            metadata={"source": "fruit_wiki"},
        ),
        Chunk(
            id=str(uuid4()),
            content="Apples are rich in fiber and vitamin C.",
            parent_id=doc_b_id,
            index=1,
            metadata={"source": "fruit_wiki"},
        ),
    ]

    # Save to Composite Storage (Both Graph & Vector)
    composite_repo.save_with_chunks(doc_a, chunks_a)
    composite_repo.save_with_chunks(doc_b, chunks_b)

    yield composite_repo, doc_a_id, doc_b_id

    # Cleanup (Optional, but good practice if not using ephemeral container)
    # Ideally, we should delete these docs.
    pass


@pytest.mark.integration
def test_homonym_isolation(stored_data):
    """
    Scenario 1: The 'Homonym' Test
    Search for 'Apple' filtering only 'Fruit' document.
    Should NOT retrieve any 'iPhone' or 'Mac' related chunks.
    """
    repo, doc_tech_id, doc_fruit_id = stored_data

    query = "Apple features"

    # 1. Search in Fruit Context
    # Note: filters argument is not yet implemented in interface, so this might fail statically or run ignoring filter.
    # We expect 'filters' to be accepted in the future implementation.
    try:
        results_fruit = repo.search(query, limit=5, filters={"doc_id": doc_fruit_id})
    except TypeError:
        pytest.fail("Repository.search does not accept 'filters' argument yet.")

    # Verification
    for chunk in results_fruit:
        print(f"DEBUG: Chunk Parent ID: {chunk.parent_id} (Type: {type(chunk.parent_id)}) vs Target: {doc_fruit_id}")
        assert str(chunk.parent_id) == str(doc_fruit_id), f"Found chunk from wrong document! content: {chunk.content}"
        assert "iPhone" not in chunk.content
        assert "Mac" not in chunk.content
        assert (
            "red" in chunk.content or "fiber" in chunk.content or "edible" in chunk.content or "fruit" in chunk.content
        )


@pytest.mark.integration
def test_context_switch(stored_data):
    """
    Scenario 2: The 'Context Switch' Test
    Search for 'Operating System' in Tech Context -> Found.
    Search for 'Operating System' in Fruit Context -> Not Found (or irrelevant).
    """
    repo, doc_tech_id, doc_fruit_id = stored_data

    query = "Operating System"

    # 1. Search in Tech Context
    results_tech = repo.search(query, limit=5, filters={"doc_id": doc_tech_id})
    assert len(results_tech) > 0
    assert any("macOS" in c.content for c in results_tech)

    # 2. Search in Fruit Context
    results_fruit = repo.search(query, limit=5, filters={"doc_id": doc_fruit_id})
    # Should be empty or at least not contain macOS
    for chunk in results_fruit:
        assert "macOS" not in chunk.content


@pytest.mark.integration
def test_multi_filter_isolation(stored_data):
    """
    Scenario 3: Multi-value filtering
    If we support lists in filters (e.g. doc_id in [A, B]), verify it works.
    """
    repo, doc_tech_id, doc_fruit_id = stored_data

    # Filter for BOTH docs
    results = repo.search("Apple", limit=10, filters={"doc_id": [doc_tech_id, doc_fruit_id]})

    # Needs to find chunks from BOTH
    found_ids = {str(c.parent_id) for c in results}
    assert str(doc_tech_id) in found_ids
    assert str(doc_fruit_id) in found_ids
