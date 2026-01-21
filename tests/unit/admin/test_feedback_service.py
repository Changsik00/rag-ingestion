import json
from unittest.mock import mock_open, patch

import pytest

from app.admin.services.feedback_service import FeedbackService


@pytest.fixture
def feedback_service():
    return FeedbackService(feedback_file="test_feedback.jsonl")


def test_save_feedback(feedback_service):
    """Test saving feedback to a file."""
    feedback_data = {
        "query": "What is RAG?",
        "response": "Retrieval Augmented Generation...",
        "feedback": "thumbs_up",
        "comment": "Good explanation",
    }

    with patch("builtins.open", mock_open()) as mock_file:
        success = feedback_service.save_feedback(feedback_data)

        assert success is True
        mock_file.assert_called_with("test_feedback.jsonl", "a", encoding="utf-8")

        # Verify written content
        handle = mock_file()
        expected_json = json.dumps(feedback_data, ensure_ascii=False)
        handle.write.assert_called_once()
        args, _ = handle.write.call_args
        assert expected_json in args[0]


def test_get_recent_feedback(feedback_service):
    """Test retrieving recent feedback."""
    mock_content = '{"query": "q1", "feedback": "up"}\n{"query": "q2", "feedback": "down"}\n'

    with patch("builtins.open", mock_open(read_data=mock_content)):
        recent = feedback_service.get_recent_feedback(limit=2)

        assert len(recent) == 2
        assert recent[0]["query"] == "q2"  # Newest first logic usually
        assert recent[1]["query"] == "q1"


def test_get_recent_feedback_file_not_found(feedback_service):
    """Test handling file not found gracefully."""
    with patch("builtins.open", side_effect=FileNotFoundError):
        recent = feedback_service.get_recent_feedback()
        assert recent == []
