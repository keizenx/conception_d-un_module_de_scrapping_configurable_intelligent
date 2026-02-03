from fastapi import APIRouter
from pydantic import BaseModel, HttpUrl

from src.core.analyzer import analyze_url
from src.core.subdomain_finder import discover_subdomains
from src.core.site_checker import SiteChecker, filter_scrapable_sites

router = APIRouter(prefix="", tags=["analyze"])


class AnalyzeRequest(BaseModel):
    url: HttpUrl
    max_candidates: int = 5
    max_items_preview: int = 5
    use_js: bool = False
    include_subdomains: bool = False


@router.post("/analyze")
def analyze(req: AnalyzeRequest):
    result = analyze_url(
        url=str(req.url),
        max_candidates=req.max_candidates,
        max_items_preview=req.max_items_preview,
        use_js=req.use_js,
    )
    
    # Si include_subdomains est True, chercher et vérifier les sous-domaines
    if req.include_subdomains:
        # Extraire le domaine principal de l'URL
        from urllib.parse import urlparse
        parsed = urlparse(str(req.url))
        domain = parsed.netloc
        
        # Découvrir les sous-domaines
        subdomain_result = discover_subdomains(domain)
        
        if subdomain_result["success"] and subdomain_result["subdomains"]:
            # Vérifier la scrapabilité des sous-domaines (max 20)
            all_subdomains = subdomain_result["subdomains"][:20]
            
            # Construire des URLs complètes avec le schéma original
            subdomain_urls = [f"{parsed.scheme}://{sub}" for sub in all_subdomains]
            
            # Filtrer les sites scrapables
            scrapable, non_scrapable, check_details = filter_scrapable_sites(subdomain_urls)
            
            # Ajouter les sous-domaines au résultat
            result["subdomains"] = {
                "total_found": subdomain_result["total_found"],
                "sources": subdomain_result["sources"],
                "all_subdomains": all_subdomains,
                "scrapable_list": [urlparse(url).netloc for url in scrapable],
                "check_details": {
                    urlparse(url).netloc: details 
                    for url, details in check_details.items()
                }
            }
        else:
            result["subdomains"] = {
                "total_found": 0,
                "sources": [],
                "all_subdomains": [],
                "scrapable_list": [],
                "check_details": {}
            }
    
    # Convertir collections en content_types pour correspondre au frontend
    if result.get("collections"):
        result["content_types"] = []
        for idx, collection in enumerate(result["collections"]):
            result["content_types"].append({
                "id": f"collection_{idx}",
                "title": f"Collection {idx + 1}",
                "description": f"{collection['estimated_items']} éléments détectés ({collection['confidence']*100:.0f}% confiance)",
                "icon": "📦",
                "count": collection['estimated_items'],
                "selector": collection['container_selector_hint']
            })
        result["page_count"] = 1  # Pour l'instant, une seule page analysée
    
    return result
