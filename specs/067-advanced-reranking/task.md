# Task List: Spec-067 Advanced Reranking Logic Research

## Progress
- [x] Spec 번호 확정 및 브랜치 생성
- [x] spec.md 작성
- [x] plan.md 작성
- [ ] task.md 작성 (In Progress)
- [ ] 백로그 업데이트 (Note 추가)
- [x] Plan Accept
- [/] Task 1: Domain & Prompt Implementation
- [ ] Task 2: Advanced Reranking Logic
### 1-1. Prompt & State Upgrade
- [x] Listwise Prompt 생성: `app/domain/services/prompts/listwise_reranker.py`
- [x] State 확장: `app/domain/value_objects/rag_state.py` (strategy 추가)
- [x] Commit: `feat(spec-067): add listwise prompt and extend state`

## Task 2: Advanced Reranking Logic
### 2-1. Context Window Expansion
- [x] `rag_nodes.py` 내 인접 청크 로딩 로직 구현
- [x] Test: `tests/unit/test_context_expansion.py` (Verified via `verify_spec_067.py`)
- [x] Commit: `feat(spec-067): implement context window expansion`

### 2-2. Listwise Reranking Implementation
- [x] `rag_nodes.py` 내 Listwise 분기 로직 구현
- [x] Test: `tests/unit/test_listwise_logic.py` (Local verification done)
- [x] Commit: `feat(spec-067): implement listwise reranking logic`

---

## Task N: PR Creation & Archiving (Mandatory)
- [x] Code Quality Check: `uv run ruff check . --fix && uv run ruff format .`
- [x] Run Full Tests: `uv run pytest`
- [x] **Walkthrough 작성**: `specs/067-advanced-reranking/walkthrough.md`
- [x] **PR Description 작성**: `specs/067-advanced-reranking/pr_description.md`
- [x] **Archive Commit**: `docs(spec-067): archive walkthrough and pr description`
- [ ] Create PR: `gh pr create --title "feat(spec-067): advanced reranking" --body-file specs/067-advanced-reranking/pr_description.md`

## Summary
**총 Task**: 3개  
**예상 커밋 수**: 7개  
**현재 진행**: Completed (Pending PR)
