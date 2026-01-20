# Task List: Spec-022 Human-in-the-loop

## Progress
- [x] Spec 번호 확정 (022)
- [x] spec.md 작성
- [x] plan.md 작성
- [x] task.md 작성
- [x] User Plan Accept

## Task 1: Documentation (Design Guide)
### 1-1. Concept Guide
- [ ] 문서 작성: `docs/design_guides/human_in_the_loop_workflow.md`
    - HITL 개념 (Interrupt/Resume)
    - 사용자 행동 가이드 (수정, 승인, 포기)
    - Workflow Mermaid Diagram
- [ ] Commit: `docs(spec-022): add human-in-the-loop design guide`

## Task 2: In-Memory Checkpointer & Human Review Node
### 2-1. TDD Setup (Integration Test)
- [ ] Test Case 작성: `tests/integration/bdd/test_human_loop.py`
    - 시나리오: 그래프 실행 -> `human_review` 인터럽트 확인 -> 상태 조회 -> 상태 수정 -> 실행 재개.
- [ ] Test 실행 (Fail): `uv run pytest tests/integration/bdd/test_human_loop.py`
- [ ] Commit: `test(spec-022): add integration test for human-in-the-loop`

### 2-2. Graph Implementation
- [ ] 코드 구현: `app/infrastructure/brain/graph.py`
    - `IngestionGraphBuilder` 수정: `checkpointer` 인자 처리
    - `human_review` 노드 추가 및 연결
    - `interrupt_before` 설정
- [ ] 코드 구현: `app/infrastructure/brain/nodes.py`
    - `human_review` 메서드 추가
- [ ] Test 실행 (Pass): `uv run pytest tests/integration/bdd/test_human_loop.py`
- [ ] Commit: `feat(spec-022): implement human_review node and memory checkpointer`

## Task 3: Finalize & PR
- [x] Run Lint: `uv run ruff check . --fix`
- [ ] Run Full Tests: `uv run pytest`
- [ ] Create PR: `gh pr create --title "feat(spec-022): human-in-the-loop checkpointer"`

## Summary
**총 Task**: 3개
**예상 커밋 수**: 4개
