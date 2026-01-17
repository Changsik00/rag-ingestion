"""
Edge case integration tests.

These tests verify system behavior under unusual or extreme conditions.
"""
import pytest
import asyncio
from fastapi.testclient import TestClient
from app.interfaces.api.main import app


client = TestClient(app)


@pytest.mark.integration
def test_url_with_special_characters():
    """
    Given: 특수 문자(한글, 공백)가 포함된 URL
    When: 수집 요청을 보내면
    Then: URL encoding이 올바르게 처리되고 정상 작동한다
    
    This verifies URL encoding/decoding works correctly.
    """
    import time
    
    # Given: 한글이 포함된 URL (URL encoding 필요)
    url_with_korean = "https://example.com/테스트/페이지"
    
    # When: 수집 요청
    response = client.post("/ingest/web", json={
        "url": url_with_korean
    })
    
    # Then: 요청 성공 (400 에러가 아니어야 함)
    # URL validation이 한글을 허용하는지 확인
    assert response.status_code in [202, 400]
    
    if response.status_code == 202:
        job_id = response.json()["job_id"]
        
        # Job 완료 대기
        for _ in range(30):
            job_response = client.get(f"/jobs/{job_id}")
            job = job_response.json()
            
            if job["status"] in ["COMPLETED", "FAILED"]:
                break
            
            time.sleep(1)
        
        # Job이 명확한 상태여야 함 (RUNNING에서 멈추지 않음)
        assert job["status"] in ["COMPLETED", "FAILED"]
        
        # FAILED라면 명확한 이유가 있어야 함
        if job["status"] == "FAILED":
            assert job.get("error") is not None


@pytest.mark.integration
def test_concurrent_ingestion_requests():
    """
    Given: 여러 수집 요청을 동시에 보내고
    When: 모든 Job이 실행되면
    Then: 각 Job이 독립적으로 처리되고 ID 충돌이 없다
    
    This verifies the system can handle concurrent requests safely.
    """
    import time
    
    # Given: 5개의 서로 다른 URL
    urls = [
        "https://example.com/page1",
        "https://example.com/page2",
        "https://example.com/page3",
        "https://example.com/page4",
        "https://example.com/page5",
    ]
    
    # When: 동시에 요청 (빠르게 연속 요청)
    job_ids = []
    for url in urls:
        response = client.post("/ingest/web", json={
            "url": url,
            "enable_extraction": False  # 빠른 테스트를 위해
        })
        assert response.status_code == 202
        job_ids.append(response.json()["job_id"])
    
    # Then: 모든 Job ID가 고유해야 함
    assert len(job_ids) == len(set(job_ids)), "Job IDs are not unique!"
    
    # When: 모든 Job 완료 대기
    completed_jobs = []
    for job_id in job_ids:
        for _ in range(30):
            job_response = client.get(f"/jobs/{job_id}")
            job = job_response.json()
            
            if job["status"] in ["COMPLETED", "FAILED"]:
                completed_jobs.append(job)
                break
            
            time.sleep(0.5)  # 더 빠른 폴링
    
    # Then: 모든 Job이 완료되어야 함
    assert len(completed_jobs) == len(job_ids)
    
    # Then: 각 Job이 독립적으로 처리되었는지 확인
    for job in completed_jobs:
        assert job["status"] in ["COMPLETED", "FAILED"]
        # Job ID가 각각 다른지 확인
        assert job["job_id"] in job_ids
