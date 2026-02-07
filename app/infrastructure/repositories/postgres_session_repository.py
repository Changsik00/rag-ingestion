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
            # Using a transaction block with autocommit behavior for simple deletes
            async with conn.transaction():
                await conn.execute("DELETE FROM checkpoint_writes WHERE thread_id = %s", (thread_id,))
                await conn.execute("DELETE FROM checkpoint_blobs WHERE thread_id = %s", (thread_id,))
                await conn.execute("DELETE FROM checkpoints WHERE thread_id = %s", (thread_id,))
