from unittest.mock import Mock, patch

from app.domain.entities.chunk import Chunk
from app.infrastructure.storage.chroma import ChromaVectorRepository


@patch("chromadb.HttpClient")
@patch.dict("os.environ", {"GEMINI_API_KEY": "fake-key"})
def test_chroma_storage_save_chunks(mock_client_cls):
    """
    Given: List of Chunks
    When: save_chunks is called
    Then: It should extract contents, ids, and metadata and call collection.add
    """
    # Setup Mock
    mock_client = Mock()
    mock_collection = Mock()
    mock_client.get_or_create_collection.return_value = mock_collection
    mock_client_cls.return_value = mock_client

    storage = ChromaStorage()

    # Given Chunks
    chunk1 = Chunk(id="c1", content="Chunk 1", parent_id="p1", index=0, metadata={"meta": "1"})
    chunk2 = Chunk(id="c2", content="Chunk 2", parent_id="p1", index=1, metadata={"meta": "2"})
    chunks = [chunk1, chunk2]

    # When
    storage.save_chunks(chunks)

    # Then
    mock_collection.add.assert_called_once()
    call_args = mock_collection.add.call_args[1]

    assert call_args["ids"] == ["c1", "c2"]
    assert call_args["documents"] == ["Chunk 1", "Chunk 2"]

    # Metadata check
    # Should include original metadata + parent_id + index
    metadatas = call_args["metadatas"]
    assert len(metadatas) == 2
    assert metadatas[0]["parent_id"] == "p1"
    assert metadatas[0]["index"] == 0
    assert metadatas[1]["meta"] == "2"
