from abc import ABC, abstractmethod
from datetime import datetime, timedelta, timezone

from app.core.logger import setup_logger
from app.domain.entities.job import IngestionJob, JobStatus
from app.domain.interfaces.job_repository import JobRepository

logger = setup_logger(__name__)


class DeduplicationStrategy(ABC):
    """Abstract base class for deduplication strategies."""

    def __init__(self, job_repository: JobRepository):
        self.job_repository = job_repository

    @abstractmethod
    async def is_duplicate(self, job: IngestionJob) -> bool:
        """Check if the given job is a duplicate."""
        pass


class IDCheckingStrategy(DeduplicationStrategy):
    """
    Checks for duplication by Source ID (URL).
    If a completed or running job exists for this Source URL, it is considered a duplicate.
    Useful for immutable resources or 'ingest once' policies.
    """

    async def is_duplicate(self, job: IngestionJob) -> bool:
        # 1. Get the last job for this source, excluding the current job
        last_job = None
        if hasattr(self.job_repository, "find_last_job_by_source"):
            last_job = self.job_repository.find_last_job_by_source(
                job.source_url,
                exclude_job_id=job.job_id,
                statuses=[JobStatus.COMPLETED, JobStatus.RUNNING, JobStatus.PENDING],
            )

        if last_job and last_job.status in [JobStatus.COMPLETED, JobStatus.RUNNING, JobStatus.PENDING]:
            logger.info(f"Duplicate detected via ID Checking Strategy (Status: {last_job.status})")
            return True

        return False


class MetadataCheckStrategy(DeduplicationStrategy):
    """
    Checks for duplication by comparing specific metadata keys.
    Useful for Files (size, mtime) or YouTube (video_id).
    Note: Also acts as a concurrency guard if another job is RUNNING for the same URL.
    """

    def __init__(self, job_repository: JobRepository, keys: list[str]):
        super().__init__(job_repository)
        self.keys = keys

    async def is_duplicate(self, job: IngestionJob) -> bool:
        if not hasattr(self.job_repository, "find_last_job_by_source"):
            return False

        last_job = self.job_repository.find_last_job_by_source(
            job.source_url,
            exclude_job_id=job.job_id,
            statuses=[JobStatus.COMPLETED, JobStatus.RUNNING, JobStatus.PENDING],
        )

        if not last_job:
            return False

        # Concurrency Guard: If a job is currently RUNNING for this URL, it's a duplicate
        if last_job.status == JobStatus.RUNNING:
            logger.info("Duplicate detected via Metadata Strategy (Concurrent job running)")
            return True

        if last_job.status != JobStatus.COMPLETED:
            return False

        # Compare Metadata
        if not self.keys:
            return False

        current_meta = job.custom_metadata or {}
        last_meta = last_job.custom_metadata or {}

        for key in self.keys:
            current_val = current_meta.get(key)
            last_val = last_meta.get(key)

            if current_val is None or current_val != last_val:
                return False

        logger.info(f"Duplicate detected via Metadata Strategy (Keys: {self.keys})")
        return True


class TTLStrategy(DeduplicationStrategy):
    """
    Checks for duplication based on Time-To-Live (TTL).
    If the last ingestion was recent (within TTL), it is considered a duplicate.
    """

    def __init__(self, job_repository: JobRepository, ttl_hours: int = 24):
        super().__init__(job_repository)
        self.ttl_hours = ttl_hours

    async def is_duplicate(self, job: IngestionJob) -> bool:
        if not hasattr(self.job_repository, "find_last_job_by_source"):
            return False

        last_job = self.job_repository.find_last_job_by_source(
            job.source_url,
            exclude_job_id=job.job_id,
            statuses=[JobStatus.COMPLETED, JobStatus.RUNNING, JobStatus.PENDING],
        )

        if not last_job:
            return False

        # Concurrency Guard
        if last_job.status == JobStatus.RUNNING:
            logger.info("Duplicate detected via TTL Strategy (Concurrent job running)")
            return True

        if last_job.status != JobStatus.COMPLETED:
            return False

        # Calculate time diff
        now = datetime.now(timezone.utc)
        last_time = last_job.created_at

        if (now - last_time) < timedelta(hours=self.ttl_hours):
            logger.info(f"Duplicate detected via TTL Strategy (Within {self.ttl_hours}h)")
            return True

        return False


class ContentsStrategy(DeduplicationStrategy):
    """
    Checks for duplication by comparing content hashes.
    Useful for Web Pages where content changes matter but URL is same.
    Note: Also acts as a concurrency guard if another job is RUNNING for the same URL.
    """

    async def is_duplicate(self, job: IngestionJob) -> bool:
        if not hasattr(self.job_repository, "find_last_job_by_source"):
            return False

        last_job = self.job_repository.find_last_job_by_source(
            job.source_url,
            exclude_job_id=job.job_id,
            statuses=[JobStatus.COMPLETED, JobStatus.RUNNING, JobStatus.PENDING],
        )

        if not last_job:
            return False

        # Concurrency Guard: If a job is currently RUNNING for this source, skip the new one.
        # This is critical because for new jobs, content_hash is None (pre-scrape).
        if last_job.status == JobStatus.RUNNING:
            logger.info("Duplicate detected via Contents Strategy (Concurrent job running)")
            return True

        if last_job.status != JobStatus.COMPLETED:
            return False

        if not job.content_hash:
            # Cannot check hash-based duplication yet (pre-scrape)
            return False

        # Compare Hash
        if last_job.content_hash == job.content_hash:
            logger.info("Duplicate detected via Contents Hash Strategy")
            return True

        return False


class DeduplicationFactory:
    """
    Factory to select the appropriate strategy based on configuration or source type.
    """

    def __init__(self, job_repository: JobRepository):
        self.job_repository = job_repository

    def get_strategy(self, source_url: str) -> DeduplicationStrategy:
        # 1. YouTube -> Metadata (video_id)
        if "youtube.com" in source_url or "youtu.be" in source_url:
            return MetadataCheckStrategy(self.job_repository, keys=["video_id"])

        # 2. Files -> Metadata (size)
        if source_url.startswith("file://"):
            return MetadataCheckStrategy(self.job_repository, keys=["file_size"])

        # 3. Dedicated / Special sites could use specialized strategies (TTL, Contents)
        # For now, default to IDCheckingStrategy for general web pages to stop concurrent job piling.
        # This is the safest default when we don't have enough metadata/hash yet.
        return IDCheckingStrategy(self.job_repository)
