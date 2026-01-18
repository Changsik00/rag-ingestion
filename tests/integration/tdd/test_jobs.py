"""
Integration Tests for Job API

Job 관련 API 엔드포인트의 통합 테스트를 수행합니다.
Job 조회, 리스트, 재시도 등의 기능을 검증합니다.
"""

from unittest.mock import Mock

from fastapi.testclient import TestClient

from app.domain.entities.job import IngestionJob, JobStatus
from app.interfaces.api.dependencies import get_ingestion_service, get_job_repository
from app.interfaces.api.main import app
from app.use_cases.ingestion import IngestionService

client = TestClient(app)

def test_list_jobs_endpoint():
    # Given: Mock JobRepository와 테스트 Job 데이터
    mock_job_repo = Mock()
    job1 = IngestionJob(source_url="http://test.com/1", status=JobStatus.COMPLETED)
    job2 = IngestionJob(source_url="http://test.com/2", status=JobStatus.PENDING)

    mock_job_repo.list_jobs.return_value = [job1, job2]

    app.dependency_overrides[get_job_repository] = lambda: mock_job_repo

    # When: GET /jobs 요청
    response = client.get("/jobs?limit=10")

    # Then: 200 응답 및 Job 리스트 반환
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["source_url"] == "http://test.com/1"
    assert data[0]["status"] == "COMPLETED"

    mock_job_repo.list_jobs.assert_called_once_with(limit=10)

    app.dependency_overrides.clear()

def test_get_job_endpoint():
    # Given: Mock JobRepository와 테스트 Job
    mock_job_repo = Mock()
    job = IngestionJob(job_id="test-id", source_url="http://test.com", status=JobStatus.COMPLETED)

    mock_job_repo.get_job.return_value = job

    app.dependency_overrides[get_job_repository] = lambda: mock_job_repo

    # When: GET /jobs/{job_id} 요청
    response = client.get("/jobs/test-id")

    # Then: 200 응답 및 Job 세부 정보 반환
    assert response.status_code == 200
    data = response.json()
    assert data["job_id"] == "test-id"
    assert data["status"] == "COMPLETED"

    mock_job_repo.get_job.assert_called_once_with("test-id")

    app.dependency_overrides.clear()

def test_retry_job_endpoint():
    # Given: Mock JobRepository와 IngestionService
    mock_job_repo = Mock()
    job = IngestionJob(job_id="test-id", source_url="http://test.com", status=JobStatus.FAILED)
    mock_job_repo.get_job.return_value = job

    mock_service = Mock(spec=IngestionService)
    new_job = IngestionJob(
        job_id="new-job-id",
        source_url="http://test.com",
        status=JobStatus.PENDING,
        retry_of="test-id"
    )
    mock_service.create_job.return_value = new_job

    app.dependency_overrides[get_job_repository] = lambda: mock_job_repo
    app.dependency_overrides[get_ingestion_service] = lambda: mock_service

    # When: POST /jobs/{job_id}/retry 요청
    response = client.post("/jobs/test-id/retry")

    # Then: 202 응답 및 새로운 Job 생성
    assert response.status_code == 202
    data = response.json()
    assert data["job_id"] == "new-job-id"
    assert data["status"] == "PENDING"

    mock_job_repo.get_job.assert_called_once_with("test-id")
    mock_service.create_job.assert_called_once_with("http://test.com", retry_of="test-id")
    mock_service.process_job.assert_called_once_with("new-job-id")

    app.dependency_overrides.clear()
