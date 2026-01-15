from app.domain.interfaces.scraper import ScraperInterface
from app.domain.models.ingest import IngestResponse
from app.domain.interfaces.document_repository import DocumentRepository
from app.domain.entities.document import AtomicDocument

class IngestionService:
    def __init__(self, scraper: ScraperInterface, repository: DocumentRepository):
        self.scraper = scraper
        self.repository = repository

    def ingest(self, url: str) -> IngestResponse:
        # 1. Scrape
        result = self.scraper.scrape(url)
        
        # 2. Map to Domain Entity
        doc = AtomicDocument(
            content=result.markdown,
            source_url=str(result.url),
            metadata=result.metadata
        )
        
        # 3. Save
        self.repository.save(doc)
        
        return result
