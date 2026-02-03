"""
Unit Tests for IngestionJob Entity

IngestionJob 엔티티의 생성 및 상태 관리 기능을 검증합니다.
"""

from datetime import datetime

from app.domain.entities.job import IngestionJob, JobStatus


def test_job_creation():
    # Given: Job 생성 요청
    # When: IngestionJob 엔티티 생성
    job = IngestionJob(source_url="http://example.com", status=JobStatus.PENDING)

    # Then: Job이 정상적으로 생성되고 기본값이 설정됨
    assert job.job_id is not None
    assert job.source_url == "http://example.com"
    assert job.status == JobStatus.PENDING
    assert job.error_message is None
    assert job.retry_of is None
    assert isinstance(job.created_at, datetime)
    assert isinstance(job.updated_at, datetime)


def test_job_status_update():
    # Given: PENDING 상태의 Job
    job = IngestionJob(source_url="http://example.com")
    # original_updated_at = job.updated_at (unused)

    # When: Job 상태를 RUNNING으로 변경
    job.status = JobStatus.RUNNING
    # In a real implementation, we might want a method to update status that also touches updated_at,
    # or rely on the repository to handle updated_at.
    # For a pure entity, let's assume direct assignment is fine for now,
    # but we might want to check if we can enforce updated_at change.

    # Then: 상태가 변경됨
    assert job.status == JobStatus.RUNNING
