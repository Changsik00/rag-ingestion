# Task List: Spec-064

## Progress
- [x] Spec 번호 확정 및 브랜치 생성 (main에서 시작)
- [x] spec.md 작성
- [x] plan.md 작성
- [ ] task.md 작성
- [ ] User Plan Accept

---

## Task 1: Environment & Dependencies
### 1-1. Install LangFuse
- [x] `pyproject.toml`: `langfuse` 패키지 추가.
- [x] `uv lock` 및 Sync.
- [x] `.env.example`: LangFuse 설정 변수 추가.
- [x] Commit: `build(spec-064): add langfuse dependency`

### 1-2. Monitoring Infrastructure
- [x] `app/infrastructure/monitoring/langfuse_helper.py` 구현.
  - `get_callback_handler()` 팩토리 함수.
  - 환경변수 없을 때 `None` 반환 (Optional 모드).
- [x] Commit: `feat(spec-064): add langfuse helper infrastructure`

---

## Task 2: RAG Service Integration
### 2-1. RAG Nodes Refactoring (Callback Propagation)
- [x] `app/infrastructure/ai/rag_nodes.py` 수정.
  - `generate_answer`: `llm.ainvoke(..., config=config)`로 수정.
  - `_get_rerank_score`: `config` 인자 추가 및 `llm.agenerate`에 전파.
  - `rerank_results`: `_get_rerank_score` 호출 시 `config` 전달.
- [x] Commit: `refactor(spec-064): propagate runnable config in rag nodes`

### 2-2. Inject Callback in RAG Service
- [x] `app/domain/value_objects/rag_state.py`: `RAGResult` (또는 state)에 `trace_id`, `trace_url` 필드 추가 필요 여부 확인 (RAGResult는 `services/rag.py`에 정의됨).
- [x] `app/application/services/rag.py`:
  - `RAGResult` dataclass에 `trace_url`, `trace_id` 필드 추가.
  - `retrieve_and_generate`: `langfuse_helper` 사용하여 Handler 생성.
  - `graph.ainvoke` 호출 시 `config["callbacks"]`에 Handler 추가.
  - 결과 `RAGResult`에 Trace 정보 매핑.
- [x] Commit: `feat(spec-064): inject langfuse callback in rag pipeline`

---

## Task 3: Admin UI Integration
### 3-1. Display Trace Link in Playground
- [x] `admin/pages/4_RAG_Playground.py` 수정.
  - `st.session_state["rag_result"]`에서 `trace_url` 확인.
  - 답변 하단 또는 사이드바에 LangFuse 링크 버튼/뱃지 표시.
- [x] Manual Verification: 링크 동작 확인.
- [x] Commit: `feat(spec-064): add trace link to rag playground`

---

## Task 4: Documentation (Mechanism & Architecture)
### 4-1. Writer Feature Doc
- [x] `docs/features/observability.md` 작성.
  - **Mechanism Section**: SSE/WebSocket/Long Polling이 아닌 **Async HTTP Batch** 방식임을 명시.
  - **Diagram**: RAG 서비스와 LangFuse 서버 간의 "Push" 데이터 흐름 시각화 (Mermaid).
  - **Q&A Context**: 사용자가 오해했던 포인트(실시간 스트리밍)와 실제 구현(Deep Link)의 차이점 정리.
- [x] Commit: `docs(spec-064): add observability mechanism documentation`

---

## Task 5: PR Creation & Archiving
- [x] Code Quality Check: `uv run ruff check . --fix && uv run ruff format .`
- [x] Run Full Tests: `uv run pytest`
- [x] **Walkthrough 작성**: `specs/064-rag-observability-dashboard/walkthrough.md`
- [x] **PR Description 작성**: `specs/064-rag-observability-dashboard/pr_description.md`
- [x] **Archive Commit**: `docs(spec-064): archive walkthrough and pr description`
- [x] Create PR: `gh pr create`

## Summary
**총 Task**: 4개 Phase (Infra, Service, UI, Docs)
**예상 커밋 수**: 7개
**현재 진행**: Completed
