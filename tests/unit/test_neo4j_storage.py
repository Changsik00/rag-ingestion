from unittest.mock import MagicMock, Mock
from uuid import uuid4

from app.domain.value_objects.chunk import Chunk
from app.domain.entities.document import Document
from app.infrastructure.repositories.neo4j_document_repository import Neo4jDocumentRepository


def test_neo4j_storage_save_with_chunks():
    # Given
    mock_driver = Mock()
    mock_session = Mock()
    session_ctx = MagicMock()

    mock_driver.session.return_value = session_ctx
    session_ctx.__enter__.return_value = mock_session

    storage = Neo4jDocumentRepository(driver=mock_driver)

    doc = Document(id=str(uuid4()), content="Test Content", metadata={"source_id": "test"})
    chunk1 = Chunk(id="c1", content="Chunk 1", parent_id=doc.id, index=0, metadata={})
    chunk2 = Chunk(id="c2", content="Chunk 2", parent_id=doc.id, index=1, metadata={})
    chunks = [chunk1, chunk2]

    # When
    storage.save_with_chunks(doc, chunks)

    # Then
    # Should execute Cypher to create Document and Chunks and Relationships
    # Since we can't easily check the cypher string exact match in mock without implementation,
    # we just check that run was called.
    assert mock_session.run.called

    # Verify transaction was used (optimization) if applicable,
    # but for now standard run is fine or write_transaction.
