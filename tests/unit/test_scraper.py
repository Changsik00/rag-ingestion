from unittest.mock import Mock, patch
from app.infrastructure.scrapers.basic import BasicWebScraper
from app.domain.models.ingest import IngestResponse

@patch("requests.get")
def test_scrape_basic_html(mock_get):
    # Mock Response
    mock_response = Mock()
    mock_response.text = "<html><body><h1>Hello World</h1><p>This is a test.</p></body></html>"
    mock_response.raise_for_status.return_value = None
    mock_response.headers = {"Content-Type": "text/html"}
    mock_get.return_value = mock_response

    scraper = BasicWebScraper()
    url = "https://example.com"
    result = scraper.scrape(url)

    assert isinstance(result, IngestResponse)
    assert str(result.url).rstrip('/') == url.rstrip('/')
    assert "Hello World" in result.markdown
    assert "This is a test" in result.markdown
    mock_get.assert_called_once_with(url)

@patch("requests.get")
def test_scrape_failure(mock_get):
    mock_response = Mock()
    mock_response.raise_for_status.side_effect = Exception("HTTP Error")
    mock_get.return_value = mock_response

    scraper = BasicWebScraper()
    try:
        scraper.scrape("https://error.com")
    except Exception as e:
        assert str(e) == "HTTP Error"
