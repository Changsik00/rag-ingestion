"""
Integration Tests for Async Ingestion API

비동기 웹 수집 API 엔드포인트의 통합 테스트를 수행합니다.
Job 생성 및 백그라운드 처리 워크플로우를 검증합니다.
"""

from unittest.mock import Mock

import pytest
from fastapi.testclient import TestClient

from app.domain.entities.job import IngestionJob, JobStatus
from app.interfaces.api.dependencies import get_ingestion_service
from app.interfaces.api.main import app

pytestmark = pytest.mark.skip(reason="Requires infrastructure setup - see specs/integration-test-improvement.md")


client = TestClient(app)


def test_async_ingest_web_endpoint():
    # Given: Mock Ingestion
    mock_service = Mock()

    def create_job_side_effect(url, retry_of=None):
        print(f"DEBUG: create_job called with {url}")
        return IngestionJob(source_url=url, status=JobStatus.PENDING, job_id="test-job-id")

    mock_service.create_job.side_effect = create_job_side_effect

    def process_job_side_effect(job_id):
        print(f"DEBUG: process_job called with {job_id}")

    mock_service.process_job.side_effect = process_job_side_effect

    app.dependency_overrides[get_ingestion_service] = lambda: mock_service

    # When: POST /ingest/web 요청
    with TestClient(app) as client:
        response = client.post("/v1/ingest/web", json={"url": "http://example.com"})

    # Then: 202 응답 및 Job 생성 확인
    assert response.status_code == 202
    data = response.json()
    assert data["job_id"] == "test-job-id"
    assert data["status"] == "PENDING"

    # Cleanup
    app.dependency_overrides.clear()
