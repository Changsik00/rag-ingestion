from abc import ABC, abstractmethod
from typing import List

from app.domain.entities.job import IngestionJob, JobStatus
from app.domain.interfaces.job_repository import JobRepository
from app.core.logger import setup_logger

logger = setup_logger(__name__)


class DeduplicationStrategy(ABC):
    """Abstract base class for deduplication strategies."""

    def __init__(self, job_repository: JobRepository):
        self.job_repository = job_repository

    @abstractmethod
    async def is_duplicate(self, job: IngestionJob) -> bool:
        """Check if the given job is a duplicate."""
        pass


class MetadataComparisonStrategy(DeduplicationStrategy):
    """
    Checks for duplication by comparing specific metadata keys.
    Useful for Source Types where metadata is reliable (e.g., YouTube video_id, Local File size/mtime).
    """

    def __init__(self, job_repository: JobRepository, keys: List[str]):
        super().__init__(job_repository)
        self.keys = keys

    async def is_duplicate(self, job: IngestionJob) -> bool:
        if not self.keys:
            logger.warning("MetadataComparisonStrategy initialized with no keys. Returning False.")
            return False

        # 1. Get the last successful job for this source
        last_job = self.job_repository.get_job_by_source(job.source_url)
        # Note: Ideally repository should support finding 'last successful job'.
        # Assuming get_job_by_source returns the most recent one or we need a new method.
        # For now, let's assume we fetch the job and check its status and metadata.
        # If get_job_by_source is not enough, we might need to extend the repository interface.
        # Let's use `find_last_job_by_source` as used in the test.
        
        # Check if the method exists on the repository (it might need to be added to interface)
        if hasattr(self.job_repository, "find_last_job_by_source"):
             last_job = self.job_repository.find_last_job_by_source(job.source_url)
        else:
            # Fallback for now if repo update is pending or mocked differently in real app
            # But the plan says we should update Infrastructure.
            pass

        if not last_job or last_job.status != JobStatus.COMPLETED:
            return False

        # 2. Compare Metadata
        current_meta = job.custom_metadata or {}
        last_meta = last_job.custom_metadata or {}

        for key in self.keys:
            current_val = current_meta.get(key)
            last_val = last_meta.get(key)
            
            if current_val is None:
                logger.debug(f"Metadata key '{key}' missing in current job. Cannot determine duplicate.")
                return False
                
            if current_val != last_val:
                logger.debug(f"Metadata mismatch for key '{key}': {current_val} != {last_val}")
                return False

        logger.info(f"Duplicate detected via Metadata Strategy (Keys: {self.keys})")
        return True


class ContentHashStrategy(DeduplicationStrategy):
    """
    Checks for duplication by comparing content hashes.
    Useful for Web Pages or Unstructured Text where metadata is unreliable.
    """

    async def is_duplicate(self, job: IngestionJob) -> bool:
        if not job.content_hash:
            logger.warning("ContentHashStrategy: Job has no content_hash. Cannot determine duplicate.")
            return False

        # 1. Get the last successful job
        last_job = None
        if hasattr(self.job_repository, "find_last_job_by_source"):
             last_job = self.job_repository.find_last_job_by_source(job.source_url)

        if not last_job or last_job.status != JobStatus.COMPLETED:
            return False

        # 2. Compare Hash
        if last_job.content_hash == job.content_hash:
             logger.info(f"Duplicate detected via Content Hash Strategy")
             return True
        
        return False


class DeduplicationFactory:
    """
    Factory to select the appropriate strategy based on configuration or source type.
    """
    def __init__(self, job_repository: JobRepository):
        self.job_repository = job_repository

    def get_strategy(self, source_url: str) -> DeduplicationStrategy:
        # Simple heuristic mapping for now. 
        # In a real system, this could be driven by a more complex Config mapping.
        
        if "youtube.com" in source_url or "youtu.be" in source_url:
            # For YouTube, we check 'video_id' (and maybe others like 'channel_id' if needed)
            return MetadataComparisonStrategy(self.job_repository, keys=["video_id"])
        
        if source_url.startswith("file://"):
            # For Files, we check size and mtime
            return MetadataComparisonStrategy(self.job_repository, keys=["file_size", "last_modified"])
            
        # Default Web or others -> Content Hash
        return ContentHashStrategy(self.job_repository)
