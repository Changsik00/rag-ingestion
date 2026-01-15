from fastapi.testclient import TestClient
from unittest.mock import Mock, ANY
from app.interfaces.api.main import app
from app.interfaces.api.dependencies import get_job_repository, get_ingestion_service
from app.domain.entities.job import IngestionJob, JobStatus
from datetime import datetime, timezone
from app.use_cases.ingestion import IngestionService
from app.domain.models.ingest import IngestResponse

client = TestClient(app)

def test_list_jobs_endpoint():
    mock_job_repo = Mock()
    job1 = IngestionJob(source_url="http://test.com/1", status=JobStatus.COMPLETED)
    job2 = IngestionJob(source_url="http://test.com/2", status=JobStatus.PENDING)
    
    mock_job_repo.list_jobs.return_value = [job1, job2]
    
    app.dependency_overrides[get_job_repository] = lambda: mock_job_repo
    
    response = client.get("/jobs?limit=10")
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["source_url"] == "http://test.com/1"
    assert data[0]["status"] == "COMPLETED"
    
    mock_job_repo.list_jobs.assert_called_once_with(limit=10)
    
    app.dependency_overrides.clear()

def test_get_job_endpoint():
    mock_job_repo = Mock()
    job = IngestionJob(job_id="test-id", source_url="http://test.com", status=JobStatus.COMPLETED)
    
    mock_job_repo.get_job.return_value = job
    
    app.dependency_overrides[get_job_repository] = lambda: mock_job_repo
    
    response = client.get("/jobs/test-id")
    
    assert response.status_code == 200
    data = response.json()
    assert data["job_id"] == "test-id"
    assert data["status"] == "COMPLETED"
    
    mock_job_repo.get_job.assert_called_once_with("test-id")
    
    app.dependency_overrides.clear()

def test_retry_job_endpoint():
    mock_job_repo = Mock()
    job = IngestionJob(job_id="test-id", source_url="http://test.com", status=JobStatus.FAILED)
    mock_job_repo.get_job.return_value = job
    
    mock_service = Mock(spec=IngestionService)
    expected_response = IngestResponse(url="http://test.com/", markdown="# Rescraped", metadata={})
    mock_service.ingest.return_value = expected_response
    
    app.dependency_overrides[get_job_repository] = lambda: mock_job_repo
    app.dependency_overrides[get_ingestion_service] = lambda: mock_service
    
    response = client.post("/jobs/test-id/retry")
    
    assert response.status_code == 200
    data = response.json()
    assert data["markdown"] == "# Rescraped"
    
    mock_job_repo.get_job.assert_called_once_with("test-id")
    mock_service.ingest.assert_called_once_with("http://test.com")
    
    app.dependency_overrides.clear()
