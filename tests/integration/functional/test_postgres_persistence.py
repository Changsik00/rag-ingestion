import uuid

import pytest
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from psycopg_pool import AsyncConnectionPool

from app.application.interfaces.llm import LLMInterface
from app.core.config import get_settings
from app.domain.value_objects.extracted_metadata import ExtractedMetadata
from app.infrastructure.ai.ingestion_orchestrator import IngestionOrchestrator


# Mock LLM needed for Orchestrator
class MockInnerLLM(LLMInterface):
    async def aextract_metadata(self, text: str, thread_id: str | None = None) -> ExtractedMetadata | None:
        return ExtractedMetadata(
            title="Persisted Title", summary="Summary", keywords=["test"], entities={}, language="en"
        )

    def generate(self, prompt: str) -> str:
        return "mock"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_postgres_persistence_flow():
    settings = get_settings()

    # 1. Setup Connection Pool (Test Scoped)
    try:
        pool = AsyncConnectionPool(conninfo=settings.postgres_db_url, min_size=1, max_size=2)
        await pool.open()
    except Exception as e:
        pytest.skip(f"Could not connect to Postgres: {e}")

    thread_id = str(uuid.uuid4())

    try:
        # 2. Setup Tables
        async with pool.connection() as conn:
            await conn.set_autocommit(True)
            saver = AsyncPostgresSaver(conn)
            await saver.setup()

        # 3. Create Orchestrator with manual checkpointer injection
        # Note: In real app, checkpointer is passed as dependency.
        # Here we manually simulate what dependency injection does.

        async with pool.connection() as conn:
            checkpointer = AsyncPostgresSaver(conn)
            orchestrator = IngestionOrchestrator(llm=MockInnerLLM(), checkpointer=checkpointer)

            # 4. Execute Workflow
            # This should persist state to Postgres
            await orchestrator.aextract_metadata("Test content", thread_id=thread_id)

            # 5. Verify Persistence
            # Check state using get_state
            snapshot = await orchestrator.get_state(thread_id)
            assert snapshot.values is not None, "Snapshot should exist"
            assert snapshot.values["metadata"] is not None
            assert snapshot.values["metadata"].title == "Persisted Title"

            # Verify basic messages history
            assert "messages" in snapshot.values
            assert len(snapshot.values["messages"]) > 0

    finally:
        await pool.close()
