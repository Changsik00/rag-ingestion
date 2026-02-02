from app.interfaces.api.v1.dto.common import GenericResponse, ErrorResponse, PaginationResponse

def test_generic_response_creation():
    response = GenericResponse[str](data="test_data")
    assert response.status == "success"
    assert response.data == "test_data"
    assert response.message is None

def test_generic_response_json():
    response = GenericResponse[int](data=123, message="ok")
    json_data = response.model_dump()
    assert json_data["status"] == "success"
    assert json_data["data"] == 123
    assert json_data["message"] == "ok"

def test_error_response_creation():
    response = ErrorResponse(error_code="ERR_001", message="Something wrong")
    assert response.status == "error"
    assert response.error_code == "ERR_001"
    assert response.message == "Something wrong"
    assert response.details is None

def test_pagination_response():
    items = ["a", "b", "c"]
    response = PaginationResponse[str](data=items, total=100, page=1, size=10)
    assert response.data == ["a", "b", "c"]
    assert response.total == 100
    assert response.size == 10
