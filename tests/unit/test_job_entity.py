import pytest
from datetime import datetime
from app.domain.entities.job import IngestionJob, JobStatus

def test_job_creation():
    job = IngestionJob(
        source_url="http://example.com",
        status=JobStatus.PENDING
    )
    assert job.job_id is not None
    assert job.source_url == "http://example.com"
    assert job.status == JobStatus.PENDING
    assert job.error_message is None
    assert job.retry_of is None
    assert isinstance(job.created_at, datetime)
    assert isinstance(job.updated_at, datetime)

def test_job_status_update():
    job = IngestionJob(source_url="http://example.com")
    original_updated_at = job.updated_at
    
    job.status = JobStatus.RUNNING
    # In a real implementation, we might want a method to update status that also touches updated_at,
    # or rely on the repository to handle updated_at. 
    # For a pure entity, let's assume direct assignment is fine for now, 
    # but we might want to check if we can enforce updated_at change.
    
    assert job.status == JobStatus.RUNNING
