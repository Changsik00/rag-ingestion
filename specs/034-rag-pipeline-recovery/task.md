# Task List: Spec-034 (RAG Pipeline Recovery)

## Progress
- [x] Spec 번호 확정
- [x] spec.md 작성
- [ ] plan.md 작성
- [x] task.md 작성
- [x] 백로그 업데이트 (Note 추가)
- [ ] User Plan Accept

## Task 1: RAG Domain & Infrastructure (Fallback Logic)
### 1-1. Domain Update
- [ ] `app/domain/rag/state.py` 수정: `fallback_triggered: bool` 필드 추가
- [ ] Commit: `feat(spec-034): add fallback_triggered field to RAGGraphState`

### 1-2. Implementation - Nodes Fallback
- [ ] `app/infrastructure/rag/nodes.py` 수정 (`retrieve_hybrid` 노드)
  - 필터링된 검색 결과가 0건일 경우 필터 없이 재검색하는 로직 추가
- [ ] TDD: `tests/unit/infrastructure/rag/test_rag_nodes.py`에 Fallback 테스트 추가 및 검증
- [ ] Commit: `feat(spec-034): implement filter fallback in retrieve_hybrid node`

## Task 2: Prompting & Guardrails (Empty Guard)
### 2-1. Prompt Refinement
- [ ] `app/infrastructure/rag/nodes.py` 수정 (`generate_answer` 노드)
  - 컨텍스트 부재 시 "정보 부족" 답변을 강제하는 System Prompt 강화
- [ ] TDD: 비어있는 컨텍스트로 `generate_answer` 호출 시 답변 양식 검증
- [ ] Commit: `feat(spec-034): strengthen prompt guard for empty context`

## Task 3: Infrastructure & Admin (Checkpointer)
### 3-1. Checkpointer Stability
- [ ] `app/interfaces/api/dependencies.py` 수정: Graph Builder에 Checkpointer 주입 확인
- [ ] `app/admin/pages/4_RAG_Playground.py` 수정: `graph_builder.build(checkpointer=...)` 명시적 주입
- [ ] Commit: `fix(spec-034): stabilize checkpointer usage and integrate with playground`

### 3-2. UI Integration (HITL & Trace)
- [ ] `app/admin/pages/4_RAG_Playground.py` 수정
  - `render_debug_ui`에 Reasoning Trace/Fallback 상태 표시 추가
  - HITL Interrupt 발생 시 Resume 제어부 활성화 확인
- [ ] Commit: `feat(spec-034): integrate HITL control and reasoning trace in admin UI`

## Task 4: Documentation
- [ ] `docs/architecture/rag_pipeline.md` 업데이트 (Fallback 로직 기술)
- [ ] `docs/guides/admin_guide.md` 업데이트 (Playground 기능 가이드)
- [ ] Commit: `docs(spec-034): update rag architecture and admin guide`

## Task 5: PR Creation
- [ ] Code Quality Check: `uv run ruff check . --fix && uv run ruff format .`
- [ ] Run Full Tests: `uv run pytest`
- [ ] Walkthrough 작성: `specs/034-rag-pipeline-recovery/walkthrough.md`
- [ ] PR Description 작성: `specs/034-rag-pipeline-recovery/pr_description.md`
- [ ] Create PR: `gh pr create --title "feat(spec-034): rag pipeline recovery and stability" --body-file specs/034-rag-pipeline-recovery/pr_description.md`

## Summary
**총 Task**: 4개
**예상 커밋 수**: 7개
