import csv
import io
from typing import List, Dict, Any

from fastapi import APIRouter
from fastapi.responses import StreamingResponse, PlainTextResponse
from pydantic import BaseModel, HttpUrl

from src.core.scraper import scrape_url

router = APIRouter(prefix="/export", tags=["export"])


class ExportRequest(BaseModel):
    url: HttpUrl
    collection_index: int = 0
    max_items: int = 1000


def _flatten_item(item: Dict[str, Any]) -> Dict[str, str]:
    """Aplatir un item pour l'export CSV"""
    flat = {}
    for field in item.get("fields", []):
        field_type = field["type"]
        if field_type == "link":
            flat[f"{field_type}_text"] = field.get("text", "")
            flat[f"{field_type}_href"] = field.get("href", "")
        elif field_type == "image":
            flat[f"{field_type}_src"] = field.get("src", "")
            flat[f"{field_type}_alt"] = field.get("alt", "")
        else:
            flat[field_type] = field.get("text", "")
    return flat


@router.post("/csv")
def export_csv(req: ExportRequest):
    """Exporter les résultats en CSV"""
    result = scrape_url(
        url=str(req.url), collection_index=req.collection_index, max_items=req.max_items
    )

    if not result.get("success"):
        return {"error": result.get("error", "Erreur inconnue")}

    items = result.get("items", [])
    if not items:
        return {"error": "Aucun item à exporter"}

    # Aplatir les items
    flat_items = [_flatten_item(item) for item in items]

    # Créer le CSV
    output = io.StringIO()
    if flat_items:
        fieldnames = list(flat_items[0].keys())
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(flat_items)

    # Retourner le CSV
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=scrape_results.csv"},
    )


@router.post("/text")
def export_text(req: ExportRequest):
    """Exporter les résultats en texte lisible"""
    result = scrape_url(
        url=str(req.url), collection_index=req.collection_index, max_items=req.max_items
    )

    if not result.get("success"):
        return PlainTextResponse(f"ERREUR: {result.get('error', 'Erreur inconnue')}")

    items = result.get("items", [])
    summary = result.get("summary", {})

    # Créer le texte formaté
    lines = []
    lines.append("=" * 80)
    lines.append(f"RÉSULTATS DU SCRAPING")
    lines.append("=" * 80)
    lines.append(f"URL: {result.get('url')}")
    lines.append(f"Total items extraits: {summary.get('total_items_extracted', 0)}")
    lines.append(
        f"Types de champs détectés: {', '.join(summary.get('detected_field_types', []))}"
    )
    lines.append("=" * 80)
    lines.append("")

    for idx, item in enumerate(items, 1):
        lines.append(f"--- ITEM {idx} ---")
        for field in item.get("fields", []):
            field_type = field["type"].upper()
            if field_type == "LINK":
                lines.append(
                    f"  {field_type}: {field.get('text', '')} ({field.get('href', '')})"
                )
            elif field_type == "IMAGE":
                lines.append(
                    f"  {field_type}: {field.get('src', '')} (alt: {field.get('alt', 'N/A')})"
                )
            else:
                lines.append(f"  {field_type}: {field.get('text', '')}")
        lines.append("")

    lines.append("=" * 80)
    lines.append(f"FIN - {len(items)} items extraits")
    lines.append("=" * 80)

    return PlainTextResponse("\n".join(lines))


@router.post("/markdown")
def export_markdown(req: ExportRequest):
    """Exporter les résultats en Markdown"""
    result = scrape_url(
        url=str(req.url), collection_index=req.collection_index, max_items=req.max_items
    )

    if not result.get("success"):
        return PlainTextResponse(
            f"# ERREUR\n\n{result.get('error', 'Erreur inconnue')}"
        )

    items = result.get("items", [])
    summary = result.get("summary", {})

    # Créer le Markdown
    lines = []
    lines.append("# Résultats du Scraping")
    lines.append("")
    lines.append(f"**URL:** {result.get('url')}")
    lines.append(f"**Total items extraits:** {summary.get('total_items_extracted', 0)}")
    lines.append(
        f"**Types de champs:** {', '.join(summary.get('detected_field_types', []))}"
    )
    lines.append("")
    lines.append("---")
    lines.append("")

    for idx, item in enumerate(items, 1):
        lines.append(f"## Item {idx}")
        lines.append("")
        for field in item.get("fields", []):
            field_type = field["type"].capitalize()
            if field["type"] == "link":
                lines.append(
                    f"- **{field_type}:** [{field.get('text', '')}]({field.get('href', '')})"
                )
            elif field["type"] == "image":
                lines.append(
                    f"- **{field_type}:** ![{field.get('alt', '')}]({field.get('src', '')})"
                )
            else:
                lines.append(f"- **{field_type}:** {field.get('text', '')}")
        lines.append("")

    return PlainTextResponse("\n".join(lines), media_type="text/markdown")
