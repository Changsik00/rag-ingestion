from fastapi import APIRouter, BackgroundTasks, Depends, status

from app.application.services.ingestion import Ingestion
from app.domain.entities.job import IngestionJob
from app.domain.exceptions import EntityNotFoundError
from app.domain.interfaces.job_repository import JobRepository
from app.infrastructure.ai.ingestion_orchestrator import IngestionOrchestrator
from app.interfaces.api.dependencies import get_ingestion_orchestrator, get_ingestion_service, get_job_repository
from app.interfaces.api.v1.dto.jobs import (
    JobResponse,
    JobStatusResponse,
    ResumeRequest,
    ResumeResponse,
    ThreadResponse,
    TraceResponse,
)

router = APIRouter(tags=["Jobs"])


def map_job_to_response(job: IngestionJob) -> JobResponse:
    return JobResponse(
        job_id=job.job_id,
        current_status=job.status,
        source_url=job.source_url,
        created_at=job.created_at,
        updated_at=job.updated_at,
        docs_ids=job.docs_ids,
        metadata={},
    )


@router.get("", response_model=list[JobResponse])
async def list_jobs(limit: int = 50, repo: JobRepository = Depends(get_job_repository)):
    jobs = repo.list_jobs(limit=limit)
    return [map_job_to_response(job) for job in jobs]


@router.get("/active/threads", response_model=list[ThreadResponse])
async def list_active_threads(limit: int = 10, adapter: IngestionOrchestrator = Depends(get_ingestion_orchestrator)):
    """List threads managed by LangGraph checkpointer."""
    threads = await adapter.list_threads(limit=limit)
    return [
        ThreadResponse(
            thread_id=t.config["configurable"]["thread_id"],
            checkpoint_id=t.checkpoint["id"],
            metadata=t.metadata,
        )
        for t in threads
    ]


@router.get("/{job_id}", response_model=JobResponse)
async def get_job(job_id: str, repo: JobRepository = Depends(get_job_repository)):
    job = repo.get_job(job_id)
    if not job:
        raise EntityNotFoundError("Job", job_id)
    return map_job_to_response(job)


@router.get("/{job_id}/status", response_model=JobStatusResponse)
async def get_job_status(job_id: str, adapter: IngestionOrchestrator = Depends(get_ingestion_orchestrator)):
    """Get LangGraph execution status for a job/thread."""
    status = await adapter.get_thread_status(job_id)
    return JobStatusResponse(job_id=job_id, current_status=status)


@router.get("/{job_id}/trace", response_model=TraceResponse)
async def get_job_trace(job_id: str, adapter: IngestionOrchestrator = Depends(get_ingestion_orchestrator)):
    """Get LangGraph state snapshot."""
    snapshot = await adapter.get_state(job_id)
    return TraceResponse(
        values=snapshot.values,
        next=snapshot.next,
        tasks=str(snapshot.tasks),
        metadata=snapshot.metadata,
    )


@router.post("/{job_id}/resume", response_model=ResumeResponse, status_code=status.HTTP_202_ACCEPTED)
async def resume_job(
    job_id: str, request: ResumeRequest, adapter: IngestionOrchestrator = Depends(get_ingestion_orchestrator)
):
    """Resume an interrupted job."""
    result = await adapter.resume(job_id, request.input)
    return ResumeResponse(result_metadata=result.get("metadata", None))


@router.post("/{job_id}/retry", response_model=JobResponse, status_code=status.HTTP_202_ACCEPTED)
async def retry_job(
    job_id: str,
    background_tasks: BackgroundTasks,
    repo: JobRepository = Depends(get_job_repository),
    service: Ingestion = Depends(get_ingestion_service),
):
    job = repo.get_job(job_id)
    if not job:
        raise EntityNotFoundError("Job", job_id)

    new_job = service.create_job(job.source_url, retry_of=job_id)
    background_tasks.add_task(service.process_job, new_job.job_id)
    return map_job_to_response(new_job)
