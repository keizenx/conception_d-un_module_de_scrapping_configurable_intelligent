from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel, HttpUrl

from src.core.scraper import scrape_url
from src.core.database import get_db
from src.core.models import ScrapingJob
from src.core.schemas import JobCreate, JobResponse, JobResult
from src.core.job_manager import process_scraping_job

router = APIRouter(tags=["scrape"])

class ScrapeRequest(BaseModel):
    url: HttpUrl
    collection_index: int = 0
    max_items: int = 1000
    use_js: bool = False

@router.post("/scrape", response_model=JobResult)
def scrape_sync(req: ScrapeRequest):
    """
    Scraping synchrone (bloquant). Utile pour des tests rapides.
    """
    return scrape_url(
        url=str(req.url),
        collection_index=req.collection_index,
        max_items=req.max_items,
        use_js=req.use_js,
    )

@router.post("/jobs", response_model=JobResponse)
def create_job(
    req: JobCreate, 
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Créer une tâche de scraping asynchrone.
    Retourne l'ID de la tâche pour suivi.
    """
    job = ScrapingJob(
        url=str(req.url),
        collection_index=req.collection_index,
        max_items=req.max_items
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    
    background_tasks.add_task(process_scraping_job, job.id)
    
    return job

@router.get("/jobs/{job_id}", response_model=JobResult)
def get_job_status(job_id: int, db: Session = Depends(get_db)):
    """
    Obtenir le statut et les résultats d'une tâche.
    """
    job = db.query(ScrapingJob).filter(ScrapingJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job
