# Task List: Spec-061

## Progress
- [x] Spec 번호 확정 및 브랜치 생성
- [x] spec.md 작성
- [x] plan.md 작성
- [x] task.md 작성
- [ ] 백로그 업데이트 (Note 추가)
- [ ] User Plan Accept

---

## Task 1: Backend Session Cleanup Logic
### 1-1. TDD Setup
- [x] Test Case 작성: `tests/unit/test_xxx.py`rag_api_cleanup.py` 작성:
  - 세션 생성 -> 데이터 확인 -> Reset API 호출 -> 데이터 삭제 확인.
- [x] Test 실행 (Fail Expected).
- [x] Commit: `test(spec-061): add integration test for session cleanup`

### 1-2. Implementation
- [x] `app/interfaces/api/v1/endpoints/rag.py` 수정:
  - `reset_session` 엔드포인트에서 `database.pool`을 통해 직접 `DELETE` 쿼리 실행 구현.
  - Queries:
    ```sql
    DELETE FROM checkpoint_writes WHERE thread_id = $1;
    DELETE FROM checkpoints WHERE thread_id = $1;
    DELETE FROM checkpoint_blobs WHERE thread_id = $1; -- (If mapped by thread_id, otherwise check schema)
    ```
- [x] Test 실행 (Pass).
- [x] Commit: `feat(spec-061): implement robust session cleanup using sql`

---

## Task 2: Admin UI UX Improvement
### 2-1. RAG Playground Update
- [x] `admin/pages/4_RAG_Playground.py` 수정:
  - 기존 "Advanced Settings" 내부 버튼 제거.
  - 사이드바에 "New Chat (+Reset Thread ID)", "Delete History" 버튼 추가.
  - Toast 메시지 및 Rerun 로직 최적화.
- [x] Commit: `feat(spec-061): move chat controls to sidebar`

---

## Task 3: Verification & PR
- [x] Code Quality Check: `uv run ruff check . --fix && uv run ruff format .`
- [x] Run Full Tests: `uv run pytest tests/integration/test_rag_api_cleanup.py`
- [x] **Walkthrough 작성**: `specs/spec-061-rag-session-cleanup/walkthrough.md`
- [x] **PR Description 작성**: `specs/spec-061-rag-session-cleanup/pr_description.md`
- [ ] **Archive Commit**: `docs(spec-061): archive walkthrough and pr description`
- [ ] Create PR: `gh pr create`

## Summary
**총 Task**: 3개 Phase
**예상 커밋 수**: 5개
**현재 진행**: Planning
