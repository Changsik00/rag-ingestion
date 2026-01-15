from app.domain.interfaces.scraper import ScraperInterface
from app.domain.models.ingest import IngestResponse
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

    def ingest(self, url: str) -> IngestResponse:
        # 1. Create Job (PENDING)
        job = IngestionJob(source_url=url, status=JobStatus.PENDING)
        self.job_repository.create_job(job)

        try:
            # 2. Scrape
            result = self.scraper.scrape(url)
            
            # 3. Map to Domain Entity
            doc = AtomicDocument(
                content=result.markdown,
                source_url=str(result.url),
                metadata=result.metadata
            )
            
            # 4. Save
            self.repository.save(doc)
            
            # 5. Update Job (COMPLETED)
            job.status = JobStatus.COMPLETED
            job.updated_at = datetime.now(timezone.utc)
            self.job_repository.update_job(job)
            
            return result

        except Exception as e:
            # Update Job (FAILED)
            job.status = JobStatus.FAILED
            job.updated_at = datetime.now(timezone.utc)
            job.error_message = str(e)
            self.job_repository.update_job(job)
            raise e
