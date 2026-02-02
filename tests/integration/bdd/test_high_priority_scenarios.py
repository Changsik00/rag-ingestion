"""
Integration Tests: High Priority Scenarios

Spec 009에서 미구현된 High Priority Integration Test를 구현합니다:
1. Invalid Job ID → 404
2. Duplicate URL 처리 (멱등성)
"""

import time

import pytest
import requests

# pytestmark = pytest.mark.skip(reason="Requires infrastructure setup - see specs/integration-test-improvement.md")


# Base URL for the API
BASE_URL = "http://localhost:8000"


class TestHighPriorityScenarios:
    """
    High Priority Integration Scenarios

    Verifies critical failure paths and idempotency logic.
    """

    @pytest.fixture(autouse=True)
    def setup(self):
        from app.interfaces.api.main import app
        from fastapi.testclient import TestClient
        self.client = TestClient(app)

    def _wait_for_job_completion(self, job_id: str, timeout: int = 30) -> None:
        """
        Helper: Job이 COMPLETED 또는 FAILED 상태가 될 때까지 대기
        """
        start_time = time.time()
        while time.time() - start_time < timeout:
            job = self._get_job_status(job_id)
            if job.get("status") == "NOT_FOUND":
                time.sleep(1)
                continue
                
            status = job.get("current_status") or job.get("status")
            if status in ["COMPLETED", "FAILED"]:
                return
            time.sleep(1)
        raise TimeoutError(f"Job {job_id} did not complete within {timeout}s")

    def _get_job_status(self, job_id: str) -> dict:
        """
        Helper: Job 상태 조회
        """
        response = self.client.get(f"/v1/jobs/{job_id}")
        if response.status_code != 200:
             return {"status": "NOT_FOUND"}
        return response.json()

    @pytest.mark.integration
    def test_should_return_404_for_invalid_job_id(self):
        """
        Scenario: 존재하지 않는 Job ID 조회

        Given: 존재하지 않는 Job ID "non-existent-job-id-12345"
        When: GET /jobs/{job_id} 요청
        Then: 404 Not Found 및 명확한 에러 메시지 반환
        """
        # Given
        non_existent_job_id = "non-existent-job-id-12345"

        # When
        response = self.client.get(f"/v1/jobs/{non_existent_job_id}")

        # Then
        assert response.status_code == 404, f"Expected 404 but got {response.status_code}"

        error_response = response.json()
        error_detail = error_response.get("message") or error_response.get("detail") or ""
        
        # Note: API might return "Job {job_id} not found" or similar.
        # Checking for "not found" is generally safe.
        assert "not found" in str(error_detail).lower(), f"Error message should contain 'not found', but got: {error_detail}"

    @pytest.mark.integration
    def test_should_handle_duplicate_url_sequentially(self):
        """
        Scenario: 동일한 URL을 두 번 순차적으로 수집 (Idempotency check / Standard behavior)

        Given: 동일한 URL로 두 번 순차적으로 수집 요청
        When: 두 Job이 완료되면
        Then:
          - 두 Job 모두 COMPLETED 상태
          - 2개의 별도 Document가 생성됨 (현재 정책: UUID 기반 ID, 중복 허용)
        """
        # Setup mocks
        from app.interfaces.api.v1.dto.ingest import IngestResponse
        from app.interfaces.api.dependencies import get_scraper
        from app.interfaces.api.main import app
        from unittest.mock import Mock, AsyncMock

        mock_scraper = Mock()
        mock_scraper.scrape = AsyncMock(return_value=IngestResponse(
            url="https://httpbin.org/html", 
            markdown="# Dummy Content", 
            metadata={"title": "Dummy", "source_id": "https://httpbin.org/html"}
        ))
        app.dependency_overrides[get_scraper] = lambda: mock_scraper

        try:
            # Given
            url = "https://httpbin.org/html"

            # When 1: 첫 번째 수집
            response1 = self.client.post("/v1/ingest/web", json={"url": url})
            assert response1.status_code == 202, f"Expected 202 but got {response1.status_code}"
            job_id_1 = response1.json()["job_id"]

            self._wait_for_job_completion(job_id_1)

            # When 2: 두 번째 수집 (동일 URL)
            response2 = self.client.post("/v1/ingest/web", json={"url": url})
            assert response2.status_code == 202, f"Expected 202 but got {response2.status_code}"
            job_id_2 = response2.json()["job_id"]

            self._wait_for_job_completion(job_id_2)

            # Then: 두 Job 모두 COMPLETED
            job1 = self._get_job_status(job_id_1)
            job2 = self._get_job_status(job_id_2)

            status1 = job1.get("current_status") or job1.get("status")
            status2 = job2.get("current_status") or job2.get("status")

            assert status1 == "COMPLETED", f"Job 1 Status: {status1}"
            assert status2 == "COMPLETED", f"Job 2 Status: {status2}"

            # Then: 2개의 별도 Document 생성 확인
            docs_response = self.client.get("/v1/documents", params={"limit": 100})
            assert docs_response.status_code == 200
            docs = docs_response.json()

            matching_docs = [d for d in docs if d.get("metadata", {}).get("source_url") == url]

            # 최소 2개 이상
            assert len(matching_docs) >= 2, f"Expected at least 2 documents with URL {url}, but got {len(matching_docs)}"

            # ID 유니크 확인
            doc_ids = [d["id"] for d in matching_docs]
            assert len(set(doc_ids)) == len(doc_ids), "All document IDs should be unique"
        
        finally:
            app.dependency_overrides = {}
