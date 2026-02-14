from unittest.mock import AsyncMock

from fastapi.testclient import TestClient

from app.interfaces.api.dependencies import get_discovery_service
from app.interfaces.api.main import app

client = TestClient(app)


def test_start_discovery_endpoint():
    mock_service = AsyncMock()
    mock_service.start_discovery.return_value = ["job-1", "job-2"]

    app.dependency_overrides[get_discovery_service] = lambda: mock_service

    response = client.post("/v1/discovery/", json={"topic": "test", "max_depth": 1, "max_docs": 5})

    assert response.status_code == 202
    data = response.json()
    assert len(data["job_ids"]) == 2
    assert "Discovery started" in data["message"]

    mock_service.start_discovery.assert_called_once_with(topic="test", max_depth=1, max_docs=5)
