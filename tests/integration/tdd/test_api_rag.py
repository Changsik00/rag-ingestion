from unittest.mock import AsyncMock, Mock

from fastapi.testclient import TestClient

from app.domain.entities.document import Document
from app.domain.value_objects.document_metadata import DocumentMetadata
from app.interfaces.api.dependencies import get_checkpointer, get_conversational_rag_agent, get_repository
from app.interfaces.api.main import app

client = TestClient(app)


def test_autocomplete_endpoint():
    mock_repo = Mock()
    mock_repo.list_documents.return_value = [
        Document(content="content", metadata=DocumentMetadata(source_id="src-1", title="Doc 1"))
    ]
    app.dependency_overrides[get_repository] = lambda: mock_repo

    response = client.get("/v1/rag/documents/autocomplete?q=test")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "Doc 1"

    app.dependency_overrides.clear()


def test_ask_agent_endpoint():
    mock_agent = Mock()
    mock_workflow = AsyncMock()
    mock_agent.build_workflow.return_value = mock_workflow

    # Mock Message object using SimpleNamespace to avoid Mock magic issues
    from types import SimpleNamespace

    mock_msg = SimpleNamespace(type="ai", content="Hello")

    # Mock ainvoke result
    mock_workflow.ainvoke.return_value = {
        "messages": [mock_msg],
        "context_data": {},
        "intent": "greeting",
        "draft_content": None,
    }

    # Mock aget_state result (snapshot)
    mock_snapshot = Mock()
    mock_snapshot.next = ()
    mock_workflow.aget_state.return_value = mock_snapshot

    app.dependency_overrides[get_conversational_rag_agent] = lambda: mock_agent
    app.dependency_overrides[get_checkpointer] = lambda: AsyncMock()

    response = client.post("/v1/rag/sessions/thread-1/ask", json={"message": "Hi"})

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["current_status"] == "completed"
    assert len(data["messages"]) == 1
    assert data["messages"][0]["content"] == "Hello"

    app.dependency_overrides.clear()
