import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from neo4j import Driver

from app.domain.exceptions import DomainError, DuplicateEntityError, EntityNotFoundError
from app.infrastructure.repositories.composite import CompositeDocumentRepository
from app.infrastructure.repositories.neo4j_graph_repository import Neo4jGraphRepository
from app.interfaces.api.dependencies import get_graph_repository, get_neo4j_driver, get_repository
from app.interfaces.api.error_handlers import register_exception_handlers


@pytest.mark.integration
class TestInfrastructure:
    """
    Functional tests for core system infrastructure.
    Pattern: Given-When-Then (GWT)
    """

    def test_dependency_injection_integrity(self):
        # Given: Access to DI dependencies

        # When: Requesting a composite repository
        repo = get_repository()

        # Then: Returns a valid CompositeDocumentRepository with both backends
        assert isinstance(repo, CompositeDocumentRepository)
        assert repo.neo4j is not None
        assert repo.chroma is not None

        # When: Requesting a Neo4j driver
        driver = get_neo4j_driver()

        # Then: Returns a valid Neo4j Driver instance
        assert isinstance(driver, Driver)

        # When: Requesting a Graph repository
        graph_repo = get_graph_repository(driver)

        # Then: Returns a valid Neo4jGraphRepository instance
        assert isinstance(graph_repo, Neo4jGraphRepository)

    def test_global_exception_handlers(self):
        # Given: A test FastAPI app with registered handlers
        test_app = FastAPI()
        register_exception_handlers(test_app)

        @test_app.get("/trigger/{exc_type}")
        def trigger_exception(exc_type: str):
            if exc_type == "not_found":
                raise EntityNotFoundError("Test", "1")
            if exc_type == "duplicate":
                raise DuplicateEntityError("Test", "1")
            if exc_type == "domain":
                raise DomainError("Logic error")
            raise ValueError("Internal error")

        client = TestClient(test_app, raise_server_exceptions=False)

        # When: Triggering ENTITY_NOT_FOUND
        resp = client.get("/trigger/not_found")
        # Then: Returns 404 with standard error format
        assert resp.status_code == 404
        assert resp.json()["error_code"] == "ENTITY_NOT_FOUND"

        # When: Triggering DUPLICATE_ENTITY
        resp = client.get("/trigger/duplicate")
        # Then: Returns 409
        assert resp.status_code == 409
        assert resp.json()["error_code"] == "DUPLICATE_ENTITY"

        # When: Triggering default error
        resp = client.get("/trigger/other")
        # Then: Returns 500
        assert resp.status_code == 500
        assert resp.json()["error_code"] == "INTERNAL_SERVER_ERROR"

    def test_test_fixtures_readiness(self, check_infrastructure, seed_test_data):
        # Given: Test environment

        # When: check_infrastructure fixture is requested
        # Then: It returns True (otherwise tests skip)
        assert check_infrastructure is True

        # When: seed_test_data fixture is requested
        # Then: It returns a dictionary of seeded jobs
        assert isinstance(seed_test_data, dict)
