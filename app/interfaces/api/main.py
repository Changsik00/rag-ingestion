from contextlib import asynccontextmanager

from fastapi import FastAPI
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from psycopg_pool import AsyncConnectionPool

from app.core import database
from app.core.config import get_settings
from app.interfaces.api.admin_jobs import router as admin_jobs_router
from app.interfaces.api.error_handlers import register_exception_handlers
from app.interfaces.api.v1.endpoints import router as v1_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    # initialize pool
    pool = AsyncConnectionPool(conninfo=settings.postgres_db_url, max_size=20, open=False)
    database.pool = pool
    await pool.open()

    # ensure tables exist
    async with pool.connection() as conn:
        await conn.set_autocommit(True)
        saver = AsyncPostgresSaver(conn)
        await saver.setup()

    yield

    await pool.close()


app = FastAPI(
    title="RAG Ingestion API",
    description="API for ingesting web content into Markdown and storing it in Atomic Layer",
    version="1.0.0",
    lifespan=lifespan,
)

register_exception_handlers(app)

# [Spec 072] Include Admin API under /v1 prefix for consistency
app.include_router(v1_router, prefix="/v1")
app.include_router(admin_jobs_router, prefix="/v1")  # Admin API: /v1/admin/jobs
