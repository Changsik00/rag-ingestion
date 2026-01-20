from typing import Any

from app.domain.ingestion.state import IngestionState, StrategyType, ValidationConstraints, ValidationFeedback
from app.domain.interfaces.llm import LLMInterface


def construct_extraction_prompt(
    strategy: StrategyType,
    feedback: ValidationFeedback | None,
    constraints: ValidationConstraints | None
) -> str:
    """
    Builds the system prompt dynamically based on the current strategy.

    Strategies:
    - STANDARD: Default extraction instructions.
    - CORRECTION (Reasoning Retry): Injects previous feedback and target fields.
    - RELAXATION: Injects instructions to be less strict.
    """
    base_prompt = (
        "You are an expert knowledge extractor. "
        "Your goal is to extract structured metadata from the provided content."
    )

    if strategy == StrategyType.CORRECTION and feedback:
        # Reflexion Pattern: Feed back the error
        correction_instruction = (
            f"\n\nCRITICAL FEEDBACK: Previous attempt failed.\n"
            f"Error Message: {feedback.message}\n"
        )
        if hasattr(feedback, 'target_fields') and feedback.target_fields:
            # Explicitly format list as string representation
            fields_str = str(feedback.target_fields)
            correction_instruction += f"TARGET FIELDS: {fields_str}\n"
            correction_instruction += "Please FOCUS primarily on fixing these fields."

        return base_prompt + correction_instruction

    if strategy == StrategyType.RELAXATION:
        # Relaxation Pattern: Loosen constraints
        relaxation_instruction = (
            "\n\nRELAXATION MODE: Enabled.\n"
            "Please be less strict with validation rules. "
            "If exact matches are not found, provide the best available approximation."
        )
        return base_prompt + relaxation_instruction

    return base_prompt


class IngestionNodes:
    """
    LangGraph의 각 노드에서 실행될 비즈니스 로직을 캡슐화한 클래스.
    Clean Architecture의 Use Case/Domain Logic에 해당하며,
    State를 입력받아 State Update를 반환합니다.
    """

    def __init__(self, llm: LLMInterface):
        self.llm = llm

    def extract_metadata(self, state: IngestionState) -> dict[str, Any]:
        """
        Raw Content에서 메타데이터(Title, Summary, Entities 등)를 추출합니다.

        Args:
            state (IngestionState): 현재 파이프라인 상태

        Returns:
            Dict[str, Any]: 상태 업데이트 (metadata, steps_history)
        """
        raw_content = state["raw_content"]

        # 1. Construct Dynamic Prompt based on Strategy & Feedback
        system_prompt = construct_extraction_prompt(
            strategy=state.get("current_strategy", StrategyType.STANDARD),
            feedback=state.get("last_feedback"),
            constraints=state.get("active_constraints")
        )

        # 2. LLM 호출 (Prompt Injection)
        # LLMInterface.extract_metadata needs to accept system_prompt override.
        # However, if LLMInterface is fixed, we might need to pass it differently or implementation specific.
        # For now, assuming standard method but we should ideally pass instructions.
        # Since the interface signature is `extract_metadata(content: str) -> ExtractedMetadata`,
        # we might need to prepend the system prompt to the content OR update the interface.
        # For this iteration, we prepending instructions to content if interface doesn't support prompt.

        # NOTE: Temporary measure until LLMInterface supports dynamic prompts explicitly.
        # We append the system instructions to the content for the LLM to see.
        enriched_content = f"{system_prompt}\n\n--- CONTENT ---\n{raw_content}"

        extracted = self.llm.extract_metadata(enriched_content)

        # History 업데이트
        current_history = state.get("steps_history", [])
        new_history = current_history + ["extract_metadata"]

        # 3. Update Attempt History (if not exists for this run)
        # Note: Retry logic typically handles attempt counting, but we record success/fail here?
        # Actually Attempt recording is better done in the Logic/Router or before 'extract'.
        # We keep it simple here.

        return {"metadata": extracted, "steps_history": new_history}

    def validate_content(self, state: IngestionState) -> dict[str, Any]:
        """
        추출된 콘텐츠의 유효성을 검사합니다.
        (현재는 Placeholder implementation. Actual validation logic to be added.)
        """
        # Placeholder validation: Always pass unless mock error injected
        # In a real scenario, this would check schema constraints.

        # NOTE: For now, we assume validation is part of the flow.
        # If we want to simulate failure, we need a mechanism.
        # But for this task, we focus on the WIRING.

        current_history = state.get("steps_history", [])
        new_history = current_history + ["validate_content"]

        return {"steps_history": new_history}

    def resolve_logic(self, state: IngestionState) -> dict[str, Any]:
        """
        [Logic Resolver Node]
        검증 결과(Feedback)와 에러 상태를 기반으로 다음 전략(Strategy)을 결정합니다.
        
        Returns:
            dict: Updates current_strategy, attempts, retry_count
        """
        from app.domain.ingestion.state import Attempt
        from app.infrastructure.brain.logic import select_strategy

        current_retry = state.get("retry_count", 0)
        feedbacks = []
        if state.get("last_feedback"):
            feedbacks.append(state["last_feedback"])

        # 1. Select Strategy
        next_strategy = select_strategy(current_retry, feedbacks)

        # 2. Record Attempt (Preparing for next run)
        new_attempt = Attempt(
            attempt_number=current_retry + 1,
            strategy=next_strategy,
            feedback=state.get("last_feedback")
        )
        current_attempts = state.get("attempt_history", []) + [new_attempt]

        # 3. Update State
        return {
            "current_strategy": next_strategy,
            "retry_count": current_retry + 1,
            "attempt_history": current_attempts,
            "steps_history": state.get("steps_history", []) + ["resolve_logic"]
        }
