import os
import time

import requests

BASE_URL = "http://localhost:8000"


def test_multiple_files_upload(file_paths):
    print(f"--- Testing multi-upload of {file_paths} ---")
    files_to_upload = []
    for path in file_paths:
        if os.path.exists(path):
            filename = os.path.basename(path)
            f = open(path, "rb")
            files_to_upload.append(("files", (filename, f, "application/octet-stream")))
        else:
            print(f"Skipping: {path} not found.")

    if not files_to_upload:
        print("No files to upload.")
        return

    response = requests.post(f"{BASE_URL}/ingest/files", files=files_to_upload)

    # Close files
    for _, (_, f, _) in files_to_upload:
        f.close()

    if response.status_code == 202:
        jobs = response.json().get("jobs", [])
        print(f"✅ Success: {len(jobs)} Jobs created")

        for job_info in jobs:
            job_id = job_info.get("job_id")
            print(f"Monitoring Job: {job_id}")
            # Monitor job status
            for _ in range(10):
                time.sleep(2)
                status_res = requests.get(f"{BASE_URL}/jobs/{job_id}")
                if status_res.status_code == 200:
                    job_data = status_res.json()
                    status = job_data.get("status")
                    print(f"Job {job_id} Status: {status}")
                    if status == "completed":
                        print(f"🎉 Job {job_id} Completed!")
                        break
                    elif status == "failed":
                        print(f"❌ Job {job_id} Failed: {job_data.get('error_message')}")
                        break
                else:
                    print(f"Error fetching status: {status_res.status_code}")
    else:
        print(f"❌ Upload Failed: {response.status_code} - {response.text}")


if __name__ == "__main__":
    # Create test files
    files = ["test1.txt", "test2.md"]
    with open("test1.txt", "w") as f:
        f.write("Content 1")
    with open("test2.md", "w") as f:
        f.write("# Content 2")

    test_multiple_files_upload(files)

    # Cleanup
    for f in files:
        if os.path.exists(f):
            os.remove(f)
