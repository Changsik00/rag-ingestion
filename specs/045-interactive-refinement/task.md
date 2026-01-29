# Task List: Spec-045

## Progress
- [x] Spec 번호 확정 (045)
- [x] spec.md 작성
- [x] plan.md 작성
- [x] task.md 작성 (Template 적용)
- [x] 백로그 업데이트
- [x] User Plan Accept

## Task 1: Backend Implementation (AdminAgent)
### 1-1. State Schema & Ambiguity Detection
- [x] Test Case 작성: `tests/unit/test_admin_agent_clarification.py` (State 검증)
- [x] `app/domain/services/admin_agent.py` 수정: `AdminState`에 `draft_content`, `is_clarification` 추가
- [x] `router_node` 수정: 프롬프트에 Missing Slot 감지 로직 추가
- [x] Test 실행 및 Pass 확인: `uv run pytest tests/unit/test_admin_agent_clarification.py`
- [x] Commit: `feat(spec-045): update admin state and router for clarification`

### 1-2. Clarify Node & Graph Wiring
- [x] `clarify_node` 구현: 역질문 메시지 생성 로직
- [x] `build_workflow` 수정: `router` -> `clarify` (Conditional Edge) 연결
- [x] `clarify` -> `END` 연결 (Interrupt 설정)
- [x] Test 실행: Graph Routing 검증
- [x] Commit: `feat(spec-045): implement clarify node and graph wiring`

## Task 2: Frontend Implementation (Playground)
### 2-1. Draft Editor (Canvas) & Clarification UI
- [x] `admin/pages/4_RAG_Playground.py` 수정: `draft_content` 감지 시 `st.text_area` 렌더링
- [x] `admin/pages/4_RAG_Playground.py` 수정: `is_clarification` 상태 시각적 강조 UI
- [x] Resume Logic 구현: 수정된 Content를 API로 전송
- [x] Manual Verification: Playground에서 UI 렌더링 확인 (Syntax Check 완료)
- [x] Commit: `feat(spec-045): add draft editor and clarification ui`

## Task 3: Verification & Documentation
### 3-1. Verification Script
- [x] Test Case 작성: `tests/unit/test_admin_agent_clarification.py` (Script 대안으로 Unit Test 강화)
- [x] Scenario A: Ambiguity -> Clarification Loop 검증 (Unit Test)
- [x] Scenario B: Draft -> Feedback Loop 검증 (Unit Test)
- [x] Commit: `test(spec-045): add unit tests for clarification and feedback loop`

### 3-2. Documentation
- [x] `docs/features/hitl_interactive.md` 작성 (Optional: Spec 문서로 대체)

## Task 4: PR Creation
- [x] Code Quality Check: `uv run ruff check . --fix && uv run ruff format .`
- [x] Test Suite 실행: `uv run pytest` (전체 테스트 확인)
- [x] PR 생성: `gh pr create` (Body는 `specs/045-interactive-refinement/pr_description.md` 내용 사용)

## Summary
**총 Task**: 4개 (Backend, Frontend, Vertification, PR)
**예상 커밋 수**: 5~6개
