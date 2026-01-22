from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from langchain_core.messages import AIMessage, HumanMessage

from app.admin.agents.admin_agent import AdminAgent, AdminState


@pytest.fixture
def mock_services():
    ingestion = MagicMock()
    rag = AsyncMock()
    return ingestion, rag

@pytest.fixture
def mock_llm_class():
    with patch("app.admin.agents.admin_agent.ChatGoogleGenerativeAI") as mock:
        yield mock

def test_router_detects_url_intent(mock_services, mock_llm_class):
    ingestion, rag = mock_services
    mock_llm_instance = mock_llm_class.return_value
    mock_llm_instance.invoke.return_value = AIMessage(content="ingest")

    agent = AdminAgent(rag, ingestion)

    state = AdminState(messages=[HumanMessage(content="https://example.com 읽어줘")], intent="", tool_output="")
    result = agent.router_node(state)

    assert result["intent"] == "ingest"

def test_router_detects_search_intent(mock_services, mock_llm_class):
    ingestion, rag = mock_services
    mock_llm_instance = mock_llm_class.return_value
    mock_llm_instance.invoke.return_value = AIMessage(content="search")

    agent = AdminAgent(rag, ingestion)

    state = AdminState(messages=[HumanMessage(content="RAG가 뭐야?")], intent="", tool_output="")
    result = agent.router_node(state)

    assert result["intent"] == "search"
