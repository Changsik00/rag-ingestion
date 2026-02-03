import pytest
import time
from fastapi.testclient import TestClient
from app.interfaces.api.main import app

@pytest.mark.integration
def test_ingestion_with_semantic_chunking(api_client):
    # 1. 수집 요청 (Semantic Chunking 설정 포함)
    payload = {
        "url": "https://pypi.org/project/langchain-experimental/",
        "chunking_config": {
            "strategy": "semantic",
            "breakpoint_threshold_type": "percentile",
            "breakpoint_threshold_amount": 95.0
        }
    }
    
    response = api_client.post("/v1/ingest/web", json=payload)
    assert response.status_code == 202
    
    job_id = response.json()["job_id"]
    assert job_id is not None
    
    # 2. 작업 완료 대기 및 상태 확인 (최대 30초)
    # 비동기 작업이므로 실제 환경에서는 시간이 걸릴 수 있음
    for _ in range(15):
        job_res = api_client.get(f"/v1/jobs/{job_id}")
        if job_res.status_code == 200 and job_res.json()["current_status"] == "COMPLETED":
            break
        time.sleep(3)
    
    # 3. 결과 확인
    # /v1/jobs/{job_id} 결과에서 docs_ids가 존재하는지 확인
    status_res = api_client.get(f"/v1/jobs/{job_id}")
    assert status_res.status_code == 200
    job_data = status_res.json()
    assert job_data["current_status"] == "COMPLETED"
    assert len(job_data["docs_ids"]) > 0
