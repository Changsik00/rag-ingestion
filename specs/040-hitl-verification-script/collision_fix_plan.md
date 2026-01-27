# AdminAgent Checkpointer Collision Fix

## Problem
Currently, `AdminAgent` and `RAGService` (invoked inside AdminAgent) use the **Same Thread ID** and **Same Checkpointer**.
This causes state collision:
1. `AdminAgent` saves `AdminState`.
2. `RAGService` loads this state, potentially causing schema mismatch or logic errors during retrieval.
3. `RAGService` saves `RAGState`, overwriting `AdminState`.
4. `AdminAgent` resumes, overwriting `RAGState`.

This race condition/schema violation manifests as retrieval failures ("Not Found") or erratic behavior, especially when HITL interrupts force strict checkpointing.

## Fix
In `app/domain/services/admin_agent.py`, when calling `rag_service.retrieve_and_generate`, we must use a **namespaced thread_id** (e.g., `rag_{thread_id}`) to segregate the RAG Service's internal state from the Admin Agent's orchestration state.

## Proposed Changes
### `app/domain/services/admin_agent.py`
- Modify `search_node`:
  ```python
  # Use a separate thread_id for the inner RAG Service to avoid checkpoint collision
  rag_thread_id = f"rag_{thread_id}" if thread_id else None
  result = await self.rag_service.retrieve_and_generate(..., thread_id=rag_thread_id)
  ```

## Verification
- Restart Backend.
- Test in Playground: Enable HITL -> Retrieval should now succeed AND interrupt.
