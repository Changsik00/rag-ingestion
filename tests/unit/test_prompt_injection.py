from app.domain.ingestion.state import FailureHypothesis, StrategyType
from app.infrastructure.brain.nodes import construct_extraction_prompt


def test_prompt_includes_reasoning_context():
    """FailureHypothesis가 존재할 경우 프롬프트에 분석 내용이 포함되는지 검증"""

    # Given
    failure_hypothesis: FailureHypothesis = {
        "cause": "missing_info",
        "description": "Required field 'year' is missing",
        "invalid_assumptions": ["Document has explicit year"],
    }

    # When
    prompt = construct_extraction_prompt(
        strategy=StrategyType.CORRECTION,
        feedback=None,
        constraints=None,
        failure_hypothesis=failure_hypothesis,  # New argument
    )

    # Then
    assert "FAILURE ANALYSIS" in prompt
    assert "Required field 'year' is missing" in prompt
    assert "Document has explicit year" in prompt
    assert "Why failed:" in prompt


def test_prompt_without_hypothesis_is_standard():
    """FailureHypothesis가 없으면 기본 프롬프트가 반환되는지 검증"""
    prompt = construct_extraction_prompt(
        strategy=StrategyType.STANDARD, feedback=None, constraints=None, failure_hypothesis=None
    )

    assert "FAILURE ANALYSIS" not in prompt
