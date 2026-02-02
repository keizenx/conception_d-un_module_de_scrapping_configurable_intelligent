import requests
import pandas as pd
import io
import sys
import os

# Add parent directory to path to import src
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.core.models import ScrapingJob, JobStatus
from src.core.database import Base

# Configuration
BASE_URL = "http://127.0.0.1:8001"
DB_URL = "sqlite:///./scraper.db"

def setup_dummy_job():
    engine = create_engine(DB_URL)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    # Create dummy job
    dummy_result = {
        "items": [
            {
                "fields": [
                    {"type": "title", "text": "Article 1"},
                    {"type": "price", "text": "10.00"}
                ]
            },
            {
                "fields": [
                    {"type": "title", "text": "Article 2"},
                    {"type": "price", "text": "20.00"}
                ]
            },
            {
                "fields": [
                    {"type": "title", "text": "Article 3"},
                    {"type": "price", "text": "30.00"}
                ]
            }
        ]
    }
    
    job = ScrapingJob(
        url="http://dummy.com",
        status=JobStatus.COMPLETED,
        result_json=dummy_result,
        result_count=3
    )
    
    session.add(job)
    session.commit()
    job_id = job.id
    session.close()
    print(f"Created dummy job with ID: {job_id}")
    return job_id

def test_export(job_id):
    print(f"Testing export for job {job_id}...")
    response = requests.get(f"{BASE_URL}/export/{job_id}/csv")
    
    if response.status_code == 200:
        print("Export successful!")
        content = response.content.decode('utf-8')
        print("CSV Content preview:")
        print(content)
        
        # Verify CSV structure
        df = pd.read_csv(io.StringIO(content))
        if len(df) == 3 and "title" in df.columns and "price" in df.columns:
            print("CSV structure is correct.")
        else:
            print("CSV structure is incorrect.")
    else:
        print(f"Export failed with status {response.status_code}: {response.text}")

if __name__ == "__main__":
    try:
        job_id = setup_dummy_job()
        test_export(job_id)
    except Exception as e:
        print(f"An error occurred: {e}")
