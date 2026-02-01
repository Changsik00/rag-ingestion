from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from langchain_core.messages import AIMessage, HumanMessage

from app.application.services.admin_agent import AgentState, ConversationalRAGAgent


@pytest.fixture
def mock_services():
    ingestion = MagicMock()
    rag = AsyncMock()
    return ingestion, rag


@pytest.fixture
def mock_llm_class():
    with patch("app.application.services.admin_agent.ChatGoogleGenerativeAI") as mock:
        yield mock


@pytest.mark.asyncio
async def test_router_detects_url_intent(mock_services, mock_llm_class):
    ingestion, rag = mock_services
    mock_llm_instance = mock_llm_class.return_value
    mock_llm_instance.ainvoke = AsyncMock(return_value = AIMessage(content="ingest"))

    agent = ConversationalRAGAgent(rag, ingestion)

    state = AgentState(messages=[HumanMessage(content="https://example.com 읽어줘")], intent="", tool_output="")
    result = await agent.router_node(state)

    assert result["intent"] == "ingest"


@pytest.mark.asyncio
async def test_router_detects_search_intent(mock_services, mock_llm_class):
    ingestion, rag = mock_services
    mock_llm_instance = mock_llm_class.return_value
    mock_llm_instance.ainvoke = AsyncMock(return_value = AIMessage(content="search"))

    agent = ConversationalRAGAgent(rag, ingestion)

    state = AgentState(messages=[HumanMessage(content="RAG가 뭐야?")], intent="", tool_output="")
    result = await agent.router_node(state)

    assert result["intent"] == "search"
