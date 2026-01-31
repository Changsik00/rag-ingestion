from typing import Any

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from pydantic import BaseModel

from app.application.services.ingestion import IngestionUseCase
from app.domain.entities.job import IngestionJob
from app.domain.interfaces.job_repository import JobRepository
from app.infrastructure.ai.orchestrators.ingestion_orchestrator import IngestionOrchestrator
from app.interfaces.api.dependencies import get_ingestion_service, get_job_repository, get_ingestion_orchestrator

router = APIRouter()


class ResumeRequest(BaseModel):
    input: dict[str, Any]


@router.get("", response_model=list[IngestionJob])
async def list_jobs(limit: int = 50, repo: JobRepository = Depends(get_job_repository)):
    return repo.list_jobs(limit=limit)


@router.get("/active/threads")
async def list_active_threads(limit: int = 10, adapter: IngestionOrchestrator = Depends(get_ingestion_orchestrator)):
    """List threads managed by LangGraph checkpointer."""
    try:
        threads = await adapter.list_threads(limit=limit)
        return [
            {
                "thread_id": t.config["configurable"]["thread_id"],
                "checkpoint_id": t.checkpoint["id"],
                "metadata": t.metadata,
            }
            for t in threads
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{job_id}", response_model=IngestionJob)
async def get_job(job_id: str, repo: JobRepository = Depends(get_job_repository)):
    job = repo.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    return job


@router.get("/{job_id}/status")
async def get_job_status(job_id: str, adapter: IngestionOrchestrator = Depends(get_ingestion_orchestrator)):
    """Get LangGraph execution status for a job/thread."""
    try:
        status = await adapter.get_thread_status(job_id)
        return {"status": status}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{job_id}/trace")
async def get_job_trace(job_id: str, adapter: IngestionOrchestrator = Depends(get_ingestion_orchestrator)):
    """Get LangGraph state snapshot."""
    try:
        snapshot = await adapter.get_state(job_id)
        return {
            "values": snapshot.values,
            "next": snapshot.next,
            "tasks": str(snapshot.tasks),
            "metadata": snapshot.metadata,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{job_id}/resume")
async def resume_job(job_id: str, request: ResumeRequest, adapter: IngestionOrchestrator = Depends(get_ingestion_orchestrator)):
    """Resume an interrupted job."""
    try:
        result = await adapter.resume(job_id, request.input)
        return {"status": "Resumed", "result_metadata": result.get("metadata", None)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{job_id}/retry")
async def retry_job(
    job_id: str,
    background_tasks: BackgroundTasks,
    repo: JobRepository = Depends(get_job_repository),
    service: IngestionUseCase = Depends(get_ingestion_service),
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
