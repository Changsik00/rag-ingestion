from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from app.domain.services.storage_integrity_service import StorageIntegrityService
from app.interfaces.api.dependencies import get_checkpointer, get_semantic_extractor, get_storage_integrity_service

router = APIRouter()


@router.get("/stats")
async def get_stats(service: Annotated[StorageIntegrityService, Depends(get_storage_integrity_service)]):
    try:
        return service.get_drift_report()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/reports")
async def get_reports(service: Annotated[StorageIntegrityService, Depends(get_storage_integrity_service)]):
    try:
        return service.get_document_drift_report()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/documents/{doc_id}/diagnostic")
async def get_diagnostic(
    doc_id: str, service: Annotated[StorageIntegrityService, Depends(get_storage_integrity_service)]
):
    try:
        sample = service.get_missing_chunk_sample(doc_id)
        return {"doc_id": doc_id, "sample": sample}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/documents/{doc_id}/preview-context")
async def get_preview_context(
    doc_id: str, service: Annotated[StorageIntegrityService, Depends(get_storage_integrity_service)]
):
    try:
        context = await service.get_cleaned_context(doc_id)
        return {"doc_id": doc_id, "context": context}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/documents/{doc_id}/sync")
async def sync_document(
    doc_id: str, service: Annotated[StorageIntegrityService, Depends(get_storage_integrity_service)]
):
    try:
        return service.sync_document(doc_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/documents/{doc_id}/enrich")
async def enrich_document(
    doc_id: str,
    service: Annotated[StorageIntegrityService, Depends(get_storage_integrity_service)],
    checkpointer=Depends(get_checkpointer),
):
    try:
        extractor = await get_semantic_extractor(checkpointer)
        return await service.enrich_knowledge_graph(doc_id, extractor)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sync-all")
async def sync_all(service: Annotated[StorageIntegrityService, Depends(get_storage_integrity_service)]):
    # BackgroundTasks 를 사용하거나 간단히 실행 (현재는 동기 실행으로 구현되어 있음)
    try:
        service.sync_all()
        return {"success": True, "message": "Bulk sync completed"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
