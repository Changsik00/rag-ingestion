# Task List: Spec-060

## Progress
- [x] Spec 번호 확정 및 브랜치 생성 (Pending Execution)
- [x] spec.md 작성
- [x] plan.md 작성
- [x] task.md 작성
- [x] 백로그 업데이트
- [x] User Plan Accept

---

## Task 1: Infrastructure & Dependencies Setup
### 1-1. Dependency Update
- [x] `pyproject.toml` 수정: `langgraph-checkpoint-sqlite` 제거, `langgraph-checkpoint-postgres` 및 `psycopg[binary]`, `psycopg-pool` 추가.
- [x] Lock file update: `uv sync` 실행.
- [x] Commit: `build(spec-060): switch checkpointer dependencies to postgres`

### 1-2. Docker Environment
- [x] `docker-compose.yml` 수정: PostgreSQL 16 서비스 추가.
- [x] `.env.example` 및 `.env` 업데이트: DB 연결 정보 추가.
- [x] `app/core/config.py` 수정: Settings 모델에 DB Config 추가.
- [x] Verification: `docker-compose up -d postgres` 성공 확인.
- [x] Commit: `infra(spec-060): add postgres service to docker-compose`

---

## Task 2: Checkpointer Implementation (Adapter Pattern)
### 2-1. Connection Pooling & Lifespan
- [x] `app/interfaces/api/lifespan.py` (or `main.py`) 수정: `AsyncConnectionPool` 생성 및 종료 로직 추가.
- [x] Commit: `feat(spec-060): manage postgres connection pool in app lifespan`

### 2-2. Checkpointer Dependency Injection
- [x] `app/interfaces/api/dependencies.py` 수정: `get_checkpointer`가 `AsyncPostgresSaver`를 반환하도록 변경 (Startup 시 create_tables 호출 포함).
- [x] Commit: `refactor(spec-060): inject AsyncPostgresSaver instead of sqlite`

### 2-3. Orchestrator Adaptation
- [x] `app/infrastructure/ai/ingestion_orchestrator.py` 수정: `reset_checkpoints` 로직을 Postgres SQL(`TRUNCATE` 등)로 변경.
- [x] Commit: `refactor(spec-060): adapt orchestrator reset logic for postgres`

---

## Task 3: MessagesState Migration (Enhancement)
### 3-1. State Definition
- [x] `app/domain/value_objects/ingestion_state.py` 수정: `IngestionGraphState`가 `MessagesState`를 상속받거나 `messages` 필드를 포함하도록 변경.
- [x] Commit: `refactor(spec-060): migrate IngestionGraphState to use MessagesState`

### 3-2. Orchestrator Logic Update
- [x] `app/infrastructure/ai/ingestion_orchestrator.py` 수정: `steps_history` (List[str]) 사용처를 `messages` (List[BaseMessage])로 변경.
- [x] Commit: `refactor(spec-060): update orchestrator to use standard messages`

---

## Task 4: Verification & PR
### 4-1. Automated Testing
- [x] `tests/integration/test_ingestion_graph.py` 실행 및 Pass 확인 (DB 연결 환경 필요).
- [x] Commit: `test(spec-060): verify ingestion graph with postgres checkpointer`

### 4-2. Manual Verification
- [x] Admin Dashboard에서 Job 실행 테스트.
- [x] Postgres DB 데이터 적재 확인.

### 4-3. Final Review
- [x] Code Quality Check: `uv run ruff check . --fix && uv run ruff format .`
- [x] **Walkthrough 작성**: `specs/spec-060-postgres-checkpointer/walkthrough.md`
- [x] **PR Description 작성**: `specs/spec-060-postgres-checkpointer/pr_description.md`
- [x] **Archive Commit**: `docs(spec-060): archive walkthrough and pr description`
- [x] Create PR: `gh pr create`

## Summary
**총 Task**: 4개 Phase
**예상 커밋 수**: 7~9개
**현재 진행**: Completion
