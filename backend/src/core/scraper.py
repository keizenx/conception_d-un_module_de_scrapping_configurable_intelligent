from __future__ import annotations

from typing import Any, Dict, List

from bs4 import BeautifulSoup, Tag

from src.core.analyzer import _selector_for, _text_candidates, _find_repeating_candidates, _node_signature
from src.core.fetcher import fetch_html


def scrape_url(
    url: str,
    collection_index: int = 0,
    max_items: int = 1000
) -> Dict[str, Any]:
    html = fetch_html(url)
    soup = BeautifulSoup(html, "lxml")

    candidates = _find_repeating_candidates(soup, max_candidates=10)
    
    if collection_index >= len(candidates):
        return {
            "error": f"Collection index {collection_index} not found. Only {len(candidates)} collections detected.",
            "url": url,
            "items": []
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
    
    return {
        "url": url,
        "collection_index": collection_index,
        "container_selector": _selector_for(selected_candidate.container, with_parent=True),
        "item_tag": selected_candidate.item_tag_name,
        "total_items": len(items),
        "items": items
    }
