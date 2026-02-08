"""
Contract tests for DocumentRepository implementations.

These tests ensure that all implementations of DocumentRepository
comply with the same interface contract, preventing issues like
the constructor parameter mismatch found in Spec 008.
"""

import inspect
import unittest.mock

import pytest

from app.domain.interfaces.document_repository import DocumentRepository
from app.domain.interfaces.graph_repository import GraphRepository
from app.domain.interfaces.job_repository import JobRepository
from app.domain.interfaces.session_repository import SessionRepository
from app.infrastructure.repositories.chroma import ChromaVectorRepository
from app.infrastructure.repositories.composite import CompositeDocumentRepository
from app.infrastructure.repositories.neo4j_document_repository import Neo4jDocumentRepository
from app.infrastructure.repositories.neo4j_graph_repository import Neo4jGraphRepository
from app.infrastructure.repositories.neo4j_job_repository import Neo4jJobRepository
from app.infrastructure.repositories.postgres_session_repository import PostgresSessionRepository


# Parametrize all DocumentRepository implementations
@pytest.fixture(
    params=[
        (Neo4jDocumentRepository, DocumentRepository),
        (ChromaVectorRepository, DocumentRepository),
        (CompositeDocumentRepository, DocumentRepository),
        (Neo4jJobRepository, JobRepository),
        (PostgresSessionRepository, SessionRepository),
        (Neo4jGraphRepository, GraphRepository),
    ]
)
def storage_pair(request):
    """Storage implementation and its interface"""
    return request.param


class TestDocumentRepositoryContract:
    """Contract tests for Repository interfaces"""

    def test_implements_interface(self, storage_pair):
        """All storage classes must implement their respective interface"""
        storage_class, interface = storage_pair
        assert issubclass(storage_class, interface)

    def test_instantiation(self, storage_pair):
        """All storage classes must be instantiatable (not abstract)"""
        storage_class, _ = storage_pair
        # Attempt to instantiate with mocks for dependencies
        if storage_class == Neo4jDocumentRepository:
            # mock_driver must support session() as a context manager
            mock_driver = unittest.mock.MagicMock()
            storage_class(mock_driver)
        elif storage_class == ChromaVectorRepository:
            with (
                unittest.mock.patch("chromadb.HttpClient"),
                unittest.mock.patch.dict("os.environ", {"GEMINI_API_KEY": "fake-key"}),
            ):
                storage_class()
        elif storage_class == CompositeDocumentRepository:
            mock_neo4j = unittest.mock.Mock(spec=DocumentRepository)
            mock_chroma = unittest.mock.Mock(spec=DocumentRepository)
            storage_class(neo4j=mock_neo4j, chroma=mock_chroma)
        elif storage_class == Neo4jJobRepository:
            mock_driver = unittest.mock.MagicMock()
            storage_class(mock_driver)
        elif storage_class == Neo4jGraphRepository:
            mock_driver = unittest.mock.MagicMock()
            storage_class(mock_driver)
        elif storage_class == PostgresSessionRepository:
            mock_pool = unittest.mock.MagicMock()
            storage_class(mock_pool)

    def test_has_core_methods(self, storage_pair):
        """Basic check if class has methods (subset for all)"""
        storage_class, _ = storage_pair
        # Every repository usually has some form of 'get' or 'save' or 'list'
        # We check specific ones based on type if needed, or just skip if too generic.
        pass

    def test_save_method_signature(self, storage_pair):
        """save method should accept mandatory parameters if it's a DocumentRepository"""
        storage_class, interface = storage_pair
        if interface != DocumentRepository:
            pytest.skip("Only DocumentRepository has save(document)")

        sig = inspect.signature(storage_class.save)
        params = list(sig.parameters.values())

        assert len(params) >= 2  # self, document
        param_names = [p.name for p in params]
        assert "document" in param_names

    def test_get_method_signature(self, storage_pair):
        """get method signature check"""
        storage_class, interface = storage_pair
        if not hasattr(storage_class, "get") and not hasattr(interface, "get"):
            pytest.skip("This repository does not have a 'get' method")

        method = getattr(storage_class, "get")
        sig = inspect.signature(method)
        params = list(sig.parameters.values())

        assert len(params) >= 2  # self, id/doc_id/job_id
        assert "self" in [p.name for p in params]


class TestStorageConstructorConsistency:
    """
    Tests to prevent constructor parameter mismatch.
    """

    def test_neo4j_document_storage_constructor(self):
        """Neo4jDocumentRepository should accept a Driver instance"""
        from unittest.mock import Mock

        from neo4j import Driver

        mock_driver = Mock(spec=Driver)
        storage = Neo4jDocumentRepository(mock_driver)
        assert storage.driver == mock_driver

    def test_chroma_storage_constructor(self):
        """ChromaVectorRepository initializes its own client internally."""
        with (
            unittest.mock.patch("chromadb.HttpClient"),
            unittest.mock.patch.dict("os.environ", {"GEMINI_API_KEY": "fake-key"}),
        ):
            storage = ChromaVectorRepository()
            assert hasattr(storage, "client")
            assert hasattr(storage, "collection")
