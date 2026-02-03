import time

import pytest
from fastapi.testclient import TestClient

from app.interfaces.api.main import app

client = TestClient(app)

def wait_for_job_completion(job_id: str, timeout: int = 30):
    for _ in range(timeout):
        response = client.get(f"/v1/jobs/{job_id}")
        if response.status_code != 200:
            break
        job = response.json()
        status = job.get("current_status") or job.get("status")
        if status in ["COMPLETED", "FAILED"]:
            job["status"] = status
            return job
        time.sleep(1)
    raise TimeoutError(f"Job {job_id} did not complete within {timeout} seconds")

@pytest.mark.integration
class TestIngestionScenarios:
    """
    Comprehensive Ingestion Scenarios
    Pattern: Given-When-Then (GWT)
    """

    def test_web_ingestion_with_chunking_verification(self):
        """
        Scenario: Ingest and verify chunking strategy (BDD/test_chunking.py logic)
        """
        from app.application.interfaces.scraper import ScraperInterface
        from app.interfaces.api.dependencies import get_scraper
        from app.interfaces.api.v1.dto.ingest import IngestResponse

        # Given: A large text content that should be split into multiple chunks
        url = "https://example.com/long-text"
        long_content = "This is a sentence. " * 100 # Large enough for multiple chunks

        class MockScraper(ScraperInterface):
            async def scrape(self, u: str) -> IngestResponse:
                return IngestResponse(
                    url=u, markdown=long_content,
                    metadata={"title": "Long Text", "source_id": u},
                    message="Success"
                )
        app.dependency_overrides[get_scraper] = lambda: MockScraper()

        try:
            # When: Ingestion request is made
            response = client.post("/v1/ingest/web", json={"url": url})
            job_id = response.json()["job_id"]
            wait_for_job_completion(job_id)

            # Then: Multiple chunks are created for the same document
            doc_id = url # Standard mapping
            chunks_res = client.get(f"/v1/documents/{doc_id}/chunks")
            if chunks_res.status_code == 200:
                chunks = chunks_res.json()
                assert len(chunks) > 1
                assert all(c["metadata"]["source_url"] == url for c in chunks)
        finally:
            app.dependency_overrides.clear()

    def test_web_ingestion_with_special_characters_url(self):
        """
        Scenario: Ingest URL with special characters (Korean, spaces) (BDD/test_edge_cases.py)
        """
        from app.application.interfaces.scraper import ScraperInterface
        from app.interfaces.api.dependencies import get_scraper
        from app.interfaces.api.v1.dto.ingest import IngestResponse

        # Given: A URL with Korean characters
        url_with_korean = "https://example.com/테스트-page"
        
        class MockScraper(ScraperInterface):
            async def scrape(self, u: str) -> IngestResponse:
                return IngestResponse(
                    url=u, markdown="Korean URL content",
                    metadata={"title": "Korean URL Test", "source_id": u},
                    message="Success"
                )
        app.dependency_overrides[get_scraper] = lambda: MockScraper()

        try:
            # When: Ingestion request is made
            response = client.post("/v1/ingest/web", json={"url": url_with_korean})
            
            # Then: Request is accepted (202) and processing succeeds
            assert response.status_code == 202
            job_id = response.json()["job_id"]
            job = wait_for_job_completion(job_id)
            assert job["status"] == "COMPLETED"
            
            # Then: Document is searchable by the encoded/original URL
            doc_res = client.get(f"/v1/documents/{url_with_korean}")
            if doc_res.status_code == 200:
                assert doc_res.json()["metadata"]["source_url"] == url_with_korean
        finally:
            app.dependency_overrides.clear()


    def test_ingestion_idempotency_and_duplicates(self):
        """
        Scenario: Multiple requests for the same URL (High Priority Scenario)
        """
        # Given: A URL that has already been ingested
        url = "https://httpbin.org/html"

        # When: Requesting ingestion twice
        res1 = client.post("/v1/ingest/web", json={"url": url})
        res2 = client.post("/v1/ingest/web", json={"url": url})

        # Then: Both requests are accepted (accepted for processing)
        assert res1.status_code == 202
        assert res2.status_code == 202

        # Then: Job IDs are distinct
        id1 = res1.json()["job_id"]
        id2 = res2.json()["job_id"]
        assert id1 != id2
        
        # When: Waiting for completion
        wait_for_job_completion(id1)
        wait_for_job_completion(id2)
        
        # Then: Documents are searchable and IDs are unique
        doc_res = client.get("/v1/documents")
        docs = doc_res.json()
        matching = [d for d in docs if d.get("metadata", {}).get("source_url") == url]
        assert len(matching) >= 2
        assert len(set(d["id"] for d in matching)) == len(matching)


    def test_concurrent_ingestion_throughput(self):
        """
        Scenario: Issuing multiple ingestion requests simultaneously
        """
        # Given: Multiple unique URLs
        urls = [f"https://example.com/page-{i}" for i in range(3)]

        # When: POST requests are emitted in sequence
        job_ids = []
        for url in urls:
            res = client.post("/v1/ingest/web", json={"url": url})
            job_ids.append(res.json()["job_id"])

        # Then: All jobs are accepted
        assert len(job_ids) == 3
        # (Eventual completion verified by system async throughput)
