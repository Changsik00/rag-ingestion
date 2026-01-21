import pytest
from unittest.mock import MagicMock, patch
from app.admin.services.hitl_service import HitlService

import pytest
from unittest.mock import MagicMock, patch
from app.admin.services.hitl_service import HitlService

@pytest.fixture
def hitl_service():
    return HitlService()

@patch("app.admin.services.hitl_service.requests.get")
def test_list_threads_empty(mock_get, hitl_service):
    """Test listing threads when none exist."""
    mock_response = MagicMock()
    mock_response.json.return_value = []
    mock_get.return_value = mock_response
    
    threads = hitl_service.list_threads()
    assert threads == []

@patch("app.admin.services.hitl_service.requests.get")
def test_list_threads_populated(mock_get, hitl_service):
    """Test listing threads with data."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = [{"thread_id": "t1", "status": "interrupted"}]
    mock_get.return_value = mock_response
    
    threads = hitl_service.list_threads()
    assert len(threads) == 1
    assert threads[0]["thread_id"] == "t1"

@patch("app.admin.services.hitl_service.requests.post")
def test_resume_thread(mock_post, hitl_service):
    """Test resuming a thread via API."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_post.return_value = mock_response
    
    success = hitl_service.resume_thread("t1", {"decision": "continue"})
    
    assert success is True
    mock_post.assert_called_with("http://localhost:8000/jobs/t1/resume", json={"input": {"decision": "continue"}})
