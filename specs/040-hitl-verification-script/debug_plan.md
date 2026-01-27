# AdminAgent HITL Fix Plan

## Goal
Fix the bug where enabling HITL in Admin Chat causes RAG retrieval to fail (returning "No context found") instead of just pausing for review.

## Diagnosis (Hypothesis)
1. **Interrupt Logic**: The `human_review` node might be causing an early exit or state issue that prevents the *previous* `search_node` output from being returned correctly to the API.
2. **State Persistence**: When `hitl_enabled`, the graph uses `interrupt_before`. This might affect how `ainvoke` returns the final result (`result.answer` might be lost or not fully generated if `await` returns early).
3. **Retrieval**: The user reports "Information not found", which implies `search_node` RAN but failed to retrieve. This is suspicious.

## Proposed Changes

### [Investigation]
1. **Analyze `retrieve_and_generate`**: Check `app/domain/services/rag_service.py`.
2. **Reproduction Script**: Create `scripts/debug_admin_agent.py` to simulate the exact flow with `hitl_enabled=True`.

### [Fix Candidates]
- **AdminAgent**: Ensure `human_review` node preserves or passes through the `messages` from `search_node`.
- **RAG Endpoint**: Handle `GraphInterrupt` or partial state return from `ainvoke`. If `ainvoke` raises `GraphInterrupt`, we must catch it and manually fetch the state from the checkpointer to return the "Thinking..." or "Answer" so far.

## Verification Plan

### Automated Test
- `scripts/debug_admin_agent.py`:
  - Run with `hitl_enabled=True`.
  - Check if `result` contains the correct answer AND indicates interruption.

### Manual Verification
- Use `Admin Playground` again after fix.
