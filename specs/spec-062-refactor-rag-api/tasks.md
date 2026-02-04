# Task List: Spec-062

## Progress
- [x] Spec 번호 확정 및 브랜치 생성
- [x] spec.md 작성
- [x] plan.md 작성
- [x] tasks.md 작성
- [x] 백로그 업데이트 (Note 추가)
- [x] User Plan Accept

---

## Task 1: DTO & Repository Layer Refactoring
### 1-1. DTO Mapper Extraction
- [x] 코드 구현: `app/interfaces/api/v1/dto/mappers.py` 생성 및 `ChatResponseMapper` 구현.
- [x] Commit: `feat(spec-062): implement chat response mapper`

### 1-2. Session Repository Implementation
- [x] 코드 구현: `app/domain/interfaces/session_repository.py` 및 `app/infrastructure/repositories/postgres_session_repository.py` 작성.
- [x] 의존성 등록: `app/interfaces/api/dependencies.py`
- [x] Test 실행 (TDD): `tests/integration/functional/test_rag_session_cleanup.py` (아직 연결 전이라 Pass 유지)
- [x] Commit: `feat(spec-062): implement postgres session repository`

---

## Task 2: Service Layer Refactoring
### 2-1. Agent Service Encapsulation
- [x] 코드 구현: `app/application/services/agent.py`에 `ask()` 및 `resume()` 메서드 추가.
- [x] Test 실행: `uv run pytest tests/unit/test_agent_service.py` (Optional Unit Test)
- [x] Commit: `feat(spec-062): encapsulate langgraph logic in conversational rag agent`

---

## Task 3: API Controller Refactoring (Integration)
### 3-1. Refactor RAG Endpoint
- [x] 코드 수정: `app/interfaces/api/v1/endpoints/rag.py`
  - SQL 제거 -> `repo.delete_session()`
  - LangGraph 코드 제거 -> `agent.ask()`
  - Response Mapping 제거 -> `mapper.map(...)`
- [x] Test 실행 (Full Regression): `uv run pytest tests/integration/functional/`
- [x] Commit: `refactor(spec-062): convert rag api to clean architecture`

---

## Task 4: PR Creation & Archiving (Mandatory)
- [x] Code Quality Check: `uv run ruff check . --fix && uv run ruff format .`
- [x] Run Full Tests: `uv run pytest`
- [x] **Walkthrough 작성**: `specs/spec-062-refactor-rag-api/walkthrough.md`
- [x] **PR Description 작성**: `specs/spec-062-refactor-rag-api/pr_description.md` (템플릿 준수)
- [x] **Archive Commit**: `docs(spec-062): archive walkthrough and pr description`
- [x] Create PR: `gh pr create --title "refactor(spec-062): rag api clean architecture" --body-file specs/spec-062-refactor-rag-api/pr_description.md`

## Summary
**총 Task**: 4개 Phase
**예상 커밋 수**: 5개
**현재 진행**: Planning
