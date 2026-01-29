from unittest.mock import Mock, patch

import pytest
from langchain_google_genai import ChatGoogleGenerativeAI

from app.core.config import Settings
from app.core.llm import LLMFactory


class TestLLMFactory:
    def setup_method(self):
        # Clear cache before each test
        LLMFactory.get_google_llm.cache_clear()
        LLMFactory.get_llm_adapter.cache_clear()

    @patch("app.core.llm.get_settings")
    def test_get_google_llm_with_gemini_key(self, mock_get_settings):
        """Should succeed when GEMINI_API_KEY is present"""
        mock_settings = Mock(spec=Settings)
        mock_settings.GEMINI_API_KEY = "test_gemini_key"
        mock_settings.GEMINI_MODEL_NAME = "gemini-1.5-pro"
        mock_get_settings.return_value = mock_settings

        llm = LLMFactory.get_google_llm()
        assert isinstance(llm, ChatGoogleGenerativeAI)
        assert llm.google_api_key.get_secret_value() == "test_gemini_key"

    @patch("app.core.llm.get_settings")
    def test_get_google_llm_no_key_raises_error(self, mock_get_settings):
        """Should raise ValueError when GEMINI_API_KEY is missing"""
        mock_settings = Mock(spec=Settings)
        mock_settings.GEMINI_API_KEY = None
        mock_settings.GEMINI_MODEL_NAME = "gemini-1.5-pro"
        mock_get_settings.return_value = mock_settings

        with pytest.raises(ValueError, match="GEMINI_API_KEY environment variable is not set"):
            LLMFactory.get_google_llm()

    @patch("app.core.llm.get_settings")
    def test_get_google_llm_ignores_google_key(self, mock_get_settings):
        """Should raise ValueError even if GOOGLE_API_KEY is present (strict mode)"""
        # Scenario: GOOGLE_API_KEY is in env (settings ignored it or mapped to legacy),
        # but GEMINI_API_KEY is empty in Settings object.
        mock_settings = Mock(spec=Settings)
        mock_settings.GEMINI_API_KEY = None
        mock_settings.GEMINI_MODEL_NAME = "gemini-1.5-pro"
        mock_get_settings.return_value = mock_settings

        with pytest.raises(ValueError, match="GEMINI_API_KEY environment variable is not set"):
            LLMFactory.get_google_llm()
