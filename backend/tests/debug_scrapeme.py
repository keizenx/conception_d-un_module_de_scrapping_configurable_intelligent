import httpx
from bs4 import BeautifulSoup
from src.core.analyzer import _find_repeating_candidates, _selector_for, _text_candidates

url = "https://scrapeme.live/shop/"

html = httpx.get(url, follow_redirects=True, timeout=20.0).text
soup = BeautifulSoup(html, "lxml")

candidates = _find_repeating_candidates(soup, max_candidates=10)

print(f"\n{'='*80}")
print(f"DEBUG: {url}")
print('='*80)

for i, c in enumerate(candidates):
    print(f"\n[{i}] Candidate:")
    print(f"    Container: {_selector_for(c.container, with_parent=True)}")
    print(f"    Container tag: {c.container.name}")
    print(f"    Container id: {c.container.get('id', 'N/A')}")
    print(f"    Container classes: {c.container.get('class', [])}")
    print(f"    Item tag: {c.item_tag_name}")
    print(f"    Item count: {c.item_count}")
    print(f"    Score: {c.score}")
    
    children = [ch for ch in c.container.find_all(recursive=False) if hasattr(ch, 'name')]
    item_nodes = [ch for ch in children if ch.name == c.item_tag_name]
    
    if item_nodes:
        print(f"\n    Premier item:")
        fields = _text_candidates(item_nodes[0])
        for field in fields[:5]:
            if field['type'] == 'title':
                print(f"      - {field['type']}: {field['text'][:60]}")
            elif field['type'] == 'price':
                print(f"      - {field['type']}: {field['text']}")
            elif field['type'] == 'link':
                print(f"      - {field['type']}: {field['text'][:40]}")
            elif field['type'] == 'image':
                print(f"      - {field['type']}: {field.get('src', '')[:50]}")

print("\n\nRecherche manuelle des produits:")
products = soup.find_all("li", class_="product")
print(f"Produits trouvés avec class='product': {len(products)}")
if products:
    print(f"Premier produit:")
    fields = _text_candidates(products[0])
    for field in fields[:5]:
        print(f"  - {field['type']}: {field.get('text', field.get('src', ''))[:60]}")
