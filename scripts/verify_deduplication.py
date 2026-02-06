import time
import requests
import sys

BASE_URL = "http://localhost:8000/v1"

def print_step(msg):
    print(f"\n[STEP] {msg}")

def check_server():
    try:
        requests.get(f"{BASE_URL}/jobs")
        print("✅ Server is reachable.")
        return True
    except Exception as e:
        print(f"❌ Server unreachable at {BASE_URL}. Ensure backend is running.")
        print(e)
        return False

def verify_web_deduplication():
    print_step("Verifying Web URL Deduplication")
    url = "https://example.com/verify-dedup-test"
    
    payload = {
        "url": url,
        "force_refresh": False,
        "chunking_config": {"strategy": "recursive", "chunk_size": 500}
    }
    
    resp1 = requests.post(f"{BASE_URL}/ingest/web", json=payload)
    if resp1.status_code != 202:
        print(f"❌ First request failed: {resp1.text}")
        return
    
    job1_id = resp1.json()["job_id"]
    print(f"   -> Job 1 Created: {job1_id}")
    
    print("   -> Waiting 2 seconds for Job 1 to start processing...")
    time.sleep(2)
    
    j1_info = requests.get(f"{BASE_URL}/jobs/{job1_id}").json()
    j1_status = j1_info["current_status"]
    print(f"   -> Job 1 Status: {j1_status}")
    
    print(f"2. Requesting DUPLICATE ingestion for: {url}")
    resp2 = requests.post(f"{BASE_URL}/ingest/web", json=payload)
    job2_id = resp2.json()["job_id"]
    print(f"   -> Job 2 Created: {job2_id}")
    
    print("   -> Waiting 2 seconds for Job 2 to be processed...")
    time.sleep(2)
    
    j2_info = requests.get(f"{BASE_URL}/jobs/{job2_id}").json()
    j2_status = j2_info["current_status"]
    j2_msg = j2_info.get("error_message", "")
    
    print(f"   -> Job 2 Status: {j2_status} (Msg: {j2_msg})")
    
    if j2_status == "SKIPPED":
        print("✅ SUCCESS: Job 2 was SKIPPED as duplicate.")
    else:
        print(f"❌ FAILURE: Job 2 was NOT Skipped. Status: {j2_status}")

def verify_file_deduplication():
    print_step("Verifying File Ingestion Deduplication")
    filename = "test_dedup_file.txt"
    content = b"This is a test content for deduplication verification."
    
    files = [('files', (filename, content, 'text/plain'))]
    
    print("1. Uploading file first time...")
    resp1 = requests.post(f"{BASE_URL}/ingest/files", files=files)
    if resp1.status_code != 202:
        print(f"❌ First upload failed: {resp1.text}")
        return

    job1_id = resp1.json()["jobs"][0]["job_id"]
    print(f"   -> Job 1 Created: {job1_id}")
    
    print("   -> Waiting 2 seconds...")
    time.sleep(2)
    
    print("2. Uploading SAME file second time...")
    files2 = [('files', (filename, content, 'text/plain'))]
    resp2 = requests.post(f"{BASE_URL}/ingest/files", files=files2)
    job2_id = resp2.json()["jobs"][0]["job_id"]
    print(f"   -> Job 2 Created: {job2_id}")
    
    print("   -> Waiting 2 seconds...")
    time.sleep(2)
    
    j2_info = requests.get(f"{BASE_URL}/jobs/{job2_id}").json()
    j2_status = j2_info["current_status"]
    
    print(f"   -> Job 2 Status: {j2_status}")
    
    if j2_status == "SKIPPED":
        print("✅ SUCCESS: Job 2 was SKIPPED as duplicate.")
    else:
        print(f"❌ FAILURE: Job 2 was NOT Skipped. Status: {j2_status}")

if __name__ == "__main__":
    print("🚀 Starting Deduplication Verification Script...")
    if check_server():
        verify_web_deduplication()
        verify_file_deduplication()
    else:
        print("Skipping tests due to connection failure.")
