# Task List: Spec-029

## Progress
- [x] Spec 번호 확정 (029)
- [x] spec.md 작성
- [x] plan.md 작성
- [x] task.md 작성
- [x] 백로그 업데이트 (Note 추가)
- [x] User Plan Accept

## Task 1: Environment & Agent Core
### 1-1. TDD Warming up
- [x] Test Case 작성: `tests/unit/admin/test_admin_router.py`
- [x] Test 실행 (Fail): `uv run pytest tests/unit/admin/test_admin_router.py`
- [x] Commit: `test(spec-029): add router intent classification tests` (Merged into feat)

### 1-2. Implementation
- [x] 코드 구현: `app/admin/agents/admin_agent.py` (Router, Tools, Graph)
- [x] Test 실행 (Pass): `uv run pytest tests/unit/admin/test_admin_router.py`
- [x] Commit: `feat(spec-029): implement admin agent with langgraph`

## Task 2: Admin UI Integration
- [x] 코드 구현: `app/admin/pages/4_RAG_Playground.py` (Agent 연동)
- [x] Manual Check: Streamlit 실행 (`uv run streamlit run ...`)
- [x] Commit: `feat(spec-029): integrate agent into admin playground`

## Task 3: PR Creation
- [x] Code Quality Check: `uv run ruff check . --fix && uv run ruff format .`
- [x] Manual Verification: URL 수집 및 검색 시나리오 검증
- [x] Create PR: `gh pr create`

## Task 4: Post-Release Stabilization
- [x] Debugging: Fix Service Instantiation & Hybrid Search Wiring
- [x] Reliability: Fix Neo4j/Chroma Data Validation Errors
- [x] Tooling: Add Data Inspection Scripts & Pure Scraper API

## Summary
**총 Task**: 3개
**예상 커밋 수**: 4~5개
