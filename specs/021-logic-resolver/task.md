# Task List: Spec-021 (Advanced Backtracking)

## Progress
- [x] Spec 번호 확정
- [x] spec.md 작성 (Advanced & Polymorphic)
- [x] plan.md 작성 (Test Scenarios Included)
- [x] task.md 작성 (Expanded Testing)
- [x] pr_description.md 작성 (Draft)
- [x] User Plan Accept

## Task 1: Advanced State Infrastructure
### 1-1. Branch & State Definition
- [x] Feature Branch 생성: `feature/spec-021-logic-resolver`
- [x] `IngestionState` Refactoring:
    - [x] `StrategyType` Enum (4 strategies)
    - [x] `ValidationFeedback` with `target_fields`
    - [x] `ValidationConstraints` model
- [x] **Unit Test**: `tests/unit/domain/ingestion/test_state_advanced.py` (State Transitions)
- [x] Commit: `feat(spec-021): implement advanced state architecture`

## Task 2: Intelligent Logic Resolver (TDD)
### 2-1. Logic Unit Tests
- [x] **Create Test**: `tests/unit/infrastructure/brain/test_logic_selector.py`
    - [x] Test: Error -> `CORRECTION` mapping
    - [x] Test: Repeated Error -> `RELAXATION` mapping
    - [x] Test: Schema Mismatch -> `REINTERPRETATION` mapping
- [x] Implement `select_strategy` in `logic.py`
- [x] Commit: `feat(spec-021): implement logic selector with unit tests`

## Task 3: Context-Aware Extractor (TDD)
### 3-1. Prompt Mutation Unit Tests
- [x] **Create Test**: `tests/unit/infrastructure/brain/test_prompt_mutation.py`
    - [x] Test: `CORRECTION` strategy -> Check "Fix fields" prompt
    - [x] Test: `RELAXATION` strategy -> Check "Loosen rules" prompt
- [x] Implement Prompt Logic in `nodes.py`
- [x] Commit: `feat(spec-021): implement partial retry prompting with unit tests`

## Task 4: Integration & BDD Scenarios
### 4-1. Graph Wiring
- [x] Wire Conditional Edges in `graph.py`
- [x] Commit: `feat(spec-021): wire up conditional edges`

### 4-2. BDD Scenario Implementation
- [x] **Create BDD Test**: `tests/integration/bdd/test_logic_resolver.py`
    - [x] **Scenario 1 (Partial Retry)**: 
        - Given: Validator fails on 'title'
        - When: Graph runs
        - Then: Logic selects CORRECTION & Prompt requests 'title' fix
    - [x] **Scenario 2 (Relaxation)**: 
        - Given: Validator fails repeatedly on 'entities'
        - When: Retry count hits threshold
        - Then: Logic selects RELAXATION & Prompt requests looser rules
- [x] Run Scenarios & Verify Pass
- [x] Commit: `test(spec-021): add BDD integration scenarios`

## Task 5: Final Review & Delivery
- [x] **Linting & Quality Check**
    - [x] Run Ruff: `uv run ruff check . --fix`
    - [x] Verify No Errors
- [x] **Documentation & Task Update**
    - [x] Update `walkthrough.md` with Evidence
    - [x] Update `backlog/queue.md` (Mark Spec 021 as Complete)
    - [x] Finalize `pr_description.md`
- [x] **PR Creation**
    - [x] `gh pr create` using description template

## Task 6: Refinement (User Feedback)
- [x] **Test Restructuring**
    - [x] Move to `tests/integration/bdd/test_logic_resolver.py`
    - [x] Standardize Naming (should_...)
    - [x] Expand Scenarios coverage
- [x] **Documentation Polish**
    - [x] Enhance `pr_description.md` details
    - [x] Cross-check Task Checklist

## Summary
**현재 진행**: 완료 (PR 머지됨)
