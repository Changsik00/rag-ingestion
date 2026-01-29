# Task List: Spec 048

## Progress
- [x] Spec 번호 확정 및 브랜치 생성
- [x] spec.md 작성
- [x] plan.md 작성
- [x] task.md 작성
- [x] 백로그 업데이트 (Note 추가)
- [x] User Plan Accept

---

## Task 1: Foundation & Reranker Logic
### 1-1. Branch Creation
- [x] 브랜치 생성: `git checkout -b feature/048-rag-precision`

### 1-2. Reranker Prompt & Schema
- [x] Reranker 전용 프롬프트 작성: `app/domain/services/prompts/reranker.py`
- [x] `RAGGraphState` 업데이트 (필요시): `app/domain/rag/state.py`

### 1-3. TDD: Reranker Node
- [x] Test Case 작성: `tests/unit/test_rag_reranker.py` (리랭킹 점수 부여 로직 검증)
- [x] Test 실행 (Fail)
- [x] Commit: `test(spec-048): add failing test for reranker node`

---

## Task 2: Graph Integration & Filtering
### 2-1. Reranker Node Implementation
- [x] `RAGService.rerank_results` 노드 함수 구현
- [x] 유사도 및 리랭킹 점수 기반 필터링 로직 개발

### 2-2. Graph Workflow Update
- [x] `_create_graph()`에 신규 노드 및 엣지 연결
- [x] 검색(Retrieve) → 리랭킹(Rerank) → 생성(Generate) 흐름 완성

### 2-3. Verification
- [x] Test 실행 (Pass)
- [x] 통합 테스트 작성 및 실행: `tests/integration/test_rag_precision.py`

---

## Task 3: PR Creation & Archiving (Mandatory)
- [x] Code Quality Check: `uv run ruff check . --fix && uv run ruff format .`
- [x] Run Full Tests: `uv run pytest`
- [x] **Walkthrough 작성**: `specs/048-rag-precision/walkthrough.md`
- [x] **PR Description 작성**: `specs/048-rag-precision/pr_description.md`
- [x] **Archive Commit**: `docs(spec-048): archive walkthrough and pr description`
- [x] Create PR: `gh pr create --title "feat(spec-048): rag precision refinement" --body-file specs/048-rag-precision/pr_description.md`

## Task 4: Fix RAG Timeout (Async LLM Refactoring)
### 4-1. Interface Refactoring
- [/] `app/domain/interfaces/llm.py`에 비동기 메서드 추가

### 4-2. Infrastructure Implementation
- [ ] `app/infrastructure/llm/langchain_adapter.py` 비동기 구현 (`ainvoke`)

### 4-3. Workflow Optimization
- [ ] `app/infrastructure/rag/nodes.py`의 `rerank_results` 및 주요 노드 비동기화

### 4-4. Verification
- [ ] `uv run pytest` (Unit & Integration)
- [ ] Admin UI에서 타임아웃 여부 재확인
- [ ] Commit: `fix(spec-048): implement async llm adapter to fix rag timeout`

## Summary
**총 Task**: 4개  
**예상 커밋 수**: 8~10개  
**현재 진행**: Execution (Fixing Timeout)
