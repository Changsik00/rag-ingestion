from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from app.interfaces.api.v1.dto.common import BaseResponse


class JobResponse(BaseResponse):
    """
    Standard Job Information.
    """

    job_id: str
    current_status: str = Field(..., alias="current_status")
    status: str = Field(default=None, alias="status")  # [Spec 072] Alias for compatibility
    source_url: str
    created_at: datetime | None = None
    updated_at: datetime | None = None
    docs_ids: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    skip_reason: str | None = Field(default=None)  # [Spec 072]
    error_message: str | None = Field(default=None)  # For failed jobs

    class Config:
        populate_by_name = True  # Allow both current_status and status


class JobStatusResponse(BaseResponse):
    """
    Job Status Wrapper.
    """

    job_id: str
    current_status: str
    checkpoint_id: str | None = None


class ResumeRequest(BaseModel):
    """
    Request body for resuming a job.
    """

    input: dict[str, Any]


class ResumeResponse(BaseResponse):
    """
    Response for resume action.
    """

    result_metadata: dict[str, Any] | None = None


class ThreadResponse(BaseModel):
    """
    Thread information managed by checkpointer.
    """

    thread_id: str
    checkpoint_id: str
    metadata: dict[str, Any]


class TraceResponse(BaseResponse):
    """
    LangGraph state snapshot.
    """

    values: dict[str, Any]
    next: tuple[str, ...] | list[str]
    tasks: str
    metadata: dict[str, Any]
