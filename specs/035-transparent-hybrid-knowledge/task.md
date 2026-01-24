# Task List: Spec-035

## Progress
- [x] Spec 번호 확정 (035)
- [x] spec.md 상세화 (Hybrid 전략 및 Citation 시나리오)
- [x] plan.md 상세화 (Prompt Engineering 및 파싱 로직)
- [x] task.md 업데이트 (완료)
- [x] 백로그 업데이트 (Note 및 문서 링크 추가)
- [x] User Plan Accept

## Task 0: Documentation of Search Strategy
### 0-1. Design Guide 작성
- [x] `docs/design_guides/006-hybrid-knowledge-mixing.md` 작성 ("Sparse but Powerful" 전략 및 배경 기록)
- [x] Commit: `docs: document hybrid knowledge mixing strategy (sparse but powerful)`

## Task 1: Domain & State Update
### 1-1. State Schema 확장 (TDD)
- [x] Test Case 작성: `RAGGraphState`에 `citations` 필드 접근 검증
- [x] 코드 구현: `app/domain/rag/state.py` 수정
- [x] Commit: `feat(spec-035): add citations field to RAGGraphState`

## Task 2: Infrastructure - Citation & Hybrid Logic
### 2-1. Context Formatting (Source ID 주입)
- [x] Test Case 작성: 컨텍스트 내 `[ID: n]` 포함 여부 검증
- [x] 코드 구현: `app/infrastructure/rag/nodes.py` 내 로직 수정
- [x] Commit: `feat(spec-035): inject explicit source IDs into context chunks`

### 2-2. Output Parsing & Citation Mapping
- [x] Test Case 작성: `[1]` 포함 텍스트에서 Citation 데이터 적중 검증 (`test_citation_parsing`)
- [x] 코드 구현: `generate_answer` 노드의 regex 파싱 및 State 매핑 구현
- [x] Commit: `feat(spec-035): implement regex-based citation parsing`

### 2-3. Prompt Engineering (Hybrid Strategy)
- [x] System Prompt 수정: "Sparse but Powerful" 지침 및 Citation 규칙 주입
- [x] 통합 테스트 (Mocked): LLM이 두 지식을 섞어서 답변하는지 검증
- [x] Commit: `feat(spec-035): harden system prompt for hybrid knowledge mixing`

## Task 3: Admin UI - Transparent Reference Section
### 3-1. Reference List Rendering
- [x] Manual Check: Playground 하단에 `[1] (Source)` 링크 출력 확인
- [x] 코드 구현: `app/admin/pages/4_RAG_Playground.py` 수정
- [x] Commit: `feat(spec-035): render clickable references in admin UI`

## Task 4: PR Creation
- [x] Code Quality Check: `uv run ruff check . --fix && uv run ruff format .`
- [x] Run Full Tests: `uv run pytest tests/unit/domain/rag/test_state.py tests/unit/infrastructure/rag/test_citation_parsing.py tests/integration/bdd/test_hybrid_knowledge.py`
- [x] Create PR: `gh pr create` (PR Description 포함)

## Summary
**총 Task**: 8개 세부 항목
**예상 커밋 수**: 9개
