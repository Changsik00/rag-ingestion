from unittest.mock import Mock
from fastapi.testclient import TestClient
from app.interfaces.api.main import app
from app.interfaces.api.dependencies import get_repository
from app.domain.entities.document import Document
from app.domain.value_objects.document_metadata import DocumentMetadata

client = TestClient(app)

def test_health_check():
    response = client.get("/v1/health")
    # Endpoint is /v1/health (included in system router, system router included without prefix? No wait)
    # in __init__.py: router.include_router(system.router)
    # system.router has @router.get("/health")
    # So /v1/health
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success" # BaseResponse
    assert data["components"]["api"] == "ok"

def test_list_documents_endpoint():
    mock_repo = Mock()
    mock_repo.list_documents.return_value = [
        Document(
            content="content",
            metadata=DocumentMetadata(source_id="src-1", title="Doc 1")
        )
    ]
    app.dependency_overrides[get_repository] = lambda: mock_repo

    response = client.get("/v1/documents")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["content"] == "content"
    assert data[0]["metadata"]["title"] == "Doc 1"

    app.dependency_overrides.clear()
