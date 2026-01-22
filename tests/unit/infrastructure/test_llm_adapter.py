from unittest.mock import MagicMock

import pytest
from langchain_core.messages import AIMessage
from langchain_google_genai import ChatGoogleGenerativeAI

from app.infrastructure.llm.langchain_adapter import LangChainLLMAdapter


@pytest.fixture
def mock_chat_model():
    return MagicMock(spec=ChatGoogleGenerativeAI)


def test_generate_returns_string(mock_chat_model):
    # Setup
    mock_chat_model.invoke.return_value = AIMessage(content="Generated response")
    adapter = LangChainLLMAdapter(llm=mock_chat_model)

    # Execute
    result = adapter.generate("Test prompt")

    # Verify
    assert result == "Generated response"
    mock_chat_model.invoke.assert_called_once()

def test_generate_handles_error(mock_chat_model):
    # Setup
    mock_chat_model.invoke.side_effect = Exception("API Error")
    adapter = LangChainLLMAdapter(llm=mock_chat_model)

    # Execute
    result = adapter.generate("Test prompt")

    # Verify
    # Assuming implementation returns error message or empty string on failure
    # Let's decide it should return the error message for the dashboard
    assert "Failed" in result or result == ""
