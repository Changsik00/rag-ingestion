# Task Checklist: Spec 012 - Integration Test High Priority

## Progress

- [x] Spec 번호 확정 (012)
- [x] spec.md 작성
- [x] plan.md 작성
- [x] task.md 작성
- [x] 사용자 승인 완료
- [x] 브랜치 생성 및 구현

---

## Task 1: 브랜치 생성 및 준비

- [x] 브랜치 생성: `git checkout -b feature/012-integration-test-high-priority`
- [x] spec.md, plan.md, task.md 커밋
- [x] 커밋: `docs: add spec 012 - integration test high priority`

---

## Task 2: Integration Test 파일 작성

- [x] `tests/integration/bdd/test_high_priority_scenarios.py` 생성
- [x] Helper functions 작성:
  - [x] `wait_for_job_completion(job_id, timeout)`
  - [x] `get_job_status(job_id)`
- [x] 커밋: `test: add helper functions for high priority scenarios`

---

## Task 3: Test 1 - Invalid Job ID

- [x] `test_invalid_job_id_returns_404()` 작성
- [x] 테스트 실행 확인
- [x] 커밋: `test: add invalid job id returns 404 test`

---

## Task 4: Test 2 - Duplicate URL

- [x] `test_duplicate_url_sequential_ingestion()` 작성
- [x] 테스트 실행 확인
- [x] 커밋: `test: add duplicate url handling test`

---

## Task 5: 테스트 실행 및 검증

- [x] New Tests: `pytest tests/integration/bdd/test_high_priority_scenarios.py -v -m integration`
- [x] All Integration Tests: `pytest tests/integration/ -v -m integration`
- [x] All Tests: `pytest tests/ -v`
- [ ] Ruff: `ruff check tests/`
- [x] 모든 테스트 통과 확인 (79 passed, 6 failed 기존, 4 skipped)

---

## Task 6: 수동 검증 (선택)

- [ ] Invalid Job ID: `curl http://localhost:8000/jobs/non-existent-id`
- [ ] Duplicate URL: 같은 URL 두 번 수집
- [ ] Document 개수 확인

---

## Task 7: PR 준비 및 문서화

- [ ] `pr_description.md` 작성
- [ ] `remaining_scenarios.md` 업데이트 (완료된 시나리오 제거)
- [ ] 모든 변경사항 커밋
- [ ] 푸시: `git push origin feature/012-integration-test-high-priority`
- [ ] PR 생성

---

## Notes

- API는 이미 구현됨 (404 반환)
- 테스트만 추가하면 됨
- 중복 URL 정책: 현재 방식 유지 (Option A)
- 예상 소요 시간: ~1시간
