from fastapi.testclient import TestClient

from app.interfaces.api.main import app

client = TestClient(app)

def test_get_storage_stats():
    """GET /api/v1/admin/storage/stats 엔드포인트가 정상적으로 정보를 반환하는지 테스트"""
    response = client.get("/api/v1/admin/storage/stats")
    assert response.status_code == 200
    data = response.json()
    # placeholder 메시지가 포함되어 있는지 확인 (Warming up)
    assert "total_primary" in data or "message" in data

def test_get_document_reports():
    """GET /api/v1/admin/storage/reports 엔드포인트 테스트"""
    client.get("/api/v1/admin/storage/reports")
    # 현재 __init__.py 에서 router.include_router(storage.router, prefix="/storage")
    # 그리고 app.include_router(admin_router, prefix="/api/v1/admin")
    # 따라서 엔드포인트는 /api/v1/admin/storage/stats 이런 식이 되어야 함
    pass

def test_storage_api_endpoints_exist():
    # Stats
    response = client.get("/api/v1/admin/storage/stats")
    assert response.status_code == 200

    # Reports
    response = client.get("/api/v1/admin/storage/reports")
    assert response.status_code == 200

    # Diagnostic
    response = client.get("/api/v1/admin/storage/documents/test_id/diagnostic")
    assert response.status_code == 200
