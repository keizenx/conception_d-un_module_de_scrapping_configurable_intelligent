import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session
from src.core.database import get_db, SessionLocal
from src.core.models import ScrapingJob

router = APIRouter(tags=["websocket"])

@router.websocket("/ws/jobs/{job_id}")
async def websocket_job_status(websocket: WebSocket, job_id: int):
    await websocket.accept()
    db = SessionLocal()
    try:
        last_status = None
        while True:
            job = db.query(ScrapingJob).filter(ScrapingJob.id == job_id).first()
            if not job:
                await websocket.send_json({"error": "Job not found"})
                break
            
            current_status = job.status
            
            # Envoyer le statut si c'est la première connexion ou si le statut a changé
            if current_status != last_status:
                await websocket.send_json({
                    "id": job.id,
                    "status": current_status,
                    "result_count": job.result_count,
                    "created_at": str(job.created_at),
                    "updated_at": str(job.updated_at)
                })
                last_status = current_status
            
            if current_status in ["completed", "failed"]:
                break
                
            await asyncio.sleep(1)  # Poll DB every 1 second
            
            # Rafraîchir la session pour avoir les dernières données
            db.expire_all()
            
    except WebSocketDisconnect:
        pass
    finally:
        db.close()
