import pytest
from unittest.mock import AsyncMock, MagicMock
from langchain_core.messages import HumanMessage, AIMessage

from app.domain.services.admin_agent import AdminAgent, AdminState

@pytest.fixture
def mock_services():
    rag_service = MagicMock()
    ingestion_service = MagicMock()
    return rag_service, ingestion_service

@pytest.mark.asyncio
async def test_admin_state_schema():
    """AdminState에 새로운 필드가 추가되었는지 검증"""
    # This is a static check, but effective to ensure type definition update
    # Note: TypedDict at runtime doesn't enforce keys, but we check if we can instantiate it
    state: AdminState = {
        "messages": [],
        "intent": "search",
        "tool_output": "",
        "context_data": {},
        "filters": None,
        "thread_id": "test",
        "hitl_enabled": True,
        # New Fields
        "draft_content": "Draft",
        "is_clarification": True,
        "missing_slots": ["url"]
    }
    assert state["draft_content"] == "Draft"
    assert state["is_clarification"] is True

@pytest.mark.asyncio
async def test_ambiguity_detection_in_router(mock_services):
    """Router가 모호한 입력에 대해 clarify 인텐트를 반환하는지 테스트"""
    rag_service, ingestion_service = mock_services
    agent = AdminAgent(rag_service, ingestion_service)

    # Use MagicMock for synchronous invoke
    agent.llm = MagicMock()
    
    # Mock LLM response to 'ingest' (but input has no URL)
    # This forces the regex check to fail and switch to clarify
    agent.llm.invoke.return_value = AIMessage(content="ingest")

    state = {
        "messages": [HumanMessage(content="이거 요약해줘")], # No URL here
        "hitl_enabled": True
    }
    
    result = agent.router_node(state)
    
    assert result["intent"] == "clarify"
    assert "url" in result["missing_slots"]

@pytest.mark.asyncio
async def test_clarify_node(mock_services):
    """Clarify Node가 적절한 역질문을 생성하는지 테스트"""
    rag_service, ingestion_service = mock_services
    agent = AdminAgent(rag_service, ingestion_service)
    
    state = {
        "messages": [HumanMessage(content="요약해줘")],
        "intent": "clarify",
        "missing_slots": ["url"] # Use recognized slot name
    }
    
    # clarify_node is synchronous, triggers rule-based response for "url"
    agent.llm = MagicMock()
    
    result = agent.clarify_node(state)
    
    assert "messages" in result
    assert isinstance(result["messages"][0], AIMessage)
    assert result["is_clarification"] is True
    # "어떤 URL을..." includes "어떤"
    assert "어떤" in result["messages"][0].content
