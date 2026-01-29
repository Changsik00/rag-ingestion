# Task List: Spec-025

## Progress
- [x] Spec 번호 확정
- [x] spec.md 작성
- [x] plan.md 작성
- [x] task.md 작성
- [x] 백로그 업데이트 (Note 추가)
- [x] User Plan Accept

## Task 1: Domain Service Implementation (TDD)
### 1-1. TDD Warming up
- [x] Test Case 작성: `tests/unit/domain/test_query_rewriter.py`
    - Case: 빈 히스토리 -> 원본 반환
    - Case: 히스토리 포함 -> LLM 호출 및 파싱 검증
- [x] Test 실행 (Fail): `uv run pytest tests/unit/domain/test_query_rewriter.py`
- [x] Commit: `test(spec-025): add test case for query rewriter`

### 1-2. Implementation
- [x] 코드 구현: `app/domain/services/query_rewriter.py`
- [x] Test 실행 (Pass): `uv run pytest tests/unit/domain/test_query_rewriter.py`
- [x] Commit: `feat(spec-025): implement query rewriter service using llm`

## Task 2: UI Integration
### 2-1. Playground Integration
- [x] 코드 수정: `app/admin/pages/4_RAG_Playground.py`
    - `QueryRewriter` 인스턴스 주입
    - `repo.search()` 호출 전 `rewrite()` 실행
    - Debug Expander에 `Rewritten Query` 표시
- [x] Manual Check: 멀티턴 대화 시나리오 수행 ("일론 머스크" -> "그는?")
- [x] Commit: `feat(spec-025): integrate query rewriting into rag playground`

## Task 3: PR Creation
- [x] Code Quality Check: `uv run ruff check . --fix && uv run ruff format .`
- [x] Run Full Tests: `uv run pytest`
- [x] Create PR: `gh pr create --title "feat(spec-025): contextual rag query rewriting" --body-file specs/025-contextual-rag/pr_description.md`

## Summary
**현재 진행**: 완료 (PR 머지됨)
