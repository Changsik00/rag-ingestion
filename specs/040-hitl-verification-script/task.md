# Task List: Spec-040

## Progress
- [x] Spec 번호 확정 (040)
- [x] spec.md 작성
- [x] plan.md 작성
- [x] task.md 작성
- [x] 백로그 업데이트 (Phase 4 이동)
- [ ] User Plan Accept

## Task 1: HITL 검증 스크립트 작성
### 1-1. TDD Warming up
- [ ] Test Case 작성: `tests/tooling/test_verify_hitl_real.py`
- [ ] Test 실행 (Fail): `uv run pytest tests/tooling/test_verify_hitl_real.py -v`
- [ ] Commit: `test(spec-040): add test cases for HITL verification script`

### 1-2. Implementation
- [ ] 스크립트 구현: `scripts/verify_hitl_real.py`
- [ ] Test 실행 (Pass): `uv run pytest tests/tooling/test_verify_hitl_real.py -v`
- [ ] Commit: `feat(spec-040): implement real-world HITL verification script`

## Task 2: 실제 시나리오 검증
### 2-1. TDD Warming up
- [ ] Integration Test 작성: `tests/integration/test_hitl_scenario.py`
- [ ] Test 실행 (Fail): `uv run pytest tests/integration/test_hitl_scenario.py -v`
- [ ] Commit: `test(spec-040): add integration test for HITL scenario`

### 2-2. Implementation
- [ ] 시나리오 검증 실행: `uv run python scripts/verify_hitl_real.py`
- [ ] Test 실행 (Pass): `uv run pytest tests/integration/test_hitl_scenario.py -v`
- [ ] Commit: `feat(spec-040): verify HITL scenario with real LLM`

## Task 3: Documentation & PR
### 3-1. Documentation
- [ ] README 업데이트: 스크립트 사용법 추가
- [ ] Commit: `docs(spec-040): add HITL verification script usage to README`

### 3-2. PR Creation
- [ ] Branch: `feature/040-hitl-verification-script`
- [ ] PR 생성: `pr_description.md` 작성
- [ ] Review 요청
