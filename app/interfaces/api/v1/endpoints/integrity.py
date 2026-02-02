from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.application.services.integrity import Integrity
from app.interfaces.api.dependencies import get_integrity_service
from app.interfaces.api.v1.dto.integrity import ResetResultResponse

router = APIRouter(tags=["Integrity"])


@router.post("/reset", response_model=ResetResultResponse, status_code=status.HTTP_202_ACCEPTED)
async def reset_all_data(
    service: Annotated[Integrity, Depends(get_integrity_service)],
):
    """
    [Danger] 시스템의 모든 데이터(Neo4j, Chroma, SQLite)를 초기화합니다.
    """
    result = await service.reset_all()
    return ResetResultResponse(status="success", message="All data has been reset.", details=result._asdict())
