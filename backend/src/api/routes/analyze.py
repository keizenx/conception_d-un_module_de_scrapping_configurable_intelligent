from fastapi import APIRouter
from pydantic import BaseModel, HttpUrl

from src.core.analyzer import analyze_url

router = APIRouter(prefix="", tags=["analyze"])


class AnalyzeRequest(BaseModel):
    url: HttpUrl
    max_candidates: int = 5
    max_items_preview: int = 5


@router.post("/analyze")
def analyze(req: AnalyzeRequest):
    return analyze_url(
        url=str(req.url),
        max_candidates=req.max_candidates,
        max_items_preview=req.max_items_preview,
    )
