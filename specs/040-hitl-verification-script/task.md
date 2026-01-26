# Task List: Spec-040

## Progress
- [x] Spec 번호 확정 (040)
- [x] spec.md 작성
- [x] plan.md 작성
- [x] task.md 작성
- [x] 백로그 업데이트 (Phase 4 이동)
- [x] User Plan Accept

## Task 1: HITL 검증 스크립트 작성
### 1-1. TDD Warming up (Skeleton & Execution Check)
- [x] 스크립트 파일 생성: `scripts/verify_hitl_real.py` (Skeleton)
- [x] 실행 확인 (Basic Run): `uv run python scripts/verify_hitl_real.py`
- [x] Commit: `test(spec-040): add script skeleton`

### 1-2. Implementation (Logic)
- [x] 코드 구현: `scripts/verify_hitl_real.py` (Graph Init, Checkpointer, Interrupt/Resume)
- [x] 검증 실행 (Manual Verification): `uv run python scripts/verify_hitl_real.py`
- [x] Commit: `feat(spec-040): implement hitl verification logic`

## Task 2: Fix Admin HITL Toggle (Scope Expanded)
### 2-1. Backend Logic Update
- [x] State Update: `IngestionState`에 `hitl_enabled` 필드 추가
- [x] Graph Logic: `route_after_validation`에서 `hitl_enabled` 확인 로직 추가
- [x] API Update: `POST /rag/sessions/{id}/ask` payload에 `hitl_enabled` 파라미터 추가

### 2-2. Frontend Integration
- [x] UI Logic: `4_RAG_Playground.py`에서 `hitl_enabled` 상태를 API 호출 시 전달

## Task 3: PR Creation (Updated)
- [x] Update Verification Script: `scripts/verify_hitl_real.py`에 Toggle 테스트 추가
- [x] Code Quality Check: `uv run ruff check . --fix && uv run ruff format .`
- [x] Run Full Tests: `uv run pytest`
- [x] Update PR: 기존 PR 업데이트 (`git push --force` or just push)

## Summary
**총 Task**: 3개
**예상 커밋 수**: 5개
