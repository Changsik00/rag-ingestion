import requests
from markdownify import markdownify as md
from app.domain.models.ingest import IngestResponse
from app.domain.interfaces.scraper import ScraperInterface

class BasicWebScraper(ScraperInterface):
    def scrape(self, url: str) -> IngestResponse:
        response = requests.get(url)
        response.raise_for_status()
        
        # Convert HTML to Markdown
        markdown_content = md(response.text)
        
        return IngestResponse(
            url=url,
            markdown=markdown_content,
            metadata={
                "status_code": response.status_code,
                "content_type": response.headers.get("Content-Type")
            }
        )
