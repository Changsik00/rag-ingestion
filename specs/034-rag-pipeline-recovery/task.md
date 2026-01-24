# Task List: Spec-034 (RAG Pipeline Recovery)

## Progress
- [x] Spec 번호 확정
- [x] spec.md 작성
- [x] plan.md 작성
- [x] task.md 작성
- [x] 백로그 업데이트 (Note 추가)
- [x] User Plan Accept
- [x] Feature 브랜치 생성: `feature/034-rag-pipeline-recovery`

## Task 1: RAG Domain & Infrastructure (Fallback Logic)
### 1-1. Domain Update
- [x] `app/domain/rag/state.py` 수정: `fallback_triggered: bool`, `reasoning_log: list[str]` 필드 추가
- [x] Commit: `feat(spec-034): add reasoning_log and fallback_triggered to state`

### 1-2. Implementation - Nodes Fallback & Reasoning
- [x] `app/infrastructure/rag/nodes.py` 수정: `reasoning_log` 기록 및 Fallback 로직 추가
- [x] TDD: `tests/unit/infrastructure/rag/test_rag_nodes.py` 검증
- [x] Commit: `feat(spec-034): record reasoning logs and implement filter fallback`

## Task 2: Prompting & Guardrails (Empty Guard)
### 2-1. Prompt Refinement
- [x] `app/infrastructure/rag/nodes.py` 수정 (`generate_answer` 노드)
  - 컨텍스트 부재 시 "정보 부족" 답변을 강제하는 System Prompt 강화
- [x] TDD: 비어있는 컨텍스트로 `generate_answer` 호출 시 답변 양식 검증
- [x] Commit: `feat(spec-034): implement filter fallback and strengthen prompt guard`

## Task 3: Infrastructure & Admin (Checkpointer)
### 3-1. Checkpointer Stability
- [x] `app/interfaces/api/dependencies.py` 수정: Graph Builder에 Checkpointer 주입 확인
- [x] `app/admin/pages/4_RAG_Playground.py` 수정: `graph_builder.build(checkpointer=...)` 명시적 주입
- [x] Commit: `fix(spec-034): stabilize checkpointer usage and integrate with playground`

### 3-2. UI Integration (HITL & Trace)
- [x] `app/infrastructure/rag/graph.py` 수정: `interrupt_before` 파라미터 지원
- [x] `app/admin/pages/4_RAG_Playground.py` 수정
  - `render_debug_ui`에 `reasoning_log` 표시 및 디버그 UI 개선
  - HITL 활성화 토글 및 Interrupt 발생 시 Resume 버튼 UI 추가
- [x] Commit: `feat(spec-034): integrate HITL control and reasoning trace in admin UI`

## Task 4: Documentation
- [x] `docs/architecture/rag_pipeline.md` 업데이트 (Fallback 로직 기술)
- [x] `docs/guides/admin_guide.md` 업데이트 (Playground 기능 가이드)
- [x] Commit: `docs(spec-034): update rag architecture and admin guide`

## Task 5: PR Creation
- [x] Code Quality Check: `uv run ruff check . --fix && uv run ruff format .`
- [x] Run Full Tests: `uv run pytest`
- [x] Walkthrough 작성: `specs/034-rag-pipeline-recovery/walkthrough.md`
- [x] PR Description 작성: `specs/034-rag-pipeline-recovery/pr_description.md`
- [x] Create PR: `gh pr create --title "feat(spec-034): rag pipeline recovery and stability" --body-file specs/034-rag-pipeline-recovery/pr_description.md`

## Task 6: Hotfix - Async Checkpointer
- [x] `pyproject.toml`: `aiosqlite` 의존성 추가
- [x] `app/interfaces/api/dependencies.py`: `AsyncSqliteSaver` 도입
- [x] `app/admin/pages/4_RAG_Playground.py`: async checkpointer 핸들링
- [x] Verify: RAG Playground 실행 시 에러 해소 확인

## Summary
**총 Task**: 6개 대항목 완료
**검증 결과**: 204개 테스트 통과 (Spec 034 기준)
