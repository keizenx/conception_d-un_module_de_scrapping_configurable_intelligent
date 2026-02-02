from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse, Response
from sqlalchemy.orm import Session
import io

from src.core.database import get_db
from src.core.models import ScrapingJob
from src.core.exporter import generate_csv, generate_json, generate_excel

router = APIRouter(prefix="/export", tags=["export"])

@router.get("/{job_id}/csv")
def export_job_csv(job_id: int, db: Session = Depends(get_db)):
    """Exporter les résultats d'un job en CSV"""
    job = db.query(ScrapingJob).filter(ScrapingJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if not job.result_json:
        raise HTTPException(status_code=400, detail="Job has no results or is not completed")
    
    items = job.result_json.get("items", [])
    csv_content = generate_csv(items)
    
    return StreamingResponse(
        iter([csv_content]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=job_{job_id}.csv"}
    )

@router.get("/{job_id}/json")
def export_job_json(job_id: int, db: Session = Depends(get_db)):
    """Exporter les résultats d'un job en JSON"""
    job = db.query(ScrapingJob).filter(ScrapingJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if not job.result_json:
        raise HTTPException(status_code=400, detail="Job has no results or is not completed")
    
    items = job.result_json.get("items", [])
    json_content = generate_json(items)
    
    return Response(
        content=json_content,
        media_type="application/json",
        headers={"Content-Disposition": f"attachment; filename=job_{job_id}.json"}
    )

@router.get("/{job_id}/excel")
def export_job_excel(job_id: int, db: Session = Depends(get_db)):
    """Exporter les résultats d'un job en Excel (XLSX)"""
    job = db.query(ScrapingJob).filter(ScrapingJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if not job.result_json:
        raise HTTPException(status_code=400, detail="Job has no results or is not completed")
    
    items = job.result_json.get("items", [])
    excel_content = generate_excel(items)
    
    return Response(
        content=excel_content,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename=job_{job_id}.xlsx"}
    )
