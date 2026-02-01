import httpx
from bs4 import BeautifulSoup

url = "https://scrapeme.live/shop/"
html = httpx.get(url, follow_redirects=True, timeout=20.0).text
soup = BeautifulSoup(html, "lxml")

products = soup.find_all("li", class_="product")
print(f"Produits trouvés: {len(products)}")

if products:
    product = products[0]
    parent = product.parent
    print(f"\nParent des produits:")
    print(f"  Tag: {parent.name}")
    print(f"  Classes: {parent.get('class', [])}")
    print(f"  ID: {parent.get('id', 'N/A')}")
    
    siblings = [ch for ch in parent.find_all(recursive=False) if hasattr(ch, 'name')]
    print(f"\n  Enfants directs du parent: {len(siblings)}")
    
    product_siblings = [ch for ch in siblings if ch.name == 'li']
    print(f"  Enfants <li>: {len(product_siblings)}")
    
    print(f"\n  Signatures des enfants:")
    for i, ch in enumerate(siblings[:5]):
        classes = ch.get("class") or []
        print(f"    [{i}] {ch.name} - classes: {classes}")
