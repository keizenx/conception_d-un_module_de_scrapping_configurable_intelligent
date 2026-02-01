from fastapi import APIRouter
from pydantic import BaseModel, HttpUrl

from src.core.scraper import scrape_url

router = APIRouter(prefix="", tags=["scrape"])


class ScrapeRequest(BaseModel):
    url: HttpUrl
    collection_index: int = 0
    max_items: int = 1000


@router.post("/scrape")
def scrape(req: ScrapeRequest):
    return scrape_url(
        url=str(req.url),
        collection_index=req.collection_index,
        max_items=req.max_items
    )
