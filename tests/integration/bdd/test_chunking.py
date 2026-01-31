import time
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from app.interfaces.api.dependencies import get_repository
from app.interfaces.api.main import app

pytestmark = pytest.mark.skip(reason="Requires infrastructure setup - see specs/integration-test-improvement.md")


client = TestClient(app)


def wait_for_job_completion(job_id: str, timeout: int = 10):
    for _ in range(timeout):
        response = client.get(f"/jobs/{job_id}")
        if response.status_code != 200:
            break
        job = response.json()
        if job.get("status") in ["COMPLETED", "FAILED"]:
            return job
        time.sleep(1)
    raise TimeoutError(f"Job {job_id} did not complete within {timeout} seconds")


@pytest.mark.integration
def test_ingestion_saves_chunks():
    """
    Given: Ingestion request
    When: Job completes
    Then: Repository.save_with_chunks is called
    """
    # Given
    # Create a wrapper or spy for the repository
    # We need to override the dependency to inspect calls

    # Check if we can get the real repository and just wrap it, or just use a full Mock?
    # Using a full Mock avoids DB requirement for this specific verify,
    # but we want "Integration" test.
    # If we use Full Mock, we lose "Integration" value (we tested this in unit test).
    # Ideally we spy on the real repository.
    # But for now, let's use a Mock Repository to ensure the PIPELINE calls the right method.

    mock_repo = MagicMock()
    app.dependency_overrides[get_repository] = lambda: mock_repo

    url = "https://example.com"

    try:
        # When
        response = client.post("/v1/ingest/web", json={"url": url, "enable_extraction": False})

        # Then
        assert response.status_code == 202
        job_id = response.json()["job_id"]

        job = wait_for_job_completion(job_id)

        assert job["status"] == "COMPLETED"

        # Verify save_with_chunks was called
        # mock_repo.save_with_chunks.assert_called()
        # Note: In threaded environment (BackgroundTasks), assertion on Mock might be tricky
        # because the Mock object is shared. TestClient runs synchronously?
        # FastAPI BackgroundTasks run in the same thread/process usually in TestClient unless using actual workers.
        # But `process_job` is called in background.

        mock_repo.save_with_chunks.assert_called()

    finally:
        app.dependency_overrides = {}
