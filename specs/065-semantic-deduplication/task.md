# Task List: Spec-065

## Progress
- [x] Spec 번호 확정 및 브랜치 생성
- [x] spec.md 작성
- [x] plan.md 작성
- [x] task.md 작성
- [x] 백로그 업데이트 (Note 추가)
- [x] User Plan Accept

---

## Task 1: Domain & Infrastructure Setup
### 1-1. TDD Warming up
- [x] Test Case 작성: `tests/unit/test_deduplication_strategies.py` (Metadata & Hash Strategies)
- [x] Test 실행 (Fail): `uv run pytest tests/unit/test_deduplication_strategies.py`
- [x] Commit: `test(spec-065): add test case for logic-based strategies`

### 1-2. Implementation
- [x] 코드 구현: `app/domain/entities/job.py` (Schema: custom_metadata)
- [x] 코드 구현: `app/application/services/deduplication_strategies.py` (Strategies)
- [x] 코드 구현: `app/infrastructure/repositories/neo4j_job_repository.py` (Repo Update)
- [x] Test 실행 (Pass): `uv run pytest tests/unit/test_deduplication_strategies.py`
- [x] Commit: `feat(spec-065): implement generic deduplication strategies`

---

## Task 2: Application Logic Integration
### 2-1. TDD Warming up
- [x] Test Case 작성: `tests/integration/test_ingestion_deduplication.py` (Skip Scenario)
- [x] Test 실행 (Fail): `uv run pytest tests/integration/test_ingestion_deduplication.py`
- [x] Commit: `test(spec-065): add integration test for duplicate skipping`

### 2-2. Implementation
- [x] 코드 구현: `app/application/services/ingestion.py` (Integrate Checker)
- [x] Test 실행 (Pass): `uv run pytest tests/integration/test_ingestion_deduplication.py`
- [x] Commit: `feat(spec-065): integrate duplicate check into ingestion pipeline`

---

## Task 3: Admin UI Update
### 3-1. Implementation
- [x] 코드 구현: `admin/pages/0_Ingestion_Management.py` (Force Refresh UI)
- [x] Manual Verification
- [x] Commit: `feat(spec-065): add force refresh option to admin ui`

---

## Task N: PR Creation & Archiving (Mandatory)
<!-- 이 단계는 모든 작업 완료 후 수행합니다. -->
- [x] Code Quality Check: `uv run ruff check . --fix && uv run ruff format .`
- [x] Run Full Tests: `uv run pytest`
- [x] **Walkthrough 작성**: `specs/065-semantic-deduplication/walkthrough.md`
- [x] **PR Description 작성**: `specs/065-semantic-deduplication/pr_description.md` (템플릿 준수)
- [x] **Archive Commit**: 위 파일을 `specs/`에 커밋 (`docs(spec-065): archive walkthrough and pr description`)
- [ ] Create PR: `gh pr create --title "feat(spec-065): Semantic De-Duplication" --body-file specs/065-semantic-deduplication/pr_description.md`

## Summary
**총 Task**: 3개 + Common Task  
**현재 진행**: PR Creation Pending
