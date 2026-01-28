# Task List: Spec-XXX

## Progress
- [ ] Spec 번호 확정 및 브랜치 생성
- [ ] spec.md 작성
- [ ] plan.md 작성
- [ ] task.md 작성
- [ ] 백로그 업데이트 (Note 추가)
- [ ] User Plan Accept

---

## Task 1: <Korean Title>
### 1-1. TDD Warming up
- [ ] Test Case 작성: `tests/unit/test_xxx.py`
- [ ] Test 실행 (Fail): `uv run pytest ...`
- [ ] Commit: `test(spec-xxx): add test case for ...`

### 1-2. Implementation
- [ ] 코드 구현: `app/path/to/file.py`
- [ ] Test 실행 (Pass): `uv run pytest ...`
- [ ] Commit: `feat(spec-xxx): implement ...`

---

## Task N: PR Creation & Archiving (Mandatory)
<!-- 이 단계는 모든 작업 완료 후 수행합니다. -->
- [ ] Code Quality Check: `uv run ruff check . --fix && uv run ruff format .`
- [ ] Run Full Tests: `uv run pytest`
- [ ] **Walkthrough 작성**: `specs/XXX/walkthrough.md`
- [ ] **PR Description 작성**: `specs/XXX/pr_description.md` (템플릿 준수)
- [ ] **Archive Commit**: 위 파일을 `specs/`에 커밋 (`docs(spec-xxx): archive walkthrough and pr description`)
- [ ] Create PR: `gh pr create --title "..." --body-file specs/XXX/pr_description.md`

## Summary
**총 Task**: X개  
**예상 커밋 수**: Y개  
**현재 진행**: Planning / Execution / Verification
