from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from app.domain.entities.document import Document
from app.domain.interfaces.document_repository import DocumentRepository
from app.interfaces.api.dependencies import get_repository
from app.interfaces.api.v1.dto.system import SystemStatusResponse
from app.interfaces.api.v1.dto.rag import DocumentDTO

router = APIRouter(tags=["System"])


@router.get("/health", response_model=SystemStatusResponse)
async def health_check():
    # Placeholder values for uptime and components
    return SystemStatusResponse(
        version="1.0.0", 
        uptime=0.0, 
        components={"api": "ok", "db": "ok"}
    )


@router.get("/documents", response_model=list[DocumentDTO])
async def list_documents(repository: Annotated[DocumentRepository, Depends(get_repository)], limit: int = 10):
    docs = repository.list_documents(limit=limit)
    return [
        DocumentDTO(
            id=str(d.id),
            content=d.content,
            metadata=d.metadata.model_dump(),
            score=None
        ) for d in docs
    ]
