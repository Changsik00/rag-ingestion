# Task List: Spec-042

## Progress
- [x] Spec 번호 확정 (042)
- [x] spec.md 작성
- [x] plan.md 작성
- [x] task.md 작성
- [ ] 백로그 업데이트 (Note 추가)
- [x] User Plan Accept

## Task 1: 인프라 계층 리셋 메서드 구현
### 1-1. TDD Warming up
- [x] Test Case 작성: `tests/unit/test_storage_reset.py` (Mock 기반)
- [x] Test 실행 (Fail): `uv run pytest tests/unit/test_storage_reset.py`
- [x] Commit: `test(spec-042): add unit tests for storage reset methods`

### 1-2. Implementation
- [x] Sqlite Reset 구현: `app/infrastructure/brain/adapter.py`
  - [x] Test Case 작성 (tests/unit/test_storage_reset.py)
  - [x] Test 실행 (Fail)
  - [x] 구현 및 Pass
- [x] Test 실행 (Pass): `uv run pytest tests/unit/test_storage_reset.py`
- [x] Commit: `feat(spec-042): implement database reset methods`

## Task 2: Admin API 및 서비스 구현
### 2-1. TDD Warming up
- [x] Test Case 작성: `tests/integration/test_integrity_api.py`
- [x] Test 실행 (Fail): `uv run pytest tests/integration/test_integrity_api.py`
- [x] Commit: `test(spec-042): add integration tests for reset api`

### 2-2. Implementation
- [x] IntegrityService 구현: `app/application/admin/integrity_service.py`
- [x] API Router 구현: `app/interfaces/api/v1/endpoints/admin/integrity.py`
- [x] App Wiring: `app/interfaces/api/v1/endpoints/admin/__init__.py` (Router 등록)
- [x] Test 실행 (Pass): `uv run pytest tests/integration/test_integrity_api.py`
- [x] Commit: `feat(spec-042): implement reset api and service`

## Task 3: Admin UI 구현 (Playground)
### 3-1. Implementation
- [x] Danger Zone UI 추가: `admin/pages/4_RAG_Playground.py`
- [x] Session State Persistence 로직 추가
- [x] UI 기능 수동 검증 (Implemented)
- [x] Commit: `feat(spec-042): add reset ui and improve persistence`

## Task 4: PR Creation
- [x] Code Quality Check: `uv run ruff check . --fix && uv run ruff format .`
- [x] Tests: `uv run pytest`
- [x] PR Description 작성: `specs/042-db-reset-and-admin-ui/pr_description.md`
- [x] Create PR: `gh pr create --title "feat(spec-042): implement db reset arch and admin ui" --body-file specs/042-db-reset-and-admin-ui/pr_description.md`

## Summary
**총 Task**: 4개
**예상 커밋 수**: 7개
