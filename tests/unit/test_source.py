import pytest
from pydantic import ValidationError
from src.domain.models.source import Source, Chunk

def test_source_creation_valid():
    """Source 모델이 유효한 테이터로 정상 생성되는지 검증"""
    source = Source(
        url="https://example.com",
        title="Example Title",
        raw_content="This is raw content"
    )
    assert str(source.url) == "https://example.com/"  # Pydantic HttpUrl normalizes (adds slash)
    assert source.title == "Example Title"
    assert source.id is not None  # UUID should be auto-generated
    assert len(source.chunks) == 0

def test_chunk_creation_valid():
    """Chunk 모델 생성 검증"""
    chunk = Chunk(
        content="Chunk content",
        metadata={"index": 1}
    )
    assert chunk.content == "Chunk content"
    assert chunk.chunk_id is not None

def test_source_with_chunks():
    """Source가 Chunk 리스트를 포함할 수 있는지 검증"""
    chunk1 = Chunk(content="Part 1")
    chunk2 = Chunk(content="Part 2")
    
    source = Source(
        url="https://test.com",
        chunks=[chunk1, chunk2]
    )
    
    assert len(source.chunks) == 2
    assert source.chunks[0].content == "Part 1"

def test_source_validation_error():
    """필수 필드 누락 시 에러 발생 검증"""
    with pytest.raises(ValidationError):
        Source(title="No URL")  # url is required
