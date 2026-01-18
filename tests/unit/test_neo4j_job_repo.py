from unittest.mock import MagicMock, Mock

from app.domain.entities.job import IngestionJob, JobStatus
from app.infrastructure.storage.neo4j_job_repository import Neo4jJobRepository


def test_create_job():
    # Given: Mock driver와 session
    driver_mock = Mock()
    session_mock = MagicMock()
    driver_mock.session.return_value = session_mock
    session_mock.__enter__.return_value = session_mock
    session_mock.__exit__.return_value = None

    repo = Neo4jJobRepository(driver_mock)
    job = IngestionJob(source_url="http://example.com")

    # When: Job 생성
    repo.create_job(job)

    # Then: MERGE 쿼리가 실행됨
    session_mock.run.assert_called()
    args, _ = session_mock.run.call_args
    query = args[0]
    assert "MERGE (j:IngestionJob {job_id: $job_id})" in query
    assert "SET j.source_url = $source_url" in query

def test_update_job():
    # Given: Mock driver와 repository
    driver_mock = Mock()
    session_mock = MagicMock()
    driver_mock.session.return_value = session_mock
    session_mock.__enter__.return_value = session_mock
    session_mock.__exit__.return_value = None

    repo = Neo4jJobRepository(driver_mock)
    job = IngestionJob(source_url="http://example.com", status=JobStatus.COMPLETED)

    # When: Job 업데이트
    repo.update_job(job)

    # Then: MATCH + SET 쿼리가 실행됨
    session_mock.run.assert_called()
    args, _ = session_mock.run.call_args
    query = args[0]
    assert "MATCH (j:IngestionJob {job_id: $job_id})" in query
    assert "SET j.status = $status" in query

def test_get_job():
    # Given: Mock driver와 Job 데이터
    driver_mock = Mock()
    session_mock = MagicMock()
    driver_mock.session.return_value = session_mock
    session_mock.__enter__.return_value = session_mock
    session_mock.__exit__.return_value = None

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

    # When: Job ID로 Job 조회
    repo = Neo4jJobRepository(driver_mock)
    job = repo.get_job("test-id")

    # Then: IngestionJob 엔티티 반환
    assert job is not None
    assert job.job_id == "test-id"
    assert job.status == JobStatus.COMPLETED

def test_list_jobs():
    # Given: Mock driver와 Job 리스트
    driver_mock = Mock()
    session_mock = MagicMock()
    driver_mock.session.return_value = session_mock
    session_mock.__enter__.return_value = session_mock
    session_mock.__exit__.return_value = None

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

    # When: Job 리스트 조회 (limit=10)
    repo = Neo4jJobRepository(driver_mock)
    jobs = repo.list_jobs(limit=10)

    # Then: Job 리스트 반환
    assert len(jobs) == 1
    assert jobs[0].job_id == "test-id"
