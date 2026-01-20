# Task List: Spec 020 Transition to LangGraph

## Progress
- [ ] Spec 번호 확정 (Completed: 020)
- [ ] spec.md 작성
- [ ] plan.md 작성
- [ ] task.md 작성
- [ ] 백로그 업데이트 (Note 추가)
- [ ] User Plan Accept

## Task 0: Architecture Documentation (ADR)
### 0-1. Decision Record
- [x] Create Directory: `docs/architecture_decisions`
- [x] Write ADR: `docs/architecture_decisions/001_dag_to_graph_transition.md`
    - Context: Why DAG is limited (No cycles, Stateless)
    - Decision: Adopt State Graph (LangGraph)
    - Visuals: Mermaid Diagrams (Linear DAG vs State Machine)
- [x] Update `docs/architecture.md`: Link to new ADR

### 0-2. History Archiving
- [x] Create Directory: `docs/history`
- [x] Move `spec.md` history section to `docs/history/020-decision-record.md`

## Task 1: LangGraph Setup & State Definition
### 1-1. Dependency & TDD Setup
- [ ] Install `langgraph`: `uv add langgraph`
- [ ] Test Case 작성: `tests/unit/test_ingestion_state.py` (State 데이터 구조 검증)
- [ ] Test 실행 (Fail)
- [ ] Commit: `test(spec-020): add test for ingestion state`

### 1-2. Define IngestionState
- [ ] 코드 구현: `app/domain/ingestion/state.py` (TypedDict for Document, Metadata, Steps)
- [ ] Test 실행 (Pass)
- [ ] Commit: `feat(spec-020): define IngestionState`

## Task 2: Core Graph Implementation
### 2-1. Node Implementation
- [ ] Test Case 작성: `tests/unit/test_graph_nodes.py` (각 노드별 단위 테스트)
- [ ] 코드 구현: `app/infrastructure/brain/nodes.py` (Extract, Validate, Transform nodes)
- [ ] Test 실행 (Pass)
- [ ] Commit: `feat(spec-020): implement basic graph nodes`

### 2-2. Graph Construction
- [ ] Test Case 작성: `tests/unit/test_ingestion_graph.py` (Graph 흐름 검증)
- [ ] 코드 구현: `app/infrastructure/brain/graph.py` (StateGraph 구성)
- [ ] Test 실행 (Pass)
- [ ] Commit: `feat(spec-020): construct ingestion state graph`

## Task 3: Service Integration
### 3-1. Adapter Refactoring
- [ ] Test Case 작성: `tests/integration/tdd/test_langgraph_adapter.py`
- [ ] 코드 구현: `app/infrastructure/brain/langgraph_adapter.py` (기존 LangChainAdapter 대체/래핑)
- [ ] Test 실행 (Pass)
- [ ] Commit: `refactor(spec-020): integrate langgraph adapter`

### 3-2. Verify Async Pipeline
- [ ] Integration Test 실행: `pytest tests/integration/bdd/test_success_flows.py`
- [ ] Commit: `test(spec-020): verify async pipeline with langgraph`

## Task 4: PR Creation
- [ ] Run Full Tests: `uv run pytest`
- [ ] Create PR: `gh pr create`

## Summary
**총 Task**: 8개
**예상 커밋 수**: 8~10개
