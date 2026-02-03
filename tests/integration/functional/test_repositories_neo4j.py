import time
from uuid import uuid4

import pytest

from app.domain.entities.document import Document
from app.domain.value_objects.chunk import Chunk
from app.infrastructure.repositories.neo4j_document_repository import Neo4jDocumentRepository
from app.interfaces.api.dependencies import get_neo4j_driver


@pytest.fixture
def neo4j_repo():
    # Given: Neo4j repository instance
    driver = get_neo4j_driver()
    repo = Neo4jDocumentRepository(driver)
    yield repo

@pytest.mark.integration
def test_neo4j_fulltext_search_logic(neo4j_repo):
    """
    Scenario: Verify Neo4j Fulltext Search on Chunks
    """
    # Given: A document and a chunk containing a unique keyword
    doc_id = str(uuid4())
    chunk_id = str(uuid4())
    unique_keyword = f"Neo4jKeyword{uuid4().hex[:6]}"
    chunk_content = f"This content contains {unique_keyword} for search."

    doc = Document(id=doc_id, content="Doc Content", metadata={"source_id": "test_neo4j", "title": "Neo4j Test"})
    chunk = Chunk(id=chunk_id, content=chunk_content, parent_id=doc_id, index=0, metadata={"page": 1})

    # When: Saving data and creating index
    neo4j_repo.save_with_chunks(doc, [chunk])

    with neo4j_repo.driver.session() as session:
        session.run("DROP INDEX chunk_fulltext IF EXISTS")

    neo4j_repo.create_fulltext_index()

    # When: Searching for the unique keyword (with retries for eventual consistency)
    target_query = f"*{unique_keyword}*"
    results = []
    for _ in range(20):
        results = neo4j_repo.search(target_query, limit=5)
        if len(results) > 0:
            break
        time.sleep(0.5)

    # Then: The exact chunk is found and correctly mapped
    assert len(results) > 0
    found_chunk = next((c for c in results if str(c.id) == chunk_id), None)
    assert found_chunk is not None
    assert found_chunk.content == chunk_content
    assert found_chunk.metadata.get("page") == 1
