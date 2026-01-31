from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi.testclient import TestClient

from app.application.admin.integrity_service import ResetResult
from app.interfaces.api.dependencies import get_integrity_service
from app.interfaces.api.main import app

pytestmark = pytest.mark.skip(reason="Requires infrastructure setup - see specs/integration-test-improvement.md")


client = TestClient(app)


@pytest.fixture
def mock_integrity_service():
    mock = MagicMock()
    # AsyncMock for async methods
    mock.reset_all = AsyncMock(return_value=ResetResult(neo4j="ok", chroma="ok", sqlite="ok"))
    return mock


def test_reset_all_data_success(mock_integrity_service):
    # Given
    app.dependency_overrides[get_integrity_service] = lambda: mock_integrity_service

    try:
        # When
        response = client.post("/api/v1/admin/integrity/reset")

        # Then
        assert response.status_code == 200
        assert response.json() == {
            "status": "success",
            "message": "All data has been reset.",
            "details": {"neo4j": "ok", "chroma": "ok", "sqlite": "ok"},
        }

        # Verify service method called
        mock_integrity_service.reset_all.assert_called_once()
    finally:
        app.dependency_overrides = {}
