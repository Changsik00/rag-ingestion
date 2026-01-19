# Task List: Spec 018 - System Stability & Test Refactoring

## Progress

- [ ] Spec 번호 확정 (018)
- [ ] spec.md 작성
- [ ] plan.md 작성
- [ ] task.md 작성
- [ ] 백로그 업데이트 (Note 추가)
- [ ] User Plan Accept

---

## Task 1: Core Foundation (Exceptions & Logging)

### 1-1. Branch & TDD Setup
- [ ] 브랜치 생성: `git checkout -b feature/018-system-stability`
- [x] Test Case 작성: `tests/unit/test_exceptions.py` (Custom Exception Hierarchy 검증)
- [x] Test 실행 (Fail): `uv run pytest tests/unit/test_exceptions.py` (ImportError 예상)
- [x] Commit: `test(spec-018): add unit tests for custom exceptions`

### 1-2. Implementation (Exceptions & Logger)
- [x] 코드 구현: `app/core/exceptions.py` 및 `app/core/logging_config.py` 작성
- [x] Test 실행 (Pass): `uv run pytest tests/unit/test_exceptions.py`
- [x] Commit: `feat(spec-018): implement custom exceptions and logging config`

---

## Task 2: Infrastructure Hardening

### 2-1. ChromaStorage TDD
- [x] Test Case 수정: `tests/unit/test_storage.py` (ChromaStorage의 에러 상황, None 리턴 검증 강화)
- [x] Test 실행 (Fail): `uv run pytest tests/unit/test_storage.py`
- [x] 코드 수정: `app/infrastructure/storage/chroma.py` (Null Check, Exception Wrapping)
- [x] Test 실행 (Pass): `uv run pytest tests/unit/test_storage.py`
- [x] Commit: `refactor(spec-018): harden chroma storage with null safety`

### 2-2. Neo4jStorage TDD
- [x] Test Case 수정: `tests/unit/test_storage.py` (Neo4jStorage 에러 핸들링 검증)
- [x] Test 실행 (Fail 또는 확인): `uv run pytest tests/unit/test_storage.py`
- [x] 코드 수정: `app/infrastructure/storage/neo4j_document_repository.py`
- [x] Test 실행 (Pass): `uv run pytest tests/unit/test_storage.py`
- [x] Commit: `refactor(spec-018): harden neo4j storage with proper exception handling`

---

## Task 3: Application Layer Refactoring

### 3-1. IngestionService TDD
- [x] Test Case 수정: `tests/unit/test_ingestion_service.py` (Custom Exception 발생 시 Job Status FAILED 처리 검증)
- [x] 코드 수정: `app/use_cases/ingestion.py`
    - [x] `try-except Exception` 제거
    - [x] `DoitException` 핸들링
    - [x] `logger` 적용
- [x] Test 실행 (Pass): `uv run pytest tests/unit/test_ingestion_service.py`
- [x] Commit: `refactor(spec-018): replace blanket exceptions with custom hierarchy in ingestion service`

---

## Task 4: Test Restoration (Skipped Tests)

### 4-1. Fix BDD Failure Flows
- [x] Test 확인: `tests/integration/bdd/test_failure_flows.py`의 `test_llm_failure_still_saves_document` Skip 제거
- [x] Test 실행 (Fail): `uv run pytest ...`
- [x] Test Fix: `mocker` 설정 또는 Mocking 방식 수정
- [x] Test 실행 (Pass): `uv run pytest ...`
- [x] Commit: `test(spec-018): restore skipped test for llm failure scenario`

### 4-2. Fix Entity Relationship Tests
- [x] Test 확인: `tests/integration/bdd/test_entity_relationships.py`의 Skip 제거
- [x] Test 실행 (Fail): `uv run pytest ...`
- [x] Test Fix: 유효한 URL (`httpbin.org` 등) 사용하도록 시나리오 수정
- [x] Test 실행 (Pass): `uv run pytest ...`
- [x] Commit: `test(spec-018): restore skipped entity relationship integration tests`

---

## Task 5: Final Verification & PR

### 5-1. Anti-Pattern Fix (Unit)
- [x] `tests/unit/test_scraper.py`의 `try-except` 제거 및 `pytest.raises` 적용
- [x] Test 실행 (Pass): `uv run pytest tests/unit/test_scraper.py`
- [x] Commit: `test(spec-018): remove try-except anti-pattern from scraper tests`

### 5-2. Full Suite Verification
- [x] 전체 테스트 실행: `uv run pytest -v` (Must be all PASSED)

### 5-3. PR Creation
- [x] PR 생성: `gh pr create --title "refactor(spec-018): system stability and test restoration" --body-file specs/018-system-stability-refactoring/pr_description.md`

## Summary
**총 Task**: 6개
**예상 커밋 수**: 8~10개
