from app.domain.ingestion.state import Attempt, IngestionState, StrategyType, ValidationConstraints, ValidationFeedback


def test_ingestion_state_initialization():
    """IngestionState의 필수 필드와 새로운 Reflexion 필드가 올바르게 타입 정의되었는지 확인"""
    state: IngestionState = {
        "original_url": "http://example.com",
        "raw_content": "test content",
        "metadata": None,
        "steps_history": [],
        "error": None,
        "retry_count": 0,
        "max_retries": 3,
        "current_strategy": StrategyType.STANDARD,  # Updated
        "active_constraints": ValidationConstraints(),  # Updated
        "attempt_history": [],
        "last_feedback": None,
        "predicted_category": None,
    }

    assert state["retry_count"] == 0
    assert state["current_strategy"] == StrategyType.STANDARD
    assert len(state["attempt_history"]) == 0


def test_validation_feedback_model():
    """ValidationFeedback 모델 생성 및 유효성 검사"""
    feedback = ValidationFeedback(source="validator", message="Missing title")
    assert feedback.source == "validator"
    assert feedback.message == "Missing title"
    assert feedback.timestamp is not None


def test_attempt_tracking():
    """Attempt 모델을 이용한 히스토리 추적 시나리오 테스트"""
    # 1st Attempt (Initial)
    attempt1 = Attempt(attempt_number=1, strategy=StrategyType.STANDARD)

    # Validation Failed
    feedback = ValidationFeedback(source="validator", message="Title is empty")

    # 2nd Attempt (Retry with Correction)
    attempt2 = Attempt(attempt_number=2, strategy=StrategyType.CORRECTION, feedback=feedback)

    history = [attempt1, attempt2]

    assert len(history) == 2
    assert history[0].strategy == StrategyType.STANDARD
    assert history[1].strategy == StrategyType.CORRECTION
    assert history[1].feedback.message == "Title is empty"
