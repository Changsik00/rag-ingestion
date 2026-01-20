import pytest
from typing import TypedDict, get_type_hints

def test_ingestion_state_import():
    """IngestionState 모듈이 존재하고 임포트 가능한지 검증"""
    try:
        from app.domain.ingestion.state import IngestionState
    except ImportError:
        pytest.fail("app.domain.ingestion.state module or IngestionState class not found")

def test_ingestion_state_structure():
    """IngestionState가 정의된 스키마(TypedDict)를 준수하는지 검증"""
    from app.domain.ingestion.state import IngestionState
    
    assert issubclass(IngestionState, dict)
    
    # Type Hint 검사
    hints = get_type_hints(IngestionState)
    
    # 필수 필드 확인
    expected_fields = [
        "original_url",
        "raw_content",
        "metadata",
        "extracted_entities",
        "steps_history"
    ]
    
    for field in expected_fields:
        assert field in hints, f"IngestionState must have '{field}' field"
