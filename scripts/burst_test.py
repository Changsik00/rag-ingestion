import time
import requests
import concurrent.futures

BASE_URL = "http://localhost:8000/v1"

def burst_test():
    url = "https://www.youtube.com/watch?v=burst-test-" + str(time.time())
    payload = {
        "url": url,
        "chunking_config": {"strategy": "recursive", "chunk_size": 1000, "chunk_overlap": 200},
        "force_refresh": False
    }
    
    print(f"--- BURST START for {url} ---")
    
    # Simulate 3 identical requests almost simultaneously
    def send_req():
        return requests.post(f"{BASE_URL}/ingest/web", json=payload).json()
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        results = list(executor.submit(send_req) for _ in range(3))
        outputs = [r.result() for r in results]
    
    for i, out in enumerate(outputs):
        msg = out.get("message", "")
        job_id = out.get("job_id")
        status = out.get("current_status")
        print(f"Req {i+1}: ID={job_id}, Status={status}, Msg={msg}")

    # All 3 should ideally have the SAME Job ID if caught at API level
    ids = set(out.get("job_id") for out in outputs)
    if len(ids) == 1:
        print("\n✅ SUCCESS: Only 1 Job ID issued for burst requests!")
    else:
        print(f"\n❌ FAILURE: {len(ids)} different Job IDs issued.")

if __name__ == "__main__":
    burst_test()
