from unittest.mock import MagicMock

import pytest
from langchain_google_genai import ChatGoogleGenerativeAI

from app.infrastructure.ai.langchain_extractor import LangChainExtractor


@pytest.fixture
def mock_chat_model():
    return MagicMock(spec=ChatGoogleGenerativeAI)


def test_generate_returns_string(mock_chat_model):
    # Setup
    # Mock for chain: llm | StrOutputParser()
    mock_chain = MagicMock()
    mock_chain.invoke.return_value = "Generated response"
    mock_chat_model.__or__.return_value = mock_chain

    adapter = LangChainExtractor(llm=mock_chat_model)

    # Execute
    result = adapter.generate("Test prompt")

    # Verify
    assert result == "Generated response"
    mock_chat_model.__or__.assert_called_once()
    mock_chain.invoke.assert_called_once_with("Test prompt")


def test_generate_handles_error(mock_chat_model):
    # Setup
    mock_chain = MagicMock()
    mock_chain.invoke.side_effect = Exception("API Error")
    mock_chat_model.__or__.return_value = mock_chain

    adapter = LangChainExtractor(llm=mock_chat_model)

    # Execute & Verify
    with pytest.raises(Exception, match="API Error"):
        adapter.generate("Test prompt")
