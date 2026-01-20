# Task List: Spec-023

## Progress
- [x] Spec 번호 확정 (023)
- [x] spec.md 작성
- [x] plan.md 작성
- [x] task.md 작성
- [x] 백로그 업데이트 (Note 추가)
- [x] User Plan Accept

## Task 1: Domain State Models
### 1-1. TDD Warming up (State Definition)
- [x] Test Case 작성: `tests/unit/test_reasoning_state.py`
- [x] Test 실행 (Fail): `uv run pytest tests/unit/test_reasoning_state.py`
- [x] Commit: `test(spec-023): add tests for backtracking context state`

### 1-2. Implementation
- [x] 코드 구현: `app/domain/ingestion/state.py`
    - `FailureHypothesis`, `DecisionTrace` TypedDict 정의
    - `IngestionState` 업데이트
- [x] Test 실행 (Pass): `uv run pytest tests/unit/test_reasoning_state.py`
- [x] Commit: `feat(spec-023): implement backtracking context state`

## Task 2: Infrastructure & Logic
### 2-1. Analysis Node Logic
- [x] Test Case 작성: `tests/unit/test_analysis_node.py`
- [x] 코드 구현: `app/infrastructure/brain/nodes.py` (analyze_failure)
- [x] Commit: `feat(spec-023): implement analyze_failure node logic`

### 2-2. Prompt Injection Logic
- [x] Test Case 작성: `tests/unit/test_prompt_injection.py`
- [x] 코드 구현: `app/infrastructure/brain/nodes.py` (construct_extraction_prompt)
- [x] Commit: `feat(spec-023): update prompt construction with reasoning context`

## Task 3: Graph Wiring
### 3-1. Graph Integration
- [x] Test Case 작성: `tests/integration/bdd/test_reasoning_flow.py`
- [x] 코드 구현: `app/infrastructure/brain/graph.py`
- [x] Commit: `feat(spec-023): wire analyze_failure node into graph`

## Task 4: PR Creation
- [x] Run Lint: `uv run ruff check . --fix`
- [x] Run Full Tests: `uv run pytest`
- [x] Create PR: `gh pr create --title "feat(spec-023): reasoning context and failure analysis"`

## Summary
**총 Task**: 8개
**예상 커밋 수**: 9개
