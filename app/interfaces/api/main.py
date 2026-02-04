from contextlib import asynccontextmanager

from fastapi import FastAPI
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from psycopg_pool import AsyncConnectionPool

from app.core import database
from app.core.config import get_settings
from app.interfaces.api.error_handlers import register_exception_handlers
from app.interfaces.api.v1.endpoints import router as v1_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    # initialize pool
    pool = AsyncConnectionPool(conninfo=settings.POSTGRES_DB_URL, max_size=20)
    database.pool = pool
    await pool.open()

    # ensure tables exist
    async with pool.connection() as conn:
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

app.include_router(v1_router, prefix="/v1")
