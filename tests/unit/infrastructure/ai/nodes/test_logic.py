from app.domain.value_objects.ingestion_state import StrategyType, ValidationFeedback
from app.infrastructure.ai.ingestion_nodes import select_strategy


def test_select_correction_strategy_on_first_error():
    """1차 에러 발생 시 CORRECTION 전략 선택"""
    retry_count = 0
    feedback = ValidationFeedback(source="validator", message="Missing title")

    strategy = select_strategy(retry_count=retry_count, feedbacks=[feedback])

    assert strategy == StrategyType.CORRECTION


def test_select_relaxation_strategy_on_repeated_error():
    """반복된 에러(2회 이상) 발생 시 RELAXATION 전략 선택"""
    retry_count = 2
    feedbacks = [
        ValidationFeedback(source="validator", message="Too many entities"),
        ValidationFeedback(source="validator", message="Too many entities"),
    ]

    strategy = select_strategy(retry_count=retry_count, feedbacks=feedbacks)

    assert strategy == StrategyType.RELAXATION


def test_fallback_to_standard():
    """예외적인 상황에서는 기본 전략 유지 보수적 접근"""
    # 에러는 없는데 재시도 카운트만 있는 모순적 상황 (방어 로직)
    strategy = select_strategy(retry_count=1, feedbacks=[])
    assert strategy == StrategyType.STANDARD


def test_select_reinterpretation_on_schema_error():
    """스키마 불일치 에러 시 REINTERPRETATION 선택 (Future Mock)"""
    # TODO: 에러 메시지 분석 로직 고도화 필요
    pass
