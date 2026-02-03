import pytest
from pydantic import ValidationError

from app.interfaces.api.v1.dto.rag import ChatRequest, AdvancedSettings


def test_advanced_settings_defaults():
    """AdvancedSettings가 기본값을 올바르게 설정하는지 테스트"""
    settings = AdvancedSettings()
    assert settings.top_k == 5
    assert settings.temperature == 0.0
    assert settings.search_strategy == "hybrid"


def test_advanced_settings_validation():
    """AdvancedSettings의 값 범위 검증 테스트"""
    # top_k min limit
    with pytest.raises(ValidationError):
        AdvancedSettings(top_k=0)
    
    # temperature range limit
    with pytest.raises(ValidationError):
        AdvancedSettings(temperature=2.0)
    with pytest.raises(ValidationError):
        AdvancedSettings(temperature=-0.1)

    # valid setting
    settings = AdvancedSettings(top_k=10, temperature=0.7, search_strategy="vector")
    assert settings.top_k == 10
    assert settings.temperature == 0.7
    assert settings.search_strategy == "vector"


def test_chat_request_initialization():
    """ChatRequest가 올바르게 초기화되는지 테스트"""
    # basic request
    req = ChatRequest(message="Hello")
    assert req.message == "Hello"
    assert req.hitl_enabled is False
    assert isinstance(req.advanced_settings, AdvancedSettings)
    assert req.advanced_settings.top_k == 5  # default check

    # defaults
    assert req.filters == {}


def test_chat_request_with_custom_settings():
    """ChatRequest에 커스텀 설정을 전달했을 때 반영 확인"""
    custom_settings = AdvancedSettings(top_k=20, search_strategy="keyword")
    req = ChatRequest(message="Test", advanced_settings=custom_settings)
    
    assert req.advanced_settings.top_k == 20
    assert req.advanced_settings.search_strategy == "keyword"


def test_chat_request_validation():
    """ChatRequest 필수 필드 검증"""
    with pytest.raises(ValidationError):
        ChatRequest()  # missing message
