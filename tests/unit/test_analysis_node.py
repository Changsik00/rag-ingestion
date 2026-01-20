import pytest
from app.infrastructure.brain.nodes import IngestionNodes
from app.domain.ingestion.state import IngestionState, ValidationFeedback

from unittest.mock import Mock

def test_analyze_failure_creates_hypothesis():
    """analyze_failure 메서드가 에러와 피드백을 기반으로 가설을 생성하는지 검증"""
    mock_llm = Mock()
    nodes = IngestionNodes(llm=mock_llm)
    
    # Given: 실패한 상태 (Missing Field)
    state: IngestionState = {
        "error": "Validation Failed",
        "last_feedback": ValidationFeedback(
            source="validator",
            message="Required field 'summary' is missing",
            target_fields=["summary"]
        ),
        "retry_count": 1,
        "backtracking_context": {
            "failure_hypothesis": None,
            "interpretation_history": [],
            "decision_trace": []
        }
    }

    # When
    result = nodes.analyze_failure(state)

    # Then
    backtracking_context = result.get("backtracking_context")
    assert backtracking_context is not None
    hypothesis = backtracking_context.get("failure_hypothesis")
    
    assert hypothesis is not None
    assert hypothesis["cause"] == "missing_info"
    assert "summary" in hypothesis["description"]
    assert "field 'summary' is missing" in hypothesis["description"]

def test_analyze_failure_handles_unknown_error():
    """명확하지 않은 에러에 대해 default 가설을 생성하는지 검증"""
    mock_llm = Mock()
    nodes = IngestionNodes(llm=mock_llm)
    
    state: IngestionState = {
        "error": "Unknown System Error",
        "last_feedback": None,
        "retry_count": 1,
        "backtracking_context": None # Init if missing
    }

    result = nodes.analyze_failure(state)
    
    hypothesis = result["backtracking_context"]["failure_hypothesis"]
    assert hypothesis["cause"] == "system_error"
