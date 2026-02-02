import json
import logging
from sqlalchemy.orm import Session
from src.core.models import ScrapingJob, JobStatus
from src.core.scraper import scrape_url

logger = logging.getLogger(__name__)

from src.core.database import SessionLocal

def process_scraping_job(job_id: int):
    """
    Exécute le scraping en arrière-plan et met à jour la base de données.
    """
    db = SessionLocal()
    try:
        job = db.query(ScrapingJob).filter(ScrapingJob.id == job_id).first()
        if not job:
            logger.error(f"Job {job_id} not found")
            return

        try:
            # Update status to IN_PROGRESS
            job.status = JobStatus.IN_PROGRESS
            db.commit()

            # Run scraping
            result = scrape_url(
                url=job.url,
                collection_index=job.collection_index,
                max_items=job.max_items
            )

            if result.get("success"):
                job.status = JobStatus.COMPLETED
                job.result_json = result
                job.result_count = len(result.get("items", []))
            else:
                job.status = JobStatus.FAILED
                job.error_message = result.get("error", "Unknown error")
                
        except Exception as e:
            logger.exception(f"Error processing job {job_id}")
            job.status = JobStatus.FAILED
            job.error_message = str(e)
        
        finally:
            db.commit()
    finally:
        db.close()
