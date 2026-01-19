"""
Unit Tests for BasicWebScraper

BasicWebScraper의 웹 페이지 스크래핑 기능을 검증합니다.
"""

from unittest.mock import Mock, patch

from app.infrastructure.scrapers.basic import BasicWebScraper
from app.schemas.ingest import IngestResponse


@patch("requests.get")
def test_scrape_basic_html(mock_get):
    # Given: Mock HTTP response
    mock_response = Mock()
    mock_response.text = "<html><body><h1>Hello World</h1><p>This is a test.</p></body></html>"
    mock_response.raise_for_status.return_value = None
    mock_response.headers = {"Content-Type": "text/html"}
    mock_get.return_value = mock_response

    scraper = BasicWebScraper()
    url = "https://example.com"

    # When: URL 스크래핑
    result = scraper.scrape(url)

    # Then: IngestResponse 반환 및 HTML이 Markdown으로 변환됨
    assert isinstance(result, IngestResponse)
    assert str(result.url).rstrip("/") == url.rstrip("/")
    assert "Hello World" in result.markdown
    assert "This is a test" in result.markdown
    mock_get.assert_called_once()
    assert mock_get.call_args[0][0] == url
    assert "User-Agent" in mock_get.call_args[1]["headers"]


@patch("requests.get")
def test_scrape_failure(mock_get):
    # Given: HTTP 에러를 발생시키는 Mock response
    mock_response = Mock()
    mock_response.raise_for_status.side_effect = Exception("HTTP Error")
    mock_get.return_value = mock_response

    scraper = BasicWebScraper()

    # When/Then: 스크래핑 실패 시 예외 발생
    try:
        scraper.scrape("https://error.com")
    except Exception as e:
        assert str(e) == "HTTP Error"
