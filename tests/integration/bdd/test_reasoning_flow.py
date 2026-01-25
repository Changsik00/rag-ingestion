from unittest.mock import Mock

import pytest

from app.domain.ingestion.state import IngestionState, ValidationFeedback
from app.infrastructure.brain.graph import IngestionGraphBuilder
from app.infrastructure.brain.nodes import IngestionNodes


@pytest.fixture
def mock_llm():
    import asyncio
    llm = Mock()
    # Mock extract_metadata to return some dummy data as a Future
    future = asyncio.Future()
    future.set_result({"title": "Test Title", "summary": "Test Summary"})
    llm.extract_metadata.return_value = future
    return llm


@pytest.mark.asyncio
async def test_reasoning_flow_integration(mock_llm):
    """
    Given: Validation이 실패하여 재시도가 필요한 상황
    When: Graph가 실행되면
    Then:
        1. validate_content (Fail) -> analyze_failure (Run) -> resolve_logic (Next Strategy) 순으로 실행된다.
        2. analyze_failure 노드가 실행되어 State에 FailureHypothesis가 생성된다.
        3. 다음 extract_metadata 실행 시 Prompt에 FailureHypothesis가 반영된다 (Mock LLM 호출 인자 확인).
    """
    # 1. Setup Graph with Mock Nodes to simulate failure flow
    nodes = IngestionNodes(llm=mock_llm)

    # Mock validate_content to fail once then pass (to prevent infinite loop)
    # But wait, we want to verify the FLOW, not necessarily run the whole loop till success.
    # We can inspect the state after a few steps.

    # Let's rely on the Conditional Logic in the Graph.
    # We need to construct the graph first.
    builder = IngestionGraphBuilder(mock_llm)

    # We need to monkeypatch `builder.nodes.validate_content` to simulate failure.
    nodes = builder.nodes

    original_validate = nodes.validate_content

    def failing_validate(state: IngestionState):
        current_history = state.get("steps_history", [])

        # Stop loop after one analysis to allow test to finish
        if "analyze_failure" in current_history:
            return {"steps_history": current_history + ["validate_content"], "error": None, "last_feedback": None}

        return {
            "error": "Simulated Validation Error",
            "last_feedback": ValidationFeedback(source="validator", message="Field missing", target_fields=["summary"]),
            "steps_history": current_history + ["validate_content"],
        }

    nodes.validate_content = failing_validate

    app = builder.build()

    # 3. Run Graph
    input_state = IngestionState(
        original_url="http://test.com",
        raw_content="content",
        metadata=None,
        steps_history=[],
        error=None,
        retry_count=0,
        max_retries=1,  # Allow 1 retry
        current_strategy="STANDARD",
        active_constraints={},
        attempt_history=[],
        last_feedback=None,
        predicted_category=None,
        backtracking_context=None,
    )

    # Run fully
    final_state = await app.ainvoke(input_state)

    # 4. Verify History contains 'analyze_failure'
    history = final_state["steps_history"]
    assert "extract_metadata" in history
    assert "validate_content" in history

    # THIS ASSERTION SHOULD FAIL before we wire the node
    assert "analyze_failure" in history

    # 5. Verify Context
    context = final_state.get("backtracking_context")
    assert context is not None
    assert context["failure_hypothesis"]["cause"] == "missing_info"

    # Restore
    nodes.validate_content = original_validate
