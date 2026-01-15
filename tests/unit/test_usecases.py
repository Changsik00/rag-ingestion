from unittest.mock import Mock
from app.use_cases.ingestion import IngestionService
from app.domain.interfaces.scraper import ScraperInterface
from app.domain.models.ingest import IngestResponse

def test_ingest_web_page():
    # Arrange
    mock_scraper = Mock(spec=ScraperInterface)
    mock_repo = Mock()
    expected_response = IngestResponse(url="http://example.com/", markdown="# Example", metadata={})
    mock_scraper.scrape.return_value = expected_response
    
    service = IngestionService(scraper=mock_scraper, repository=mock_repo)
    
    # Act
    result = service.ingest("http://example.com")
    
    # Assert
    assert result == expected_response
    mock_scraper.scrape.assert_called_once_with("http://example.com")
    mock_repo.save.assert_called_once() # Verify save is called
