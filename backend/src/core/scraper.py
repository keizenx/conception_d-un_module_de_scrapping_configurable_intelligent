from __future__ import annotations

from typing import Any, Dict, List

from bs4 import BeautifulSoup, Tag

from src.core.analyzer import _selector_for, _text_candidates, _find_repeating_candidates, _node_signature
from src.core.fetcher import fetch_html
from src.core.fetcher_playwright import fetch_html_smart


def scrape_url(
    url: str,
    collection_index: int = 0,
    max_items: int = 1000,
    use_js: bool = False
) -> Dict[str, Any]:
    html = fetch_html_smart(url, use_js=use_js)
    soup = BeautifulSoup(html, "lxml")

    candidates = _find_repeating_candidates(soup, max_candidates=10)
    
    if collection_index >= len(candidates):
        return {
            "success": False,
            "error": f"Collection index {collection_index} not found. Only {len(candidates)} collections detected.",
            "url": url,
            "summary": {
                "total_items_extracted": 0,
                "available_collections": len(candidates)
            },
            "items": [],
            "metadata": {
                "mode": "error",
                "note": "Index de collection invalide"
            }
        }
    
    selected_candidate = candidates[collection_index]
    
    children = [ch for ch in selected_candidate.container.find_all(recursive=False) if isinstance(ch, Tag)]
    item_nodes = [ch for ch in children if ch.name == selected_candidate.item_tag_name]
    
    if max_items > 0:
        item_nodes = item_nodes[:max_items]
    
    items = []
    for node in item_nodes:
        fields = _text_candidates(node)
        
        if len(fields) > 0:
            items.append({
                "fields": fields,
                "selector_hint": _selector_for(node, with_parent=True)
            })
    
    # Créer un résumé pour meilleure lisibilité
    summary = {
        "total_items_extracted": len(items),
        "collection_info": {
            "container_selector": _selector_for(selected_candidate.container, with_parent=True),
            "item_tag": selected_candidate.item_tag_name,
            "collection_index": collection_index
        },
        "detected_field_types": list(set(
            field["type"] 
            for item in items 
            for field in item["fields"]
        )) if items else []
    }

    return {
        "success": True,
        "url": url,
        "summary": summary,
        "items": items,
        "metadata": {
            "mode": "full_extraction",
            "note": "Extraction complète de tous les items de la collection sélectionnée"
        }
    }
