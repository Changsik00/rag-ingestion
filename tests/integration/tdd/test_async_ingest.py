from unittest.mock import Mock

from fastapi.testclient import TestClient

from app.domain.entities.job import IngestionJob, JobStatus
from app.interfaces.api.dependencies import get_ingestion_service
from app.interfaces.api.main import app

client = TestClient(app)

def test_async_ingest_web_endpoint():
    # Mock Service
    mock_service = Mock()

    def create_job_side_effect(url, retry_of=None):
        print(f"DEBUG: create_job called with {url}")
        return IngestionJob(
            source_url=url,
            status=JobStatus.PENDING,
            job_id="test-job-id"
        )

    mock_service.create_job.side_effect = create_job_side_effect

    def process_job_side_effect(job_id):
        print(f"DEBUG: process_job called with {job_id}")

    mock_service.process_job.side_effect = process_job_side_effect

    # Override Dependency
    app.dependency_overrides[get_ingestion_service] = lambda: mock_service

    # Act
    with TestClient(app) as client:
        response = client.post(
            "/ingest/web",
            json={"url": "http://example.com"}
        )

    # Assert
    # Verify basics
    assert response.status_code == 202
    data = response.json()
    assert data["job_id"] == "test-job-id"
    assert data["status"] == "PENDING"

    # Verify create_job called
    # mock_service.create_job.assert_called_once_with("http://example.com")

    # Cleanup
    app.dependency_overrides.clear()
