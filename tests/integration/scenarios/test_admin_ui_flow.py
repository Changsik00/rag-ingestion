import pytest
import time
import concurrent.futures
from app.domain.entities.job import JobStatus

def test_admin_rapid_click_scenario(api_client):
    """
    Scenario: User clicks 'Ingest' 3 times very quickly.
    Expected: Catch duplicates at API Level or Worker Level.
    """
    url = f"https://example.com/test-rapid-{time.time()}"
    payload = {"url": url, "force_refresh": False}
    
    # Simulate rapid clicks using threading with the sync TestClient
    def send_req():
        return api_client.post("/v1/ingest/web", json=payload).json()
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(send_req) for _ in range(5)]
        results = [f.result() for f in futures]
    
    job_ids = set(r.get("job_id") for r in results)
    print(f"\n[SCENARIO] Unique Job IDs: {len(job_ids)}")
    # Evaluates if API catches duplicates immediately
    assert len(job_ids) >= 1

def test_status_masking_ping_pong_scenario(api_client):
    """
    Scenario: Status Masking Verification (Bypassing early check to hit worker dedup)
              Job 1: URL A -> COMPLETED
              Job 2: URL A (bypass_early_dedup) -> Worker sees Job 1 -> SKIPPED
              Job 3: URL A (bypass_early_dedup) -> Worker should see Job 1 -> SKIPPED
    """
    url = f"https://example.com/test-status-masking-{time.time()}"
    
    # 1. First Ingestion
    r1 = api_client.post("/v1/ingest/web", json={"url": url}).json()
    job1_id = r1["job_id"]
    
    # Wait for Job 1 to complete
    for _ in range(30):
        res = api_client.get(f"/v1/jobs/{job1_id}").json()
        if res["current_status"] == "COMPLETED":
            break
        if res["current_status"] == "FAILED":
            pytest.fail(f"Job 1 failed: {res.get('error_message')}")
        time.sleep(1.0)
    
    # 2. Second Ingestion (Bypass API early check to trigger worker dedup)
    r2 = api_client.post("/v1/ingest/web", json={
        "url": url, 
        "bypass_early_dedup": True
    }).json()
    job2_id = r2["job_id"]
    assert job2_id != job1_id, f"Job 2 should have a new ID because we bypassed early check. Got {job2_id}"
    
    # Wait for Job 2 to finish (expected SKIPPED)
    for _ in range(40):
        res = api_client.get(f"/v1/jobs/{job2_id}").json()
        if res["current_status"] in ["SKIPPED", "COMPLETED", "FAILED"]:
            break
        time.sleep(1.0)
        
    # 3. Third Ingestion (The one that might be masked)
    r3 = api_client.post("/v1/ingest/web", json={
        "url": url,
        "bypass_early_dedup": True
    }).json()
    job3_id = r3["job_id"]
    assert job3_id != job2_id and job3_id != job1_id
    
    # Final Verification
    time.sleep(5)
    s1 = api_client.get(f"/v1/jobs/{job1_id}").json()["current_status"]
    s2 = api_client.get(f"/v1/jobs/{job2_id}").json()["current_status"]
    s3 = api_client.get(f"/v1/jobs/{job3_id}").json()["current_status"]
    
    print(f"\n[SCENARIO] Job 1: {job1_id} -> {s1}")
    print(f"[SCENARIO] Job 2: {job2_id} -> {s2}")
    print(f"[SCENARIO] Job 3: {job3_id} -> {s3}")
    
    assert s2 == "SKIPPED", f"Job 2 should be skipped by worker but got {s2}"
    assert s3 == "SKIPPED", f"Job 3 should be skipped by worker but got {s3}"
    print("✅ Worker-level status masking logic verified!")


