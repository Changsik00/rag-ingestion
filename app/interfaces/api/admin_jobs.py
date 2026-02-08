from fastapi import APIRouter, Depends, HTTPException, Query

from app.application.services.ingestion import Ingestion
from app.domain.entities.job import IngestionJob, JobStatus
from app.domain.interfaces.job_repository import JobRepository
from app.interfaces.api.dependencies import get_ingestion_service, get_job_repository

router = APIRouter(prefix="/admin/jobs", tags=["admin"])


@router.get("/", response_model=list[IngestionJob])
async def list_jobs(
    status: JobStatus | None = Query(None, description="Filter by job status"),
    limit: int = Query(100, description="Maximum number of jobs to return"),
    job_repository: JobRepository = Depends(get_job_repository),
) -> list[IngestionJob]:
    """
    Admin Endpoint: List all ingestion jobs with optional filtering.
    
    [Spec 072] Supports filtering by status (e.g., SKIPPED) to view jobs that were
    skipped due to deduplication.
    """
    if not hasattr(job_repository, "get_jobs"):
        # Fallback: If repository doesn't have get_jobs method, return empty list
        raise HTTPException(
            status_code=501, 
            detail="get_jobs() method not implemented in JobRepository"
        )
    
    jobs = job_repository.get_jobs(status=status, limit=limit)
    return jobs


@router.post("/{job_id}/force-refresh")
async def force_refresh_job(
    job_id: str,
    ingestion: Ingestion = Depends(get_ingestion_service),
    job_repository: JobRepository = Depends(get_job_repository),
) -> dict:
    """
    Admin Endpoint: Force refresh a job, bypassing deduplication checks.
    
    [Spec 072] This is useful when a job was skipped due to deduplication,
    but the admin wants to forcefully re-ingest the content.
    """
    # 1. Check if job exists
    job = job_repository.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    
    # 2. Re-process the job with force_refresh=True
    try:
        await ingestion.process_job(job_id, force_refresh=True)
        return {
            "message": f"Job {job_id} re-ingested successfully",
            "job_id": job_id,
            "source_url": job.source_url,
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to re-ingest job {job_id}: {str(e)}"
        )
