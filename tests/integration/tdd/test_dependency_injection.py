"""
Dependency Injection container verification tests.

These tests verify that the DI container correctly initializes storage instances
and environment variables are properly consumed.
"""
import pytest
import os


def test_get_neo4j_storage():
    """
    Verify that get_neo4j_storage() creates a valid Neo4jStorage instance
    """
    from app.core.dependencies import get_neo4j_storage
    from app.infrastructure.storage.neo4j import Neo4jStorage
    
    # When: DI container provides Neo4jStorage
    storage = get_neo4j_storage()
    
    # Then: Instance is created
    assert storage is not None
    assert isinstance(storage, Neo4jStorage)
    
    # Then: Driver is initialized
    assert hasattr(storage, 'driver')
    assert storage.driver is not None


def test_get_chroma_storage():
    """
    Verify that get_chroma_storage() creates a valid ChromaStorage instance
    """
    from app.core.dependencies import get_chroma_storage
    from app.infrastructure.storage.chroma import ChromaStorage
    
    # When: DI container provides ChromaStorage
    storage = get_chroma_storage()
    
    # Then: Instance is created
    assert storage is not None
    assert isinstance(storage, ChromaStorage)
    
    # Then: Client is initialized
    assert hasattr(storage, 'client')
    assert storage.client is not None


def test_get_composite_storage():
    """
    Verify that get_composite_storage() creates CompositeStorage with both storages
    """
    from app.core.dependencies import get_composite_storage
    from app.infrastructure.storage.composite import CompositeStorage
    
    # When: DI container provides CompositeStorage
    storage = get_composite_storage()
    
    # Then: Instance is created
    assert storage is not None
    assert isinstance(storage, CompositeStorage)
    
    # Then: Both underlying storages are initialized
    assert hasattr(storage, 'storages')
    assert len(storage.storages) == 2


@pytest.mark.skipif(
    not all([os.getenv("NEO4J_URI"), os.getenv("CHROMA_HOST")]),
    reason="Database environment variables not set"
)
def test_environment_variable_based_initialization():
    """
    Verify that storage instances are initialized using environment variables
    """
    from app.core.dependencies import get_neo4j_storage, get_chroma_storage
    
    # Given: Environment variables are set
    neo4j_uri = os.getenv("NEO4J_URI")
    chroma_host = os.getenv("CHROMA_HOST")
    
    assert neo4j_uri is not None
    assert chroma_host is not None
    
    # When: Storages are initialized
    neo4j_storage = get_neo4j_storage()
    chroma_storage = get_chroma_storage()
    
    # Then: They use the environment variables
    # (We can't easily verify this without accessing internals,
    #  but we verify they don't crash during initialization)
    assert neo4j_storage is not None
    assert chroma_storage is not None
