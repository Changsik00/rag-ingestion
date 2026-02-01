from fastapi import APIRouter

from app.interfaces.api.v1.endpoints import (
    entities,
    graph,
    ingest,
    integrity,
    jobs,
    rag,
    storage,
    system,
)

router = APIRouter()

# Register all sub-routers with appropriate prefixes
router.include_router(ingest.router)
router.include_router(jobs.router, prefix="/jobs")
router.include_router(entities.router, prefix="/entities")
router.include_router(rag.router, prefix="/rag")
router.include_router(storage.router, prefix="/storage")
router.include_router(graph.router, prefix="/graph")
router.include_router(integrity.router, prefix="/integrity")
router.include_router(system.router)  # /health, /documents
