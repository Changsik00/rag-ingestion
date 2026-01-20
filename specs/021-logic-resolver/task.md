# Task List: Spec-021 (Advanced Backtracking)

## Progress
- [x] Spec 번호 확정
- [x] spec.md 작성 (Advanced & Polymorphic)
- [x] plan.md 작성 (Test Scenarios Included)
- [x] task.md 작성 (Expanded Testing)
- [x] pr_description.md 작성 (Draft)
- [ ] User Plan Accept

## Task 1: Advanced State Infrastructure
### 1-1. Branch & State Definition
- [ ] Feature Branch 생성: `feature/spec-021-logic-resolver`
- [ ] `IngestionState` Refactoring:
    - [ ] `StrategyType` Enum (4 strategies)
    - [ ] `ValidationFeedback` with `target_fields`
    - [ ] `ValidationConstraints` model
- [ ] **Unit Test**: `tests/unit/domain/ingestion/test_state_advanced.py` (State Transitions)
- [ ] Commit: `feat(spec-021): implement advanced state architecture`

## Task 2: Intelligent Logic Resolver (TDD)
### 2-1. Logic Unit Tests
- [ ] **Create Test**: `tests/unit/infrastructure/brain/test_logic_selector.py`
    - [ ] Test: Error -> `CORRECTION` mapping
    - [ ] Test: Repeated Error -> `RELAXATION` mapping
    - [ ] Test: Schema Mismatch -> `REINTERPRETATION` mapping
- [ ] Implement `select_strategy` in `logic.py`
- [ ] Commit: `feat(spec-021): implement logic selector with unit tests`

## Task 3: Context-Aware Extractor (TDD)
### 3-1. Prompt Mutation Unit Tests
- [ ] **Create Test**: `tests/unit/infrastructure/brain/test_prompt_mutation.py`
    - [ ] Test: `CORRECTION` strategy -> Check "Fix fields" prompt
    - [ ] Test: `RELAXATION` strategy -> Check "Loosen rules" prompt
- [ ] Implement Prompt Logic in `nodes.py`
- [ ] Commit: `feat(spec-021): implement partial retry prompting with unit tests`

## Task 4: Integration & BDD Scenarios
### 4-1. Graph Wiring
- [ ] Wire Conditional Edges in `graph.py`
- [ ] Commit: `feat(spec-021): wire up conditional edges`

### 4-2. BDD Scenario Implementation
- [ ] **Create BDD Test**: `tests/integration/test_backtracking_bdd.py`
    - [ ] **Scenario 1 (Partial Retry)**: 
        - Given: Validator fails on 'title'
        - When: Graph runs
        - Then: Logic selects CORRECTION & Prompt requests 'title' fix
    - [ ] **Scenario 2 (Relaxation)**: 
        - Given: Validator fails repeatedly on 'entities'
        - When: Retry count hits threshold
        - Then: Logic selects RELAXATION & Prompt requests looser rules
- [ ] Run Scenarios & Verify Pass
- [ ] Commit: `test(spec-021): add BDD integration scenarios`

## Task 5: Final Review & Delivery
- [ ] **Linting & Quality Check**
    - [ ] Run Ruff: `uv run ruff check . --fix`
    - [ ] Verify No Errors
- [ ] **Documentation & Task Update**
    - [ ] Update `walkthrough.md` with Evidence
    - [ ] Update `backlog/queue.md` (Mark Spec 021 as Complete)
    - [ ] Finalize `pr_description.md`
- [ ] **PR Creation**
    - [ ] `gh pr create` using description template

## Summary
**총 Task**: 5개 그룹
**예상 커밋 수**: 약 12~14개
