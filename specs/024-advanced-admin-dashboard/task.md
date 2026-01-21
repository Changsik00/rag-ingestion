# Task List: Spec-024

## Progress
- [x] Spec 번호 확정
- [x] spec.md 작성
- [x] plan.md 작성
- [x] task.md 작성
- [x] 백로그 업데이트 (Note 추가)
- [x] User Plan Accept

## Task 1: Environment & Main Dashboard
### 1-1. Dependencies & Setup (TDD)
- [x] Test: `tests/unit/admin/test_dashboard_config.py` (Config 로딩 테스트)
- [x] Implementation: `pyproject.toml` 업데이트 및 `app/admin/config.py` 생성
- [x] Implementation: `app/admin/dashboard.py` (Main Entry)
- [x] Verification: `streamlit run app/admin/dashboard.py` 정상 구동 확인
- [x] Commit: `build(spec-024): add streamlit dependencies and main dashboard`

## Task 2: Graph Explorer (Service TDD -> UI)
### 2-1. Graph Service Implementation
- [x] Test Case: `tests/unit/admin/test_graph_service.py` (Mock Neo4jResult)
    - `test_execute_cypher`
    - `test_get_presets`
    - `test_build_query` (Query Builder Logic)
- [x] Implementation: `app/admin/services/graph_service.py` w/ Presets
- [x] Test Run: `uv run pytest tests/unit/admin/test_graph_service.py`
- [x] Commit: `feat(spec-024): implement graph service with query builder logic`

### 2-2. Graph UI Binding
- [x] Implementation: `app/admin/pages/1_Graph_Explorer.py` (Presets/Builder UI 연결)
- [x] Manual Check: 버튼 클릭으로 쿼리 생성 및 그래프 렌더링 확인
- [x] Commit: `feat(spec-024): add graph explorer ui with visual query builder`

## Task 3: HITL & Trace (Service TDD -> UI)
### 3-1. LangGraph Service Implementation
- [/] Test Case: `tests/unit/admin/test_hitl_service.py`
    - `test_list_threads`
    - `test_get_thread_status` (State Parsing -> "Thinking", "Idle")
    - `test_resume_flag`
- [ ] Implementation: `app/admin/services/hitl_service.py`
- [ ] Test Run: `uv run pytest tests/unit/admin/test_hitl_service.py`
- [ ] Commit: `feat(spec-024): implement hitl service with detailed status parsing`

### 3-2. HITL & Trace UI
- [ ] Implementation: `app/admin/pages/2_HITL_Control.py` & `3_Trace_Viewer.py`
- [ ] Manual Check: 상태 배지 표시 및 Resume 동작 확인
- [ ] Commit: `feat(spec-024): add hitl control and trace viewer pages`

## Task 4: RAG Playground (Review Logic TDD -> UI)
### 4-1. Feedback Service Implementation
- [ ] Test Case: `tests/unit/admin/test_feedback_service.py`
    - `test_save_feedback`
- [ ] Implementation: `app/admin/services/feedback_service.py` (Log/DB 저장)
- [ ] Commit: `feat(spec-024): implement feedback service`

### 4-2. Playground UI
- [ ] Implementation: `app/admin/pages/4_RAG_Playground.py` w/ Thumbs Up/Down
- [ ] Manual Check: 채팅 및 피드백 저장 확인
- [ ] Commit: `feat(spec-024): add rag playground with feedback ui`

## Task 5: Final Review & PR
- [ ] Code Quality Check: `uv run ruff check . --fix && uv run ruff format .`
- [ ] Run Full Tests: `uv run pytest`
- [ ] Manual Walkthrough: 전체 페이지 기능 점검 및 스크린샷 캡처 (`walkthrough.md`)
- [ ] Create PR: `gh pr create --title "feat(spec-024): advanced admin dashboard" --body-file specs/024-advanced-admin-dashboard/pr_description.md`

## Summary
**총 Task**: 5개
**예상 커밋 수**: 6-8개
