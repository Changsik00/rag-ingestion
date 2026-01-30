import logging

from app.domain.interfaces.scraper import ScraperInterface
from app.infrastructure.scrapers.checker import ScrapingQualityChecker
from app.infrastructure.scrapers.firecrawl_scraper import FirecrawlWebScraper
from app.infrastructure.scrapers.trafilatura_scraper import TrafilaturaWebScraper
from app.infrastructure.scrapers.youtube_scraper import YouTubeScraper
from app.interfaces.api.schemas.ingest import IngestResponse

logger = logging.getLogger(__name__)


class CompositeScraper(ScraperInterface):
    """
    Tiered Hybrid Scraper Strategy 관리자.
    Trafilatura(Tier 1) -> Playwright(Tier 2) -> Firecrawl(Tier 3) 순서로 시도함.
    """

    def __init__(self):
        from app.infrastructure.scrapers.playwright_scraper import PlaywrightScraper

        self.primary_scraper = TrafilaturaWebScraper()
        self.playwright_scraper = PlaywrightScraper()
        self.advanced_scraper = FirecrawlWebScraper()
        self.youtube_scraper = YouTubeScraper()
        self.quality_checker = ScrapingQualityChecker()

    async def scrape(self, url: str) -> IngestResponse:
        # 0. YouTube URL 감지
        if "youtube.com" in url or "youtu.be" in url:
            return await self.youtube_scraper.scrape(url)

        # 1. Tier 1: Trafilatura (Fast) 시도
        try:
            result = await self.primary_scraper.scrape(url)

            # 품질 검사 (Heuristics + Semantic Check)
            if self.quality_checker.is_poor(result):
                logger.info(f"Primary scraper output for {url} is poor. Falling back to Playwright Scraper.")
                return await self.playwright_scraper.scrape(url)

            return result

        except Exception as e:
            logger.warning(f"Primary scraper failed for {url}: {e}. Falling back to Playwright Scraper.")
            try:
                # 2. Tier 2: Playwright (Direct Dynamic) 시도
                return await self.playwright_scraper.scrape(url)
            except Exception as pe:
                logger.error(f"Playwright scraper also failed for {url}: {pe}. Falling back to Firecrawl.")
                # 3. Tier 3: Firecrawl (Paid API) 시도
                return await self.advanced_scraper.scrape(url)
