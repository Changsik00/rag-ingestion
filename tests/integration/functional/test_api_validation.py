import pytest
from fastapi.testclient import TestClient

from app.interfaces.api.main import app

@pytest.fixture
def client(api_client):
    """Alias for session-scoped api_client."""
    return api_client



@pytest.mark.integration
class TestApiValidation:
    """
    Validation & Error Handling Integration Tests.
    Focus: Verifying standard error responses and strict Pydantic validation.
    """

    def test_validation_error_format(self, client):
        """
        Scenario: Invalid URL provided (missing scheme).
        Expected: 422 Unprocessable Entity with standard ErrorResponse format.
        """
        # Given: An invalid payload
        payload = {"url": "not-a-valid-url"}

        # When: POST /v1/ingest/web
        response = client.post("/v1/ingest/web", json=payload)

        # Then: Status 422
        assert response.status_code == 422
        data = response.json()

        # And: Standard Error Schema
        assert data["status"] == "error"
        assert data["error_code"] == "VALIDATION_ERROR"
        assert "input validation failed" in data["message"].lower()

        # And: Details contain specific field error
        assert "body.url" in data["details"]

    def test_chunking_config_validation(self, client):
        """
        Scenario: Chunking config with invalid values.
        Expected: 422 validation error.
        """
        # Given: Invalid chunking config (chunk_overlap > chunk_size)
        payload = {
            "url": "https://example.com",
            "chunking_config": {
                "strategy": "recursive",
                "chunk_size": 500,
                "chunk_overlap": 600,  # Invalid: overlap > size
            },
        }

        # When: POST /v1/ingest/web
        response = client.post("/v1/ingest/web", json=payload)

        # Then: Status 422 and specific error message
        assert response.status_code == 422
        data = response.json()
        assert "body.chunking_config.chunk_overlap" in data["details"]
        assert "smaller than chunk_size" in data["details"]["body.chunking_config.chunk_overlap"]

    def test_method_not_allowed_format(self, client):
        """
        Scenario: Using GET on a POST-only endpoint.
        Expected: 405 Method Not Allowed with standard ErrorResponse.
        """
        # When: GET /v1/ingest/web
        response = client.get("/v1/ingest/web")

        # Then: Status 405
        assert response.status_code == 405
        data = response.json()

        # And: Standard Error Schema
        assert data["status"] == "error"
        assert "HTTP_405" in data["error_code"]
        assert "method not allowed" in data["message"].lower()

    def test_not_found_format(self, client):
        """
        Scenario: Requesting a non-existent endpoint.
        Expected: 404 Not Found with standard ErrorResponse.
        """
        # When: GET /v1/non-existent
        response = client.get("/v1/non-existent")

        # Then: Status 404
        assert response.status_code == 404
        data = response.json()

        # And: Standard Error Schema
        assert data["status"] == "error"
        assert "HTTP_404" in data["error_code"]

    def test_rag_advanced_settings_validation(self, client):
        """
        Scenario: Invalid advanced settings in ChatRequest.
        Expected: 422 validation error.
        """
        # Given: Invalid top_k (out of range)
        payload = {
            "message": "Hello",
            "advanced_settings": {
                "top_k": 200,  # Max is 100
                "search_strategy": "magic",  # Invalid enum
            },
        }

        # When: POST /v1/rag/sessions/test-session/ask
        response = client.post("/v1/rag/sessions/test-session/ask", json=payload)

        # Then: Status 422
        assert response.status_code == 422
        data = response.json()

        # And: Multiple errors reported
        details = data["details"]
        assert any("top_k" in k for k in details.keys())
        assert any("search_strategy" in k for k in details.keys())
