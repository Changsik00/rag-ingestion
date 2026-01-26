import logging
from typing import Any

from firecrawl import FirecrawlApp

from app.core.config import get_settings
from app.domain.interfaces.scraper import ScraperInterface
from app.infrastructure.scrapers.cleaner import MarkdownCleaner
from app.schemas.ingest import IngestResponse

logger = logging.getLogger(__name__)


class FirecrawlWebScraper(ScraperInterface):
    """
    Advanced Web Scraper using Firecrawl API.
    Provides LLM-ready clean markdown with preserved semantic structure.
    """

    def __init__(self, api_key: str | None = None):
        settings = get_settings()
        self.api_key = api_key or settings.FIRECRAWL_API_KEY
        if not self.api_key:
            logger.warning("Firecrawl API key not found. FirecrawlWebScraper will not function correctly.")

        self.app = FirecrawlApp(api_key=self.api_key) if self.api_key else None
        self.cleaner = MarkdownCleaner()

    def scrape(self, url: str) -> IngestResponse:
        logger.info(f"Scraping URL with Firecrawl: {url}")

        if not self.app:
            raise ValueError("Firecrawl API key is missing. Cannot use FirecrawlWebScraper.")

        try:
            # 1. Scrape URL with Firecrawl
            result = self.app.scrape(url, formats=["markdown"], only_main_content=True)

            if not result:
                raise ValueError(f"Firecrawl returned None for {url}")

            # [Spec 039] v4 client returns a Document object
            if hasattr(result, "success") and result.success is False:
                error_msg = getattr(result, "error", "Unknown error")
                raise ValueError(f"Firecrawl scraping failed: {error_msg}")

            # 2. Extract Metadata
            metadata = {}
            if hasattr(result, "metadata"):
                m = result.metadata
                if isinstance(m, dict):
                    metadata = m
                elif hasattr(m, "model_dump"):
                    metadata = m.model_dump()
                else:
                    metadata = dict(m)

            # [Spec 039] 404/Error Detection (Anti-Fallback-Pollution)
            # Support both camelCase (old/raw) and snake_case (v4 client)
            status_code = metadata.get("status_code") or metadata.get("statusCode") or metadata.get("status")

            error_code = None
            if status_code and isinstance(status_code, (int, float, str)):
                try:
                    sc = int(status_code)
                    if sc >= 400:
                        error_code = sc
                except (ValueError, TypeError):
                    pass

            if error_code:
                raise ValueError(f"Firecrawl returned failure status code: {error_code}")

            markdown_content = result.markdown if hasattr(result, "markdown") else ""

            # 3. Clean Markdown (Pollution Control)
            markdown_content = self.cleaner.clean(markdown_content)

            meta_dict = self._standardize_metadata(metadata, url)

            return IngestResponse(url=url, markdown=markdown_content, metadata=meta_dict)

        except Exception as e:
            logger.error(f"Firecrawl scraping failed: {e}")
            raise e

    def _standardize_metadata(self, metadata: dict[str, Any], url: str) -> dict[str, Any]:
        """Firecrawl 메타데이터를 내부 표준 포맷으로 변환"""
        meta_dict = {
            "title": metadata.get("title"),
            "author": metadata.get("author"),
            "published_date": metadata.get("published_date") or metadata.get("date"),
            "sitename": metadata.get("sitename") or metadata.get("ogSiteName"),
            "description": metadata.get("description") or metadata.get("ogDescription"),
            "url": metadata.get("sourceURL") or url,
        }

        # Title Fallback (Trafilatura와 일관성 유지)
        if not meta_dict.get("title") or str(meta_dict["title"]).lower() == "none":
            from urllib.parse import urlparse

            path = urlparse(url).path.strip("/")
            if path:
                fallback_title = path.split("/")[-1].replace("_", " ").replace("-", " ").title()
                meta_dict["title"] = fallback_title
            else:
                meta_dict["title"] = "Untitled Document"

        return meta_dict
