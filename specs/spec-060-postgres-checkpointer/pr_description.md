# PR: Migrate Checkpointer to PostgreSQL & Adopt MessagesState (Spec 060)

## 📌 Description
Migrates the internal LangGraph Checkpointer from SQLite to PostgreSQL to improve concurrency and scalability. Also refactors `IngestionGraphState` to use the standard `MessagesState` for better alignment with LangGraph best practices.

## 🔄 Changes

### Infrastructure
- **Docker**: Added `postgres:16` service to `docker-compose.yml`.
- **Config**: Added `POSTGRES_DB_URL` using `psycopg` driver.

### Core Implementation
- **Lifespan**: Implemented `AsyncConnectionPool` initialization in `app/interfaces/api/main.py`.
- **Dependencies**: Refactored `get_checkpointer` to use `AsyncPostgresSaver` with connection pooling.
- **Orchestrator**: Updated `reset_checkpoints` to use `TRUNCATE` instead of `DELETE` on SQLite tables.

### Refactoring
- **State**: `IngestionGraphState` now inherits from `MessagesState`.
- **Nodes**: Replaced `steps_history` (list[str]) appending with `messages` (list[AIMessage]) logging.

## 🧪 Verification
- **Automated Tests**: New integration test `tests/integration/functional/test_postgres_persistence.py` passes.
- **Dependencies**: `langgraph-checkpoint-postgres`, `psycopg`, `psycopg-pool` added.

## ⚠️ Notes
- **Breaking Change**: Existing SQLite checkpoints are **NOT migrating**. The system will start with a fresh state history.
- **Env Update**: Users must update `.env` with `POSTGRES_*` variables (see `.env.example`).
