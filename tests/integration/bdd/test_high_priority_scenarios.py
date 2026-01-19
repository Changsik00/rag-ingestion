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


# ===== Helper Functions =====


def wait_for_job_completion(job_id: str, timeout: int = 30) -> None:
    """
    Job이 COMPLETED 또는 FAILED 상태가 될 때까지 대기

    Args:
        job_id: Job ID
        timeout: 최대 대기 시간 (초)

    Raises:
        TimeoutError: timeout 시간 내에 Job이 완료되지 않으면 발생
    """
    start_time = time.time()
    while time.time() - start_time < timeout:
        job = get_job_status(job_id)
        if job["status"] in ["COMPLETED", "FAILED"]:
            return
        time.sleep(1)
    raise TimeoutError(f"Job {job_id} did not complete within {timeout}s")


def get_job_status(job_id: str) -> dict:
    """
    Job 상태 조회

    Args:
        job_id: Job ID

    Returns:
        Job 정보 (dict)
    """
    response = requests.get(f"{BASE_URL}/jobs/{job_id}")
    response.raise_for_status()
    return response.json()


# ===== Test 1: Invalid Job ID → 404 =====


@pytest.mark.integration
def test_invalid_job_id_returns_404():
    """
    Scenario: 존재하지 않는 Job ID 조회

    Given: 존재하지 않는 Job ID
    When: GET /jobs/{job_id} 요청
    Then: 404 Not Found, 명확한 에러 메시지

    이 테스트는 API가 존재하지 않는 리소스를 올바르게 처리하는지 검증합니다.
    """
    # Given: 존재하지 않는 Job ID
    non_existent_job_id = "non-existent-job-id-12345"

    # When: Job 조회 요청
    response = requests.get(f"{BASE_URL}/jobs/{non_existent_job_id}")

    # Then: 404 반환
    assert response.status_code == 404, f"Expected 404 but got {response.status_code}"

    # Then: 명확한 에러 메시지
    error_detail = response.json().get("detail", "")
    assert "not found" in error_detail.lower(), f"Error message should contain 'not found', but got: {error_detail}"
    assert non_existent_job_id in error_detail, f"Error message should contain job_id, but got: {error_detail}"


# ===== Test 2: Duplicate URL 처리 =====


@pytest.mark.integration
def test_duplicate_url_sequential_ingestion():
    """
    Scenario: 동일한 URL을 두 번 순차적으로 수집

    Given: 동일한 URL로 두 번 순차적으로 수집 요청
    When: 두 Job이 완료되면
    Then:
      - 두 Job 모두 COMPLETED 상태
      - 2개의 별도 Document가 생성됨 (현재 정책: UUID 기반 ID)

    이 테스트는 시스템이 중복 URL을 어떻게 처리하는지 검증합니다.
    현재 정책: 매번 새로운 Document 생성 (Option A)
    """
    # Given: 동일한 URL
    url = "https://httpbin.org/html"

    # When: 첫 번째 수집
    response1 = requests.post(f"{BASE_URL}/ingest/web", json={"url": url})
    assert response1.status_code == 202, f"Expected 202 but got {response1.status_code}"
    job_id_1 = response1.json()["job_id"]

    # 완료 대기
    wait_for_job_completion(job_id_1)

    # When: 두 번째 수집 (동일 URL)
    response2 = requests.post(f"{BASE_URL}/ingest/web", json={"url": url})
    assert response2.status_code == 202, f"Expected 202 but got {response2.status_code}"
    job_id_2 = response2.json()["job_id"]

    # 완료 대기
    wait_for_job_completion(job_id_2)

    # Then: 두 Job 모두 COMPLETED
    job1 = get_job_status(job_id_1)
    job2 = get_job_status(job_id_2)

    assert job1["status"] == "COMPLETED", f"Job 1 should be COMPLETED but got {job1['status']}"
    assert job2["status"] == "COMPLETED", f"Job 2 should be COMPLETED but got {job2['status']}"

    # Then: 2개의 별도 Document 생성 확인
    docs_response = requests.get(f"{BASE_URL}/documents?limit=100")
    docs_response.raise_for_status()
    docs = docs_response.json()

    # 동일 URL을 가진 Document 필터링
    matching_docs = [d for d in docs if d.get("source_url") == url]

    # 최소 2개 이상 (이전 테스트 실행으로 더 있을 수 있음)
    assert len(matching_docs) >= 2, f"Expected at least 2 documents with URL {url}, but got {len(matching_docs)}"

    # 두 Document의 ID가 다른지 확인 (중복이 아니라 별도 생성)
    doc_ids = [d["id"] for d in matching_docs]
    assert len(set(doc_ids)) == len(doc_ids), "All document IDs should be unique (no duplicates)"
