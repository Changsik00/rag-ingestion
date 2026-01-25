from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException

from app.domain.entities.job import IngestionJob
from app.domain.interfaces.job_repository import JobRepository
from app.interfaces.api.dependencies import get_ingestion_service, get_job_repository
from app.use_cases.ingestion import IngestionService

router = APIRouter()

@router.get("", response_model=list[IngestionJob])
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
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    return job

@router.post("/{job_id}/retry")
async def retry_job(
    job_id: str,
    background_tasks: BackgroundTasks,
    repo: JobRepository = Depends(get_job_repository),
    service: IngestionService = Depends(get_ingestion_service),
):
    job = repo.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")

    try:
        new_job = service.create_job(job.source_url, retry_of=job_id)
        background_tasks.add_task(service.process_job, new_job.job_id)
        return {"job_id": new_job.job_id, "status": new_job.status}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
