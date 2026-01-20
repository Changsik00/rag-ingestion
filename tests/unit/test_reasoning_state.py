import pytest
from app.domain.ingestion.state import IngestionState, FailureHypothesis, DecisionTrace, QuestionInterpretation

def test_failure_hypothesis_structure():
    """FailureHypothesis TypedDict 구조 검증"""
    hypothesis: FailureHypothesis = {
        "cause": "missing_fields",
        "description": "Required fields 'summary' is missing",
        "invalid_assumptions": ["Document has summary section"]
    }
    assert hypothesis["cause"] == "missing_fields"
    assert len(hypothesis["invalid_assumptions"]) == 1

def test_decision_trace_structure():
    """DecisionTrace TypedDict 구조 검증"""
    trace: DecisionTrace = {
        "retry_count": 1,
        "selected_strategy": "CORRECTION",
        "reason": "Validation failed due to missing fields"
    }
    assert trace["selected_strategy"] == "CORRECTION"

def test_ingestion_state_has_backtracking_context():
    """IngestionState에 backtracking_context 필드가 존재하는지 검증"""
    state = IngestionState(
        original_url="http://test.com",
        raw_content="content",
        metadata=None,
        steps_history=[],
        error=None,
        retry_count=0,
        max_retries=3,
        current_strategy="STANDARD",
        active_constraints={},
        attempt_history=[],
        last_feedback=None,
        predicted_category=None,
        #New field
        backtracking_context={
            "failure_hypothesis": None,
            "interpretation_history": [],
            "decision_trace": []
        }
    )
    
    context = state.get("backtracking_context")
    assert context is not None
    assert "failure_hypothesis" in context
    assert "decision_trace" in context
