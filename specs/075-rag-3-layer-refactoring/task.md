# Task List: Spec 075

## Progress
- [x] Spec 번호 확정 및 브랜치 생성
- [x] spec.md 작성
- [x] plan.md 작성
- [x] task.md 작성
- [x] 백로그 업데이트 (Note 추가)
- [x] User Plan Accept

---

## Task 1: Brain Layer Refactoring (Week 1)
### 1-1. Brain Components Structure
- [x] Create `app/domain/rag/brain/` directory
- [x] Create `app/domain/rag/brain/service.py` (Intent Classifier, Query Rewriter logic)
- [x] Test: `tests/unit/domain/rag/brain/test_service.py`
- [x] Verify: Brain logic (classify_intent) works independently

### 1-2. Port Logic to Brain Service
- [x] Port `classify_intent` from `rag_nodes.py`
- [x] Port `IntentClassifier` related logic
- [x] Port `QueryRewriter` logic from `rag_nodes.py`
- [x] Unit Test passing
- [x] Commit: `refactor(spec-075): separate brain layer`

---

## Task 2: Retrieval Layer Refactoring (Week 2)
### 2-1. Retrieval Components Structure
- [x] Create `app/infrastructure/rag/retrieval/` directory
- [x] Create `app/infrastructure/rag/retrieval/service.py` (Hybrid Search logic)
- [x] Test: `tests/infrastructure/rag/retrieval/test_service.py`

### 2-2. Port Logic to Retrieval Service
- [x] Port `retrieve_hybrid` from `rag_nodes.py`
- [x] Port `_search_vector`, `_search_keyword`, `_search_graph` helpers
- [x] Unit Test passing (Mock DB Repos)
- [x] Commit: `refactor(spec-075): separate retrieval layer`

---

## Task 3: Orchestration Layer Refactoring (Week 3)
### 3-1. Orchestration Components Structure
- [x] Create `app/application/rag/orchestration/` directory
- [x] Create `app/application/rag/orchestration/service.py` (Main Orchestrator)
- [x] Create `app/domain/rag/brain/answer_generator.py` (LLM Answer Logic)
- [x] Create `app/domain/rag/brain/reranker.py` (Reranking Logic)
- [x] Test: `tests/application/rag/orchestration/test_service.py`

### 3-2. Wiring Components (Logic Migration)
- [x] Implement `RAGOrchestrator` class
- [x] Wiring: Brain -> Retrieval -> Brain (Rerank/Generate)
- [x] Port `generate_answer` logic to `AnswerGenerator`
- [x] Port `rerank` logic to `Reranker`
- [x] Unit Test passing (Mock ALL dependencies)
- [x] Commit: `refactor(spec-075): separate orchestration layer`

---

## Task 4: LangGraph Integration (Week 4)
### 4-1. LangGraph Refactoring
- [x] Create `app/infrastructure/ai/rag_graph_v2.py` (or update existing)
- [x] Integrate `RAGOrchestrator` into the graph nodes
- [x] Verify State Flow (Input -> Brain -> Retrieval -> Orchestrator -> Output)
- [x] Integration Test: Verify end-to-end flow with mocks

### 4-2. Cleanup & Verification
- [x] `app/infrastructure/ai/rag_nodes.py` (Legacy) removal
- [x] Run full test suite (Unit + Integration)
- [x] Update Architecture Documents (ADR)
- [x] Final Cleanup: Unused imports, comments

---

## Task 5: PR Creation & Archiving (Mandatory)
<!-- 이 단계는 모든 작업 완료 후 수행합니다. -->
- [x] Code Quality Check: `uv run ruff check . --fix && uv run ruff format .`
- [x] Run Full Tests: `uv run pytest`
- [x] **Walkthrough 작성**: `specs/075-rag-3-layer-refactoring/walkthrough.md`
- [x] **PR Description 작성**: `specs/075-rag-3-layer-refactoring/pr_description.md` (템플릿 준수)
- [x] **Archive Commit**: 위 파일을 `specs/`에 커밋 (`docs(spec-075): archive walkthrough and pr description`)
- [ ] Create PR: `gh pr create --title "refactor: RAG 3-Layer Architecture (Spec 075)" --body-file specs/075-rag-3-layer-refactoring/pr_description.md`

## Summary
**총 Task**: 5 Phases
**현재 진행**: Task 5 (PR Creation phase - Walkthrough done)
