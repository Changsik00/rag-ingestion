from datetime import datetime
from unittest.mock import Mock

from fastapi.testclient import TestClient

from app.domain.entities.job import IngestionJob
from app.interfaces.api.dependencies import get_job_repository
from app.interfaces.api.main import app

client = TestClient(app)


def test_list_jobs_endpoint():
    # Given
    mock_repo = Mock()
    now = datetime.now()
    job = IngestionJob(
        job_id="job-123", status="COMPLETED", source_url="http://example.com/1", created_at=now, updated_at=now
    )
    mock_repo.list_jobs.return_value = [job]
    app.dependency_overrides[get_job_repository] = lambda: mock_repo

    # When
    response = client.get("/v1/jobs")

    # Then
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    # Check wrapper fields if list is wrapped?
    # list_jobs returns list[JobResponse]. Not wrapped in GenericResponse?
    # spec said list[JobResponse]. So it returns Array.
    # JobResponse inherits BaseResponse.
    item = data[0]
    assert item["status"] == "success"  # BaseResponse field
    assert item["current_status"] == "COMPLETED"  # Mapped field
    assert item["job_id"] == "job-123"

    app.dependency_overrides.clear()


def test_get_job_not_found():
    mock_repo = Mock()
    mock_repo.get_job.return_value = None
    app.dependency_overrides[get_job_repository] = lambda: mock_repo

    response = client.get("/v1/jobs/non-existent")

    # Global handler should catch EntityNotFoundError (if raised)
    # But get_job logic: if not job: raise EntityNotFoundError
    assert response.status_code == 404
    err = response.json()
    assert err["error_code"] == "ENTITY_NOT_FOUND"

    app.dependency_overrides.clear()
