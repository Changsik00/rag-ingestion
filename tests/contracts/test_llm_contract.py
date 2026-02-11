"""
Contract tests for LLM interface implementations.
"""

import pytest

from app.infrastructure.ai.langchain_extractor import LangChainExtractor


@pytest.fixture(
    params=[
        LangChainExtractor,
    ]
)
def llm_class(request):
    """All LLMInterface implementation classes"""
    return request.param


class TestLLMInterfaceContract:
    """Contract tests for LLM interface"""

    def test_has_extract_metadata_method(self, llm_class):
        """All LLM classes must have an extract_metadata method"""
        assert hasattr(llm_class, "extract_metadata")
        assert callable(getattr(llm_class, "extract_metadata"))

    def test_extract_metadata_method_signature(self, llm_class):
        """extract_metadata method should accept text parameter"""
        import inspect

        sig = inspect.signature(llm_class.extract_metadata)
        params = list(sig.parameters.values())
        param_names = [p.name for p in params]

        # Should have 'self', 'text', 'metadata', 'thread_id' parameters
        # In modern versions, we allow more than 2 parameters.
        assert "text" in param_names
        assert "self" in param_names


class TestLLMConstructorConsistency:
    """Tests to verify constructor consistency across LLM implementations"""

    def test_langchain_adapter_constructor(self):
        """LangChainExtractor should accept an LLM instance"""
        from unittest.mock import Mock

        from langchain_google_genai import ChatGoogleGenerativeAI

        mock_llm = Mock(spec=ChatGoogleGenerativeAI)
        adapter = LangChainExtractor(mock_llm)

        assert adapter.llm == mock_llm
