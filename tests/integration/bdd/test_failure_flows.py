"""
Core Failure Scenario Integration Tests

시스템이 실패 상황을 적절히 처리하는지 검증하는 통합 테스트입니다.
명확한 에러 메시지와 적절한 에러 상태에 초점을 맞춥니다 (BDD 접근 방식).
"""

import pytest
from fastapi.testclient import TestClient

from app.interfaces.api.main import app

client = TestClient(app)


@pytest.mark.integration
def test_invalid_url_format_returns_422():
    """
    Given: 잘못된 URL 형식을 입력하고
    When: 수집 요청을 보내면
    Then: 422 Unprocessable Entity와 명확한 에러 메시지를 받는다

    This is critical for API usability - clients need clear error messages.
    Note: FastAPI uses 422 for validation errors, not 400.
    """
    # Given: 잘못된 URL 형식
    invalid_url = "not-a-valid-url"

    # When: 수집 요청
    response = client.post("/ingest/web", json={"url": invalid_url})

    # Then: 422 Unprocessable Entity (FastAPI validation error)
    assert response.status_code == 422

    # Then: 명확한 에러 메시지
    error_detail = response.json().get("detail", "")
    # FastAPI validation error는 list로 반환될 수 있음
    if isinstance(error_detail, list):
        error_detail = str(error_detail)
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
    response = client.post("/ingest/web", json={"url": url_404})

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
    error_message = job.get("error_message", "")
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

    # Given: LLM이 에러를 발생시키도록 Mock
    # patch object using exact import path used in ingestion.py
    # Note: IngestionService imports SemanticExtractor directly effectively. 
    # But IngestionService takes extractor as dependency.
    # In integration test, we need to mock where it's instantiated or injected.
    # For simplicity in BDD/Integration with TestClient, we rely on dependency override or patching internals if DI is not fully exposed to TestClient.
    
    from app.interfaces.api.dependencies import get_semantic_extractor
    
    # Given: Mock Extractor that raises exception
    mock_extractor = mocker.Mock()
    mock_extractor.extract.side_effect = Exception("LLM API quota exceeded")
    
    # Override dependency
    app.dependency_overrides[get_semantic_extractor] = lambda: mock_extractor
    
    try:
        # When: 수집 요청 (extraction 활성화)
        url = "https://httpbin.org/uuid"  # 고유한 엔드포인트
        response = client.post("/ingest/web", json={"url": url, "enable_extraction": True})

        # Then: 요청 자체는 성공
        assert response.status_code == 202
        job_id = response.json()["job_id"]
    finally:
        # Clean up override
        app.dependency_overrides.pop(get_semantic_extractor, None)

    # When: Job 완료 대기
    for _ in range(30):
        # ... logic remains same ...
        job_response = client.get(f"/jobs/{job_id}")
        job = job_response.json()

        if job["status"] in ["COMPLETED", "FAILED"]:
            break
        time.sleep(1)

    # Then: Job 상태 - Extraction 실패는 Job 실패가 아님 (Warning Logged) -> COMPLETED여야 함
    # IngestionService refactoring changed logic: Exceptions in semantic extraction are logged as warning, Job continues.
    assert job["status"] == "COMPLETED"

    # Then: Document는 저장되어야 함 (scraping은 성공했으므로)
    docs_response = client.get("/documents")
    docs = docs_response.json()

    # URL로 document 찾기
    doc = next((d for d in docs if d["source_url"] == url), None)

    assert doc is not None
    if doc is not None:
        # Document가 저장되었다면, metadata는 비어있어야 함 (semantic_data 키가 없거나 비어있음)
        metadata = doc.get("metadata", {})
        assert "semantic_data" not in metadata or not metadata["semantic_data"]
