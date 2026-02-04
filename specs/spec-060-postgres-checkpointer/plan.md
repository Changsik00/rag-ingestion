# Implementation Plan: Spec-060

## 📋 Branch Strategy
- `feature/spec-060-postgres-checkpointer`

## 🛑 User Review Required
> [!IMPORTANT]
> - [ ] **DB Reset**: This migration will start with a fresh Checkpoint limit. Existing SQLite history will NOT be migrated.
> - [ ] **Dependency**: Adding `psycopg[binary]` adds system dependencies that might affect Docker build times slightly.

## 🎯 Core Strategy

### Architecture Context
| Component | Strategy | Reasoning |
|:---:|:---|:---|
| **Checkpointer** | `AsyncPostgresSaver` | Official support, concurrency safe. |
| **Driver** | `psycopg` (via `AsyncConnectionPool`) | High performance async driver (v3). |
| **State** | `MessagesState` | Standardizing on LangGraph defaults. |

## 📂 Proposed Changes

### [Infrastructure]

#### [MODIFY] `docker-compose.yml`
Add `postgres` (v16) service, volume, and expose ports.

#### [MODIFY] `.env.example`, `app/core/config.py`
Add `POSTGRES_DB_URL` configuration handling.

#### [MODIFY] `pyproject.toml`
Replace `langgraph-checkpoint-sqlite` with `langgraph-checkpoint-postgres`.

### [Application Layer]

#### [MODIFY] `app/interfaces/api/lifespan.py`
Manage global `AsyncConnectionPool`. Initialize Checkpointer tables on startup.

#### [MODIFY] `app/interfaces/api/dependencies.py`
Update `get_checkpointer` to yield from the global connection pool using `AsyncPostgresSaver`.

### [Domain/Infrastructure Layer]

#### [MODIFY] `app/domain/value_objects/ingestion_state.py`
Inherit from `MessagesState` (or similar TypedDict with `messages`).

#### [MODIFY] `app/infrastructure/ai/ingestion_orchestrator.py`
Refactor `steps_history` usage to `messages`. Remove SQLite reset logic and implement Postgres table truncation for resets.

## 🧪 Verification Plan

### Automated Tests
```bash
# Verify Docker Connectvity
docker-compose up -d postgres

# Run Integration Tests
uv run pytest tests/integration/test_ingestion_graph.py -v
```

### Manual Verification
1. Start Admin Dashboard: `uv run streamlit run admin/dashboard.py`
2. Submit a new URL for ingestion.
3. Check Postgres logs to verify connection.
4. Verify no `database locked` errors appear during extraction.
