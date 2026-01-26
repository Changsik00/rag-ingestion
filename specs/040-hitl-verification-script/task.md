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

## Task 2: PR Creation
- [x] Code Quality Check: `uv run ruff check . --fix && uv run ruff format .`
- [ ] Run Full Tests: `uv run pytest`
- [ ] Create PR: `gh pr create --title "feat(spec-040): real-world hitl verification script" --body-file specs/040-hitl-verification-script/pr_description.md`

## Summary
**총 Task**: 2개
**예상 커밋 수**: 2개
