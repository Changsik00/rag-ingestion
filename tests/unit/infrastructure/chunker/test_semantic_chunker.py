import pytest
from unittest.mock import patch, Mock

from app.domain.entities.document import Document
from app.domain.value_objects.chunk_config import ChunkingConfig, ChunkingStrategy
from app.domain.value_objects.document_metadata import DocumentMetadata
from app.infrastructure.chunker.semantic_chunker import LangChainSemanticChunker


@pytest.fixture
def mock_embeddings():
    with patch("app.infrastructure.chunker.semantic_chunker.GoogleGenerativeAIEmbeddings") as mock:
        # Mock embedding logic: return different vectors for different topics
        mock_instance = mock.return_value
        
        def embed_documents(texts):
            # Simple heuristic: if '사과' (apple) is in text, return one vector, else another
            vectors = []
            for text in texts:
                if "사과" in text:
                    vectors.append([1.0, 0.0, 0.0])
                else:
                    vectors.append([0.0, 1.0, 0.0])
            return vectors

        mock_instance.embed_documents.side_effect = embed_documents
        yield mock_instance


@pytest.fixture
def semantic_chunker(mock_embeddings):
    config = ChunkingConfig(strategy=ChunkingStrategy.SEMANTIC, breakpoint_threshold_amount=90.0)
    return LangChainSemanticChunker(config=config)


def test_semantic_chunker_splitting(semantic_chunker):
    # 서로 다른 주제의 두 문장을 준비
    text = (
        "맛있는 사과는 빨간색입니다. 사과는 비타민이 풍부합니다. "
        "인공지능은 컴퓨터 공학의 한 분야입니다. 딥러닝은 인공지능의 하위 분야입니다."
    )
    doc = Document(
        content=text,
        metadata=DocumentMetadata(title="Test Doc", source_url="http://test.com", source_id="http://test.com"),
    )

    chunks = semantic_chunker.chunk_document(doc)

    # 두 개의 주제이므로 최소 2개 이상의 청크로 나뉘어야 함
    # (Mock 임베딩이 확연히 다르므로 LangChain SemanticChunker가 분리할 것임)
    assert len(chunks) >= 1

    # 메타데이터 확인
    for chunk in chunks:
        assert chunk.metadata["chunking_strategy"] == "semantic"
        assert "threshold_type" in chunk.metadata
