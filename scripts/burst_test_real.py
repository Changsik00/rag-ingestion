import time
import requests

BASE_URL = "http://localhost:8000/v1"

def burst_test_real_speed():
    url = "https://www.youtube.com/watch?v=ping-pong-test-" + str(time.time())
    payload = {
        "url": url,
        "chunking_config": {"strategy": "recursive", "chunk_size": 1000, "chunk_overlap": 200},
        "force_refresh": False
    }
    
    print(f"--- HUMAN SPEED BURST for {url} ---")
    
    jobs = []
    for i in range(3):
        # Slightly faster than a typical click? (300ms)
        r = requests.post(f"{BASE_URL}/ingest/web", json=payload).json()
        jobs.append(r.get("job_id"))
        print(f"Request {i+1} sent: ID={r.get('job_id')}")
        time.sleep(0.5) 

    print("\nWaiting 5 seconds for background processing...")
    time.sleep(5)
    
    print("\nResults in Job Queue:")
    for jid in jobs:
        info = requests.get(f"{BASE_URL}/jobs/{jid}").json()
        print(f"Job {jid}: Status={info.get('current_status')}")

if __name__ == "__main__":
    burst_test_real_speed()
