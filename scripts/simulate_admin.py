import time

import requests

BASE_URL = "http://localhost:8000/v1"


def simulate_admin_request():
    url = "https://example.com/admin-ui-test"
    # Admin UI exactly sends this:
    payload = {
        "url": url,
        "chunking_config": {"strategy": "recursive", "chunk_size": 1000, "chunk_overlap": 200},
        "force_refresh": False,
    }

    print("--- ATTEMPT 1 ---")
    r1 = requests.post(f"{BASE_URL}/ingest/web", json=payload)
    print(f"Status Code: {r1.status_code}")
    job1_id = r1.json()["job_id"]
    print(f"Job 1 Created: {job1_id}")

    time.sleep(1)  # Let it reach RUNNING

    print("\n--- ATTEMPT 2 (Duplicate) ---")
    r2 = requests.post(f"{BASE_URL}/ingest/web", json=payload)
    print(f"Status Code: {r2.status_code}")
    job2_id = r2.json()["job_id"]
    print(f"Job 2 Created: {job2_id}")

    print("\nWaiting for Job 2 to process...")
    time.sleep(3)

    info2 = requests.get(f"{BASE_URL}/jobs/{job2_id}").json()
    status2 = info2.get("current_status")
    print(f"Job 2 Final Status: {status2}")

    if status2 == "SKIPPED":
        print("\n✅ SUCCESS: Admin simulation SKIPPED correctly.")
    else:
        print("\n❌ FAILURE: Admin simulation NOT SKIPPED.")


if __name__ == "__main__":
    simulate_admin_request()
