from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app.interfaces.api.main import app

# pytestmark = pytest.mark.skip(reason="Requires infrastructure setup - see specs/integration-test-improvement.md")


client = TestClient(app)


def test_rag_autocomplete():
    """GET /v1/rag/documents/autocomplete 테스트"""
    response = client.get("/v1/rag/documents/autocomplete?q=test")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_rag_ask():
    """POST /v1/rag/sessions/{id}/ask 테스트"""
    from unittest.mock import AsyncMock
    from langchain_core.messages import AIMessage

    payload = {"message": "Hello", "filters": {}}
    
    # Patch where the class is instantiated or imported
    # Assuming app.application.services.agent uses ChatGoogleGenerativeAI
    with patch("app.application.services.agent.ChatGoogleGenerativeAI") as mock_llm_cls:
        mock_instance = mock_llm_cls.return_value
        # Mock async ainvoke
        mock_instance.ainvoke = AsyncMock(return_value=AIMessage(content="Mock Answer"))
        # Mock sync invoke just in case
        mock_instance.invoke.return_value = AIMessage(content="Mock Answer")
        
        response = client.post("/v1/rag/sessions/test_session/ask", json=payload)
        # API returns 202 Accepted for async processing or standard pattern
        assert response.status_code == 202


def test_graph_schema():
    """GET /v1/graph/schema 테스트"""
    response = client.get("/v1/graph/schema")
    assert response.status_code == 200
    data = response.json()
    assert "labels" in data
    assert "relationship_types" in data


def test_graph_query_execution():
    """POST /v1/graph/query 테스트"""
    payload = {"query": "MATCH (n) RETURN n LIMIT 1"}
    response = client.post("/v1/graph/query", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "nodes" in data
    assert "edges" in data
