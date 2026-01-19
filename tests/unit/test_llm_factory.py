import os
from unittest.mock import patch

import pytest
from langchain_google_genai import ChatGoogleGenerativeAI

from app.core.llm import LLMFactory


class TestLLMFactory:
    def setup_method(self):
        # Clear cache before each test
        LLMFactory.get_google_llm.cache_clear()
        LLMFactory.get_llm_adapter.cache_clear()

    @patch.dict(os.environ, {"GEMINI_API_KEY": "test_gemini_key"}, clear=True)
    def test_get_google_llm_with_gemini_key(self):
        """Should succeed when GEMINI_API_KEY is present"""
        llm = LLMFactory.get_google_llm()
        assert isinstance(llm, ChatGoogleGenerativeAI)
        assert llm.google_api_key.get_secret_value() == "test_gemini_key"

    @patch.dict(os.environ, {}, clear=True)
    def test_get_google_llm_no_key_raises_error(self):
        """Should raise ValueError when GEMINI_API_KEY is missing"""
        with pytest.raises(ValueError, match="GEMINI_API_KEY environment variable is not set"):
            LLMFactory.get_google_llm()

    @patch.dict(os.environ, {"GOOGLE_API_KEY": "old_key"}, clear=True)
    def test_get_google_llm_ignores_google_key(self):
        """Should raise ValueError even if GOOGLE_API_KEY is present (strict mode)"""
        with pytest.raises(ValueError, match="GEMINI_API_KEY environment variable is not set"):
            LLMFactory.get_google_llm()
