from abc import ABC, abstractmethod

from app.schemas.ingest import IngestResponse


class ScraperInterface(ABC):
    @abstractmethod
    async def scrape(self, url: str) -> IngestResponse:
        """
        Scrape content from the given URL and return structured IngestResponse.
        """
        pass
