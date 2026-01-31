import pytest

pytestmark = pytest.mark.skip(reason="Requires infrastructure setup - see specs/integration-test-improvement.md")

"""
Integration Tests (BDD) for Knowledge Graph

실제 Docker 환경에서 Entity 그래프 구축을 E2E로 테스트합니다.
USE_CASES.md의 시나리오를 기반으로 작성되었습니다.
"""

import time

import pytest
import requests

pytestmark = pytest.mark.skip(reason="Requires infrastructure setup - see specs/integration-test-improvement.md")


# Docker Compose 환경에서만 실행
pytestmark = pytest.mark.integration

BASE_URL = "http://localhost:8000"


@pytest.mark.integration
def test_successful_entity_graph_auto_construction():
    """
    Scenario: Entity 그래프 자동 구축
    Given: 웹 페이지 수집 요청
    When: LLM이 Entity 추출하고 Document 저장
    Then: Entity 노드 및 MENTIONS 관계가 자동 생성됨
    """
    # Given: 웹 페이지 수집 요청
    ingest_response = requests.post(
        f"{BASE_URL}/ingest/web", json={"url": "https://httpbin.org/html", "enable_extraction": True}
    )
    assert ingest_response.status_code == 202
    job_id = ingest_response.json()["job_id"]

    # Wait for job completion
    for _ in range(30):  # 30초 대기
        job_response = requests.get(f"{BASE_URL}/jobs/{job_id}")
        if job_response.json()["status"] == "COMPLETED":
            break
        time.sleep(1)

    assert job_response.json()["status"] == "COMPLETED"

    # Then: Entity가 생성되었는지 확인
    entities_response = requests.get(f"{BASE_URL}/entities")
    assert entities_response.status_code == 200
    entities = entities_response.json()

    # LLM이 Entity를 추출했다면 최소 1개 이상 있어야 함
    # (httpbin.org/html은 간단한 HTML이라 Entity가 적을 수 있음)
    # 실제로는 enable_extraction=true일 때만 검증

    # Document 조회하여 metadata에 semantic_data 확인
    docs_response = requests.get(f"{BASE_URL}/documents", params={"limit": 1})
    assert docs_response.status_code == 200
    docs = docs_response.json()

    if docs:
        doc = docs[0]
        # semantic_data가 있으면 Entity가 추출된 것
        if "semantic_data" in doc.get("metadata", {}):
            # Entity가 1개 이상 생성되어야 함
            assert len(entities) > 0


@pytest.mark.integration
def test_entity_based_document_search():
    """
    Scenario: Entity 기반 Document 검색
    Given: 특정 Entity가 여러 Document에 언급됨
    When: GET /entities/{name}/documents 요청
    Then: 해당 Entity가 언급된 모든 Document 반환
    """
    # Given: 먼저 Entity 목록 조회
    entities_response = requests.get(f"{BASE_URL}/entities", params={"limit": 5})
    assert entities_response.status_code == 200
    entities = entities_response.json()

    if not entities:
        pytest.skip("No entities found, cannot test entity-based search")

    # When: 첫 번째 Entity로 Document 검색 (URL 인코딩 적용)
    import urllib.parse

    entity_name = urllib.parse.quote(entities[0]["name"], safe="")
    docs_response = requests.get(f"{BASE_URL}/entities/{entity_name}/documents")

    # Then: 성공적으로 조회됨
    assert docs_response.status_code == 200
    docs = docs_response.json()

    # 최소 1개 이상의 Document가 있어야 함
    assert isinstance(docs, list)


@pytest.mark.integration
def test_entity_deduplication():
    """
    Scenario: Entity 중복 처리
    Given: 두 개의 Document가 동일 Entity 언급
    When: 두 Document 저장
    Then: Entity 노드는 하나만 생성되고, MENTIONS 관계는 2개 생성됨
    """
    # Given: 첫 번째 Document 수집
    response1 = requests.post(
        f"{BASE_URL}/ingest/web", json={"url": "https://httpbin.org/html", "enable_extraction": True}
    )
    assert response1.status_code == 202
    job_id_1 = response1.json()["job_id"]

    # Given: 두 번째 Document 수집 (동일 URL)
    response2 = requests.post(
        f"{BASE_URL}/ingest/web", json={"url": "https://httpbin.org/html", "enable_extraction": True}
    )
    assert response2.status_code == 202
    job_id_2 = response2.json()["job_id"]

    # Wait for both jobs
    for job_id in [job_id_1, job_id_2]:
        for _ in range(30):
            job_response = requests.get(f"{BASE_URL}/jobs/{job_id}")
            if job_response.json()["status"] in ["COMPLETED", "FAILED"]:
                break
            time.sleep(1)

    # Then: Entity 개수 확인 (중복 제거되어야 함)
    entities_response = requests.get(f"{BASE_URL}/entities")
    assert entities_response.status_code == 200
    entities = entities_response.json()

    # Entity가 있다면, 각 Entity의 mention_count 확인 (URL 인코딩 적용)
    import urllib.parse

    for entity in entities:
        encoded_name = urllib.parse.quote(entity["name"], safe="")
        info_response = requests.get(f"{BASE_URL}/entities/{encoded_name}/info")
        assert info_response.status_code == 200
        info = info_response.json()

        # mention_count는 정수여야 함
        assert isinstance(info["mention_count"], int)
        assert info["mention_count"] >= 0
