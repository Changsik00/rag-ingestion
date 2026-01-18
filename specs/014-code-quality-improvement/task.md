# Task Checklist: Spec 014 - Code Quality Improvement

## Progress

- [x] Spec 번호 확정 (014)
- [x] spec.md 작성
- [x] plan.md 작성
- [x] task.md 작성
- [x] 백로그 업데이트
- [ ] 사용자 승인 대기
- [ ] 브랜치 생성 및 구현 시작

---

## Task 1: 브랜치 생성 및 Spec 문서 커밋

- [ ] 브랜치 생성: `git checkout -b feature/014-code-quality-improvement`
- [ ] 브랜치 확인: `git branch --show-current`
- [ ] Spec 문서 커밋: `git add specs/014-code-quality-improvement/ backlog/queue.md && git commit -m "docs: add spec 014 - code quality improvement"`

---

## Task 2: Bug Fix - semantic_data 초기화

- [ ] `app/use_cases/ingestion.py` 수정
  - [ ] Line 51에 `semantic_data = None` 추가
- [ ] 테스트 실행: `uv run pytest tests/unit/test_usecases.py -v`
- [ ] 결과: 3 passed 확인
- [ ] 커밋: `fix: initialize semantic_data to prevent NameError`

**커밋 메시지:**
```
fix: initialize semantic_data to prevent NameError

- Add semantic_data = None initialization before extractor check
- Prevents NameError when extractor=None
- Fixes bug discovered in Spec 013
```

---

## Task 3: GWT 형식 적용 - Unit Tests (1/2)

**파일 3개:**
- [ ] `tests/unit/test_job_entity.py` (2 tests)
- [ ] `tests/unit/test_neo4j_graph_repository.py` (7 tests)
- [ ] `tests/unit/test_neo4j_job_repo.py` (4 tests)

- [ ] GWT 주석 추가 (Given/When/Then)
- [ ] 테스트 실행: `uv run pytest tests/unit/test_job_entity.py tests/unit/test_neo4j_graph_repository.py tests/unit/test_neo4j_job_repo.py -v`
- [ ] 결과: 13 passed 확인
- [ ] 커밋: `test: add GWT format to unit tests (part 1/3)`

---

## Task 4: GWT 형식 적용 - Unit Tests (2/2)

**파일 3개:**
- [ ] `tests/unit/test_scraper.py` (2 tests)
- [ ] `tests/unit/test_storage.py` (2 tests)
- [ ] `tests/unit/test_usecases.py` (3 tests)

- [ ] GWT 주석 추가
- [ ] 테스트 실행: `uv run pytest tests/unit/test_scraper.py tests/unit/test_storage.py tests/unit/test_usecases.py -v`
- [ ] 결과: 7 passed 확인
- [ ] 커밋: `test: add GWT format to unit tests (part 2/3)`

---

## Task 5: GWT 형식 적용 - TDD Integration Tests

**파일 3개:**
- [ ] `tests/integration/tdd/test_api_ingest.py` (2 tests)
- [ ] `tests/integration/tdd/test_async_ingest.py` (2 tests)
- [ ] `tests/integration/tdd/test_jobs.py` (4 tests)

- [ ] GWT 주석 추가
- [ ] 테스트 실행: `uv run pytest tests/integration/tdd/test_api_ingest.py tests/integration/tdd/test_async_ingest.py tests/integration/tdd/test_jobs.py -v`
- [ ] 결과: 8 passed 확인
- [ ] 커밋: `test: add GWT format to TDD integration tests (part 3/3)`

---

## Task 6: 전체 테스트 검증 (회귀 방지)

- [ ] Contract Tests: `uv run pytest tests/contracts/ -v`
- [ ] Unit Tests: `uv run pytest tests/unit/ -v`
- [ ] Integration Tests: `uv run pytest tests/integration/ -v`
- [ ] 전체 테스트: `uv run pytest tests/ -v`
- [ ] 모든 테스트 통과 확인 (85+ passed)
- [ ] 기존 기능 영향 없음 확인

---

## Task 7: PR 준비 및 생성

- [ ] `specs/014-code-quality-improvement/walkthrough.md` 작성
- [ ] `specs/014-code-quality-improvement/pr_description.md` 작성
- [ ] Push: `git push origin feature/014-code-quality-improvement`
- [ ] PR 생성:
```bash
gh pr create --base main --head feature/014-code-quality-improvement \
  --title "fix(spec-014): code quality improvements (bug fix + test standardization)" \
  --body-file specs/014-code-quality-improvement/pr_description.md
```

---

## Notes

- 프로덕션 코드는 버그 수정만 (1줄 추가)
- 테스트 코드는 주석 추가만 (로직 변경 없음)
- GWT 주석은 한글로 작성 (명확성)
- 각 Task마다 테스트 실행하여 회귀 방지
