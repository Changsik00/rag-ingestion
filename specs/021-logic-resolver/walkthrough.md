# Walkthrough: Spec-021 (Logic Resolver & Polymorphic Backtracking)

## 📋 Changes Implemented
- [x] **Polymorphic State**: Introduced `StrategyType` (Standard, Correction, Relaxation) and `ValidationFeedback` with `target_fields`.
- [x] **Logic Resolver**: Implemented `select_strategy` mapping error patterns to retry strategies (e.g., Retry >= 2 -> Relaxation).
- [x] **Dynamic Prompting**: `Extractor` now adapts system prompts based on the strategy (e.g., injecting feedback or loosening constraints).
- [x] **Graph Wiring**: Connected `validate_content` -> `resolve_logic` -> `extract_metadata` loops.

## 🧪 Verification Results

### 1. Automated Tests
- **Unit Tests**:
    - `tests/unit/domain/ingestion/test_state_advanced.py`: ✅ Polymorphic State Transitions verified.
    - `tests/unit/infrastructure/brain/test_logic_selector.py`: ✅ Strategy Selection Logic verified.
    - `tests/unit/infrastructure/brain/test_prompt_mutation.py`: ✅ Dynamic Prompt Construction verified.

- **Integration Tests (BDD Scenarios)**:
    - `tests/integration/test_backtracking_bdd.py`:
        - **Scenario 1 (Partial Retry)**: Partial Retry logic verified (Validator Fail -> Correction Strategy -> Prompt w/ Fields).
        - **Scenario 2 (Relaxation)**: Constraint Relaxation verified (Repeated Fail -> Relaxation Strategy -> Looser Prompt).

### 2. Manual Verification
- N/A (Automated Scenarios cover the flow)

### 3. Evidence
- All tests passed.
