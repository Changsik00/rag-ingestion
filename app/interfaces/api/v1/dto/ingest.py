from typing import Any, Literal

from pydantic import BaseModel, Field, HttpUrl, field_validator

from app.interfaces.api.v1.dto.common import BaseResponse


class ChunkingConfigDTO(BaseModel):
    """
    Configuration for text chunking strategies.
    """

    strategy: Literal["recursive", "semantic"] = Field(default="recursive", description="Chunking strategy to use")

    # Recursive specific
    chunk_size: int = Field(default=1000, gt=0, description="Size of each chunk (recursive)")
    chunk_overlap: int = Field(default=200, ge=0, description="Overlap between chunks (recursive)")

    # Semantic specific
    breakpoint_threshold_type: Literal["percentile", "standard_deviation", "interquartile", "gradient"] = Field(
        default="percentile",
        description=(
            "Method to determine the semantic split point:\n"
            "- **percentile** (default): Splits at the top X% of differences (relative).\n"
            "- **standard_deviation**: Splits at outliers > Mean + (Amount * StdDev).\n"
            "- **interquartile**: Splits at outliers > Q3 + (Amount * IQR).\n"
            "- **gradient**: Splits where the gradient/slope of difference is high."
        ),
    )
    breakpoint_threshold_amount: float = Field(
        default=90.0,
        description=(
            "Sensitivity threshold based on the selected type:\n"
            "- **percentile**: The percentile value (e.g., 90.0 means split at top 10% differences).\n"
            "- **standard_deviation**: The sigma multiplier (e.g., 3.0).\n"
            "- **interquartile**: The IQR multiplier (e.g., 1.5).\n"
            "- **gradient**: The slope threshold."
        ),
    )
    number_of_chunks: int | None = Field(
        default=None, gt=0, description="Target number of chunks (optional constraint)"
    )

    @field_validator("chunk_overlap")
    @classmethod
    def validate_overlap(cls, v: int, info: Any) -> int:
        if "chunk_size" in info.data and v >= info.data["chunk_size"]:
            raise ValueError("chunk_overlap must be smaller than chunk_size")
        return v


class IngestRequest(BaseModel):
    url: HttpUrl = Field(..., description="Target URL to ingest")
    chunking_config: ChunkingConfigDTO | None = Field(default=None, description="Optional chunking configuration")


class IngestResponse(BaseResponse):
    """
    Response for debug scrape.
    """

    url: HttpUrl = Field(..., description="Source URL")
    markdown: str = Field(..., description="Extracted markdown content")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Extraction metadata")


class AsyncIngestResponse(BaseResponse):
    """
    Response for async ingestion job creation.
    """

    job_id: str = Field(..., description="Unique Job ID to track progress")
    current_status: str = Field(..., description="Current status of the job (e.g. PENDING)")


class MultiAsyncIngestResponse(BaseResponse):
    """
    Response for multiple async ingestion jobs (file upload).
    """

    jobs: list[AsyncIngestResponse] = Field(..., description="List of created jobs")
