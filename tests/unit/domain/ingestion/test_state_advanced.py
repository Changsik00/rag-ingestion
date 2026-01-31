from app.domain.ingestion.state import (
    Attempt,
    IngestionGraphState,
    StrategyType,
    ValidationConstraints,
    ValidationFeedback,
)


def test_strategy_enum_values():
    """모든 주요 전략이 Enum에 정의되어 있는지 확인"""
    assert StrategyType.STANDARD.value == "STANDARD"
    assert StrategyType.CORRECTION.value == "CORRECTION"
    assert StrategyType.RELAXATION.value == "RELAXATION"
    assert StrategyType.REINTERPRETATION.value == "REINTERPRETATION"


def test_validation_constraints_default():
    """제약 조건 모델의 기본값 확인"""
    constraints = ValidationConstraints()
    assert constraints.strict_mode is True
    assert constraints.max_retries == 3


def test_validation_feedback_with_fields():
    """Partial Retry를 위한 target_fields 동작 확인"""
    feedback = ValidationFeedback(source="validator", message="Missing Title", target_fields=["title"])
    assert feedback.target_fields == ["title"]
    assert feedback.source == "validator"


def test_attempt_tracking_polymorphic():
    """전략 전환에 따른 Attempt 기록 확인"""
    # 1. Standard Attempt
    attempt1 = Attempt(attempt_number=1, strategy=StrategyType.STANDARD)

    # 2. Correction Attempt (Partial Retry)
    feedback = ValidationFeedback(source="validator", message="Fix title", target_fields=["title"])
    attempt2 = Attempt(attempt_number=2, strategy=StrategyType.CORRECTION, feedback=feedback)

    # 3. Relaxation Attempt
    attempt3 = Attempt(attempt_number=3, strategy=StrategyType.RELAXATION)

    history = [attempt1, attempt2, attempt3]

    assert history[0].strategy == StrategyType.STANDARD
    assert history[1].strategy == StrategyType.CORRECTION
    assert history[1].feedback.target_fields == ["title"]
    assert history[2].strategy == StrategyType.RELAXATION


def test_ingestion_state_initialization():
    """확장된 필드를 포함한 IngestionGraphState 초기화"""
    state: IngestionGraphState = {
        "original_url": "http://example.com",
        "raw_content": "",
        "metadata": None,
        "steps_history": [],
        "error": None,
        "retry_count": 0,
        "max_retries": 3,
        "current_strategy": StrategyType.STANDARD,
        "active_constraints": ValidationConstraints(),
        "attempt_history": [],
        "last_feedback": None,
        "predicted_category": None,
    }

    assert state["current_strategy"] == StrategyType.STANDARD
    assert state["active_constraints"].strict_mode is True
