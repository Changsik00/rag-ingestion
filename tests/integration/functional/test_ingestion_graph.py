import pytest
import asyncio
from unittest.mock import AsyncMock, Mock, patch
from langgraph.checkpoint.memory import MemorySaver

from app.domain.value_objects.ingestion_state import IngestionGraphState, ValidationFeedback
from app.infrastructure.ai.ingestion_graph import IngestionGraphBuilder

@pytest.mark.asyncio
async def test_human_in_the_loop_workflow():
    """
    Scenario: Graph enters human_review node on critical failure (Spec-022)
    """
    # Given: A mock LLM that will trigger the validator
    mock_llm = Mock()
    mock_llm.aextract_metadata = AsyncMock(return_value={
        "title": "HIITL Test",
        "summary": "Needs manual fix",
        "entities": {},
        "language": "en"
    })
    
    checkpointer = MemorySaver()
    builder = IngestionGraphBuilder(mock_llm)

    # When: Validator is mocked to return a critical error once
    call_count = {"validate": 0}
    async def mock_validate(state: IngestionGraphState):
        call_count["validate"] += 1
        if call_count["validate"] == 1:
            return {
                "error": "Critical validation failure",
                "steps_history": state.get("steps_history", []) + ["validate_content"]
            }
        return {"error": None, "steps_history": state.get("steps_history", []) + ["validate_content"]}

    builder.nodes.validate_content = mock_validate
    graph = builder.build(checkpointer=checkpointer)

    initial_state = IngestionGraphState(
        original_url="http://hiitl-test.com",
        raw_content="Content",
        steps_history=[],
        retry_count=0,
        max_retries=3,
        current_strategy="STANDARD",
        active_constraints={"strict_mode": True}
    )

    thread_config = {"configurable": {"thread_id": "hiitl_thread"}}

    # When: Running until interrupt
    events = []
    async for event in graph.astream(initial_state, thread_config):
        events.append(event)

    # Then: Graph is interrupted at human_review
    state_snapshot = graph.get_state(thread_config)
    assert "human_review" in state_snapshot.next
    assert state_snapshot.values["error"] == "Critical validation failure"

    # When: User fixes the error manually
    graph.update_state(
        thread_config,
        {"error": None, "steps_history": state_snapshot.values["steps_history"] + ["human_review"]},
        as_node="human_review"
    )

    # When: Resuming the graph
    async for _ in graph.astream(None, thread_config):
        pass

    # Then: Graph completes successfully
    final_state = graph.get_state(thread_config)
    assert final_state.values["error"] is None
    assert "human_review" in final_state.values["steps_history"]


@pytest.mark.asyncio
async def test_reasoning_flow_backtracking():
    """
    Scenario: Graph generates failure hypothesis and backtracks (Spec-021)
    """
    mock_llm = AsyncMock()
    mock_llm.aextract_metadata.return_value = {"title": "Reasoning Test", "summary": "Initial summary"}
    
    builder = IngestionGraphBuilder(mock_llm)
    
    # When: Validator fails on first run but passes on second
    async def failing_validate(state: IngestionGraphState):
        history = state.get("steps_history", [])
        if "analyze_failure" in history:
            return {"error": None, "steps_history": history + ["validate_content"], "last_feedback": None}
        
        return {
            "error": "Missing key entities",
            "last_feedback": ValidationFeedback(source="validator", message="Retry with focus", target_fields=["entities"]),
            "steps_history": history + ["validate_content"]
        }

    builder.nodes.validate_content = failing_validate
    graph = builder.build()

    initial_state = IngestionGraphState(
        original_url="http://reasoning-test.com",
        raw_content="Content",
        steps_history=[],
        retry_count=0,
        max_retries=2,
        current_strategy="STANDARD"
    )

    # When: Invoking the graph
    final_state = await graph.ainvoke(initial_state)

    # Then: Analyze failure was executed
    history = final_state["steps_history"]
    assert "validate_content" in history
    assert "analyze_failure" in history
    assert "backtracking_context" in final_state
    assert "failure_hypothesis" in final_state["backtracking_context"]
