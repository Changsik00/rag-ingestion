"""
Integration Tests: High Priority Scenarios

Spec 009에서 미구현된 High Priority Integration Test를 구현합니다:
1. Invalid Job ID → 404
2. Duplicate URL 처리 (멱등성)
"""

import time
import pytest
import requests

# Base URL for the API
BASE_URL = "http://localhost:8000"

class TestHighPriorityScenarios:
    """
    High Priority Integration Scenarios
    
    Verifies critical failure paths and idempotency logic.
    """

    def _wait_for_job_completion(self, job_id: str, timeout: int = 30) -> None:
        """
        Helper: Job이 COMPLETED 또는 FAILED 상태가 될 때까지 대기
        """
        start_time = time.time()
        while time.time() - start_time < timeout:
            job = self._get_job_status(job_id)
            if job["status"] in ["COMPLETED", "FAILED"]:
                return
            time.sleep(1)
        raise TimeoutError(f"Job {job_id} did not complete within {timeout}s")

    def _get_job_status(self, job_id: str) -> dict:
        """
        Helper: Job 상태 조회
        """
        response = requests.get(f"{BASE_URL}/jobs/{job_id}")
        response.raise_for_status()
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
        response = requests.get(f"{BASE_URL}/jobs/{non_existent_job_id}")
        
        # Then
        assert response.status_code == 404, f"Expected 404 but got {response.status_code}"
        
        error_detail = response.json().get("detail", "")
        # Note: API might return "Job {job_id} not found" or similar.
        # Checking for "not found" is generally safe.
        assert "not found" in error_detail.lower(), f"Error message should contain 'not found', but got: {error_detail}"

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
        # Given
        url = "https://httpbin.org/html"
        
        # When 1: 첫 번째 수집
        response1 = requests.post(f"{BASE_URL}/ingest/web", json={"url": url})
        assert response1.status_code == 202, f"Expected 202 but got {response1.status_code}"
        job_id_1 = response1.json()["job_id"]
        
        self._wait_for_job_completion(job_id_1)
        
        # When 2: 두 번째 수집 (동일 URL)
        response2 = requests.post(f"{BASE_URL}/ingest/web", json={"url": url})
        assert response2.status_code == 202, f"Expected 202 but got {response2.status_code}"
        job_id_2 = response2.json()["job_id"]
        
        self._wait_for_job_completion(job_id_2)
        
        # Then: 두 Job 모두 COMPLETED
        job1 = self._get_job_status(job_id_1)
        job2 = self._get_job_status(job_id_2)
        
        assert job1["status"] == "COMPLETED", f"Job 1 Status: {job1['status']}"
        assert job2["status"] == "COMPLETED", f"Job 2 Status: {job2['status']}"
        
        # Then: 2개의 별도 Document 생성 확인
        docs_response = requests.get(f"{BASE_URL}/documents?limit=100")
        docs_response.raise_for_status()
        docs = docs_response.json()
        
        matching_docs = [d for d in docs if d.get("source_url") == url]
        
        # 최소 2개 이상
        assert len(matching_docs) >= 2, \
            f"Expected at least 2 documents with URL {url}, but got {len(matching_docs)}"
        
        # ID 유니크 확인
        doc_ids = [d["id"] for d in matching_docs]
        assert len(set(doc_ids)) == len(doc_ids), "All document IDs should be unique"
