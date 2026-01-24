import pytest
from unittest.mock import MagicMock
from uuid import uuid4
from app.domain.services.storage_integrity_service import StorageIntegrityService
from app.domain.entities.chunk import Chunk

@pytest.fixture
def mock_primary_repo():
    return MagicMock()

@pytest.fixture
def mock_target_repo():
    return MagicMock()

@pytest.fixture
def service(mock_primary_repo, mock_target_repo):
    return StorageIntegrityService(mock_primary_repo, mock_target_repo)

def test_get_drfit_report_finds_missing_ids(service, mock_primary_repo, mock_target_repo):
    # Given
    id1, id2, id3 = str(uuid4()), str(uuid4()), str(uuid4())
    
    # Primary has 3 chunks
    mock_primary_repo.get_all_chunk_ids.return_value = {id1, id2, id3}
    # Target (Chroma) only has 1 chunk
    mock_target_repo.get_all_chunk_ids.return_value = {id1}
    
    # When
    report = service.get_drift_report()
    
    # Then
    assert report["total_primary"] == 3
    assert report["total_target"] == 1
    assert report["missing_count"] == 2
    assert report["missing_ids"] == {id2, id3}

def test_get_document_drift_report_groups_by_document(service, mock_primary_repo, mock_target_repo):
    # Given
    doc_id = str(uuid4())
    chunk1 = Chunk(id=str(uuid4()), content="c1", parent_id=doc_id, index=0, metadata={"title": "Doc A"})
    chunk2 = Chunk(id=str(uuid4()), content="c2", parent_id=doc_id, index=1, metadata={"title": "Doc A"})
    
    # Primary has Document A with 2 chunks
    mock_primary_repo.list_documents.return_value = [
        MagicMock(id=doc_id, metadata={"title": "Doc A"})
    ]
    mock_primary_repo.get_chunks.return_value = [chunk1, chunk2]
    
    # All IDs from primary
    mock_primary_repo.get_all_chunk_ids.return_value = {chunk1.id, chunk2.id}
    # Target only has chunk1
    mock_target_repo.get_all_chunk_ids.return_value = {chunk1.id}
    
    # When
    doc_reports = service.get_document_drift_report()
    
    # Then
    assert len(doc_reports) == 1
    report = doc_reports[0]
    assert report["title"] == "Doc A"
    assert report["total_chunks"] == 2
    assert report["target_chunks"] == 1
    assert report["drift_ratio"] == 0.5

def test_propagate_document_metadata_updates_chunks(service, mock_primary_repo):
    # Given
    doc_id = str(uuid4())
    doc = MagicMock(id=doc_id, metadata={"title": "New Title"})
    chunk1 = Chunk(id=str(uuid4()), content="c1", parent_id=doc_id, index=0, metadata={})
    
    mock_primary_repo.get.return_value = doc
    mock_primary_repo.get_chunks.return_value = [chunk1]
    
    # When
    service.propagate_document_metadata(doc_id)
    
    # Then
    assert chunk1.metadata["title"] == "New Title"
    mock_primary_repo.save_with_chunks.assert_called_once_with(doc, [chunk1])
