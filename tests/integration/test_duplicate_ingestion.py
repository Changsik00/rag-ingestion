"""
Integration Test: ChromaDB 중복 수집 시나리오 검증

Spec 071: ChromaDB Upsert Logic
동일한 문서를 2번 수집했을 때 ChromaDB에 중복 저장되지 않는지 검증
"""
import pytest
from uuid import uuid4

from app.domain.entities.document import Document
from app.domain.value_objects.chunk import Chunk
from app.infrastructure.repositories.chroma import ChromaVectorRepository


@pytest.fixture
def chroma_repo():
    """ChromaDB Repository 인스턴스 (테스트용)"""
    repo = ChromaVectorRepository()
    yield repo
    # Cleanup: 테스트 후 컬렉션 리셋
    repo.reset_collection()


@pytest.mark.integration
def test_duplicate_document_upsert(chroma_repo):
    """동일 문서를 2번 수집 시 중복 저장 방지 테스트
    
    Given: 동일한 Document ID로 2번 save() 호출
    When: ChromaDB upsert 메서드 사용
    Then: 중복 저장 없이 업데이트만 발생
    """
    # Given: 문서 1차 수집
    doc_id = str(uuid4())
    doc_v1 = Document(
        id=doc_id,
        content="Initial content",
        metadata={
            "source_id": "https://example.com/test",
            "title": "Test Document v1"
        }
    )
    
    # When: 1차 저장
    chroma_repo.save(doc_v1)
    
    # Then: 저장 확인
    retrieved_v1 = chroma_repo.get(doc_id)
    assert retrieved_v1 is not None
    assert retrieved_v1.content == "Initial content"
    
    # When: 동일 ID로 2차 수집 (내용 변경)
    doc_v2 = Document(
        id=doc_id,
        content="Updated content",
        metadata={
            "source_id": "https://example.com/test",
            "title": "Test Document v2"
        }
    )
    chroma_repo.save(doc_v2)
    
    # Then: 중복 저장 없이 업데이트만 발생
    retrieved_v2 = chroma_repo.get(doc_id)
    assert retrieved_v2 is not None
    assert retrieved_v2.content == "Updated content"
    
    # ChromaDB 전체 문서 수 확인 (중복 없음)
    all_docs = chroma_repo.list_documents(limit=100)
    doc_ids = [str(d.id) for d in all_docs]
    assert doc_ids.count(doc_id) == 1, "중복 저장 발생!"


@pytest.mark.integration
def test_duplicate_chunks_upsert(chroma_repo):
    """동일 청크를 2번 수집 시 중복 저장 방지 테스트
    
    Given: 동일한 Chunk ID로 2번 save_chunks() 호출
    When: ChromaDB upsert 메서드 사용
    Then: 중복 저장 없이 업데이트만 발생
    """
    # Given: 청크 1차 수집
    doc_id = str(uuid4())
    chunk_id = str(uuid4())
    
    chunks_v1 = [
        Chunk(
            id=chunk_id,
            content="Initial chunk content",
            parent_id=doc_id,
            index=0,
            metadata={"title": "Chunk v1"}
        )
    ]
    
    # When: 1차 저장
    chroma_repo.save_chunks(chunks_v1)
    
    # Then: 저장 확인
    retrieved_chunks_v1 = chroma_repo.get_chunks(doc_id)
    assert len(retrieved_chunks_v1) == 1
    assert retrieved_chunks_v1[0].content == "Initial chunk content"
    
    # When: 동일 ID로 2차 수집 (내용 변경)
    chunks_v2 = [
        Chunk(
            id=chunk_id,
            content="Updated chunk content",
            parent_id=doc_id,
            index=0,
            metadata={"title": "Chunk v2"}
        )
    ]
    chroma_repo.save_chunks(chunks_v2)
    
    # Then: 중복 저장 없이 업데이트만 발생
    retrieved_chunks_v2 = chroma_repo.get_chunks(doc_id)
    assert len(retrieved_chunks_v2) == 1, "중복 저장 발생!"
    assert retrieved_chunks_v2[0].content == "Updated chunk content"
    
    # ChromaDB 전체 청크 ID 확인
    all_chunk_ids = chroma_repo.get_all_chunk_ids()
    assert list(all_chunk_ids).count(chunk_id) == 1, "중복 청크 ID 발견!"


@pytest.mark.integration
def test_batch_chunks_upsert(chroma_repo):
    """배치 청크 수집 시 중복 방지 테스트
    
    Given: 10개 청크를 2번 수집
    When: ChromaDB upsert 메서드 사용
    Then: 총 10개만 저장 (20개 아님)
    """
    # Given: 10개 청크 생성
    doc_id = str(uuid4())
    chunks = [
        Chunk(
            id=str(uuid4()),
            content=f"Chunk {i} content",
            parent_id=doc_id,
            index=i,
            metadata={"title": f"Chunk {i}"}
        )
        for i in range(10)
    ]
    
    # When: 1차 저장
    chroma_repo.save_chunks(chunks)
    retrieved_v1 = chroma_repo.get_chunks(doc_id)
    assert len(retrieved_v1) == 10
    
    # When: 동일 청크 2차 저장
    chroma_repo.save_chunks(chunks)
    
    # Then: 여전히 10개만 존재 (중복 없음)
    retrieved_v2 = chroma_repo.get_chunks(doc_id)
    assert len(retrieved_v2) == 10, f"중복 저장 발생! {len(retrieved_v2)}개 청크 발견"
    
    # 전체 청크 확인
    all_chunk_ids = chroma_repo.get_all_chunk_ids()
    expected_ids = {c.id for c in chunks}
    assert expected_ids.issubset(all_chunk_ids)
