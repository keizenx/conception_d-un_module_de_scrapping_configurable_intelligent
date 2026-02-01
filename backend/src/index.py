from fastapi import FastAPI

from src.api.routes.analyze import router as analyze_router
from src.api.routes.scrape import router as scrape_router

app = FastAPI(title="Intelligent Scraper Backend", version="0.1.0")

app.include_router(analyze_router)
app.include_router(scrape_router)
