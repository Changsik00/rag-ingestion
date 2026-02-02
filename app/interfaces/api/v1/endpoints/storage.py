from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.application.services.integrity import Integrity
from app.interfaces.api.dependencies import get_checkpointer, get_integrity_service, get_semantic_extractor
from app.interfaces.api.v1.dto.common import BaseResponse
from app.interfaces.api.v1.dto.integrity import (
    DiagnosticResponse,
    DocumentDriftResponse,
    DriftReportResponse,
    EnrichResponse,
    PreviewContextResponse,
    SyncDocumentResponse,
)

router = APIRouter(tags=["Storage"])


@router.get("/stats", response_model=DriftReportResponse)
async def get_stats(service: Annotated[Integrity, Depends(get_integrity_service)]):
    return service.get_drift_report()


@router.get("/reports", response_model=list[DocumentDriftResponse])
async def get_reports(service: Annotated[Integrity, Depends(get_integrity_service)]):
    return service.get_document_drift_report()


@router.get("/documents/{doc_id}/diagnostic", response_model=DiagnosticResponse)
async def get_diagnostic(doc_id: str, service: Annotated[Integrity, Depends(get_integrity_service)]):
    sample = service.get_missing_chunk_sample(doc_id)
    return DiagnosticResponse(doc_id=doc_id, snippet=sample)


@router.get("/documents/{doc_id}/preview-context", response_model=PreviewContextResponse)
async def get_preview_context(doc_id: str, service: Annotated[Integrity, Depends(get_integrity_service)]):
    context = await service.get_cleaned_context(doc_id)
    return PreviewContextResponse(doc_id=doc_id, content=context)


@router.post("/documents/{doc_id}/sync", response_model=SyncDocumentResponse, status_code=status.HTTP_202_ACCEPTED)
async def sync_document(doc_id: str, service: Annotated[Integrity, Depends(get_integrity_service)]):
    result = service.sync_document(doc_id)
    return SyncDocumentResponse(**result)


@router.post("/documents/{doc_id}/enrich", response_model=EnrichResponse, status_code=status.HTTP_202_ACCEPTED)
async def enrich_document(
    doc_id: str,
    service: Annotated[Integrity, Depends(get_integrity_service)],
    checkpointer=Depends(get_checkpointer),
):
    extractor = await get_semantic_extractor(checkpointer)
    result = await service.enrich_knowledge_graph(doc_id, extractor)
    return EnrichResponse(**result)


@router.post("/sync-all", response_model=BaseResponse, status_code=status.HTTP_202_ACCEPTED)
async def sync_all(service: Annotated[Integrity, Depends(get_integrity_service)]):
    # BackgroundTasks 를 사용하거나 간단히 실행 (현재는 동기 실행으로 구현되어 있음)
    service.sync_all()
    return BaseResponse(message="Bulk sync completed")
