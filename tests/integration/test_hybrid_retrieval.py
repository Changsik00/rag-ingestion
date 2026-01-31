import pytest

from app.infrastructure.repositories.neo4j_graph_repository import Neo4jGraphRepository
from app.infrastructure.repositories.neo4j_document_repository import Neo4jDocumentRepository
from app.infrastructure.repositories.chroma import ChromaVectorRepository
from app.interfaces.api.dependencies import get_neo4j_driver

pytestmark = pytest.mark.skip(reason="Requires infrastructure setup - see specs/integration-test-improvement.md")



# Skip if explicit flag not set, to avoid slow CI runs if desired
# But for now we run it.
@pytest.mark.integration
class TestHybridRetrievalReal:
    @pytest.fixture(scope="class")
    def driver(self):
        return get_neo4j_driver()

    @pytest.fixture(scope="class")
    def neo4j_repo(self, driver):
        return Neo4jDocumentRepository(driver)

    @pytest.fixture(scope="class")
    def graph_repo(self, driver):
        return Neo4jGraphRepository(driver)

    @pytest.fixture(scope="class")
    def chroma_repo(self):
        return ChromaVectorRepository()

    def test_full_pipeline_components(self, neo4j_repo, graph_repo, chroma_repo):
        """
        Verify that all three components can query their respective real DBs without error.
        We don't assert specific data unless we seed it,
        but we assert the return structures are valid (empty lists or lists of Chunks).
        """
        query = "Test Query for Hybrid Retrieval"

        # 1. Neo4j Search
        # Should return list (empty or not)
        keyword_results = neo4j_repo.search(query)
        assert isinstance(keyword_results, list)

        # 2. Graph Search
        # Should return list of dicts
        graph_results = graph_repo.get_subgraph([query])
        assert isinstance(graph_results, list)

        # 3. Chroma Search (MMR)
        # Should return list of Chunks
        # Note: Chroma might be empty if not seeded, but valid call shouldn't crash.
        vector_results = chroma_repo.search_mmr(query)
        assert isinstance(vector_results, list)

    def test_neo4j_fulltext_index_creation(self, neo4j_repo):
        """
        Verify that fulltext index creation doesn't fail.
        """
        try:
            neo4j_repo.create_fulltext_index()
        except Exception as e:
            pytest.fail(f"Fulltext index creation failed: {e}")
