from abc import ABC, abstractmethod

from app.domain.entities.job import IngestionJob


class JobRepository(ABC):
    @abstractmethod
    def create_job(self, job: IngestionJob) -> None:
        """Create a new ingestion job."""
        pass

    @abstractmethod
    def update_job(self, job: IngestionJob) -> None:
        """Update an existing ingestion job."""
        pass

    @abstractmethod
    def get_job(self, job_id: str) -> IngestionJob | None:
        """Retrieve a job by its ID."""
        pass

    @abstractmethod
    def list_jobs(self, limit: int = 50) -> list[IngestionJob]:
        """List recent ingestion jobs."""
        pass

    @abstractmethod
    def find_last_job_by_source(self, source_url: str) -> IngestionJob | None:
        """Find the last job (any status) for a given source URL."""
        pass
