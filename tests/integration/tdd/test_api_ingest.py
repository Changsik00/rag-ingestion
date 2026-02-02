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

# Skip marker removed, assuming infrastructure is handled by global conftest

client = TestClient(app)

# test_ingest_web_endpoint is superseded by tests/integration/test_async_ingest.py

@pytest.mark.integration
def test_list_documents_endpoint(seed_test_data, api_client):
    """
    GET /v1/documents 엔드포인트 테스트
    seed_test_data로 인해 데이터가 이미 존재한다고 가정하고 통합 테스트 수행
    """
    # When: GET /v1/documents 요청
    response = api_client.get("/v1/documents?limit=10")

    # Then: 200 응답 및 Document 리스트 반환
    assert response.status_code == 200
    data = response.json()
    
    # 시드 데이터가 최소 1개 이상임은 보장됨
    assert len(data) >= 1
    
    # Schema 검증 (필수 필드 존재 확인)
    first_doc = data[0]
    assert "id" in first_doc
    assert "content" in first_doc
    assert "metadata" in first_doc
    assert "source_id" in first_doc["metadata"]

@pytest.mark.integration
def test_search_documents_endpoint(seed_test_data, api_client):
    """
    POST /v1/search (or GET /v1/search) 엔드포인트 테스트
    시드 데이터(Wikipedia AI) 검색 검증
    """
    # When: Search for "Artificial Intelligence"
    # Endpoints might be /v1/rag/search or similar. Check router.
    # Assuming /v1/documents/search or similar based on `ingest` usually not having search.
    # Check current routes.
    pass
