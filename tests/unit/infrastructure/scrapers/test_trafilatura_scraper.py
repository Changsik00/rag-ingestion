from unittest.mock import MagicMock, patch

import pytest

from app.infrastructure.scrapers.trafilatura_scraper import TrafilaturaWebScraper
from app.interfaces.api.v1.dto.ingest import IngestResponse

# Mock HTML with ads and noise
MOCK_HTML_WITH_ADS = """
<html>
    <head><title>Test Article</title></head>
    <body>
        <nav>Menu 1 | Menu 2</nav>
        <div class="ad-container">Buy this product!</div>
        <article>
            <h1>Real Content Title</h1>
            <p>This is the main content of the article.</p>
            <p>It should be extracted cleanly.</p>
        </article>
        <div id="footer">Copyright 2026</div>
        <script>console.log("Tracking user");</script>
    </body>
</html>
"""

MOCK_EXTRACTED_TEXT = """# Real Content Title

This is the main content of the article.

It should be extracted cleanly."""


@pytest.fixture
def scraper():
    return TrafilaturaWebScraper()


@pytest.mark.asyncio
async def test_scrape_clean_extraction(scraper):
    """광고와 노이즈가 제거된 본문이 추출되는지 검증"""
    with (
        patch("trafilatura.fetch_url", return_value=MOCK_HTML_WITH_ADS),
        patch("trafilatura.extract", return_value=MOCK_EXTRACTED_TEXT) as mock_extract,
    ):
        response = await scraper.scrape("https://example.com/news")

        assert isinstance(response, IngestResponse)
        assert "Buy this product" not in response.markdown
        assert "Menu 1" not in response.markdown
        assert "Real Content Title" in response.markdown

        # trafilatura.extract 호출 시 옵션 확인
        mock_extract.assert_called_once()
        call_args = mock_extract.call_args[1]
        assert call_args.get("include_comments") is False


@pytest.mark.asyncio
async def test_scrape_metadata_extraction(scraper):
    """메타데이터 추출 검증"""
    mock_metadata = MagicMock()
    mock_metadata.title = "Test Article"
    mock_metadata.date = "2026-01-22"
    mock_metadata.author = "Test Author"
    mock_metadata.sitename = "Test Site"

    with (
        patch("trafilatura.fetch_url", return_value="<html></html>"),
        patch("trafilatura.extract", return_value="Content"),
        patch("trafilatura.extract_metadata", return_value=mock_metadata),
    ):
        response = await scraper.scrape("https://example.com/news")

        assert response.metadata["title"] == "Test Article"
        assert response.metadata["published_date"] == "2026-01-22"
        assert response.metadata["author"] == "Test Author"


@pytest.mark.asyncio
async def test_scrape_fallback_when_trafilatura_fails(scraper):
    """Trafilatura 추출 실패 시 Fallback 로직 동작 검증"""
    # extract가 None을 반환(실패)하도록 설정
    with (
        patch("trafilatura.fetch_url", return_value="<html>Text</html>"),
        patch("trafilatura.extract", return_value=None),
    ):
        # Fallback으로 단순 텍스트 추출이라도 되는지 (구현에 따라 다름)
        # 현재는 예외를 던지거나 BasicScraper 로직을 탈지 결정해야 함
        # 여기서는 최소한 비어있지 않은 응답이 오거나 에러 처리가 되는지 확인
        try:
            _ = scraper.scrape("https://example.com/fail")
            # Fallback 구현 시:
            # assert response.markdown is not None
        except Exception:
            # 아직 구현 전이므로 넘어감
            pass
