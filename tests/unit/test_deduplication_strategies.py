import pytest
from unittest.mock import Mock, AsyncMock
from datetime import datetime, timezone

from app.domain.entities.job import IngestionJob, JobStatus

# We'll import these even though they don't exist yet (TDD)
# logic-based strategies
from app.application.services.deduplication_strategies import (
    MetadataComparisonStrategy,
    ContentHashStrategy,
)

@pytest.fixture
def mock_job_repo():
    return Mock()

def create_job(
    source_url: str, 
    job_id: str = "job-new", 
    custom_metadata: dict = None,
    content_hash: str = None,
    **kwargs
):
    # Simulating the updated IngestionJob entity structure
    job = IngestionJob(
        job_id=job_id,
        source_url=source_url,
        status=JobStatus.PENDING,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        **kwargs
    )
    # Dynamically adding fields for test until actual entity is updated
    job.custom_metadata = custom_metadata or {}
    job.content_hash = content_hash
    return job

class TestMetadataComparisonStrategy:
    
    @pytest.mark.asyncio
    async def test_detects_duplicate_when_keys_match(self, mock_job_repo):
        # Given: Strategy checking 'video_id' and 'upload_date'
        keys_to_check = ["video_id", "upload_date"]
        strategy = MetadataComparisonStrategy(mock_job_repo, keys=keys_to_check)
        
        # New Job
        new_job = create_job(
            "https://youtube.com/v/123", 
            custom_metadata={"video_id": "vid-123", "upload_date": "2024-01-01"}
        )
        
        # Existing Job (Last successful job) with SAME metadata
        last_job = create_job(
            "https://youtube.com/v/123",
            job_id="job-old",
            status=JobStatus.COMPLETED,
            custom_metadata={"video_id": "vid-123", "upload_date": "2024-01-01"}
        )
        mock_job_repo.find_last_job_by_source.return_value = last_job
        
        # When
        is_dup = await strategy.is_duplicate(new_job)
        
        # Then
        assert is_dup is True

    @pytest.mark.asyncio
    async def test_not_duplicate_when_value_differs(self, mock_job_repo):
        # Given
        strategy = MetadataComparisonStrategy(mock_job_repo, keys=["file_size"])
        
        new_job = create_job("file://doc.pdf", custom_metadata={"file_size": 100})
        
        # Existing job has different size
        last_job = create_job("file://doc.pdf", job_id="job-old", custom_metadata={"file_size": 99})
        mock_job_repo.find_last_job_by_source.return_value = last_job
        
        # When
        is_dup = await strategy.is_duplicate(new_job)
        
        # Then
        assert is_dup is False

    @pytest.mark.asyncio
    async def test_not_duplicate_when_key_missing(self, mock_job_repo):
        # Given
        strategy = MetadataComparisonStrategy(mock_job_repo, keys=["file_size"])
        
        new_job = create_job("file://doc.pdf", custom_metadata={"file_size": 100})
        
        # Existing job is missing the key
        last_job = create_job("file://doc.pdf", job_id="job-old", custom_metadata={})
        mock_job_repo.find_last_job_by_source.return_value = last_job
        
        assert await strategy.is_duplicate(new_job) is False


class TestContentHashStrategy:
    
    @pytest.mark.asyncio
    async def test_detects_duplicate_hash(self, mock_job_repo):
        # Given
        strategy = ContentHashStrategy(mock_job_repo)
        
        new_job = create_job("http://web.com", content_hash="hash-abc")
        
        last_job = create_job("http://web.com", content_hash="hash-abc", status=JobStatus.COMPLETED)
        mock_job_repo.find_last_job_by_source.return_value = last_job
        
        assert await strategy.is_duplicate(new_job) is True

    @pytest.mark.asyncio
    async def test_not_duplicate_different_hash(self, mock_job_repo):
        # Given
        strategy = ContentHashStrategy(mock_job_repo)
        
        new_job = create_job("http://web.com", content_hash="hash-new")
        
        last_job = create_job("http://web.com", content_hash="hash-old", status=JobStatus.COMPLETED)
        mock_job_repo.find_last_job_by_source.return_value = last_job
        
        assert await strategy.is_duplicate(new_job) is False
