"""
Contract tests for DocumentRepository implementations.

These tests ensure that all implementations of DocumentRepository
comply with the same interface contract, preventing issues like
the constructor parameter mismatch found in Spec 008.
"""

import pytest

from app.domain.interfaces.document_repository import DocumentRepository
from app.infrastructure.storage.neo4j_document_repository import Neo4jDocumentRepository
from app.infrastructure.storage.chroma import ChromaVectorRepository


# Parametrize all DocumentRepository implementations
@pytest.fixture(
    params=[
        Neo4jDocumentRepository,
        ChromaVectorRepository,
    ]
)
def storage_class(request):
    """All DocumentRepository implementation classes"""
    return request.param


class TestDocumentRepositoryContract:
    """Contract tests for DocumentRepository interface"""

    def test_implements_document_repository(self, storage_class):
        """All storage classes must implement DocumentRepository"""
        assert issubclass(storage_class, DocumentRepository)

    def test_has_save_method(self, storage_class):
        """All storage classes must have a save method"""
        assert hasattr(storage_class, "save")
        assert callable(getattr(storage_class, "save"))

    def test_has_get_method(self, storage_class):
        """All storage classes must have a get method"""
        assert hasattr(storage_class, "get")
        assert callable(getattr(storage_class, "get"))

    def test_has_list_documents_method(self, storage_class):
        """All storage classes must have a list_documents method"""
        assert hasattr(storage_class, "list_documents")
        assert callable(getattr(storage_class, "list_documents"))

    def test_save_method_signature(self, storage_class):
        """save method should accept Document and return None"""
        import inspect

        sig = inspect.signature(storage_class.save)
        params = list(sig.parameters.values())

        # Should have 'self' and 'document' parameters
        assert len(params) == 2, f"{storage_class.__name__}.save should have 2 parameters (self, document)"

        # Check parameter names
        param_names = [p.name for p in params]
        assert "self" in param_names
        assert "document" in param_names

    def test_get_method_signature(self, storage_class):
        """get method should accept UUID and return Document | None"""
        import inspect

        sig = inspect.signature(storage_class.get)
        params = list(sig.parameters.values())

        # Should have 'self' and 'doc_id' parameters
        assert len(params) == 2, f"{storage_class.__name__}.get should have 2 parameters (self, doc_id)"

        param_names = [p.name for p in params]
        assert "self" in param_names
        assert "doc_id" in param_names

    def test_list_documents_method_signature(self, storage_class):
        """list_documents method should accept optional limit parameter"""
        import inspect

        sig = inspect.signature(storage_class.list_documents)
        params = list(sig.parameters.values())

        # Should have at least 'self', optionally 'limit'
        assert len(params) >= 1, f"{storage_class.__name__}.list_documents should have at least 1 parameter (self)"

        param_names = [p.name for p in params]
        assert "self" in param_names

        # If limit exists, it should have a default value
        if "limit" in param_names:
            limit_param = [p for p in params if p.name == "limit"][0]
            assert limit_param.default != inspect.Parameter.empty, "limit parameter should have a default value"


class TestStorageConstructorConsistency:
    """
    Tests to prevent constructor parameter mismatch (Spec 008 issue).

    This ensures all storage implementations can be initialized in a consistent way,
    even if they have different dependencies.
    """

    def test_neo4j_storage_constructor(self):
        """Neo4jDocumentRepository should accept a Driver instance"""
        from unittest.mock import Mock

        from neo4j import Driver

        mock_driver = Mock(spec=Driver)
        storage = Neo4jDocumentRepository(mock_driver)

        assert storage.driver == mock_driver

    def test_chroma_storage_constructor(self):
        """
        ChromaVectorRepository initializes its own client internally.
        This is different from Neo4jDocumentRepository which accepts a driver.

        NOTE: This difference in constructor signatures is documented
        and intentional - ChromaVectorRepository manages its own connection.
        """
        storage = ChromaVectorRepository()

        assert hasattr(storage, "client")
        assert hasattr(storage, "collection")

    @pytest.mark.skip(reason="Documented requirement - implement when needed")
    def test_constructor_dependencies_documented(self, storage_class):
        """All storage classes should have docstring documenting their dependencies"""
        # This is a soft requirement - helps developers
        assert storage_class.__doc__ is not None or storage_class.__init__.__doc__ is not None, (
            f"{storage_class.__name__} should have documentation about its dependencies"
        )
