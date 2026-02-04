# De-scoping Verification Lab & Future Evaluation System

## Decision
The "Verification Lab" feature (originally part of Spec 063) is being **de-scoped** and removed from the current codebase.

**Reasons**:
1.  **Low Value**: The current implementation is merely a UI wrapper around the Playground, offering no real "verification" (metrics, ground truth comparison).
2.  **Data Dependency**: It relied on hardcoded questions specific to a point-in-time state of the DB.
3.  **Better Approach Needed**: A proper evaluation system requires managed datasets (Golden Sets) and automated metric calculation (e.g., Ragas/DeepEval), which is a separate, larger scope.

## Cleanup Plan
- [x] **Remove Files**:
    - `admin/pages/5_Verification_Lab.py`
    - `admin/utils/di_helper.py`
- [x] **Update Backlog**:
    - Add "Spec 065: RAG Evaluation System" to `backlog/queue.md`.
    - Update `backlog/archive.md` to clarify Spec 063 scope.

## Future Work: Spec 065 (Proposed)
**Title**: RAG Evaluation System (Automated & Dataset-driven)
**Goal**: Build a rigorous evaluation pipeline.
**Key Features**:
*   **Feedback Integration**: Parse `feedback.jsonl` to bootstrap the Golden Dataset.
*   **Golden Dataset Management**: UI to Upload/Manage Q&A pairs (Ground Truth).
*   **Automated Testing**: Batch run RAG pipeline against the dataset.
*   **Metrics**: Calculate Relevance, Faithfulness, Retrieval Recall.
*   **Integration**: CI/CD integration for regression testing.
