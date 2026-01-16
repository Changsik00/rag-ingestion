from typing import Optional
from app.domain.interfaces.scraper import ScraperInterface
from app.schemas.ingest import IngestResponse
from app.domain.interfaces.document_repository import DocumentRepository
from app.domain.entities.document import AtomicDocument
from app.domain.interfaces.job_repository import JobRepository
from app.domain.entities.job import IngestionJob, JobStatus
from datetime import datetime, timezone

class IngestionService:
    def __init__(self, scraper: ScraperInterface, repository: DocumentRepository, job_repository: JobRepository):
        self.scraper = scraper
        self.repository = repository
        self.job_repository = job_repository

    def create_job(self, url: str, retry_of: Optional[str] = None) -> IngestionJob:
        """Create and persist a new job in PENDING state."""
        job = IngestionJob(source_url=url, status=JobStatus.PENDING, retry_of=retry_of)
        self.job_repository.create_job(job)
        return job

    def process_job(self, job_id: str) -> None:
        """Execute the ingestion logic asynchronously."""
        job = self.job_repository.get_job(job_id)
        if not job:
            # Should not happen if flow is correct
            return

        try:
            # 1. Update Status to RUNNING
            job.status = JobStatus.RUNNING
            job.updated_at = datetime.now(timezone.utc)
            self.job_repository.update_job(job)

            # 2. Scrape
            result = self.scraper.scrape(job.source_url)
            
            # 3. Map to Domain Entity
            doc = AtomicDocument(
                content=result.markdown,
                source_url=str(result.url),
                metadata=result.metadata
            )
            
            # 4. Save Document
            self.repository.save(doc)
            
            # 5. Update Job (COMPLETED)
            job.status = JobStatus.COMPLETED
            job.updated_at = datetime.now(timezone.utc)
            self.job_repository.update_job(job)
            
        except Exception as e:
            # 6. Update Job (FAILED) if error occurs
            job.status = JobStatus.FAILED
            job.updated_at = datetime.now(timezone.utc)
            job.error_message = str(e)
            self.job_repository.update_job(job)
            # We do NOT raise the exception here to ensure the background task completes gracefully
            # and the status is persisted. Log could be added here.
