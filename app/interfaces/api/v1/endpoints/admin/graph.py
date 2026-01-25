from fastapi import APIRouter

router = APIRouter()

@router.get("/schema")
async def get_schema():
    return {"message": "Admin Graph Schema placeholder"}
