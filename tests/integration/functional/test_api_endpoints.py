from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from langchain_core.messages import AIMessage

from app.interfaces.api.main import app


@pytest.fixture
def client(api_client):
    """Alias for session-scoped api_client."""
    return api_client


@pytest.mark.integration
class TestApiEndpoints:
    """
    Consolidated Functional API Tests
    Focus: Endpoint correctness and basic request/response handling.
    Pattern: Given-When-Then (GWT)
    """

    def test_health_check_flow(self, client):
        # Given: System is running

        # When: GET /v1/health requested
        response = client.get("/v1/health")

        # Then: Returns 200 with component statuses
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "api" in data["components"]

    # --- Storage & Integrity Endpoints ---

    def test_storage_stats_flow(self, client):
        # Given: Valid storage state

        # When: GET /v1/storage/stats requested
        response = client.get("/v1/storage/stats")

        # Then: Returns 200 with stats keys
        assert response.status_code == 200
        data = response.json()
        assert "total_primary" in data or "message" in data

    def test_storage_reports_access(self, client):
        # Given: Storage endpoints exist

        # When: GET /v1/storage/reports requested
        response = client.get("/v1/storage/reports")

        # Then: Returns 200 list
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    # --- RAG & Graph Endpoints ---

    def test_rag_autocomplete_query(self, client):
        # Given: Search term 'test'
        query = "test"

        # When: GET /v1/rag/documents/autocomplete called
        response = client.get(f"/v1/rag/documents/autocomplete?q={query}")

        # Then: Returns 200 string list
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    @pytest.mark.asyncio
    async def test_rag_ask_flow(self, client):
        # Given: Valid payload with advanced settings
        payload = {
            "message": "Hello",
            "filters": {},
            "advanced_settings": {"top_k": 5, "temperature": 0.5, "search_strategy": "hybrid"},
        }

        # Use patch to avoid external API calls
        with patch("app.application.services.agent.ChatGoogleGenerativeAI") as mock_llm_cls:
            mock_instance = mock_llm_cls.return_value
            mock_instance.ainvoke = AsyncMock(return_value=AIMessage(content="Mock Answer"))

            # When: POST /v1/rag/sessions/{id}/ask
            response = client.post("/v1/rag/sessions/test_session/ask", json=payload)

            # Then: Returns 202 Accepted
            assert response.status_code == 202

    @pytest.mark.asyncio
    async def test_rag_ask_validation_error(self, client):
        """Spec 055: Test validation logic for AdvancedSettings"""
        # Given: Invalid payload (top_k=0, allowed range 1-100)
        payload = {"message": "Hello", "advanced_settings": {"top_k": 0}}

        # When: POST /v1/rag/sessions/{id}/ask
        response = client.post("/v1/rag/sessions/test_validation/ask", json=payload)

        # Then: Should return 422 Unprocessable Entity (Validation Error)
        # Current implementation (dict) will return 202, so this will FAIL until ChatRequest is applied.
        assert response.status_code == 422

    def test_graph_schema_retrieval(self, client):
        # Given: Active Neo4j connection

        # When: GET /v1/graph/schema
        response = client.get("/v1/graph/schema")

        # Then: Returns labels and relationship types
        assert response.status_code == 200
        data = response.json()
        assert "labels" in data
        assert "relationship_types" in data

    # --- Jobs & Documents Endpoints ---

    def test_list_jobs_with_mock(self, client):
        # Given: Mocked Job Repository with one job
        from datetime import datetime, timezone

        from app.domain.entities.job import IngestionJob
        from app.interfaces.api.dependencies import get_job_repository

        mock_repo = MagicMock()
        now = datetime.now(timezone.utc)
        job = IngestionJob(
            job_id="job-123", status="COMPLETED", source_url="http://example.com", created_at=now, updated_at=now
        )
        mock_repo.list_jobs.return_value = [job]
        app.dependency_overrides[get_job_repository] = lambda: mock_repo

        try:
            # When: GET /v1/jobs
            response = client.get("/v1/jobs")

            # Then: Returns 200 with job list
            assert response.status_code == 200
            data = response.json()
            assert len(data) == 1
            assert data[0]["job_id"] == "job-123"
            assert data[0]["current_status"] == "COMPLETED"
        finally:
            app.dependency_overrides.clear()

    def test_list_documents_with_seed(self, seed_test_data, client):
        # Given: Seeded test data (via fixture)

        # When: GET /v1/documents
        response = client.get("/v1/documents?limit=5")

        # Then: Returns 200 with documents
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        first_doc = data[0]
        # Check for any unique identifier
        assert "id" in first_doc or "metadata" in first_doc
        if "metadata" in first_doc:
            meta = first_doc["metadata"]
            assert any(k in meta for k in ["source_id", "url", "source_url", "title"])

    def test_invalid_job_id_lookup(self, client):
        """
        Functional Test: Querying a non-existent job ID
        """
        # Given: An invalid UUID string
        invalid_job_id = "00000000-0000-0000-0000-000000000000"

        # When: GET /v1/jobs/{id} is called
        response = client.get(f"/v1/jobs/{invalid_job_id}")

        # Then: Returns 404 Not Found
        assert response.status_code == 404
