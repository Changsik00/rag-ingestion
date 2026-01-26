import logging

from app.domain.interfaces.scraper import ScraperInterface
from app.infrastructure.scrapers.checker import ScrapingQualityChecker
from app.infrastructure.scrapers.firecrawl_scraper import FirecrawlWebScraper
from app.infrastructure.scrapers.trafilatura_scraper import TrafilaturaWebScraper
from app.schemas.ingest import IngestResponse

logger = logging.getLogger(__name__)


class CompositeScraper(ScraperInterface):
    """
    Tiered Hybrid Scraper Strategy 관리자.
    Trafilatura(Fast) -> Firecrawl(Advanced) 순서로 시도함.
    """

    def __init__(self):
        self.primary_scraper = TrafilaturaWebScraper()
        self.advanced_scraper = FirecrawlWebScraper()
        self.quality_checker = ScrapingQualityChecker()

    def scrape(self, url: str) -> IngestResponse:
        # 1. Primary Scraper (Trafilatura) 시도
        try:
            result = self.primary_scraper.scrape(url)

            # 품질 검사
            if self.quality_checker.is_poor(result):
                logger.info(f"Primary scraper output for {url} is poor. Falling back to Advanced Scraper.")
                return self.advanced_scraper.scrape(url)

            return result

        except Exception as e:
            logger.warning(f"Primary scraper failed for {url}: {e}. Falling back to Advanced Scraper.")
            # 실패 시 Advanced Scraper로 Fallback
            return self.advanced_scraper.scrape(url)
