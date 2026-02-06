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
            "문장과 문장 사이의 의미가 얼마나 달라졌을 때 자를지를 결정하는 수학적 기준입니다:\n\n"
            "1. **percentile** (기본값): '상위 X%만 자르자'\n"
            "   - 전체 텍스트에서 상대적으로 의미 변화가 가장 큰 상위 구간을 골라냅니다.\n"
            "   - 텍스트 길이나 내용에 상관없이 일정한 비율로 나누고 싶을 때 유리합니다.\n"
            "2. **standard_deviation**: '유난히 튀는 구간만 자르자'\n"
            "   - 평균보다 훨씬 더 큰 차이가 나는 '아웃라이어' 지점을 찾습니다.\n"
            "   - 의미가 아주 급격하게 변하는 확실한 주제 전환점만 잡고 싶을 때 사용합니다.\n"
            "3. **interquartile**: '통계적 이상치에서 자르자'\n"
            "   - Box Plot 방식(IQR)을 사용하여 극단적인 값의 영향을 덜 받으면서 적당히 튀는 지점을 찾습니다.\n"
            "4. **gradient**: '변화의 속도가 빠를 때 자르자'\n"
            "   - 차이가 갑자기 커지는(기울기가 가파른) 구간을 예민하게 잡아냅니다."
        ),
    )
    breakpoint_threshold_amount: float = Field(
        default=90.0,
        description=(
            "선택한 Type에 대한 임계값(Threshold)입니다:\n\n"
            "- **percentile**: 백분위수 (기본 90.0). 예: 90 = 상위 10% 지점.\n"
            "- **standard_deviation**: 표준편차 배수(Sigma). 예: 3.0 = 3시그마.\n"
            "- **interquartile**: IQR 배수. 예: 1.5 (통계적 이상치 기준).\n"
            "- **gradient**: 기울기 임계값.\n\n"
            "💡 **추천 가이드**\n"
            "- 잘 모르겠다면?: 기본값 **percentile (90.0)**이 가장 무난합니다.\n"
            "- 청크가 너무 잘게 쪼개지면 -> 값을 올리세요 (예: 95)\n"
            "- 청크가 너무 크면 -> 값을 내리세요 (예: 80)\n"
            "- 주제 전환이 확실한 글: **standard_deviation**을 추천합니다."
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
    force_refresh: bool = Field(default=False, description="Whether to force ingestion even if duplicate exists")
    bypass_early_dedup: bool = Field(default=False, description="[DEBUG/TEST] Skip API-level check but still allow worker dedup.")


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
