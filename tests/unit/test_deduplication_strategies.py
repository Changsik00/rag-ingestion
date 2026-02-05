from datetime import datetime, timezone, timedelta
from unittest.mock import Mock

import pytest

from app.application.services.deduplication_strategies import (
    ContentsStrategy,
    IDCheckingStrategy,
    MetadataCheckStrategy,
    TTLStrategy,
)
from app.domain.entities.job import IngestionJob, JobStatus


@pytest.fixture
def mock_job_repo():
    return Mock()


def create_job(
    source_url: str,
    job_id: str = "job-new",
    custom_metadata: dict = None,
    content_hash: str = None,
    created_at: datetime = None,
    **kwargs,
):
    status = kwargs.pop("status", JobStatus.PENDING)
    created_at = created_at or datetime.now(timezone.utc)

    job = IngestionJob(
        job_id=job_id,
        source_url=source_url,
        status=status,
        created_at=created_at,
        updated_at=datetime.now(timezone.utc),
        **kwargs,
    )
    job.custom_metadata = custom_metadata or {}
    job.content_hash = content_hash
    return job


class TestIDCheckingStrategy:
    @pytest.mark.asyncio
    async def test_detects_duplicate_if_exists(self, mock_job_repo):
        strategy = IDCheckingStrategy(mock_job_repo)
        new_job = create_job("https://example.com/1")

        # Exists and Completed
        last_job = create_job(
            "https://example.com/1", status=JobStatus.COMPLETED, job_id="old"
        )
        mock_job_repo.find_last_job_by_source.return_value = last_job

        assert await strategy.is_duplicate(new_job) is True

    @pytest.mark.asyncio
    async def test_not_duplicate_if_failed(self, mock_job_repo):
        strategy = IDCheckingStrategy(mock_job_repo)
        new_job = create_job("https://example.com/1")

        # Exists but Failed
        last_job = create_job(
            "https://example.com/1", status=JobStatus.FAILED, job_id="old"
        )
        mock_job_repo.find_last_job_by_source.return_value = last_job

        assert await strategy.is_duplicate(new_job) is False


class TestMetadataCheckStrategy:
    @pytest.mark.asyncio
    async def test_detects_duplicate_when_keys_match(self, mock_job_repo):
        keys = ["video_id"]
        strategy = MetadataCheckStrategy(mock_job_repo, keys=keys)

        new_job = create_job(
            "https://yt.com/1", custom_metadata={"video_id": "v1"}
        )

        last_job = create_job(
            "https://yt.com/1", status=JobStatus.COMPLETED, custom_metadata={"video_id": "v1"}
        )
        mock_job_repo.find_last_job_by_source.return_value = last_job

        assert await strategy.is_duplicate(new_job) is True

    @pytest.mark.asyncio
    async def test_not_duplicate_when_value_differs(self, mock_job_repo):
        strategy = MetadataCheckStrategy(mock_job_repo, keys=["file_size"])
        new_job = create_job("file://a.txt", custom_metadata={"file_size": 100})
        
        last_job = create_job(
            "file://a.txt", status=JobStatus.COMPLETED, custom_metadata={"file_size": 200}
        )
        mock_job_repo.find_last_job_by_source.return_value = last_job

        assert await strategy.is_duplicate(new_job) is False


class TestTTLStrategy:
    @pytest.mark.asyncio
    async def test_detects_duplicate_within_ttl(self, mock_job_repo):
        # TTL = 1 hour
        strategy = TTLStrategy(mock_job_repo, ttl_hours=1)
        new_job = create_job("https://news.com")

        # Last job was 30 mins ago
        ago_30m = datetime.now(timezone.utc) - timedelta(minutes=30)
        last_job = create_job(
            "https://news.com", status=JobStatus.COMPLETED, created_at=ago_30m
        )
        mock_job_repo.find_last_job_by_source.return_value = last_job

        assert await strategy.is_duplicate(new_job) is True

    @pytest.mark.asyncio
    async def test_not_duplicate_after_ttl(self, mock_job_repo):
        # TTL = 1 hour
        strategy = TTLStrategy(mock_job_repo, ttl_hours=1)
        new_job = create_job("https://news.com")

        # Last job was 2 hours ago
        ago_2h = datetime.now(timezone.utc) - timedelta(hours=2)
        last_job = create_job(
            "https://news.com", status=JobStatus.COMPLETED, created_at=ago_2h
        )
        mock_job_repo.find_last_job_by_source.return_value = last_job

        assert await strategy.is_duplicate(new_job) is False


class TestContentsStrategy:
    @pytest.mark.asyncio
    async def test_detects_duplicate_hash(self, mock_job_repo):
        strategy = ContentsStrategy(mock_job_repo)
        new_job = create_job("http://web.com", content_hash="hash-1")
        
        last_job = create_job(
            "http://web.com", status=JobStatus.COMPLETED, content_hash="hash-1"
        )
        mock_job_repo.find_last_job_by_source.return_value = last_job

        assert await strategy.is_duplicate(new_job) is True

    @pytest.mark.asyncio
    async def test_not_duplicate_different_hash(self, mock_job_repo):
        strategy = ContentsStrategy(mock_job_repo)
        new_job = create_job("http://web.com", content_hash="hash-2")
        
        last_job = create_job(
            "http://web.com", status=JobStatus.COMPLETED, content_hash="hash-1"
        )
        mock_job_repo.find_last_job_by_source.return_value = last_job

        assert await strategy.is_duplicate(new_job) is False
