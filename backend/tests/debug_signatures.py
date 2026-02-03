import httpx
from bs4 import BeautifulSoup
from src.core.analyzer import _node_signature

url = "https://scrapeme.live/shop/"
html = httpx.get(url, follow_redirects=True, timeout=20.0).text
soup = BeautifulSoup(html, "lxml")

products = soup.find_all("li", class_="product")
parent = products[0].parent

children = [ch for ch in parent.find_all(recursive=False) if hasattr(ch, "name")]

print(f"Enfants: {len(children)}")
print(f"\nSignatures:")

sigs = [_node_signature(c) for c in children]
for i, sig in enumerate(sigs[:5]):
    print(f"  [{i}] {sig}")

print(f"\nSignatures uniques: {len(set(sigs))}")
print(f"\nSignature la plus commune:")
most_common = max(set(sigs), key=sigs.count)
print(f"  {most_common}")
print(f"  Count: {sigs.count(most_common)}")
