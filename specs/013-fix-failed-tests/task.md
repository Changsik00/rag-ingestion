# Task Checklist: Spec 013 - Fix Failed Tests

## Progress

- [ ] Spec 번호 확정 (013)
- [ ] spec.md 작성
- [ ] plan.md 작성
- [ ] task.md 작성
- [ ] 사용자 승인 대기
- [ ] 브랜치 생성 및 구현 시작

---

## Task 1: 브랜치 생성 및 Spec 문서 커밋

- [ ] 브랜치 생성: `git checkout -b feature/013-fix-failed-tests`
- [ ] 브랜치 확인: `git branch --show-current`
- [ ] Spec 문서 커밋: `git add specs/013-fix-failed-tests/ && git commit -m "docs: add spec 013 - fix failed tests"`

---

## Task 2: DI 테스트 분석 및 수정 전략 결정

- [ ] DI 테스트 실행하여 에러 메시지 확인
  - `pytest tests/integration/tdd/test_dependency_injection.py -v`
- [ ] `app/interfaces/api/dependencies.py` 파일 검토
- [ ] 수정 전략 결정:
  - Case A: Import 경로만 수정 (함수 존재 시)
  - Case B: 테스트 재작성 (함수 없음 시)

---

## Task 3: DI 테스트 수정

- [ ] `tests/integration/tdd/test_dependency_injection.py` 수정
  - [ ] Import 경로 수정 또는 테스트 재작성
  - [ ] `test_get_neo4j_storage` 수정
  - [ ] `test_get_chroma_storage` 수정
  - [ ] `test_get_composite_storage` 수정
- [ ] 테스트 실행: `pytest tests/integration/tdd/test_dependency_injection.py -v`
- [ ] 결과: 3 passed 확인
- [ ] 커밋: `test: fix dependency injection test imports`

**커밋 메시지:**
```
test: fix dependency injection test imports

- Update import path from app.core.dependencies to app.interfaces.api.dependencies
- [선택] Modify tests to match current DI structure
- All 3 DI tests now passing
```

---

## Task 4: Use Case 테스트 수정

- [ ] `tests/unit/test_usecases.py` 수정
  - [ ] `test_create_job`: Mock 추가 (graph, extractor)
  - [ ] `test_process_job_success`: Mock 추가 (graph, extractor)
  - [ ] `test_process_job_failure`: Mock 추가 (graph, extractor)
- [ ] 테스트 실행: `pytest tests/unit/test_usecases.py -v`
- [ ] 결과: 3 passed 확인
- [ ] 커밋: `test: update IngestionService test mocks`

**커밋 메시지:**
```
test: update IngestionService test mocks

- Add graph and extractor parameters to match Spec 010 changes
- All use case tests now passing
```

---

## Task 5: 전체 테스트 검증 (회귀 방지)

- [ ] Contract Tests: `pytest tests/contracts/ -v`
- [ ] Unit Tests: `pytest tests/unit/ -v`
- [ ] Integration Tests: `pytest tests/integration/ -v`
- [ ] 전체 테스트: `pytest tests/ -v`
- [ ] 모든 테스트 통과 확인
- [ ] 기존 기능 영향 없음 확인

---

## Task 6: PR 준비 및 생성

- [ ] `specs/013-fix-failed-tests/walkthrough.md` 작성
- [ ] `specs/013-fix-failed-tests/pr_description.md` 작성
- [ ] 백로그 업데이트: `backlog/queue.md` (Spec 013 Icebox → 완료로 이동)
- [ ] Push: `git push origin feature/013-fix-failed-tests`
- [ ] PR 생성:
```bash
gh pr create --base main --head feature/013-fix-failed-tests \
  --title "✅ Spec 013: Fix Failed Tests" \
  --body-file specs/013-fix-failed-tests/pr_description.md
```
- [ ] CI 파이프라인 통과 확인

---

## Notes

- 프로덕션 코드는 절대 변경하지 않음
- 테스트 코드만 최소한으로 수정
- 각 Task마다 테스트 실행하여 즉시 검증

