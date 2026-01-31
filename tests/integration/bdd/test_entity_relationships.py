"""
BDD Integration Tests for Entity-Entity Relationships

Task 10-1: BDD Scenario 작성

Given-When-Then 구조로 실제 App 로직 테스트 (TestClient 사용)
"""

from time import sleep
from unittest.mock import Mock

import pytest
from fastapi.testclient import TestClient

from app.interfaces.api.dependencies import get_scraper
from app.interfaces.api.dto.ingest import IngestResponse
from app.interfaces.api.main import app

pytestmark = pytest.mark.skip(reason="Requires infrastructure setup - see specs/integration-test-improvement.md")


client = TestClient(app)


@pytest.fixture(scope="module")
def sample_document_with_relationships():
    """관계가 포함된 샘플 문서"""
    return {
        "url": "https://example.com/elon-musk-tesla",
        "content": """
        Elon Musk founded Tesla in 2003. He also founded SpaceX and leads both companies.
        Tesla uses Python for their software development. The company is headquartered in Austin, Texas.
        Musk's leadership style is related to innovation and rapid development.
        """,
    }


@pytest.mark.integration
def test_scenario_1_to_4_entity_relationships_flow(sample_document_with_relationships):
    """

    Unified BDD Scenario for Entity Relationships

    Test Flow:
    1. Ingest document (Mock Scraper) -> Verify Job Completion
    2. Verify Extraction & Storage (Neo4j/Graph) matches 'Elon Musk'
    3. Test API retrieval of relationships
    4. Test filtering
    """
    # ----------------------------------------------------------------
    # Scenario 1: Relationship 추출 및 저장
    # ----------------------------------------------------------------

    # Given: Mock Scraper that returns the sample text
    mock_scraper = Mock()
    mock_content = IngestResponse(
        url=sample_document_with_relationships["url"],
        markdown=sample_document_with_relationships["content"],
        metadata={"title": "Elon Musk Bio"},
    )
    mock_scraper.scrape.return_value = mock_content

    # Apply Override
    app.dependency_overrides[get_scraper] = lambda: mock_scraper

    try:
        # When: 문서 수집 요청
        response = client.post("/ingest/web", json={"url": sample_document_with_relationships["url"]})

        # Then: 202 Accepted 응답
        assert response.status_code == 202, f"Ingestion failed: {response.text}"
        job_data = response.json()
        job_id = job_data["job_id"]

        # Wait for job to complete
        # Note: In TestClient, BackgroundTasks run synchronously after the response (in Starlette/FastAPI < 0.100)
        # OR we might need to poll if it's truly async in the app design using thread pool.
        # process_job uses background_tasks.add_task, which TestClient usually executes nicely.
        # But if process_job calls other async stuff or if we want to be sure, we poll.

        max_retries = 30
        job_status = None
        for _ in range(max_retries):
            # Polling
            status_response = client.get(f"/jobs/{job_id}")
            if status_response.status_code == 200:
                job_status = status_response.json()
                if job_status["status"] in ["COMPLETED", "FAILED"]:
                    break
            sleep(0.5)

        assert job_status["status"] == "COMPLETED", f"Job failed: {job_status.get('error_message')}"

    finally:
        app.dependency_overrides.pop(get_scraper, None)

    # ----------------------------------------------------------------
    # Scenario 2: Relationship API 조회
    # ----------------------------------------------------------------

    # Given: "Elon Musk" entity (extracted from text)
    entity_name = "Elon Musk"

    # When: 관계 조회 요청
    # Note: Using URL encoding for spaces if needed, but TestClient handles paths well
    response = client.get(f"/entities/{entity_name}/relationships")

    # Then: 200 OK or 404 (if extraction failed). We expect success if LLM works.
    # Note: If real LLM is used and fails to extract, this might fail.
    # We assume Integration Environment has working LLM (Gemini).
    if response.status_code == 200:
        relationships = response.json()
        assert isinstance(relationships, list)
    else:
        # If 404, maybe name is "Elon_Musk" or partial.
        # Or maybe LLM didn't extract it.
        # For stability, if LLM is flaky, we might need to mock Extractor too.
        # But for now let's assert 200 to catch regressions.
        assert response.status_code == 200, f"Entity not found: {response.text}"

    # ----------------------------------------------------------------
    # Scenario 3: Relationship 타입별 필터링
    # ----------------------------------------------------------------

    # When: FOUNDED 타입만 필터링 (Assuming 'founded' relation was extracted)
    response = client.get(f"/entities/{entity_name}/relationships", params={"relationship_type": "FOUNDED"})

    assert response.status_code == 200
    relationships = response.json()
    for rel in relationships:
        assert rel.get("relationship_type") == "FOUNDED"

    # ----------------------------------------------------------------
    # Scenario 4: 잘못된 Relationship 타입 처리
    # ----------------------------------------------------------------

    response = client.get(f"/entities/{entity_name}/relationships", params={"relationship_type": "INVALID_TYPE"})

    # Then: 400 Bad Request
    assert response.status_code == 400
    assert "Invalid relationship_type" in response.json()["detail"]
