import httpx
import json

BASE_URL = "http://localhost:8000"

def test_analyze(url: str):
    print(f"\n{'='*80}")
    print(f"TEST ANALYZE: {url}")
    print('='*80)
    
    response = httpx.post(
        f"{BASE_URL}/analyze",
        json={"url": url, "max_candidates": 3, "max_items_preview": 3},
        timeout=30.0
    )
    
    data = response.json()
    
    if data.get("success"):
        print(f"\n✓ Page Title: {data.get('page_title')}")
        print(f"\n✓ Summary:")
        print(f"  - Collections trouvées: {data['summary']['total_collections_found']}")
        print(f"  - Types de champs détectés: {', '.join(data['summary']['detected_field_types'])}")
        
        print(f"\n✓ Collections détectées:")
        for i, collection in enumerate(data.get("collections", [])):
            print(f"\n  [{i}] Collection:")
            print(f"      - Container: {collection['container_selector_hint']}")
            print(f"      - Item tag: {collection['item_tag']}")
            print(f"      - Items estimés: {collection['estimated_items']}")
            print(f"      - Confiance: {collection['confidence']}")
            print(f"      - Champs moyens/item: {collection['avg_fields_per_item']}")
            
            print(f"\n      Aperçu des items:")
            for j, item in enumerate(collection['items_preview'][:2]):
                print(f"        Item {j+1}:")
                for field in item['fields']:
                    if field['type'] == 'title':
                        print(f"          - {field['type']}: {field['text'][:60]}...")
                    elif field['type'] == 'price':
                        print(f"          - {field['type']}: {field['text']}")
                    elif field['type'] == 'image':
                        print(f"          - {field['type']}: {field['src'][:50]}...")
    else:
        print(f"\n✗ Erreur: {data.get('error')}")
    
    return data

def test_scrape(url: str, collection_index: int = 0, max_items: int = 1000):
    print(f"\n{'='*80}")
    print(f"TEST SCRAPE: {url}")
    print(f"Collection index: {collection_index}, Max items: {max_items}")
    print('='*80)
    
    response = httpx.post(
        f"{BASE_URL}/scrape",
        json={"url": url, "collection_index": collection_index, "max_items": max_items},
        timeout=30.0
    )
    
    data = response.json()
    
    if data.get("success"):
        print(f"\n✓ Summary:")
        print(f"  - Items extraits: {data['summary']['total_items_extracted']}")
        print(f"  - Collection info:")
        print(f"    - Container: {data['summary']['collection_info']['container_selector']}")
        print(f"    - Item tag: {data['summary']['collection_info']['item_tag']}")
        print(f"  - Types de champs: {', '.join(data['summary']['detected_field_types'])}")
        
        print(f"\n✓ Premiers items extraits:")
        for i, item in enumerate(data['items'][:5]):
            print(f"\n  Item {i+1}:")
            for field in item['fields']:
                if field['type'] == 'title':
                    print(f"    - {field['type']}: {field['text'][:60]}")
                elif field['type'] == 'price':
                    print(f"    - {field['type']}: {field['text']}")
                elif field['type'] == 'link':
                    print(f"    - {field['type']}: {field['text'][:40]} -> {field.get('href', '')[:30]}")
                elif field['type'] == 'image':
                    print(f"    - {field['type']}: {field.get('src', '')[:50]}")
        
        if len(data['items']) > 5:
            print(f"\n  ... et {len(data['items']) - 5} autres items")
    else:
        print(f"\n✗ Erreur: {data.get('error')}")
    
    return data

if __name__ == "__main__":
    test_urls = [
        "https://books.toscrape.com/",
        "https://scrapeme.live/shop/",
    ]
    
    for url in test_urls:
        try:
            analyze_result = test_analyze(url)
            
            if analyze_result.get("success") and analyze_result.get("collections"):
                scrape_result = test_scrape(url, collection_index=0, max_items=1000)
        except Exception as e:
            print(f"\n✗ Exception: {e}")
        
        print("\n" + "="*80 + "\n")
