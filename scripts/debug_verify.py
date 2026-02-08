import json
import time

import requests

BASE_URL = "http://localhost:8000/v1"


def verify():
    url = "https://example.com/verify-final-test-" + str(time.time())
    payload = {"url": url, "force_refresh": False, "chunking_config": {"strategy": "recursive", "chunk_size": 500}}

    print(f"Ingesting: {url}")
    r1 = requests.post(f"{BASE_URL}/ingest/web", json=payload).json()
    jid1 = r1["job_id"]
    print(f"Job 1: {jid1}")

    time.sleep(3)

    print(f"Ingesting duplicate: {url}")
    r2 = requests.post(f"{BASE_URL}/ingest/web", json=payload).json()
    jid2 = r2["job_id"]
    print(f"Job 2: {jid2}")

    time.sleep(3)

    info1 = requests.get(f"{BASE_URL}/jobs/{jid1}").json()
    info2 = requests.get(f"{BASE_URL}/jobs/{jid2}").json()

    print("--- Job 1 Info ---")
    print(json.dumps(info1, indent=2))
    print("--- Job 2 Info ---")
    print(json.dumps(info2, indent=2))

    if info2.get("current_status") == "SKIPPED":
        print("✅ SUCCESS: Job 2 SKIPPED!")
    else:
        print("❌ FAILURE: Job 2 NOT skipped.")


if __name__ == "__main__":
    verify()
