import importlib

import pytest


def test_ingestion_state_import():
    """IngestionGraphState 모듈이 존재하고 임포트 가능한지 검증"""
    if not importlib.util.find_spec("app.domain.ingestion.graph_state"):
        pytest.fail("app.domain.ingestion.graph_state module not found")

    try:
        from app.domain.ingestion.graph_state import IngestionGraphState  # noqa: F401
    except ImportError:
        pytest.fail("app.domain.ingestion.state module or IngestionGraphState class not found")


def test_ingestion_state_structure():
    """IngestionGraphState가 정의된 스키마(TypedDict)를 준수하는지 검증"""
    from app.domain.ingestion.graph_state import IngestionGraphState

    # TypedDict는 인스턴스화가 아니라 type check용이지만,
    # 런타임에 dict와 호환되는지 확인
    state: IngestionGraphState = {
        "original_url": "http://example.com",
        "raw_content": "dummy content",
        "metadata": None,
        "steps_history": [],
        "error": None,
        "retry_count": 0,
    }

    assert state["original_url"] == "http://example.com"
    assert "steps_history" in state
    assert state["retry_count"] == 0
