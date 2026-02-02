import csv
import io
import json
import pandas as pd
from typing import List, Dict, Any

def flatten_items(items: List[Dict[str, Any]]) -> List[Dict[str, str]]:
    """Aplatir une liste d'items pour l'export tabulaire"""
    flat_items = []
    for item in items:
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
        flat_items.append(flat)
    return flat_items

def generate_csv(items: List[Dict[str, Any]]) -> str:
    flat_items = flatten_items(items)
    if not flat_items:
        return ""
    
    df = pd.DataFrame(flat_items)
    return df.to_csv(index=False)

def generate_excel(items: List[Dict[str, Any]]) -> bytes:
    flat_items = flatten_items(items)
    if not flat_items:
        return b""
    
    output = io.BytesIO()
    df = pd.DataFrame(flat_items)
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    return output.getvalue()

def generate_json(items: List[Dict[str, Any]]) -> str:
    return json.dumps(items, ensure_ascii=False, indent=2)
