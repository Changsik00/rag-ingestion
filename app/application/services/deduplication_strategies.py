from abc import ABC, abstractmethod
from datetime import datetime, timezone, timedelta

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
        # 1. Get the last successful job for this source
        last_job = None
        if hasattr(self.job_repository, "find_last_job_by_source"):
            last_job = self.job_repository.find_last_job_by_source(job.source_url)

        if last_job and last_job.status in [JobStatus.COMPLETED, JobStatus.RUNNING]:
            logger.info("Duplicate detected via ID Checking Strategy (Source URL exists)")
            return True

        return False


class MetadataCheckStrategy(DeduplicationStrategy):
    """
    Checks for duplication by comparing specific metadata keys.
    Useful for Files (size, mtime) or YouTube (video_id).
    """

    def __init__(self, job_repository: JobRepository, keys: list[str]):
        super().__init__(job_repository)
        self.keys = keys

    async def is_duplicate(self, job: IngestionJob) -> bool:
        if not self.keys:
            logger.warning(
                "MetadataCheckStrategy initialized with no keys. Returning False."
            )
            return False

        last_job = None
        if hasattr(self.job_repository, "find_last_job_by_source"):
            last_job = self.job_repository.find_last_job_by_source(job.source_url)

        if not last_job or last_job.status not in [
            JobStatus.COMPLETED,
            JobStatus.RUNNING,
        ]:
            return False

        # Compare Metadata
        current_meta = job.custom_metadata or {}
        last_meta = last_job.custom_metadata or {}

        for key in self.keys:
            current_val = current_meta.get(key)
            last_val = last_meta.get(key)

            if current_val is None:
                # Key missing in current job, cannot verify duplication safely
                return False

            if current_val != last_val:
                # Mismatch found
                return False

        logger.info(f"Duplicate detected via Metadata Strategy (Keys: {self.keys})")
        return True


class TTLStrategy(DeduplicationStrategy):
    """
    Checks for duplication based on Time-To-Live (TTL).
    If the last ingestion was recent (within TTL), it is considered a duplicate (skip).
    Useful for News, periodically updated pages.
    """

    def __init__(self, job_repository: JobRepository, ttl_hours: int = 24):
        super().__init__(job_repository)
        self.ttl_hours = ttl_hours

    async def is_duplicate(self, job: IngestionJob) -> bool:
        last_job = None
        if hasattr(self.job_repository, "find_last_job_by_source"):
            last_job = self.job_repository.find_last_job_by_source(job.source_url)

        if not last_job or last_job.status not in [
            JobStatus.COMPLETED,
            JobStatus.RUNNING,
        ]:
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
    """

    async def is_duplicate(self, job: IngestionJob) -> bool:
        if not job.content_hash:
            logger.warning(
                "ContentsStrategy: Job has no content_hash. Cannot determine duplicate."
            )
            return False

        last_job = None
        if hasattr(self.job_repository, "find_last_job_by_source"):
            last_job = self.job_repository.find_last_job_by_source(job.source_url)

        if not last_job or last_job.status not in [
            JobStatus.COMPLETED,
            JobStatus.RUNNING,
        ]:
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

        # 2. Files -> Metadata (size, mtime)
        if source_url.startswith("file://"):
            return MetadataCheckStrategy(
                self.job_repository, keys=["file_size", "last_modified"]
            )

        # 3. News / Portal -> TTL Strategy (Example implementation)
        # TODO: Implement domain-based routing or config-based strategy selection
        # For News sites (e.g., cnn.com, bbc.com), where main pages update periodically,
        # we should use TTLStrategy to avoid continuous re-ingestion within a short window.
        # if "news.com" in source_url:
        #     return TTLStrategy(self.job_repository, ttl_hours=1)

        # 4. Blogs / Wikis -> Contents Strategy
        # For content-heavy sites (Blogs, Wikis) where the URL is stable but content might receive
        # minor updates or corrections, we use ContentsStrategy to compare the actual hash.
        # This is the default safely fallback for general web pages.
        return ContentsStrategy(self.job_repository)
