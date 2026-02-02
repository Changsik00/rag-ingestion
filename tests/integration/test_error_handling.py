from fastapi import FastAPI
from fastapi.testclient import TestClient
from app.interfaces.api.error_handlers import register_exception_handlers
from app.domain.exceptions import EntityNotFoundException, DuplicateEntityException, DomainException

def test_exception_handlers():
    test_app = FastAPI()
    register_exception_handlers(test_app)

    @test_app.get("/404")
    def raise_404():
        raise EntityNotFoundException("TestEntity", "123")

    @test_app.get("/409")
    def raise_409():
        raise DuplicateEntityException("TestEntity", "123")
    
    @test_app.get("/400")
    def raise_400():
        raise DomainException("Invalid domain logic")

    @test_app.get("/500")
    def raise_500():
        raise ValueError("Unexpected error")

    client = TestClient(test_app, raise_server_exceptions=False)

    # Test 404
    resp = client.get("/404")
    assert resp.status_code == 404
    data = resp.json()
    assert data["status"] == "error"
    assert data["error_code"] == "ENTITY_NOT_FOUND"
    
    # Test 409
    resp = client.get("/409")
    assert resp.status_code == 409
    assert resp.json()["error_code"] == "DUPLICATE_ENTITY"

    # Test 400
    resp = client.get("/400")
    assert resp.status_code == 400
    assert resp.json()["error_code"] == "DOMAIN_ERROR"

    # Test 500
    resp = client.get("/500")
    assert resp.status_code == 500
    assert resp.json()["error_code"] == "INTERNAL_SERVER_ERROR"
