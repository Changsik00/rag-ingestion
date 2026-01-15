from fastapi.testclient import TestClient
from unittest.mock import Mock
from app.interfaces.api.main import app, get_scraper
from app.domain.models.ingest import IngestResponse

client = TestClient(app)

def test_ingest_web_endpoint():
    # Mock Scraper
    mock_scraper = Mock()
    mock_scraper.scrape.return_value = IngestResponse(
        url="http://test.com",
        markdown="# Test",
        metadata={"status": 200}
    )
    
    # Override Dependency
    app.dependency_overrides[get_scraper] = lambda: mock_scraper
    
    # Act
    response = client.post(
        "/ingest/web",
        json={"url": "http://test.com"}
    )
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["url"] == "http://test.com/"
    assert data["markdown"] == "# Test"
    
    # Clean up
    app.dependency_overrides.clear()
