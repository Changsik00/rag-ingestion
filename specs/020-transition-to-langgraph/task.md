# Task List: Spec 020 Transition to LangGraph

## Progress
- [x] Spec 번호 확정 (Completed: 020)
- [x] spec.md 작성
- [x] plan.md 작성
- [x] task.md 작성
- [x] 백로그 업데이트 (Note 추가)
- [x] User Plan Accept

## Task 0: Architecture Documentation (ADR)
### 0-1. Decision Record
### 0-1. Architecture Documentation
- [x] ADR 작성: `docs/architecture_decisions.md` (DAG to Graph 전환 결정, Mermaid 포함)
- [x] Spec Update: `specs/020-transition-to-langgraph/spec.md` (History 복원)
- [x] Docs Link: `docs/architecture.md`에 Link 추가

## Task 1: LangGraph Setup & State Definition
### 1-1. Dependency & TDD Setup
- [x] Install `langgraph`: `uv add langgraph`
- [x] Test Case 작성: `tests/unit/test_ingestion_state.py` (State 데이터 구조 검증)
- [x] Test 실행 (Fail)
- [x] Fail)
- [x] Commit: `test(spec-020): add test for ingestion state`

### 1-2. Define IngestionState
- [x] 코드 구현: `app/domain/ingestion/state.py` (TypedDict for Document, Metadata, Steps)
- [x] Test 실행 (Pass)
- [x] Commit: `feat(spec-020): define IngestionState`

## Task 2: Core Graph Implementation
### 2-1. Node Implementation
- [x] Test Case 작성: `tests/unit/test_graph_nodes.py` (각 노드별 단위 테스트)
- [x] 코드 구현: `app/infrastructure/brain/nodes.py` (Extract, Validate, Transform nodes)
- [x] Test 실행 (Pass)
- [x] Commit: `feat(spec-020): implement basic graph nodes`

### 2-2. Graph Construction
- [x] Test Case 작성: `tests/unit/test_ingestion_graph.py` (Graph 흐름 검증)
- [x] 코드 구현: `app/infrastructure/brain/graph.py` (StateGraph 구성)
- [x] Test 실행 (Pass)
- [x] Commit: `feat(spec-020): construct ingestion state graph`

## Task 3: Service Integration
### 3-1. Adapter Refactoring
- [x] Test Case 작성: `tests/integration/tdd/test_langgraph_adapter.py`
- [x] 코드 구현: `app/infrastructure/brain/adapter.py` (기존 LangChainAdapter 대체/래핑)
- [x] Test 실행 (Pass)
- [x] Commit: `refactor(spec-020): integrate langgraph adapter`

### 3-2. Verify Async Pipeline
- [x] Integration Test 실행: `pytest tests/integration/bdd/test_success_flows.py`
- [x] Commit: `test(spec-020): verify async pipeline with langgraph`

## Task 4: PR Creation
- [x] Run Full Tests: `uv run pytest`
- [x] Create PR: `gh pr create`

## Summary
**총 Task**: 8개
**예상 커밋 수**: 8~10개
