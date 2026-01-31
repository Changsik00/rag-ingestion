import pytest

pytestmark = pytest.mark.skip(reason="Requires infrastructure setup - see specs/integration-test-improvement.md")

"""
Dependency Injection container verification tests.

These tests verify that the DI container correctly initializes storage instances
and environment variables are properly consumed.
"""

import os

import pytest


def test_get_repository_returns_composite_storage():
    """
    Verify that get_repository() creates a valid CompositeStorage instance
    with both Neo4j and Chroma storages.
    """
    # Given: DI container with repository
    from app.infrastructure.repositories.composite import CompositeDocumentRepository
    from app.interfaces.api.dependencies import get_neo4j_driver, get_repository

    # When: DI container provides repository
    driver = get_neo4j_driver()
    repository = get_repository(driver)

    # Then: Instance is CompositeStorage
    assert repository is not None
    assert isinstance(repository, CompositeDocumentRepository)

    # Then: Both underlying storages are initialized
    assert hasattr(repository, "neo4j")
    assert hasattr(repository, "chroma")
    assert repository.neo4j is not None
    assert repository.chroma is not None


def test_get_neo4j_driver_initialization():
    """
    Verify that get_neo4j_driver() creates a valid Neo4j Driver instance
    """
    # Given: DI container
    from neo4j import Driver

    from app.interfaces.api.dependencies import get_neo4j_driver

    # When: DI container provides Neo4j driver
    driver = get_neo4j_driver()

    # Then: Driver is created
    assert driver is not None
    assert isinstance(driver, Driver)


def test_get_graph_repository():
    """
    Verify that get_graph_repository() creates a valid Neo4jGraphRepository instance
    """
    # Given: DI container
    from app.infrastructure.repositories.neo4j_graph_repository import Neo4jGraphRepository
    from app.interfaces.api.dependencies import get_graph_repository, get_neo4j_driver

    # When: DI container provides GraphRepository
    driver = get_neo4j_driver()
    graph_repo = get_graph_repository(driver)

    # Then: Instance is created
    assert graph_repo is not None
    assert isinstance(graph_repo, Neo4jGraphRepository)


@pytest.mark.skipif(
    not all([os.getenv("NEO4J_URI"), os.getenv("CHROMA_HOST")]), reason="Database environment variables not set"
)
def test_environment_variable_based_initialization():
    """
    Verify that storage instances are initialized using environment variables
    """
    # Given: Environment variables are set
    from app.interfaces.api.dependencies import get_neo4j_driver, get_repository

    neo4j_uri = os.getenv("NEO4J_URI")
    chroma_host = os.getenv("CHROMA_HOST")

    assert neo4j_uri is not None
    assert chroma_host is not None

    # When: Dependencies are initialized
    driver = get_neo4j_driver()
    repository = get_repository(driver)

    # Then: They use the environment variables
    # (We can't easily verify this without accessing internals,
    #  but we verify they don't crash during initialization)
    assert driver is not None
    assert repository is not None
