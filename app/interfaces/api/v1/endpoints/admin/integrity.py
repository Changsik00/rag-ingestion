from typing import Annotated

from fastapi import APIRouter, Depends

from app.application.services.integrity import Integrity
from app.interfaces.api.dependencies import get_integrity_service

router = APIRouter()


@router.post("/reset")
async def reset_all_data(
    service: Annotated[Integrity, Depends(get_integrity_service)],
):
    """
    [Danger] 시스템의 모든 데이터(Neo4j, Chroma, SQLite)를 초기화합니다.
    """
    result = await service.reset_all()
    return {"status": "success", "message": "All data has been reset.", "details": result._asdict()}
