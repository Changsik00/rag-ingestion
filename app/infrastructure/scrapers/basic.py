import requests
from markdownify import markdownify as md

from app.domain.interfaces.scraper import ScraperInterface
from app.interfaces.api.dto.ingest import IngestResponse


class BasicWebScraper(ScraperInterface):
    def scrape(self, url: str) -> IngestResponse:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        # HTML을 Markdown으로 변환
        markdown_content = md(response.text)

        return IngestResponse(
            url=url,
            markdown=markdown_content,
            metadata={"status_code": response.status_code, "content_type": response.headers.get("Content-Type")},
        )
