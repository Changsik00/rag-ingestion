from fastapi import FastAPI

from app.interfaces.api.error_handlers import register_exception_handlers
from app.interfaces.api.v1.endpoints import router as v1_router

app = FastAPI(
    title="RAG Ingestion API",
    description="API for ingesting web content into Markdown and storing it in Atomic Layer",
    version="1.0.0",
)

register_exception_handlers(app)

app.include_router(v1_router, prefix="/v1")
