import logging

import trafilatura
from playwright.async_api import async_playwright

from app.application.interfaces.scraper import ScraperInterface
from app.interfaces.api.v1.dto.ingest import IngestResponse

logger = logging.getLogger(__name__)


class PlaywrightScraper(ScraperInterface):
    """
    Advanced Web Scraper using Playwright (Headless Browser).
    Handles dynamic content, SPA, and complex layouts by rendering JS.
    """

    def __init__(self):
        from app.infrastructure.scrapers.cleaner import MarkdownCleaner

        self.cleaner = MarkdownCleaner()

    async def scrape(self, url: str) -> IngestResponse:
        """
        Scrapes the URL using Playwright's headless browser.
        """
        logger.info(f"Scraping URL with Playwright: {url}")

        try:
            async with async_playwright() as p:
                # 1. Launch Browser
                browser = await p.chromium.launch(headless=True)

                # 2. Create Page with custom User-Agent
                context = await browser.new_context(
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                )
                page = await context.new_page()

                # 3. Navigate with Timeout
                # networkidle: 네트워크 요청이 잦아들 때까지 대기 (SPA 대응)
                await page.goto(url, wait_until="networkidle", timeout=30000)

                # 4. Extract Title and Content
                title = await page.title()
                # 원본 HTML 수집
                html_content = await page.content()
                # Fallback용 텍스트 미리 확보
                fallback_text = await page.inner_text("body")

                await browser.close()

                # 5. Extract Main Content using Trafilatura for consistency
                # Playwright로 렌더링된 HTML을 Trafilatura로 파싱하여 클린 마크다운 획득
                markdown_content = trafilatura.extract(
                    html_content,
                    include_comments=False,
                    include_tables=True,
                    include_images=False,
                    output_format="markdown",
                )

                if not markdown_content:
                    logger.warning(f"Trafilatura failed to extract from Playwright HTML for {url}. Using fallback.")
                    markdown_content = fallback_text

                # 6. Cleaning
                markdown_content = self.cleaner.clean(markdown_content) if markdown_content else ""

                # 7. Metadata
                metadata = {"title": title, "url": url, "engine": "playwright"}

                return IngestResponse(url=url, markdown=markdown_content, metadata=metadata)

        except Exception as e:
            logger.error(f"Playwright scraping failed for {url}: {e}")
            raise e
