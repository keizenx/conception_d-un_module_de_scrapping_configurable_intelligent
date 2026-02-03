from __future__ import annotations

from typing import Any, Dict, List

from bs4 import BeautifulSoup, Tag

from src.core.analyzer import (
    _selector_for,
    _text_candidates,
    _find_repeating_candidates,
    _node_signature,
)
from src.core.fetcher import fetch_html
from src.core.fetcher_playwright import fetch_html_smart, extract_complete_content_sync


def scrape_url(
    url: str, collection_index: int = 0, max_items: int = 1000, use_js: bool = False
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
                "available_collections": len(candidates),
            },
            "items": [],
            "metadata": {"mode": "error", "note": "Index de collection invalide"},
        }

    selected_candidate = candidates[collection_index]

    children = [
        ch
        for ch in selected_candidate.container.find_all(recursive=False)
        if isinstance(ch, Tag)
    ]
    item_nodes = [ch for ch in children if ch.name == selected_candidate.item_tag_name]

    if max_items > 0:
        item_nodes = item_nodes[:max_items]

    items = []
    for node in item_nodes:
        fields = _text_candidates(node)

        if len(fields) > 0:
            items.append(
                {
                    "fields": fields,
                    "selector_hint": _selector_for(node, with_parent=True),
                }
            )

    # Créer un résumé pour meilleure lisibilité
    summary = {
        "total_items_extracted": len(items),
        "collection_info": {
            "container_selector": _selector_for(
                selected_candidate.container, with_parent=True
            ),
            "item_tag": selected_candidate.item_tag_name,
            "collection_index": collection_index,
        },
        "detected_field_types": list(
            set(field["type"] for item in items for field in item["fields"])
        )
        if items
        else [],
    }

    return {
        "success": True,
        "url": url,
        "summary": summary,
        "items": items,
        "metadata": {
            "mode": "full_extraction",
            "note": "Extraction complète de tous les items de la collection sélectionnée",
        },
    }


def scrape_url_ultra_complete(
    url: str, use_scroll: bool = True, timeout_seconds: float = 20.0
) -> Dict[str, Any]:
    """
    🚀 NOUVELLE FONCTION : Extraction ULTRA-COMPLÈTE basée sur les meilleures pratiques
    - Extraction métadonnées complètes
    - Images (incluant background CSS)
    - Vidéos, audio, iframes (YouTube/Vimeo)
    - Formulaires et tableaux structurés
    - Données JSON-LD
    - Scroll automatique pour contenu dynamique
    - 100% GRATUIT !
    """
    try:
        print(f"🌟 EXTRACTION ULTRA-COMPLÈTE démarrée pour : {url}")
        
        # Utiliser la nouvelle fonction d'extraction complète
        complete_content = extract_complete_content_sync(url, timeout_seconds, use_scroll)
        
        return {
            "success": True,
            "url": url,
            "extraction_type": "ultra_complete",
            "data": complete_content,
            "summary": {
                "total_text_length": complete_content['extraction_stats']['text_length'],
                "media_found": {
                    "images": complete_content['extraction_stats']['images'],
                    "background_images": complete_content['extraction_stats']['background_images'],
                    "videos": complete_content['extraction_stats']['videos'],
                    "audios": complete_content['extraction_stats']['audios'],
                    "iframes": complete_content['extraction_stats']['iframes'],
                },
                "content_found": {
                    "links": complete_content['extraction_stats']['links'],
                    "files": complete_content['extraction_stats']['files'],
                    "forms": complete_content['extraction_stats']['forms'],
                    "tables": complete_content['extraction_stats']['tables'],
                    "structured_data": complete_content['extraction_stats']['structured_data'],
                },
                "metadata": {
                    "title": complete_content['metadata']['title'],
                    "description": complete_content['metadata']['description'],
                    "language": complete_content['metadata']['language'],
                }
            },
            "metadata": {
                "mode": "ultra_complete_extraction", 
                "note": "Extraction complète avec métadonnées, médias, formulaires, tableaux et données structurées",
                "extraction_timestamp": complete_content['extraction_timestamp'],
                "techniques_used": [
                    "Scroll automatique pour contenu dynamique",
                    "Extraction images background CSS",
                    "Données structurées JSON-LD",
                    "Métadonnées OpenGraph complètes",
                    "Formulaires et tableaux structurés",
                    "Médias multiples (vidéo, audio, iframes)"
                ]
            }
        }
        
    except Exception as e:
        print(f"❌ Erreur extraction ultra-complète: {str(e)}")
        return {
            "success": False,
            "url": url,
            "extraction_type": "ultra_complete",
            "error": str(e),
            "summary": {"total_items_extracted": 0},
            "metadata": {"mode": "error", "note": f"Erreur extraction ultra-complète: {str(e)}"}
        }
