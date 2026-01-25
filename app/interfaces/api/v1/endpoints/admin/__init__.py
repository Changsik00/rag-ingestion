from fastapi import APIRouter
from app.interfaces.api.v1.endpoints.admin import storage, rag, jobs, graph

router = APIRouter()

router.include_router(storage.router, prefix="/storage", tags=["Admin Storage"])
router.include_router(rag.router, prefix="/rag", tags=["Admin RAG"])
router.include_router(jobs.router, prefix="/jobs", tags=["Admin Jobs"])
router.include_router(graph.router, prefix="/graph", tags=["Admin Graph"])
