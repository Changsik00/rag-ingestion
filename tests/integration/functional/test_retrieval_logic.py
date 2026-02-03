from uuid import uuid4

import pytest

from app.domain.value_objects.chunk import Chunk
from app.infrastructure.repositories.chroma import ChromaVectorRepository
from app.infrastructure.repositories.neo4j_document_repository import Neo4jDocumentRepository
from app.infrastructure.repositories.neo4j_graph_repository import Neo4jGraphRepository
from app.interfaces.api.dependencies import get_neo4j_driver


@pytest.fixture(scope="module")
def driver():
    return get_neo4j_driver()

@pytest.fixture(scope="module")
def chroma_repo():
    return ChromaVectorRepository()

@pytest.fixture(scope="module")
def neo4j_repo(driver):
    return Neo4jDocumentRepository(driver)

@pytest.fixture(scope="module")
def graph_repo(driver):
    return Neo4jGraphRepository(driver)

@pytest.mark.integration
class TestRetrievalLogic:
    """
    Functional tests for retrieval and search strategies.
    Pattern: Given-When-Then (GWT)
    """

    def test_hybrid_pipeline_components(self, neo4j_repo, graph_repo, chroma_repo):
        # Given: A common query term
        query = "Artificial Intelligence"

        # When: Executing Neo4j keyword search
        kw_results = neo4j_repo.search(query)
        # Then: Returns a valid list of chunks
        assert isinstance(kw_results, list)

        # When: Executing Graph subgraph retrieval
        graph_results = graph_repo.get_subgraph([query])
        # Then: Returns a valid adjacency list/dict structure
        assert isinstance(graph_results, list)

        # When: Executing Chroma MMR search
        vector_results = chroma_repo.search_mmr(query, limit=5)
        # Then: Returns a valid list of chunks
        assert isinstance(vector_results, list)

    def test_filtered_search_isolation(self, chroma_repo):
        # Given: Two documents with distinct topics ("Apple" as Brand vs Fruit)
        doc_tech_id = str(uuid4())
        doc_fruit_id = str(uuid4())

        chunks = [
            Chunk(id=str(uuid4()), content="Apple macOS is an operating system.", parent_id=doc_tech_id, index=0),
            Chunk(id=str(uuid4()), content="Apple is a red edible fruit with high fiber.", parent_id=doc_fruit_id, index=0),
        ]
        chroma_repo.save_chunks(chunks)

        # When: Searching for "Apple" filtered by Tech document
        tech_results = chroma_repo.search("Apple", limit=5, filters={"doc_id": doc_tech_id})

        # Then: Only the Tech chunk is found
        assert len(tech_results) > 0
        assert all(str(c.parent_id) == doc_tech_id for c in tech_results)
        assert any("macOS" in c.content for c in tech_results)
        assert not any("fruit" in c.content for c in tech_results)

        # When: Searching for "Apple" filtered by Fruit document
        fruit_results = chroma_repo.search("Apple", limit=5, filters={"doc_id": doc_fruit_id})

        # Then: Only the Fruit chunk is found
        assert len(fruit_results) > 0
        assert all(str(c.parent_id) == doc_fruit_id for c in fruit_results)
        assert any("fruit" in c.content for c in fruit_results)
        assert not any("macOS" in c.content for c in fruit_results)

    def test_graph_navigation_retrieval(self, graph_repo):
        # Given: A set of entities (A -> B)
        # (Assuming these were seeded or dynamically created if repo supports it)
        # For functional test, we verify the capability to query neighbors

        # When: Requesting neighbors for a known entity
        neighbors = graph_repo.get_entity_relationships("Python")

        # Then: Returns a valid list structure (even if empty in clean state)
        assert isinstance(neighbors, list)
