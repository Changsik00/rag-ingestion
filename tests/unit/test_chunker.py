from datetime import datetime
from uuid import uuid4

import pytest

from app.core.config import get_settings
from app.domain.entities.document import Document
from app.infrastructure.chunker.langchain_chunker import LangChainChunker


@pytest.fixture
def chunker():
    return LangChainChunker()


@pytest.fixture
def document():
    return Document(
        id=str(uuid4()),
        content="Hello world. " * 300,  # Long content (~3900 chars)
        metadata={"source": "test"},
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )


def test_chunk_document_splits_long_content(chunker, document):
    settings = get_settings()
    chunk_size = settings.CHUNK_SIZE

    chunks = chunker.chunk_document(document)

    assert len(chunks) > 1
    # Check if chunks are within size limit (approximately)
    # Note: RecursiveCharacterTextSplitter length function defaults to len() which is char count
    for chunk in chunks:
        assert len(chunk.content) <= chunk_size


def test_chunk_document_preserves_metadata(chunker, document):
    chunks = chunker.chunk_document(document)

    assert len(chunks) > 0
    for chunk in chunks:
        assert chunk.parent_id == document.id
        assert chunk.metadata["source"] == document.metadata["source"]
        assert "start_index" in chunk.metadata  # Splitter usually adds this


def test_chunk_overlap_preservation(chunker):
    """
    Test that overlap is actually applied.
    We create a document with known content and check if end of Chunk N
    matches start of Chunk N+1.
    """
    settings = get_settings()
    # Override settings for this test to make it easier to verify
    # Note: LangChainChunker should read from config at initialization,
    # but for simplicity we assume default config unless we mock settings.
    # Here we rely on the default settings (1000/200).

    content = "abcdefghij" * 200  # 2000 chars
    doc = Document(
        id="test-doc",
        content=content,
        metadata={},
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )

    chunks = chunker.chunk_document(doc)
    assert len(chunks) >= 2

    chunk1 = chunks[0]
    chunk2 = chunks[1]

    # Calculate expected overlap text
    # The last N chars of chunk1 should exist in chunk2
    overlap_size = settings.CHUNK_OVERLAP

    # We find the common substring
    # NOTE: Recursive splitter behavior can be tricky with exact overlap
    # because it tries to split on smart separators.
    # With simple repeated text without separators, it might split strictly.
    # Let's verify that some significant portion of the end of chunk1 is in chunk2.

    overlap_text = chunk1.content[-overlap_size:]
    assert overlap_text in chunk2.content
