import logging
import asyncio
from typing import Dict, Any, Optional

from playwright.async_api import async_playwright
import trafilatura

from app.domain.interfaces.scraper import ScraperInterface
from app.schemas.ingest import IngestResponse

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

                await browser.close()

                # 5. Extract Main Content using Trafilatura for consistency
                # Playwright로 렌더링된 HTML을 Trafilatura로 파싱하여 클린 마크다운 획득
                markdown_content = trafilatura.extract(
                    html_content, 
                    include_comments=False, 
                    include_tables=True, 
                    include_images=False, 
                    output_format="markdown"
                )

                if not markdown_content:
                    # Trafilatura가 실패할 경우 page.inner_text() 등을 활용한 Fallback 가능
                    # 여기서는 일단 body 텍스트를 기본으로 활용
                    logger.warning(f"Trafilatura failed to extract from Playwright HTML for {url}. Using fallback.")
                    # 간단한 fallback: 텍스트만이라도 추출
                    # markdown_content = await page.inner_text("body") # 브라우저 닫기 전에 수행했어야 함
                    # 일단 에러 처리 or 기본 빈값 방지
                    raise ValueError("Failed to extract content even with Playwright")

                # 6. Cleaning
                markdown_content = self.cleaner.clean(markdown_content)

                # 7. Metadata
                metadata = {
                    "title": title,
                    "url": url,
                    "engine": "playwright"
                }

                return IngestResponse(
                    url=url,
                    markdown=markdown_content,
                    metadata=metadata
                )

        except Exception as e:
            logger.error(f"Playwright scraping failed for {url}: {e}")
            raise e
