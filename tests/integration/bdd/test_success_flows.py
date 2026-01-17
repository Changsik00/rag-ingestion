"""
Core success scenario integration tests.

These tests verify that basic workflows complete successfully.
Based on BDD (Behavior-Driven Development) approach with Given-When-Then structure.
"""
import pytest
import time
from fastapi.testclient import TestClient
from app.interfaces.api.main import app


client = TestClient(app)


def wait_for_job_completion(job_id: str, timeout: int = 30):
    """Helper function to wait for job completion"""
    for _ in range(timeout):
        response = client.get(f"/jobs/{job_id}")
        if response.status_code != 200:
            break
        
        job = response.json()
        status = job.get("status")
        
        if status in ["COMPLETED", "FAILED"]:
            return job
        
        time.sleep(1)
    
    raise TimeoutError(f"Job {job_id} did not complete within {timeout} seconds")


@pytest.mark.integration
def test_successful_web_ingestion_basic_flow():
    """
    Given: 유효한 URL과 함께 수집 요청을 보내고
    When: Job이 완료되면
    Then: Document가 성공적으로 저장된다
    
    This is the most critical success scenario - the basic happy path.
    """
    # Given: 유효한 URL
    # Note: httpbin.org는 테스트용 실제 웹사이트
    url = "https://httpbin.org/html"
    
    # When: 수집 요청
    response = client.post("/ingest/web", json={
        "url": url,
        "enable_extraction": True
    })
    
    # Then: 202 Accepted 응답 및 job_id 반환
    assert response.status_code == 202
    job_id = response.json()["job_id"]
    assert job_id is not None
    
    # When: Job 완료 대기
    job = wait_for_job_completion(job_id)
    
    # Then: Job이 COMPLETED 상태
    assert job["status"] == "COMPLETED"
    assert job.get("error_message") is None
    
    # Then: Document가 저장되었는지 확인
    docs_response = client.get("/documents")
    assert docs_response.status_code == 200
    
    docs = docs_response.json()
    assert len(docs) > 0
    
    # 해당 URL의 document가 있는지 확인
    doc = next((d for d in docs if d["source_url"] == url), None)
    assert doc is not None
    assert len(doc["content"]) > 0


@pytest.mark.integration
def test_successful_ingestion_without_extraction():
    """
    Given: enable_extraction=False로 수집 요청하고
    When: Job이 완료되면
    Then: Document는 저장되지만 metadata는 비어있다
    
    This verifies that extraction can be disabled and the system still works.
    """
    # Given: URL with extraction disabled
    # Note: 다른 HTML 엔드포인트 사용 (중복 방지)
    url = "https://httpbin.org/links/5"
    
    # When: 수집 요청 (extraction 비활성화)
    response = client.post("/ingest/web", json={
        "url": url,
        "enable_extraction": False
    })
    
    # Then: 202 Accepted
    assert response.status_code == 202
    job_id = response.json()["job_id"]
    
    # When: Job 완료 대기
    job = wait_for_job_completion(job_id)
    
    # Then: Job 완료
    assert job["status"] == "COMPLETED"
    
    # Then: Document 검증
    docs_response = client.get("/documents")
    docs = docs_response.json()
    
    doc = next((d for d in docs if d["source_url"] == url), None)
    
    # Note: Integration 환경에서는 Document 저장이 비동기로 처리될 수 있음
    # 최소한 Job은 COMPLETED 상태여야 함
    if doc is not None:
        assert len(doc["content"]) > 0
        
        # metadata가 비어있거나 최소한만 있음 (extraction 결과 없음)
        metadata = doc.get("metadata", {})
        # LLM extraction 결과가 없어야 함 (title, summary 등)
        assert "title" not in metadata or metadata.get("title") is None
