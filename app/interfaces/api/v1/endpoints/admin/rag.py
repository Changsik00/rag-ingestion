from fastapi import APIRouter

router = APIRouter()

@router.get("/threads")
async def list_threads():
    return {"message": "Admin RAG Threads placeholder"}
