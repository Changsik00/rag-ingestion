"""
Integration Tests for Document API

Document 관련 API 엔드포인트의 통합 테스트를 수행합니다.
FastAPI TestClient를 사용하여 실제 HTTP 요청을 시뮬레이션합니다.
"""

from unittest.mock import Mock
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.domain.entities.document import Document
from app.interfaces.api.dependencies import get_repository
from app.interfaces.api.main import app

pytestmark = pytest.mark.skip(reason="Requires infrastructure setup - see specs/integration-test-improvement.md")


client = TestClient(app)

# test_ingest_web_endpoint is superseded by tests/integration/test_async_ingest.py


def test_list_documents_endpoint():
    # Given: Mock Repository와 테스트 데이터
    mock_repo = Mock()
    doc_id = uuid4()
    mock_docs = [
        Document(id=str(doc_id), content="Doc 1", metadata={"source_url": "http://test.com/1"}),
        Document(content="Doc 2", metadata={"source_url": "http://test.com/2"}),
    ]
    mock_repo.list_documents.return_value = mock_docs

    app.dependency_overrides[get_repository] = lambda: mock_repo

    # When: GET /documents 요청
    response = client.get("/documents?limit=5")

    # Then: 200 응답 및 Document 리스트 반환
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["metadata"]["source_url"] == "http://test.com/1"

    mock_repo.list_documents.assert_called_once_with(limit=5)

    app.dependency_overrides.clear()
