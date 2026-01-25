from fastapi import APIRouter

router = APIRouter()

@router.get("/stats")
async def get_stats():
    return {"message": "Admin Storage Stats placeholder"}

@router.get("/reports")
async def get_reports():
    return {"message": "Admin Storage Reports placeholder"}

@router.get("/documents/{doc_id}/diagnostic")
async def get_diagnostic(doc_id: str):
    return {"message": f"Admin Storage Diagnostic placeholder for {doc_id}"}
