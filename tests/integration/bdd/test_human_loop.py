import pytest
from langgraph.checkpoint.memory import MemorySaver

from app.domain.ingestion.graph_state import IngestionGraphState
from app.infrastructure.ai.graphs.ingestion_graph import IngestionGraphBuilder

pytestmark = pytest.mark.skip(reason="Requires infrastructure setup - see specs/integration-test-improvement.md")


class MockLLM:
    def __init__(self):
        pass

    def extract_metadata(self, content: str, *args, **kwargs):
        return {
            "title": "Test Doc",
            "summary": "Summary",
            "keywords": ["test"],
            "entities": [],
            "language": "en",
            "category": "test",
        }


@pytest.mark.asyncio
async def test_human_in_the_loop_workflow():
    """
    Spec-022: Human-in-the-loop Integration Test
    """
    # 1. Setup
    mock_llm = MockLLM()
    checkpointer = MemorySaver()
    builder = IngestionGraphBuilder(mock_llm)

    # Mocking validate_content to return error on first run

    call_count = {"validate": 0}

    def mock_validate(state: IngestionGraphState):
        call_count["validate"] += 1
        if call_count["validate"] == 1:
            # Simulate Critical Error
            return {
                "error": "Critical Error: Something bad happened",
                "steps_history": state.get("steps_history", []) + ["validate_content"],
            }
        # Second time pass
        return {"error": None, "steps_history": state.get("steps_history", []) + ["validate_content"]}

    builder.nodes.validate_content = mock_validate

    app = builder.build(checkpointer=checkpointer)

    initial_state = IngestionGraphState(
        original_url="http://test.com",
        raw_content="Dummy content",
        metadata=None,
        steps_history=[],
        error=None,
        retry_count=0,
        max_retries=3,
        current_strategy="STANDARD",
        active_constraints={"strict_mode": True, "max_retries": 3, "retry_depth": 0},
        attempt_history=[],
        last_feedback=None,
        predicted_category=None,
    )

    thread_config = {"configurable": {"thread_id": "test_thread_1"}}

    # 2. Run until Interrupt
    print("\n--- Starting Graph Execution ---")
    # Using astream to consume events until interruption
    events = []
    async for event in app.astream(initial_state, thread_config):
        print(f"Event: {event}")
        events.append(event)

    # 3. Verify Interrupt
    state_snapshot = app.get_state(thread_config)
    print(f"\n--- Snapshot at Interrupt: {state_snapshot.next} ---")

    # Assertions for Interrupt
    assert len(state_snapshot.next) > 0, "Graph should be interrupted"
    assert "human_review" in state_snapshot.next, "Next node should be 'human_review'"
    assert state_snapshot.values["error"] == "Critical Error: Something bad happened"

    # 4. User Intervention (Simulate Manual Fix)
    print("\n--- User Updating State ---")
    current_history = state_snapshot.values.get("steps_history", [])
    app.update_state(
        thread_config,
        {
            "error": None,
            "last_feedback": None,
            "steps_history": current_history + ["human_review"],
        },  # Clear error AND record that human review happened
        as_node="human_review",
    )

    # 5. Resume
    print("\n--- Resuming Graph ---")
    async for event in app.astream(None, thread_config):
        print(f"Resume Event: {event}")

    # 6. Verify Completion
    final_state = app.get_state(thread_config)
    # Since mock_validate clears error on 2nd run (if we looped back), or if we cleared it manually.
    # Flow: human_review -> resolve_logic -> extract -> validate(2) -> End
    assert final_state.values["error"] is None, "Error should be cleared after resume"
    assert "human_review" in final_state.values["steps_history"]
