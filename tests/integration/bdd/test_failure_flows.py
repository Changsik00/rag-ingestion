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
def test_llm_failure_still_saves_document():
    """
    Given: LLM이 실패하는 상황에서
    When: 수집 요청을 보내면
    Then: Document는 저장되지만 metadata 추출은 실패한다

    This verifies graceful degradation - partial failures don't break the entire flow.
    """
    import time
    from unittest.mock import Mock

    # Given: LLM이 에러를 발생시키도록 Mock
    # patch object using exact import path used in ingestion.py
    # Note: IngestionService imports SemanticExtractor directly effectively.
    # But IngestionService takes extractor as dependency.
    # In integration test, we need to mock where it's instantiated or injected.
    # For simplicity in BDD/Integration with TestClient, we rely on dependency override or patching internals if DI is not fully exposed to TestClient.
    from app.interfaces.api.dependencies import (
        get_graph_repository,
        get_ingestion_service,
        get_job_repository,
        get_neo4j_driver,
        get_scraper,
    )
    from app.use_cases.ingestion import IngestionService

    # Given: Mock LLM
    mock_llm = Mock()
    mock_llm.extract_metadata.side_effect = Exception("LLM API quota exceeded")

    # Given: Mock Repository
    mock_repo = Mock()

    # We need other real dependencies or mocks.
    # Since we are overriding get_ingestion_service, we can resolve them manually or use a dependency chain.
    # Simpler: Instantiate IngestionService with mocks/real mix.
    # We need real JobRepo for status updates to work? Or we mock JobRepo too?
    # Test checks API /jobs/{id}. This reads from DB.
    # So we need REAL JobRepository and REAL GraphDatabase (unless we mock the API response too, which defeats 'Integration' test).
    # We want Integration of: API -> Service -> Logic -> (Mock Failure) -> (Mock Save) -> (Real Job Update)

    # To get Real JobRepository, we need the driver.
    # We can fetch it via the original dependency function or create a new one.
    # Since we are in the same process, we can just call valid dependencies.

    driver = get_neo4j_driver()  # Assumes Neo4j is available?
    # Wait, earlier I assumed Neo4j IS running because Job status check passed.

    # But if I construct IngestionService, I need a JobRepository instance.
    real_job_repo_instance = get_job_repository(driver)
    real_graph_repo_instance = get_graph_repository(driver)
    real_scraper_instance = get_scraper()

    # Since I cannot easily use Depends inside the lambda assignment, I prepare the instance.

    # Mock Extractor wrapping Mock LLM
    # We need a proper SemanticExtractor instance that uses our mock LLM, OR just a mock extractor.
    # Let's use mock extractor directly to be safe.
    mock_extractor = Mock()
    mock_extractor.extract.side_effect = Exception("LLM API quota exceeded")

    # Mock Chunker
    mock_chunker = Mock()
    mock_chunker.chunk.return_value = []  # Return empty chunks as fallback

    service_instance = IngestionService(
        scraper=real_scraper_instance,
        repository=mock_repo,  # The mock we want to verify
        graph=real_graph_repo_instance,
        job_repository=real_job_repo_instance,
        chunker=mock_chunker,
        extractor=mock_extractor,
    )

    app.dependency_overrides[get_ingestion_service] = lambda: service_instance

    try:
        # When: 수집 요청 (extraction 활성화)
        url = "https://httpbin.org/uuid"
        response = client.post("/ingest/web", json={"url": url, "enable_extraction": True})

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

        # Then: Job 상태 - Extraction 실패는 Job 실패가 아님 (Warning Logged) -> COMPLETED여야 함
        # If Neo4j is down, real_job_repo methods might fail.
        # But earlier test runs suggested Neo4j IS running.
        assert job["status"] == "COMPLETED"

        # Then: Document 저장이 호출되었는지 확인
        mock_repo.save_with_chunks.assert_called()

        # Args verification
        saved_doc = mock_repo.save_with_chunks.call_args[0][0]
        # source_url is now in metadata
        assert saved_doc.metadata["source_url"] == url
        assert "semantic_data" not in saved_doc.metadata

    finally:
        app.dependency_overrides.pop(get_ingestion_service, None)
