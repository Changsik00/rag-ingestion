# Task List: Spec-058 (Unit Test Restructuring)

## Progress
- [x] Spec 번호 확정 및 브랜치 생성
- [x] spec.md 작성 (Template 준수)
- [x] plan.md 작성 (Template 준수)
- [x] task.md 작성 (Template 준수)
- [x] 백로그 업데이트 (Note 추가)
- [x] User Plan Accept

---

## Task 1: 테스트 안정성 복구 (Stability Update)
- [x] `tests/unit/infrastructure/rag/test_rag_nodes.py` 수정: `RunnableConfig` 인자 주입
- [x] Test 실행 (Pass 확인): `uv run pytest tests/unit/infrastructure/rag/test_rag_nodes.py`
- [x] Commit: `fix(test): add RunnableConfig to RAGNodes unit tests`

### 1-2. Reranker 및 기타 테스트 수정
- [x] `tests/unit/infrastructure/test_rag_reranker.py` 수정
- [x] 기타TypeError 전수 조사 및 해결
- [x] Commit: `fix(test): resolve remaining TypeErrors in unit tests`

---

## Task 2: 유닛 테스트 구조 재편 (Restructuring)
- [x] Infrastructure 레이어 세분화 (`repositories`, `factories`, `scrapers`, `chunker`)
- [x] Domain 레이어 폴더 세분화 (`entities`, `services`, `value_objects`)
- [x] Application 레이어 정리
- [x] Interface 레이어 정리 (`api/dto`, `api/endpoints`)
- [x] 파일 이동에 따른 내부 `import` 경로 수정
- [x] Commit: `refactor(test): restructure unit tests and finalize imports`

---

## Task 3: PR Creation & Archiving (Mandatory)
- [x] Code Quality Check: `uv run ruff check . --fix && uv run ruff format .`
- [x] Run Full Tests: `uv run pytest tests/unit`
- [x] **Walkthrough 작성**: `specs/058-unit-test-restructuring/walkthrough.md`
- [x] **PR Description 작성**: `specs/058-unit-test-restructuring/pr_description.md`
- [x] **Archive Commit**: 문서 아카이브 (`docs(spec-058): archive walkthrough and pr description`)

## Summary
**총 Task**: 3개 (세부 8개)  
**예상 커밋 수**: 약 6-8개  
**현재 진행**: Verification (Completed)
