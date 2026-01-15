from app.domain.interfaces.scraper import ScraperInterface
from app.domain.models.ingest import IngestResponse

class IngestionService:
    def __init__(self, scraper: ScraperInterface):
        self.scraper = scraper

    def ingest(self, url: str) -> IngestResponse:
        return self.scraper.scrape(url)
