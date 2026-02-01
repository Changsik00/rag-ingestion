from app.domain.ingestion.graph_state import StrategyType, ValidationFeedback


def select_strategy(retry_count: int, feedbacks: list[ValidationFeedback]) -> StrategyType:
    """
    Meta-Reasoner: 현재 상황(재시도 횟수, 피드백)을 분석하여 최적의 재시도 전략을 선택합니다.

    Rules:
    - Retry 0~1: CORRECTION (Reasoning Retry)
    - Retry >= 2: RELAXATION (Constraint Re-evaluation) - 반복된 실패 시 완화
    """
    if not feedbacks:
        # 피드백이 없으면 재시도 의미가 모호하므로 기본(방어) 로직
        return StrategyType.STANDARD

    # Level 3: Constraint Re-evaluation (Relaxation)
    # 2번 이상 시도했는데도 실패했다면, 기준이 너무 높은 것일 수 있음.
    if retry_count >= 2:
        return StrategyType.RELAXATION

    # Level 2: Reasoning Retry (Correction)
    # 초기 실패는 LLM의 단순 실수일 확률이 높으므로 교정 시도.
    return StrategyType.CORRECTION
