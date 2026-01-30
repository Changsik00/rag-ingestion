import requests
import os
import time

BASE_URL = "http://localhost:8000"

def test_file_upload(file_path):
    print(f"--- Testing upload of {file_path} ---")
    if not os.path.exists(file_path):
        print(f"Skipping: {file_path} not found.")
        return

    filename = os.path.basename(file_path)
    with open(file_path, "rb") as f:
        files = {"file": (filename, f, "application/octet-stream")}
        response = requests.post(f"{BASE_URL}/ingest/file", files=files)
    
    if response.status_code == 202:
        job_id = response.json().get("job_id")
        print(f"✅ Success: Job created with ID {job_id}")
        
        # Monitor job status
        for _ in range(10):
            time.sleep(2)
            status_res = requests.get(f"{BASE_URL}/jobs/{job_id}")
            if status_res.status_code == 200:
                job_data = status_res.json()
                status = job_data.get("status")
                print(f"Current Status: {status}")
                if status == "completed":
                    print("🎉 Job Completed Successfully!")
                    return
                elif status == "failed":
                    print(f"❌ Job Failed: {job_data.get('error_message')}")
                    return
            else:
                print(f"Error fetching status: {status_res.status_code}")
    else:
        print(f"❌ Upload Failed: {response.status_code} - {response.text}")

if __name__ == "__main__":
    # Create a test file
    test_txt = "test_file_ingestion.txt"
    with open(test_txt, "w") as f:
        f.write("This is a test content for local file ingestion.\nRAG system should be able to index this.")
    
    test_file_upload(test_txt)
    
    # Cleanup
    if os.path.exists(test_txt):
        os.remove(test_txt)
