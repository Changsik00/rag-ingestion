# Task List: Spec 043 - Robust Ingestion (Chroma Batching)

## Progress
- [x] Spec 번호 확정 (044 -> 043)
- [x] spec.md 작성 (SDD Format)
- [x] plan.md 작성 (SDD Format)
- [x] task.md 작성 (SDD Format)
- [x] 백로그 업데이트
- [x] User Plan Accept
- [x] Feature 브랜치 생성: `feat/spec-043-robust-ingestion`

---

## Task 1: Configuration & Infrastructure

### 1-1. Config Update
- [x] `admin/config.py`에 `CHROMA_BATCH_SIZE` 추가 <!-- id: 5 -->
- [x] Commit: `feat(spec-043): add chroma batch size config`

### 1-2. ChromaStorage Refactoring
- [x] `app/infrastructure/storage/chroma.py` 수정 (Batch Logic 적용) <!-- id: 6 -->
- [x] Logging 추가 <!-- id: 7 -->
- [x] Commit: `feat(spec-043): implement batch processing in chroma storage`

---

## Task 2: Verification

### 2-1. Verification Script (Automated)
- [x] `scripts/test_robust_ingestion.py` 작성 (Mock Test)
- [x] Test 실행 및 Pass 확인: `uv run python scripts/test_robust_ingestion.py`
- [x] Commit: `test(spec-043): add robust ingestion verification script`

### 2-2. Manual Verification (Optional)
- [ ] 실제 데이터(일론 머스크) 수집 테스트 수행 (Log 확인)

---

## Task 3: PR Creation

### 3-1. Quality Check
- [x] Code Quality: `uv run ruff check . --fix && uv run ruff format .`
- [x] Full Tests: `uv run pytest -v`

### 3-2. Documentation & Merge
- [x] Walkthrough 작성: `specs/043-robust-ingestion/walkthrough.md`
- [x] PR Description 작성: `specs/043-robust-ingestion/pr_description.md`
- [x] Create PR: `gh pr create --title "feat(spec-043): robust ingestion with chroma batching" --body-file specs/043-robust-ingestion/pr_description.md`

---

## Summary
**총 Task**: 3개 Category
**예상 커밋 수**: 5개
**현재 진행**: Planning 완료, User Review 대기
