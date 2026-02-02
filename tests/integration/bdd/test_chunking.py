import time
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from app.interfaces.api.dependencies import get_repository
from app.interfaces.api.main import app

# pytestmark = pytest.mark.skip(reason="Requires infrastructure setup - see specs/integration-test-improvement.md")


client = TestClient(app)


def wait_for_job_completion(job_id: str, timeout: int = 30):
    for _ in range(timeout):
        response = client.get(f"/v1/jobs/{job_id}")
        if response.status_code != 200:
            break
        job = response.json()
        status = job.get("current_status") or job.get("status")
        if status in ["COMPLETED", "FAILED"]:
            return job
        time.sleep(1)
    raise TimeoutError(f"Job {job_id} did not complete within {timeout} seconds")


@pytest.mark.integration
def test_ingestion_saves_chunks():
    """
    Given: Ingestion request
    When: Job completes
    Then: Repository.save_with_chunks is called (verified by DB check)
    """
    from app.interfaces.api.dependencies import get_repository, get_scraper, get_neo4j_driver, get_semantic_extractor, get_chroma_vector_repository
    from app.application.interfaces.scraper import ScraperInterface
    from app.interfaces.api.v1.dto.ingest import IngestResponse
    from app.domain.value_objects.extracted_metadata import ExtractedMetadata
    from app.infrastructure.repositories.composite import CompositeDocumentRepository
    from app.infrastructure.repositories.neo4j_document_repository import Neo4jDocumentRepository

    # Mock Scraper
    # Mock Scraper
    class MockScraper(ScraperInterface):
        async def scrape(self, url: str) -> IngestResponse:
            return IngestResponse(
                url=url,
                markdown="# Mock Title\n\nChunk 1 content.\n\nChunk 2 content.",
                metadata={"title": "Mock Title", "source_id": url},
                message="Mock scrape success"
            )
            
    # Mock Semantic Extractor
    class MockSemanticExtractor:
        def __init__(self, llm=None): pass
        async def extract(self, text: str, thread_id: str = None) -> ExtractedMetadata:
             return ExtractedMetadata(
                 title="Mock Title", 
                 summary="Mock Summary", 
                 keywords=["chunk", "test"], 
                 entities={}, 
                 language="en"
             )

    # Mock Chroma Repo (to avoid Embedding API call)
    mock_chroma = MagicMock()
    app.dependency_overrides[get_chroma_vector_repository] = lambda: mock_chroma
    
    # Must override get_repository because it calls get_chroma_vector_repository directly (not via Depends)
    def get_repository_override():
        driver = get_neo4j_driver()
        neo4j_storage = Neo4jDocumentRepository(driver)
        return CompositeDocumentRepository(neo4j=neo4j_storage, chroma=mock_chroma)
        
    app.dependency_overrides[get_repository] = get_repository_override
            
    app.dependency_overrides[get_scraper] = lambda: MockScraper()
    app.dependency_overrides[get_semantic_extractor] = lambda: MockSemanticExtractor()

    url = "https://mock-example.com/chunking-test"

    try:
        # When
        response = client.post("/v1/ingest/web", json={"url": url, "enable_extraction": False})

        # Then
        assert response.status_code == 202
        job_id = response.json()["job_id"]

        job = wait_for_job_completion(job_id)

        status = job.get("current_status") or job.get("status")
        assert status == "COMPLETED"

        # Verify Chunks in Neo4j
        driver = get_neo4j_driver()
        with driver.session() as session:
            # Check Document existence (property stored in Neo4j is source_url from metadata)
            result = session.run("MATCH (d:Document {source_url: $url}) RETURN d", url=url)
            doc_node = result.single()
            
            assert doc_node is not None, f"Document node with source_url {url} not found in Neo4j"
            
            # Check Chunks existence
            result = session.run(
                "MATCH (d:Document {source_url: $url})-[:HAS_CHUNK]->(c:Chunk) RETURN count(c) as count", 
                url=url
            )
            record = result.single()
            count = record["count"]
            assert count > 0, f"Expected chunks, found {count}"

    finally:
        app.dependency_overrides = {}
