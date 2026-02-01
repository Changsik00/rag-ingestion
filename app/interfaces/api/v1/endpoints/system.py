from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException

from app.domain.entities.document import Document
from app.domain.interfaces.document_repository import DocumentRepository
from app.interfaces.api.dependencies import get_repository

router = APIRouter(tags=["System"])

@router.get("/health")
async def health_check():
    return {"status": "ok"}

@router.get("/documents", response_model=list[Document])
async def list_documents(
    repository: Annotated[DocumentRepository, Depends(get_repository)], 
    limit: int = 10
):
    try:
        return repository.list_documents(limit=limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
