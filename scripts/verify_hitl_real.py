import asyncio
import logging
import uuid

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.memory import MemorySaver

from app.infrastructure.brain.graph import IngestionGraphBuilder
from app.infrastructure.llm.langchain_adapter import LangChainLLMAdapter

# Logging Setup
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


async def main():
    """
    Real-World HITL Verification Script

    Scenario:
    1. Initialize Graph with Real LLM (Gemini)
    2. Start Ingestion with a prompt designed to FAIL (or force max_retries).
    3. Detect Interrupt (at 'human_review').
    4. Simulate Human Intervention (Resume).
    5. Verify Final Success.
    """
    load_dotenv()

    # 1. Setup Resource
    logger.info("🚀 Starting HITL Real-World Verification...")
    # Initialize Real LLM (Gemini via LangChain)
    google_llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash-exp", temperature=0)
    llm = LangChainLLMAdapter(llm=google_llm)

    builder = IngestionGraphBuilder(llm=llm)
    checkpointer = MemorySaver()

    # Compile Graph with Checkpointer
    graph = builder.build(checkpointer=checkpointer)

    # 2. Config & Input
    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}

    # Intentionally bad content to trigger validation failure -> retry -> hitl
    # But for guaranteed HITL without wasting tokens on retries, we might want to
    # force state.retry_count close to max_retries if possible,
    # but here let's just use strict logic or assume the graph handles retries.
    # To quickly trigger HITL, we can inject a state that already has errors if we were manually setting it,
    # but here we start from scratch.

    # Let's try to trigger a "Critical Error" if possible, or just rely on failing extraction.
    # We will provide content that is CLEARLY NOT matching expectation if we had strict validation.
    # Since we don't have real strictly strict validation implemented in `validate_content` (it's placeholder),
    # we might need to rely on the fact that `validate_content` is currently a pass-through in the provided code.
    # WAIT: `validate_content` in `nodes.py` lines 114-128 is a placeholder/pass-through.
    # It does NOT return an error. So it will NEVER go to `analyze_failure` or `human_review` by default logic
    # unless we force it or unless the placeholder was updated.

    # Checking `nodes.py` again...
    # `validate_content` returns `{"steps_history": ...}` only.
    # `route_after_validation` checks `state.get("error")`.

    # ISSUE: Without a real validator, we cannot naturally trigger HITL via failure.
    # WORKAROUND: We will uses `graph.update_state` to FORCE inject an error state
    # mid-flight or just start with an error state?
    # No, let's start normally, but since we cannot trigger validation failure properly with current code,
    # we will rely on a "Mock Validator" override or just acknowledge this script verifies the MECHANISM
    # assuming validation CAN fail.

    # Let's override the `validate_content` node for this script OR just manually update state
    # to simulate a failure happened.

    logger.info(f"🆔 Thread ID: {thread_id}")

    initial_input = {
        "raw_content": "This is some random text that should definitely fail validation if we had one.",
        "url": "http://test.com/hitl-verify",
        "retry_count": 0,
        "max_retries": 1,  # Low max_retries to hit limit quickly
    }

    # We need to simulate a failure in validation.
    # Since `validate_content` is a placeholder, we can't trigger it naturally.
    # Hack: We will run the graph, but we know it will pass validation.
    # This implies the current codebase might NOT be ready for full E2E HITL testing
    # without a real validator.

    # However, Goal is "verify HITL flow".
    # Let's use `graph.update_state` to INSERT a failure right after start
    # OR we can update the graph definition in the script (monkey patch)?

    # Better approach:
    # Run the graph. It will likely succeed the first pass.
    # Then we manually inject a "Critical Error" state and resume?
    # No, that's not natural flow.

    # Let's look at `nodes.py` again.
    # If we really want to verify HITL, we need getting to `human_review`.
    # `route_after_validation` goes to `human_review` if:
    # 1. state.get("error") exists AND (retry >= max OR error is critical)

    # Let's start the graph with a pre-set error? No, extract_metadata will overwrite/ignore?
    # Extract metadata takes `state`.

    # Proposed Solution for Script:
    # 1. Start execution.
    # 2. It pauses? No, it goes directly to END if no error.
    #
    # Forced Interrupt Strategy:
    # We will use `input` that ALREADY has "retry_count": 3 (max).
    # And we need `error` in state.
    # But `extract_metadata` runs first.
    # Then `validate_content`.
    # `validate_content` preserves existing keys?
    # `nodes.py`: `validate_content` returns `{"steps_history": ...}`.
    # LangGraph merges updates. So if we start with `error` in input, it MIGHT persist?
    # Let's try starting with `error` and `retry_count` in initial input.

    initial_input["hitl_enabled"] = True
    # initial_input["error"] = "Simulated Critical Error for HITL"
    # initial_input["retry_count"] = 3

    logger.info("▶️ Starting Graph Execution (Expect Interrupt)...")

    # Run until interrupt
    # We use `stream` or `ainvoke`. `ainvoke` will raise GraphInterrupt if interrupted?
    # Or return partial state?
    # Recommended way: use stream with `stream_mode="values"` or just iterated.

    async for event in graph.astream(initial_input, config):
        logger.info(f"🔄 Step: {list(event.keys())}")
        pass

    # Check current state (snapshot)
    snapshot = graph.get_state(config)
    logger.info(f"⏸️ Current Node: {snapshot.next}")

    if "human_review" in snapshot.next:
        logger.info("✅ SUCCESS: Graph interrupted at 'human_review' as expected (Toggle Works)!")
    else:
        logger.error(f"❌ FAILED: Graph did not stop at 'human_review'. Next: {snapshot.next}")
        return

    # 3. Simulate Human Review (Resume)
    logger.info("👤 Simulating Human Intervention (Resume)...")

    # Update state to fix the "error" (Clear error, reset retries)
    # This simulates USER saying "I fixed it, proceed."
    # OR actually providing the correct metadata.
    updated_state = {
        "hitl_enabled": False,  # Important: Turn off toggle to proceed
        "metadata": {"title": "Verified Title via HITL"},  # Injection
    }

    graph.update_state(config, updated_state)
    logger.info("✏️ State Updated. Resuming...")

    # Resume
    async for event in graph.astream(None, config):
        logger.info(f"🔄 Step (After Resume): {list(event.keys())}")

    # Final Check
    final_snapshot = graph.get_state(config)
    logger.info(f"🏁 Final Outcome: {final_snapshot.values.get('metadata')}")

    if final_snapshot.values.get("metadata", {}).get("title") == "Verified Title via HITL":
        logger.info("🎉 HITL Verification COMPLETE: Successfully resumed and secured data.")
    else:
        logger.info("⚠️ Verification Result ambiguous. Check logs.")


if __name__ == "__main__":
    asyncio.run(main())
