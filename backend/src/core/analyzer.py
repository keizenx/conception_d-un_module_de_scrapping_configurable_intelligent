from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

from bs4 import BeautifulSoup, Tag

from src.core.fetcher import fetch_html


_PRICE_RE = re.compile(r"(?i)(£|€|\$)?\s?(\d{1,3}(?:[\s.,]\d{3})*(?:[.,]\d{2})?)\s?(£|€|eur|fcfa|xof|usd|\$|gbp)?")
_DATE_RE = re.compile(r"(?i)\b(\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{4}[/-]\d{1,2}[/-]\d{1,2}|\w+ \d{1,2},? \d{4}|\d{1,2} \w+ \d{4})\b")


def _clean_text(s: str) -> str:
    return re.sub(r"\s+", " ", s or "").strip()


def _node_signature(tag: Tag) -> Tuple[str, Tuple[str, ...]]:
    classes = tag.get("class") or []
    classes = tuple(sorted([c for c in classes if isinstance(c, str)]))
    return tag.name, classes


def _selector_for(tag: Tag, with_parent: bool = False) -> str:
    parts = []
    
    if tag.get("id"):
        parts.append(f"#{tag.get('id')}")
    else:
        classes = tag.get("class") or []
        classes = [c for c in classes if isinstance(c, str) and not c.startswith("js-")]
        if classes:
            parts.append(tag.name + "".join([f".{c}" for c in classes[:2]]))
        else:
            parts.append(tag.name)
    
    if with_parent and tag.parent and tag.parent.name not in ["html", "body", "[document]"]:
        parent_sel = _selector_for(tag.parent, with_parent=False)
        return f"{parent_sel} > {parts[0]}"
    
    return parts[0]


def _text_candidates(item: Tag, limit: int = 8) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []

    for h in item.find_all(["h1", "h2", "h3", "h4", "h5", "h6"]):
        t = _clean_text(h.get_text(" "))
        if t and len(t) <= 120:
            out.append({"type": "title", "text": t, "selector": _selector_for(h, with_parent=True)})
            break

    for a in item.find_all("a", href=True):
        t = _clean_text(a.get_text(" "))
        if t and len(t) <= 140 and len(t) > 3:
            out.append({"type": "link", "text": t, "href": a.get("href"), "selector": _selector_for(a, with_parent=True)})
            break

    img = item.find("img")
    if img and img.get("src"):
        out.append({"type": "image", "src": img.get("src"), "alt": img.get("alt"), "selector": _selector_for(img)})

    for p in item.find_all(["p", "div"], class_=re.compile(r"(?i)(desc|summary|excerpt|content)")):
        t = _clean_text(p.get_text(" "))
        if t and 20 <= len(t) <= 300:
            out.append({"type": "description", "text": t[:200], "selector": _selector_for(p)})
            break

    price_elem = item.find(class_=re.compile(r"(?i)(price|cost|amount)"))
    if price_elem:
        price_text = _clean_text(price_elem.get_text(" "))
        m_price = _PRICE_RE.search(price_text)
        if m_price:
            out.append({"type": "price", "text": m_price.group(0).strip(), "selector": _selector_for(price_elem)})
    else:
        text_blob = _clean_text(item.get_text(" "))
        m_price = _PRICE_RE.search(text_blob)
        if m_price:
            out.append({"type": "price", "text": m_price.group(0).strip()})
    
    text_blob = _clean_text(item.get_text(" "))
    m_date = _DATE_RE.search(text_blob)
    if m_date:
        out.append({"type": "date", "text": m_date.group(0)})
    
    for elem in item.find_all(class_=re.compile(r"(?i)(author|by|user|posted)")):
        t = _clean_text(elem.get_text(" "))
        if t and len(t) <= 50:
            out.append({"type": "author", "text": t, "selector": _selector_for(elem)})
            break

    if len(out) > limit:
        out = out[:limit]
    return out


@dataclass
class _Candidate:
    container: Tag
    item_tag_name: str
    item_count: int
    score: float


def _is_navigation_or_filter(container: Tag) -> bool:
    container_id = container.get("id", "").lower()
    container_classes = " ".join(container.get("class", [])).lower()
    
    nav_patterns = [
        "nav", "menu", "sidebar", "filter", "refinement", "facet",
        "breadcrumb", "pagination", "footer", "header", "toolbar"
    ]
    
    for pattern in nav_patterns:
        if pattern in container_id or pattern in container_classes:
            return True
    
    return False


def _find_repeating_candidates(soup: BeautifulSoup, max_candidates: int) -> List[_Candidate]:
    candidates: List[_Candidate] = []

    for container in soup.find_all(True):
        if _is_navigation_or_filter(container):
            continue
        
        children = [c for c in container.find_all(recursive=False) if isinstance(c, Tag)]
        if len(children) < 4:
            continue

        sigs = [_node_signature(c) for c in children]
        if not sigs:
            continue

        most_common = max(set(sigs), key=sigs.count)
        count = sigs.count(most_common)
        if count < 4:
            continue

        density = count / max(1, len(children))
        score = count * density

        candidates.append(
            _Candidate(
                container=container,
                item_tag_name=most_common[0],
                item_count=count,
                score=score,
            )
        )

    candidates.sort(key=lambda c: (c.score, c.item_count), reverse=True)

    unique: List[_Candidate] = []
    seen: set[int] = set()
    for c in candidates:
        if id(c.container) in seen:
            continue
        seen.add(id(c.container))
        unique.append(c)
        if len(unique) >= max_candidates:
            break

    return unique


def analyze_url(url: str, max_candidates: int = 5, max_items_preview: int = 5) -> Dict[str, Any]:
    html = fetch_html(url)
    soup = BeautifulSoup(html, "lxml")

    page_title = None
    if soup.title and soup.title.string:
        page_title = _clean_text(soup.title.string)

    candidates = _find_repeating_candidates(soup, max_candidates=max_candidates * 2)

    collections: List[Dict[str, Any]] = []
    for c in candidates:
        children = [ch for ch in c.container.find_all(recursive=False) if isinstance(ch, Tag)]
        item_nodes = [ch for ch in children if ch.name == c.item_tag_name]
        if len(item_nodes) < 1:
            continue

        preview_nodes = item_nodes[: max_items_preview]
        preview = []
        total_fields = 0
        for node in preview_nodes:
            fields = _text_candidates(node)
            preview.append(
                {
                    "item_selector_hint": _selector_for(node, with_parent=True),
                    "fields": fields,
                }
            )
            total_fields += len(fields)
        
        avg_fields = total_fields / max(1, len(preview_nodes))
        if avg_fields < 1.0:
            continue
        
        confidence = round(min(1.0, 0.2 + (c.score / 20.0) + (avg_fields * 0.1)), 3)
        
        if confidence < 0.65:
            continue

        collections.append(
            {
                "container_selector_hint": _selector_for(c.container, with_parent=True),
                "item_tag": c.item_tag_name,
                "estimated_items": c.item_count,
                "confidence": confidence,
                "avg_fields_per_item": round(avg_fields, 2),
                "items_preview": preview,
            }
        )
        
        if len(collections) >= max_candidates:
            break

    return {
        "url": url,
        "page_title": page_title,
        "collections": collections,
        "notes": {
            "mode": "auto_analysis_mvp",
            "limitations": [
                "Ce MVP analyse uniquement le HTML statique renvoyé par la requête (pas de rendu JS).",
                "Les sélecteurs sont des 'hints' (id/classes) et seront améliorés dans la prochaine itération.",
            ],
        },
    }
