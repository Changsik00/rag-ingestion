from uuid import uuid4

import pytest

from app.domain.entities.chunk import Chunk
from app.domain.entities.document import Document
from app.infrastructure.storage.neo4j_document_repository import Neo4jStorage
from app.interfaces.api.dependencies import get_neo4j_driver


@pytest.fixture
def neo4j_repo():
    driver = get_neo4j_driver()
    repo = Neo4jStorage(driver)
    yield repo
    # Cleanup (Optional)
    # repo.close() # Shared driver usually managed by dependency injection


@pytest.mark.integration
def test_neo4j_fulltext_search_flow(neo4j_repo):
    """
    Scenario: Verify Neo4j Fulltext Search on Chunks
    1. Save a document with chunks.
    2. Create Fulltext Index (using new method).
    3. Search by keyword found in a chunk.
    4. Verify the CHUNK is returned.
    """
    # 1. Setup Data
    doc_id = str(uuid4())
    chunk_id = str(uuid4())
    unique_keyword = f"Neo4jKeyword{uuid4().hex[:6]}"
    chunk_content = f"This content contains {unique_keyword} for search."

    doc = Document(id=doc_id, content="Doc Content", metadata={"title": "Neo4j Test"})
    chunk = Chunk(id=chunk_id, content=chunk_content, parent_id=doc_id, index=0, metadata={"page": 1})

    neo4j_repo.save_with_chunks(doc, [chunk])

    # DEBUG: Verify Chunk Exists
    with neo4j_repo.driver.session() as session:
        count = session.run("MATCH (c:Chunk {id: $id}) RETURN count(c) as count", id=chunk_id).single()["count"]
        print(f"DEBUG: Chunk count for {chunk_id}: {count}")
        assert count == 1, "Chunk was not saved to Neo4j!"

        # Ensure clean state for index
        session.run("DROP INDEX chunk_fulltext IF EXISTS")

    # 2. Create Index
    if hasattr(neo4j_repo, "create_fulltext_index"):
        neo4j_repo.create_fulltext_index()
    else:
        pytest.fail("create_fulltext_index method not implemented yet (TDD Step 1)")

    # 3. Search
    # Wait for index consistency (Eventual Consistency handling)
    # 3. Search
    # Wait for index consistency (Eventual Consistency handling)
    import time

    results = []
    # Search for the unique keyword
    target_query = unique_keyword

    # print(f"DEBUG: Searching for '{target_query}'...")
    for i in range(20):  # Retry for up to 10 seconds
        results = neo4j_repo.search(target_query, limit=5)
        # print(f"DEBUG: Attempt {i+1} results: {len(results)}")
        if len(results) > 0:
            break
        time.sleep(0.5)

    # 4. Assert
    assert len(results) > 0, "Expected at least one chunk found after waiting for index"
    found_chunk = next((c for c in results if c.id == chunk_id or str(c.id) == chunk_id), None)
    assert found_chunk is not None, f"Expected chunk {chunk_id} to be found"
    assert found_chunk.content == chunk_content
    # Check simple metadata mapping
    assert found_chunk.metadata.get("page") == 1
