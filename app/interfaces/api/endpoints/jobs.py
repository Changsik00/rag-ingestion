from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Annotated
from app.domain.entities.job import IngestionJob
from app.domain.interfaces.job_repository import JobRepository
from app.use_cases.ingestion import IngestionService
from app.domain.models.ingest import IngestResponse
from app.interfaces.api.dependencies import get_job_repository, get_ingestion_service

router = APIRouter(prefix="/jobs", tags=["jobs"])

@router.get("", response_model=List[IngestionJob])
async def list_jobs(
    limit: int = 50,
    repo: JobRepository = Depends(get_job_repository)
):
    return repo.list_jobs(limit=limit)

@router.get("/{job_id}", response_model=IngestionJob)
async def get_job(
    job_id: str,
    repo: JobRepository = Depends(get_job_repository)
):
    job = repo.get_job(job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Job {job_id} not found"
        )
    return job

@router.post("/{job_id}/retry", response_model=IngestResponse)
async def retry_job(
    job_id: str,
    repo: JobRepository = Depends(get_job_repository),
    service: IngestionService = Depends(get_ingestion_service)
):
    job = repo.get_job(job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Job {job_id} not found"
        )
    
    # Re-trigger ingestion (creates a new job trace)
    try:
        result = service.ingest(job.source_url)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
