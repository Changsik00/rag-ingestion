from app.domain.value_objects.ingestion_state import StrategyType, ValidationFeedback
from app.infrastructure.ai.ingestion_nodes import construct_extraction_prompt


def test_standard_prompt_construction():
    """STANDARD 전략일 때는 기본 프롬프트 반환"""
    prompt = construct_extraction_prompt(strategy=StrategyType.STANDARD, feedback=None, constraints=None)
    assert "You are an expert knowledge extractor" in prompt
    assert "FIX" not in prompt
    assert "RELAX" not in prompt


def test_correction_prompt_with_feedback():
    """CORRECTION 전략 시 피드백이 프롬프트에 주입되어야 함"""
    feedback = ValidationFeedback(source="validator", message="Missing title", target_fields=["title"])

    prompt = construct_extraction_prompt(strategy=StrategyType.CORRECTION, feedback=feedback, constraints=None)

    assert "CRITICAL FEEDBACK: Previous attempt failed." in prompt
    assert "Missing title" in prompt
    assert "TARGET FIELDS: ['title']" in prompt  # Partial Retry


def test_relaxation_prompt():
    """RELAXATION 전략 시 제약 완화 지시가 포함되어야 함"""
    prompt = construct_extraction_prompt(strategy=StrategyType.RELAXATION, feedback=None, constraints=None)

    assert "RELAXATION MODE: Enabled" in prompt
    assert "be less strict" in prompt.lower()
