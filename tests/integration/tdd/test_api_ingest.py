from unittest.mock import Mock
from uuid import uuid4

from fastapi.testclient import TestClient

from app.domain.entities.document import AtomicDocument
from app.interfaces.api.dependencies import get_repository
from app.interfaces.api.main import app

client = TestClient(app)

# test_ingest_web_endpoint is superseded by tests/integration/test_async_ingest.py

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
