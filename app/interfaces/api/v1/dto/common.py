from typing import Any, Generic, Literal, TypeVar

from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")


class BaseResponse(BaseModel):
    """
    Standard API Response Envelope.
    All successful responses should satisfy this schema.
    """

    model_config = ConfigDict(from_attributes=True)
    status: str = Field(default="success", description="Response status (success/error)")
    message: str | None = Field(default=None, description="Optional message")


class GenericResponse(BaseResponse, Generic[T]):
    """
    Generic Data Response Wrapper.
    """

    data: T | None = Field(default=None, description="Payload data")


class ErrorResponse(BaseResponse):
    """
    Standard Error Response.
    """

    status: Literal["error"] = "error"
    error_code: str = Field(..., description="Machine readable error code")
    details: dict[str, Any] | None = Field(default=None, description="Error details or debug info")


class PaginationResponse(GenericResponse[list[T]]):
    """
    Standard Pagination Response.
    """

    total: int = Field(..., description="Total count of items")
    page: int = Field(default=1, description="Current page number")
    size: int = Field(default=50, description="Items per page")
