# Walkthrough: Spec 060 - Postgres Checkpointer Migration

## 1. Goal
Migrate LangGraph persistence from local SQLite (`AsyncSqliteSaver`) to PostgreSQL (`AsyncPostgresSaver`) to enable:
-   **Concurrency**: Handling multiple jobs without `database locked` errors.
-   **Scalability**: Supporting distributed deployments.
-   **Standardization**: Adopting `MessagesState` for better LangSmith integration.

## 2. Changes

### Infrastructure (`docker-compose.yml`, `config.py`)
-   Added `postgres` service (v16).
-   Added `POSTGRES_DB_URL` to settings.

### Dependencies (`pyproject.toml`)
-   Replaced `langgraph-checkpoint-sqlite` with `langgraph-checkpoint-postgres` + `psycopg`.

### Core Logic (`dependencies.py`, `main.py`)
-   Implemented `AsyncConnectionPool` management in `lifespan`.
-   Refactored `get_checkpointer` to yield `AsyncPostgresSaver` from the global pool.

```diff
- async def get_checkpointer() -> AsyncSqliteSaver:
+ async def get_checkpointer() -> AsyncIterator[AsyncPostgresSaver]:
+     async with database.pool.connection() as conn:
+         yield AsyncPostgresSaver(conn)
```

### State Management (`ingestion_state.py`, `ingestion_nodes.py`)
-   Migrated `IngestionGraphState` to inherit from `MessagesState`.
-   Renamed `steps_history` (List[str]) to `messages` (List[BaseMessage]).

## 3. Verification

### Automated Tests
`tests/integration/functional/test_postgres_persistence.py` passes successfully, validating:
1.  Connection pool initialization.
2.  Table creation (`setup()`).
3.  Ingestion Graph execution and persistence.
4.  Retrieval via `get_state`.

```bash
uv run pytest tests/integration/functional/test_postgres_persistence.py

# Output
tests/integration/functional/test_postgres_persistence.py::test_postgres_persistence_flow PASSED [100%]
```

### Manual Verification
Postgres container is healthy:
`rag-postgres` is running on port 5432.
