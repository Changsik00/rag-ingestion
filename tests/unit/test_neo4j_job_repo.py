import pytest
from unittest.mock import Mock, MagicMock
from app.domain.entities.job import IngestionJob, JobStatus
from app.infrastructure.storage.neo4j_job_repo import Neo4jJobRepository

def test_create_job():
    driver_mock = Mock()
    session_mock = MagicMock()
    driver_mock.session.return_value = session_mock
    # session context manager
    session_mock.__enter__.return_value = session_mock
    session_mock.__exit__.return_value = None
    
    repo = Neo4jJobRepository(driver_mock)
    job = IngestionJob(source_url="http://example.com")
    
    repo.create_job(job)
    
    # Verify run was called
    session_mock.run.assert_called()
    args, _ = session_mock.run.call_args
    query = args[0]
    assert "MERGE (j:IngestionJob {job_id: $job_id})" in query
    assert "SET j.source_url = $source_url" in query

def test_update_job():
    driver_mock = Mock()
    session_mock = MagicMock()
    driver_mock.session.return_value = session_mock
    session_mock.__enter__.return_value = session_mock
    session_mock.__exit__.return_value = None
    
    repo = Neo4jJobRepository(driver_mock)
    job = IngestionJob(source_url="http://example.com", status=JobStatus.COMPLETED)
    
    repo.update_job(job)
    
    session_mock.run.assert_called()
    args, _ = session_mock.run.call_args
    query = args[0]
    assert "MATCH (j:IngestionJob {job_id: $job_id})" in query
    assert "SET j.status = $status" in query

def test_get_job():
    driver_mock = Mock()
    session_mock = MagicMock()
    driver_mock.session.return_value = session_mock
    session_mock.__enter__.return_value = session_mock
    session_mock.__exit__.return_value = None
    
    # Mock result
    record_mock = MagicMock()
    node_mock = {
        "job_id": "test-id",
        "source_url": "http://example.com",
        "status": "COMPLETED",
        "created_at": "2023-01-01T12:00:00+00:00",
        "updated_at": "2023-01-01T13:00:00+00:00",
        "error_message": None,
        "retry_of": None
    }
    record_mock.__getitem__.side_effect = lambda k: node_mock if k == "j" else None
    
    result_mock = Mock()
    result_mock.single.return_value = record_mock
    session_mock.run.return_value = result_mock
    
    repo = Neo4jJobRepository(driver_mock)
    job = repo.get_job("test-id")
    
    assert job is not None
    assert job.job_id == "test-id"
    assert job.status == JobStatus.COMPLETED

def test_list_jobs():
    driver_mock = Mock()
    session_mock = MagicMock()
    driver_mock.session.return_value = session_mock
    session_mock.__enter__.return_value = session_mock
    session_mock.__exit__.return_value = None
    
    # Mock result iteration
    record_mock = MagicMock()
    node_mock = {
        "job_id": "test-id",
        "source_url": "http://example.com",
        "status": "PENDING",
        "created_at": "2023-01-01T12:00:00+00:00",
        "updated_at": "2023-01-01T12:00:00+00:00",
        "error_message": None
    }
    record_mock.__getitem__.side_effect = lambda k: node_mock if k == "j" else None
    
    result_mock = Mock()
    result_mock.__iter__ = Mock(return_value=iter([record_mock]))
    session_mock.run.return_value = result_mock
    
    repo = Neo4jJobRepository(driver_mock)
    jobs = repo.list_jobs(limit=10)
    
    assert len(jobs) == 1
    assert jobs[0].job_id == "test-id"
