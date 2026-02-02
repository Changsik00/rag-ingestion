from app.interfaces.api.v1.dto.common import BaseResponse


class SystemStatusResponse(BaseResponse):
    """
    System Health Status.
    """

    version: str
    uptime: float
    components: dict[str, str]  # e.g., {"db": "ok", "cache": "ok"}


class IntegrityStatusResponse(BaseResponse):
    """
    Data Integrity Check Response.
    """

    details: dict[str, str]  # e.g., {"neo4j": "ok", "chroma": "ok"}
