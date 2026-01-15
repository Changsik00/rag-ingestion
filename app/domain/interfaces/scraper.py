from abc import ABC, abstractmethod
from app.domain.models.ingest import IngestResponse

class ScraperInterface(ABC):
    @abstractmethod
    def scrape(self, url: str) -> IngestResponse:
        """
        Scrape content from the given URL and return structured IngestResponse.
        """
        pass
