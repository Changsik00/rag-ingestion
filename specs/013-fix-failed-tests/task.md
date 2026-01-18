# Task Checklist: Spec 013 - Fix Failed Tests

## Progress

- [x] Spec 번호 확정 (013)
- [x] spec.md 작성
- [x] plan.md 작성
- [x] task.md 작성
- [x] 사용자 승인 완료
- [x] 브랜치 생성 및 구현 시작

---

## Task 1: 브랜치 생성 및 Spec 문서 커밋

- [x] 브랜치 생성: `git checkout -b feature/013-fix-failed-tests`
- [x] 브랜치 확인: `git branch --show-current`
- [x] Spec 문서 커밋: `git add specs/013-fix-failed-tests/ && git commit -m "docs: add spec 013 - fix failed tests"`

---

## Task 2: DI 테스트 분석 및 수정 전략 결정

- [x] DI 테스트 실행하여 에러 메시지 확인
  - `pytest tests/integration/tdd/test_dependency_injection.py -v`
- [x] `app/interfaces/api/dependencies.py` 파일 검토
- [x] 수정 전략 결정:
  - Case A: Import 경로만 수정 (함수 존재 시)
  - **Case B 선택**: 테스트 재작성 (함수 없음)

---

## Task 3: DI 테스트 수정

- [x] `tests/integration/tdd/test_dependency_injection.py` 수정
  - [x] Import 경로 수정 (`app.core.dependencies` → `app.interfaces.api.dependencies`)
  - [x] `test_get_neo4j_storage` → `test_get_repository_returns_composite_storage` (재작성)
  - [x] `test_get_chroma_storage` → `test_get_neo4j_driver_initialization` (재작성)
  - [x] `test_get_composite_storage` → `test_get_graph_repository` (재작성)
- [x] 테스트 실행: `pytest tests/integration/tdd/test_dependency_injection.py -v`
- [x] 결과: 3 passed, 1 skipped 확인
- [x] 커밋: `test: fix dependency injection test imports`

**커밋 메시지:**
```
test: fix dependency injection test imports

- Update import path from app.core.dependencies to app.interfaces.api.dependencies
- Rewrite tests to match current DI structure (get_repository, get_neo4j_driver, get_graph_repository)
- All 3 DI tests now passing (3 passed, 1 skipped)
```

---

## Task 4: Use Case 테스트 수정

- [x] `tests/unit/test_usecases.py` 수정
  - [x] `test_create_job`: Mock 추가 (graph, extractor)
  - [x] `test_process_job_success`: Mock 추가 (graph, extractor)
  - [x] `test_process_job_failure`: Mock 추가 (graph, extractor)
- [x] 테스트 실행: `pytest tests/unit/test_usecases.py -v`
- [x] 결과: 3 passed 확인
- [x] 커밋: `test: update IngestionService test mocks`

**커밋 메시지:**
```
test: update IngestionService test mocks

- Add graph and extractor parameters to match Spec 010 changes
- All use case tests now passing (3 passed)
```

---

## Task 5: 전체 테스트 검증 (회귀 방지)

- [x] Contract Tests: `pytest tests/contracts/ -v`
- [x] Unit Tests: `pytest tests/unit/ -v`
- [x] Integration Tests: `pytest tests/integration/ -v`
- [x] 전체 테스트: `pytest tests/ -v`
- [x] 모든 테스트 통과 확인 (85 passed, 4 skipped)
- [x] 기존 기능 영향 없음 확인

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

