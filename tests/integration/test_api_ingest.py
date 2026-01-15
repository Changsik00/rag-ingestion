from fastapi.testclient import TestClient
from unittest.mock import Mock
from uuid import uuid4
from app.interfaces.api.main import app, get_scraper, get_repository
from app.domain.models.ingest import IngestResponse
from app.domain.entities.document import AtomicDocument

client = TestClient(app)

def test_ingest_web_endpoint():
    # Mock Scraper
    mock_scraper = Mock()
    mock_scraper.scrape.return_value = IngestResponse(
        url="http://test.com",
        markdown="# Test",
        metadata={"status": 200}
    )
    
    # Mock Repository
    mock_repo = Mock()
    mock_repo.save.return_value = None

    # Override Dependencies
    app.dependency_overrides[get_scraper] = lambda: mock_scraper
    app.dependency_overrides[get_repository] = lambda: mock_repo
    
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
    
    # Verify Mock Interactions
    mock_scraper.scrape.assert_called_once()
    mock_repo.save.assert_called_once()
    
    # Clean up
    app.dependency_overrides.clear()

def test_list_documents_endpoint():
    # Mock Repository
    mock_repo = Mock()
    doc_id = uuid4()
    mock_docs = [
        AtomicDocument(id=doc_id, content="Doc 1", source_url="http://test.com/1"),
        AtomicDocument(content="Doc 2", source_url="http://test.com/2")
    ]
    mock_repo.list_documents.return_value = mock_docs
    
    app.dependency_overrides[get_repository] = lambda: mock_repo
    
    # Act
    response = client.get("/documents?limit=5")
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["source_url"] == "http://test.com/1"
    
    mock_repo.list_documents.assert_called_once_with(limit=5)
    
    app.dependency_overrides.clear()
