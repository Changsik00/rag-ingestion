from pydantic import BaseModel


class ResetResultResponse(BaseModel):
    status: str
    message: str
    details: dict[str, str]


class DriftReportResponse(BaseModel):
    total_primary: int
    total_target: int
    missing_count: int
    missing_ids: list[str]
    orphan_count: int
    orphan_ids: list[str]
    drift_ratio: float


class DocumentDriftResponse(BaseModel):
    id: str
    title: str
    url: str
    total_chunks: int
    target_chunks: int
    drift_ratio: float
    status: str
    missing_sample: str = ""


class DiagnosticResponse(BaseModel):
    doc_id: str
    snippet: str


class PreviewContextResponse(BaseModel):
    doc_id: str
    content: str


class SyncDocumentResponse(BaseModel):
    success: bool
    count: int = 0
    error: str | None = None


class EnrichResponse(BaseModel):
    success: bool
    entities: int = 0
    rels: int = 0
    error: str | None = None
