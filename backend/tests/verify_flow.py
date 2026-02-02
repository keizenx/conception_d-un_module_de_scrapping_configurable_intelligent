import httpx
import time
import sys

BASE_URL = "http://127.0.0.1:8001"

def test_flow():
    print("1. Creating a scraping job...")
    url_to_scrape = "https://example.com"
    try:
        resp = httpx.post(f"{BASE_URL}/jobs", json={
            "url": url_to_scrape,
            "max_items": 5
        })
        resp.raise_for_status()
        job = resp.json()
        job_id = job["id"]
        print(f"Job created with ID: {job_id}")
    except Exception as e:
        print(f"Failed to create job: {e}")
        return

    print("2. Waiting for job completion...")
    for _ in range(30):  # Wait up to 30 seconds
        resp = httpx.get(f"{BASE_URL}/jobs/{job_id}")
        job_status = resp.json()
        status = job_status["status"]
        print(f"Status: {status}")
        
        if status in ["completed", "failed"]:
            break
        time.sleep(1)
    
    if status == "completed":
        print("Job completed successfully!")
        print(f"Items found: {job_status['result_count']}")
        
        # Test Export
        print("3. Testing CSV Export...")
        resp = httpx.get(f"{BASE_URL}/export/{job_id}/csv")
        if resp.status_code == 200:
            print("CSV Export successful (first 100 chars):")
            print(resp.text[:100])
        else:
            print(f"CSV Export failed: {resp.status_code}")
            
    else:
        print(f"Job failed or timed out. Error: {job_status.get('error_message')}")

if __name__ == "__main__":
    try:
        test_flow()
    except Exception as e:
        print(f"Test failed with exception: {e}")
