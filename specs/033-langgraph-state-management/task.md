# Task List: Spec 033 - LangGraph State Management

## Progress
- [x] Spec 번호 확정
- [x] spec.md 작성
- [x] plan.md 작성
- [x] task.md 작성
- [x] 백로그 업데이트 (Note 추가)
- [x] User Plan Accept
- [x] Feature 브랜치 생성: `feature/033-langgraph-state-management`

---

## Task 1: RAG Domain Layer (State 정의)

### 1-1. Domain Structure Setup
- [x] 디렉토리 생성: `app/domain/rag/`
- [x] `__init__.py` 생성
- [x] Commit: `chore(spec-033): create rag domain package`

### 1-2. State Schema Definition
- [x] `app/domain/rag/state.py` 작성 (RAGGraphState TypedDict)
- [x] Type hints 및 Docstring 작성
- [x] Commit: `feat(spec-033): define RAGGraphState schema`

---

## Task 2: RAG Infrastructure Layer (Nodes \u0026 Graph Builder)

### 2-1. TDD Warming up - Nodes
- [x] Test Case 작성: `tests/unit/infrastructure/rag/test_rag_nodes.py` (5개 시나리오)
- [x] Test 실행 (Fail): `uv run pytest tests/unit/infrastructure/rag/test_rag_nodes.py -v`
- [x] Commit: `test(spec-033): add rag nodes unit tests`

### 2-2. Implementation - Nodes
- [x] 디렉토리 생성: `app/infrastructure/rag/`
- [x] `app/infrastructure/rag/nodes.py` 구현 (RAGNodes 클래스)
  - `classify_intent()` - Intent + Query Rewrite
  - `route_decision()` - Intent → Filters 변환
  - `retrieve_hybrid()` - Parallel Search
  - `generate_answer()` - LLM Generation
- [x] Test 실행 (Pass): `uv run pytest tests/unit/infrastructure/rag/test_rag_nodes.py -v`
- [x] Commit:  `feat(spec-033): implement rag nodes business logic`

### 2-3. Implementation - Graph Builder
- [x] `app/infrastructure/rag/graph.py` 구현 (RAGGraphBuilder 클래스)
- [x] Linear Pipeline (4 nodes) 구성
- [x] Checkpointer 통합
- [x] Commit: `feat(spec-033): implement rag graph builder`

---

## Task 3: RAGService 리팩토링

### 3-1. TDD - Integration Test 준비
- [x] Test Case 작성: `tests/integration/bdd/test_rag_graph_flow.py` (3개 시나리오)
- [x] Test 실행 (Skip): `uv run pytest tests/integration/bdd/test_rag_graph_flow.py -v`
- [x] Commit: `test(spec-033): add rag graph integration tests`

### 3-2. Implementation - RAGService 전환
- [x] `app/domain/services/rag_service.py` 수정
  - Constructor에 `graph: CompiledStateGraph` 주입
  - `retrieve_and_generate()` → Graph Invocation으로 변경
  - `_state_to_result()` 헬퍼 메서드 추가
- [x] 기존 헬퍼 메서드를 RAGNodes로 이동 (코드 정리)
- [x] Test 실행 (Pass): `uv run pytest tests/integration/bdd/test_rag_graph_flow.py -v`
- [x] Commit: `refactor(spec-033): migrate rag service to langgraph`

---

## Task 4: Dependency Injection 업데이트

### 4-1. Implementation
- [x] `app/interfaces/api/dependencies.py` 수정
  - `get_rag_nodes()` 추가
  - `get_rag_graph_builder()` 추가
  - `get_rag_service()` 리팩토링 (Graph Builder 주입)
- [x] Commit: `feat(spec-033): update di for rag graph components`

---

## Task 5: 기존 테스트 회귀 수정

### 5-1. Test Compatibility Fix
- [ ] `tests/integration/bdd/test_rag_service.py` 수정 (State 기반 동작 확인)
- [ ] 기타 RAGService 의존 테스트 확인 및 수정
- [ ] Full Test Suite 실행: `uv run pytest -v`
- [ ] Commit: `test(spec-033): update existing rag tests for graph compatibility`

---

## Task 6: Admin Dashboard 연동 (Optional - State Snapshot View)

### 6-1. Implementation
- [ ] `app/admin/pages/4_RAG_Playground.py` 수정
  - "🔍 RAG State Snapshot" Expander 추가
  - State의 `user_intent`, `filters`, `rewritten_query` 표시
- [ ] Manual Verification (Streamlit 로컬 테스트)
- [ ] Commit: `feat(spec-033): add state snapshot view to admin dashboard`

---

## Task 7: Documentation

### 7-1. Architecture Documentation
- [ ] `docs/architecture/rag_pipeline.md` 신규 작성
  - LangGraph 기반 RAG 파이프라인 설명
  - State Schema 문서화
  - Graph Flow 다이어그램 (Mermaid)
- [ ] Commit: `docs(spec-033): add rag pipeline architecture documentation`

---

## Task 8: PR Creation

- [ ] Code Quality: `uv run ruff check . --fix && uv run ruff format .`
- [ ] Full Tests: `uv run pytest -v`
- [ ] Walkthrough 작성: `specs/033-langgraph-state-management/walkthrough.md`
- [ ] PR Description 작성: `specs/033-langgraph-state-management/pr_description.md`
- [ ] Create PR: `gh pr create --title "feat(spec-033): langgraph state management for rag pipeline" --body-file specs/033-langgraph-state-management/pr_description.md`

---

## Summary

**총 Task**: 8개  
**예상 커밋 수**: 13개  
**현재 진행**: Planning 완료 (Plan Accept 대기)
