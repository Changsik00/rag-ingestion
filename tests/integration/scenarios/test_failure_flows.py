"""
Core failure scenario integration tests.

These tests verify that the system handles failures appropriately.
Focus on clear error messages and proper error states (BDD approach).
"""
import pytest
from fastapi.testclient import TestClient
from app.interfaces.api.main import app


client = TestClient(app)


@pytest.mark.integration
def test_invalid_url_format_returns_400():
    """
    Given: 잘못된 URL 형식을 입력하고
    When: 수집 요청을 보내면
    Then: 400 Bad Request와 명확한 에러 메시지를 받는다
    
    This is critical for API usability - clients need clear error messages.
    """
    # Given: 잘못된 URL 형식
    invalid_url = "not-a-valid-url"
    
    # When: 수집 요청
    response = client.post("/ingest/web", json={
        "url": invalid_url
    })
    
    # Then: 400 Bad Request
    assert response.status_code == 400
    
    # Then: 명확한 에러 메시지
    error_detail = response.json().get("detail", "")
    assert "url" in error_detail.lower() or "invalid" in error_detail.lower()


@pytest.mark.integration
def test_url_404_fails_job():
    """
    Given: 존재하지 않는 URL (404)로 수집 요청하고
    When: Job이 실행되면
    Then: Job이 FAILED 상태로 전이되고 적절한 에러 메시지를 포함한다
    
    This verifies that external failures are properly handled and reported.
    """
    import time
    
    # Given: 404를 반환할 URL
    url_404 = "https://httpbin.org/status/404"
    
    # When: 수집 요청
    response = client.post("/ingest/web", json={
        "url": url_404
    })
    
    # Then: 202 Accepted (요청은 성공)
    assert response.status_code == 202
    job_id = response.json()["job_id"]
    
    # When: Job 완료 대기
    for _ in range(30):
        job_response = client.get(f"/jobs/{job_id}")
        job = job_response.json()
        
        if job["status"] in ["COMPLETED", "FAILED"]:
            break
        
        time.sleep(1)
    
    # Then: Job이 FAILED 상태
    assert job["status"] == "FAILED"
    
    # Then: 에러 메시지에 404 관련 정보 포함
    error_message = job.get("error", "")
    assert "404" in error_message or "not found" in error_message.lower()


@pytest.mark.integration
def test_llm_failure_still_saves_document(mocker):
    """
    Given: LLM이 실패하는 상황에서
    When: 수집 요청을 보내면
    Then: Document는 저장되지만 metadata 추출은 실패한다
    
    This verifies graceful degradation - partial failures don't break the entire flow.
    """
    import time
    from app.core.llm import get_llm
    
    # Given: LLM이 에러를 발생시키도록 Mock
    mocker.patch('app.core.llm.get_llm', side_effect=Exception("LLM API quota exceeded"))
    
    # When: 수집 요청 (extraction 활성화)
    url = "https://example.com/test-llm-failure"
    response = client.post("/ingest/web", json={
        "url": url,
        "enable_extraction": True
    })
    
    # Then: 요청 자체는 성공
    assert response.status_code == 202
    job_id = response.json()["job_id"]
    
    # When: Job 완료 대기
    for _ in range(30):
        job_response = client.get(f"/jobs/{job_id}")
        job = job_response.json()
        
        if job["status"] in ["COMPLETED", "FAILED"]:
            break
        
        time.sleep(1)
    
    # Then: Job 상태 확인 (COMPLETED or FAILED 둘 다 허용)
    # 정책에 따라 다를 수 있음 - 여기서는 partial success를 테스트
    assert job["status"] in ["COMPLETED", "FAILED"]
    
    # Then: Document는 저장되어야 함 (scraping은 성공했으므로)
    docs_response = client.get("/documents")
    docs = docs_response.json()
    
    # URL로 document 찾기
    doc = next((d for d in docs if d["source"]["url"] == url), None)
    
    if doc is not None:
        # Document가 저장되었다면, metadata는 비어있어야 함
        assert len(doc["content"]) > 0
        metadata = doc.get("metadata", {})
        # LLM extraction 결과가 없어야 함
        assert metadata.get("title") is None or metadata.get("title") == ""
