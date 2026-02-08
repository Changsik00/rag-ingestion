from typing import Any

from langchain_core.messages import AIMessage

from app.application.interfaces.llm import LLMInterface
from app.domain.value_objects.ingestion_state import (
    IngestionGraphState,
    StrategyType,
    ValidationConstraints,
    ValidationFeedback,
)


def construct_extraction_prompt(
    strategy: StrategyType,
    feedback: ValidationFeedback | None,
    constraints: ValidationConstraints | None,
    failure_hypothesis: dict | None = None,
) -> str:
    """
    Builds the system prompt dynamically based on the current strategy.

    Strategies:
    - STANDARD: Default extraction instructions.
    - CORRECTION (Reasoning Retry): Injects previous feedback and target fields.
    - RELAXATION: Injects instructions to be less strict.
    """
    base_prompt = (
        "You are an expert knowledge extractor. Your goal is to extract structured metadata from the provided content."
    )

    if failure_hypothesis:
        # Spec 023: Reasoning Context Injection
        reasoning_instruction = (
            f"\n\nFAILURE ANALYSIS:\n"
            f"Previous attempt failed. Why failed:\n"
            f"- Cause: {failure_hypothesis['cause']}\n"
            f"- Description: {failure_hypothesis['description']}\n"
        )
        if failure_hypothesis.get("invalid_assumptions"):
            assumptions_str = ", ".join(failure_hypothesis["invalid_assumptions"])
            reasoning_instruction += f"- Invalid Assumptions: {assumptions_str}\n"

        reasoning_instruction += "\nPlease adjust your extraction strategy based on this analysis."
        return base_prompt + reasoning_instruction

    if strategy == StrategyType.CORRECTION and feedback:
        # Reflexion Pattern: Feed back the error
        correction_instruction = f"\n\nCRITICAL FEEDBACK: Previous attempt failed.\nError Message: {feedback.message}\n"
        if hasattr(feedback, "target_fields") and feedback.target_fields:
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

    async def extract_metadata(self, state: IngestionGraphState) -> dict[str, Any]:
        """
        Raw Content에서 메타데이터(Title, Summary, Entities 등)를 추출합니다.

        Args:
            state (IngestionGraphState): 현재 파이프라인 상태

        Returns:
            Dict[str, Any]: 상태 업데이트 (metadata, steps_history)
        """
        raw_content = state["raw_content"]

        # 1. Construct Dynamic Prompt based on Strategy & Feedback
        backtracking_context = state.get("backtracking_context")
        failure_hypothesis = backtracking_context.get("failure_hypothesis") if backtracking_context else None

        system_prompt = construct_extraction_prompt(
            strategy=state.get("current_strategy", StrategyType.STANDARD),
            feedback=state.get("last_feedback"),
            constraints=state.get("active_constraints"),
            failure_hypothesis=failure_hypothesis,
        )

        # 2. LLM 호출 (Prompt Injection)
        content_meta = state.get("content_metadata", {})
        enriched_content = (
            f"{system_prompt}\n\n--- SOURCE METADATA ---\n{content_meta}\n\n--- CONTENT ---\n{raw_content}"
        )

        # The orchestrator/llm implementation must provide aextract_metadata
        extracted = await self.llm.aextract_metadata(enriched_content)

        # History 업데이트 (MessagesState)
        return {"metadata": extracted, "messages": [AIMessage(content="Step: extract_metadata")]}

    def validate_content(self, state: IngestionGraphState) -> dict[str, Any]:
        """
        추출된 콘텐츠의 유효성을 검사합니다.
        (현재는 Placeholder implementation. Actual validation logic to be added.)
        """
        # Placeholder validation: Always pass unless mock error injected
        # In a real scenario, this would check schema constraints.

        # NOTE: For now, we assume validation is part of the flow.
        # If we want to simulate failure, we need a mechanism.
        # But for this task, we focus on the WIRING.

        return {"messages": [AIMessage(content="Step: validate_content")]}

    def resolve_logic(self, state: IngestionGraphState) -> dict[str, Any]:
        """
        [Logic Resolver Node]
        검증 결과(Feedback)와 에러 상태를 기반으로 다음 전략(Strategy)을 결정합니다.

        Returns:
            dict: Updates current_strategy, attempts, retry_count
        """
        from app.domain.value_objects.ingestion_state import Attempt

        current_retry = state.get("retry_count", 0)
        feedbacks = []
        if state.get("last_feedback"):
            feedbacks.append(state["last_feedback"])

        # 1. Select Strategy
        next_strategy = select_strategy(current_retry, feedbacks)

        # 2. Record Attempt (Preparing for next run)
        new_attempt = Attempt(
            attempt_number=current_retry + 1, strategy=next_strategy, feedback=state.get("last_feedback")
        )
        current_attempts = state.get("attempt_history", []) + [new_attempt]

        return {
            "current_strategy": next_strategy,
            "retry_count": current_retry + 1,
            "attempt_history": current_attempts,
            "messages": [AIMessage(content="Step: resolve_logic")],
        }

    def human_review(self, state: IngestionGraphState) -> dict[str, Any]:
        """
        [Human Review Node]
        사용자 개입을 위한 일시 정지 지점 (Passthrough).
        graph.compile(interrupt_before=["human_review"]) 설정을 통해
        이 노드 실행 직전에 멈추게 됩니다.

        실제로는 아무 작업도 하지 않고 상태를 유지한 채 반환합니다.
        사용자가 update_state를 통해 상태를 수정한 후 resume하면
        이 노드가 실행되고(pass), 그 다음 노드(resolve_logic)로 넘어갑니다.
        """
        return {"messages": [AIMessage(content="Step: human_review")]}

    def analyze_failure(self, state: IngestionGraphState) -> dict[str, Any]:
        """
        [Failure Analysis Node] (Spec 023)
        검증 실패 원인을 분석하여 FailureHypothesis를 생성합니다.

        Logic:
        1. If feedback exists, map feedback to hypothesis.
        2. If error exists, map error to hypothesis.
        3. Else, unknown error.
        """
        from app.domain.value_objects.ingestion_state import BacktrackingContext, FailureHypothesis

        error = state.get("error")
        feedback = state.get("last_feedback")

        cause = "unknown_error"
        description = "Unknown error occurred"
        invalid_assumptions = []

        if feedback:
            # Rule 1: Missing Fields
            if feedback.target_fields:
                cause = "missing_info"
                fields_str = ", ".join(feedback.target_fields)
                description = f"Required field '{fields_str}' is missing or invalid."
                invalid_assumptions.append(f"Document has explicit {fields_str}")
            else:
                cause = "validation_error"
                description = feedback.message
        elif error:
            cause = "system_error"
            description = str(error)

        hypothesis: FailureHypothesis = {
            "cause": cause,
            "description": description,
            "invalid_assumptions": invalid_assumptions,
        }

        # Update Backtracking Context
        current_context = state.get("backtracking_context") or {
            "failure_hypothesis": None,
            "interpretation_history": [],
            "decision_trace": [],
        }

        # Ensure TypedDict structure (shallow copy update)
        new_context: BacktrackingContext = {
            "failure_hypothesis": hypothesis,
            "interpretation_history": current_context.get("interpretation_history", []),
            "decision_trace": current_context.get("decision_trace", []),
        }

        return {
            "backtracking_context": new_context,
            "messages": [AIMessage(content="Step: analyze_failure")],
        }


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
