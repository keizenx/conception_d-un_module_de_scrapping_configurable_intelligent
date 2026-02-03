from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, HttpUrl
from typing import Optional

from src.core.scraper import scrape_url, scrape_url_ultra_complete
from src.core.fetcher_playwright import get_fetcher, cleanup_fetcher

router = APIRouter(prefix="", tags=["scrape"])


class ScrapeRequest(BaseModel):
    url: HttpUrl
    collection_index: int = 0
    max_items: int = 1000
    use_js: bool = False


class UltraCompleteRequest(BaseModel):
    url: HttpUrl
    use_scroll: bool = True
    timeout_seconds: float = 20.0


@router.post("/scrape")
def scrape(req: ScrapeRequest):
    return scrape_url(
        url=str(req.url),
        collection_index=req.collection_index,
        max_items=req.max_items,
        use_js=req.use_js,
    )


@router.post("/scrape/ultra-complete")
async def scrape_ultra_complete(req: UltraCompleteRequest):
    """
    🚀 SCRAPER ULTRA-COMPLET - Extrait TOUT automatiquement
    
    Fonctionnalités:
    - Texte complet + HTML
    - Images (img + background CSS)  
    - Vidéos, Audios, iframes (YouTube/Vimeo)
    - Liens, Fichiers téléchargeables
    - Formulaires, Tableaux
    - Métadonnées (OpenGraph, Twitter, etc.)
    - Données structurées (JSON-LD)
    - Scripts, Styles
    - Headers anti-détection avancés
    - User-Agent rotation automatique
    - Scroll automatique pour contenu dynamique
    - 100% GRATUIT !
    """
    try:
        fetcher = await get_fetcher()
        
        result = await fetcher.extract_everything(
            url=str(req.url),
            use_scroll=req.use_scroll,
            timeout_seconds=req.timeout_seconds,
            wait_for_selector=None
        )
        
        if not result.get('success', False):
            raise HTTPException(
                status_code=500, 
                detail=result.get('error', 'Erreur inconnue lors de l\'extraction')
            )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur serveur: {str(e)}")


@router.post("/scrape/ultra-complete-advanced")
async def scrape_ultra_complete_advanced(req: UltraCompleteRequest):
    """
    🌟 VERSION AVANCÉE - Avec sélecteur d'attente personnalisé
    """
    class AdvancedRequest(BaseModel):
        url: HttpUrl
        use_scroll: bool = True
        timeout_seconds: float = 30.0
        wait_for_selector: Optional[str] = None
    
    try:
        fetcher = await get_fetcher()
        
        result = await fetcher.extract_everything(
            url=str(req.url),
            use_scroll=req.use_scroll, 
            timeout_seconds=req.timeout_seconds,
            wait_for_selector=getattr(req, 'wait_for_selector', None)
        )
        
        if not result.get('success', False):
            raise HTTPException(
                status_code=500,
                detail=result.get('error', 'Erreur extraction avancée')
            )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur extraction avancée: {str(e)}")


# Event handlers pour gérer proprement le lifecycle
@router.on_event("shutdown")
async def shutdown_event():
    """Fermer proprement le navigateur au shutdown de l'API"""
    await cleanup_fetcher()
