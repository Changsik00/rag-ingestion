from psycopg_pool import AsyncConnectionPool

from app.domain.interfaces.session_repository import SessionRepository


class PostgresSessionRepository(SessionRepository):
    def __init__(self, pool: AsyncConnectionPool):
        self.pool = pool

    async def delete_session(self, thread_id: str) -> None:
        """
        Deletes session data from LangGraph Postgres tables.
        Target tables: checkpoint_writes, checkpoint_blobs, checkpoints.
        """
        if not self.pool:
            raise RuntimeError("Database pool is not initialized")

        async with self.pool.connection() as conn:
            # LangGraph Postgres Checkpointer Tables
            # Checkpoints, Writes, Blobs (if any associated with thread)
            # Order: Child -> Parent (Writes/Blobs -> Checkpoints)
            await conn.execute("DELETE FROM checkpoint_writes WHERE thread_id = %s", (thread_id,))
            await conn.execute("DELETE FROM checkpoint_blobs WHERE thread_id = %s", (thread_id,))
            await conn.execute("DELETE FROM checkpoints WHERE thread_id = %s", (thread_id,))
            # Ensure commit if not in autocommit mode (psycopg 3 pool usually needs explicit commit or autocommit)
            # Using set_autocommit(True) or explicit commit if transaction block.
            # Here we use implicit transaction control if needed, but context manager commits if no error?
            # Psycopg3 connection-context commits on exit if no exception? No, that's regular connection.
            # Let's be explicit like the original code.
            await conn.set_autocommit(True)
