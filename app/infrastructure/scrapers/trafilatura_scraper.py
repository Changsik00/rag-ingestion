import logging

import trafilatura

from app.domain.interfaces.scraper import ScraperInterface
from app.schemas.ingest import IngestResponse

logger = logging.getLogger(__name__)


class TrafilaturaWebScraper(ScraperInterface):
    """
    Intelligent Web Scraper using Trafilatura.
    Extracts only the main content (article) and metadata, removing ads and noise.
    """

    def scrape(self, url: str) -> IngestResponse:
        logger.info(f"Scraping URL with Trafilatura: {url}")

        try:
            # 1. Fetch URL
            downloaded = trafilatura.fetch_url(url)

            if downloaded is None:
                raise ValueError(f"Failed to fetch URL: {url}")

            # 2. Extract Main Content (Markdown)
            # include_comments=False: 댓글 제거
            # include_tables=True: 표 유지
            # include_images=False: 이미지는 텍스트 위주로 처리 (RAG 목적)
            markdown_content = trafilatura.extract(
                downloaded, include_comments=False, include_tables=True, include_images=False, output_format="markdown"
            )

            if not markdown_content:
                logger.warning(f"Trafilatura returned empty content for {url}. Fallback might be needed.")
                # Fallback 로직은 추후 고도화하거나, 현재는 빈 문자열 대신 에러 유발
                # 여기서는 테스트 통과를 위해 기본 처리
                raise ValueError("Extracted content is empty")

            # 3. Extract Metadata
            metadata = trafilatura.extract_metadata(downloaded)

            meta_dict = {}
            if metadata:
                meta_dict = {
                    "title": metadata.title,
                    "author": metadata.author,
                    "published_date": str(metadata.date) if metadata.date else None,
                    "sitename": metadata.sitename,
                    "description": metadata.description,
                    "url": metadata.url or url,
                }

            # [Spec 037] Title Fallback: Meta title이 없으면 URL이나 본문에서 추출
            if not meta_dict.get("title") or meta_dict["title"].lower() == "none":
                # URL에서 마지막 부분 추출 (e.g. /Elon_Musk -> Elon Musk)
                from urllib.parse import urlparse
                path = urlparse(url).path.strip('/')
                if path:
                    fallback_title = path.split('/')[-1].replace('_', ' ').replace('-', ' ').title()
                    meta_dict["title"] = fallback_title
                else:
                    meta_dict["title"] = "Untitled Document"

            # [Spec 037] Context Cleaning: 지저분한 위키피디아 navbox나 빈 표 제거
            # Trafilatura가 가끔 추출하는 불필요한 마바크다운 패턴 정제
            markdown_content = re.sub(r'\|\s*\|\s*\|\n\| --- \| --- \| --- \|\n\| \| \| \|', '', markdown_content) # 빈 표 제거
            markdown_content = re.sub(r'\[\s*\]\(\s*\)', '', markdown_content) # 빈 링크 제거

            return IngestResponse(url=url, markdown=markdown_content, metadata=meta_dict)

        except Exception as e:
            logger.error(f"Trafilatura scraping failed: {e}")
            raise e
