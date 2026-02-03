"""
Script de test manuel simple pour tester le scraper sur n'importe quelle URL
"""
import httpx
import json

BASE_URL = "http://localhost:8000"


def test_url(url: str, use_js: bool = False):
    """Teste une URL avec analyse puis scraping"""

    print(f"\n{'='*100}")
    print(f"TEST: {url}")
    print(f"Mode: {'JavaScript (Playwright)' if use_js else 'HTTP classique'}")
    print("=" * 100)

    # 1. Analyser la page
    print("\n1️⃣  ANALYSE DE LA PAGE...")
    try:
        response = httpx.post(
            f"{BASE_URL}/analyze",
            json={
                "url": url,
                "max_candidates": 3,
                "max_items_preview": 2,
                "use_js": use_js,
            },
            timeout=60.0,
        )

        if response.status_code != 200:
            print(f"❌ Erreur HTTP {response.status_code}")
            return

        data = response.json()

        if not data.get("success"):
            print(f"❌ Erreur: {data.get('error')}")
            return

        print(f"✅ Page: {data.get('page_title', 'N/A')[:80]}")
        print(f"✅ Collections trouvées: {data['summary']['total_collections_found']}")

        if data["summary"]["total_collections_found"] == 0:
            print("⚠️  Aucune collection détectée sur cette page")
            return

        print(f"\n📊 Collections disponibles:")
        for i, col in enumerate(data["collections"]):
            print(f"\n   [{i}] {col['item_tag']} items")
            print(f"       Container: {col['container_selector_hint']}")
            print(f"       Items estimés: {col['estimated_items']}")
            print(f"       Confiance: {col['confidence']}")
            print(f"       Champs/item: {col['avg_fields_per_item']}")

            if col["items_preview"]:
                print(f"       Aperçu:")
                for field in col["items_preview"][0]["fields"][:3]:
                    field_text = field.get("text", field.get("src", ""))[:50]
                    print(f"         - {field['type']}: {field_text}")

        # 2. Scraper la première collection
        print(f"\n2️⃣  SCRAPING DE LA COLLECTION [0]...")

        response = httpx.post(
            f"{BASE_URL}/scrape",
            json={
                "url": url,
                "collection_index": 0,
                "max_items": 1000,
                "use_js": use_js,
            },
            timeout=60.0,
        )

        if response.status_code != 200:
            print(f"❌ Erreur HTTP {response.status_code}")
            return

        data = response.json()

        if not data.get("success"):
            print(f"❌ Erreur: {data.get('error')}")
            return

        print(f"✅ Items extraits: {data['summary']['total_items_extracted']}")
        print(
            f"✅ Types de champs: {', '.join(data['summary']['detected_field_types'])}"
        )

        print(f"\n📦 Premiers items extraits:")
        for i, item in enumerate(data["items"][:3], 1):
            print(f"\n   Item {i}:")
            for field in item["fields"][:4]:
                if field["type"] in ["title", "link"]:
                    print(f"     - {field['type']}: {field.get('text', '')[:50]}")
                elif field["type"] == "price":
                    print(f"     - {field['type']}: {field.get('text', '')}")
                elif field["type"] == "image":
                    print(f"     - {field['type']}: {field.get('src', '')[:50]}")

        if len(data["items"]) > 3:
            print(f"\n   ... et {len(data['items']) - 3} autres items")

        print(f"\n✅ SUCCÈS - {data['summary']['total_items_extracted']} items extraits")

    except httpx.TimeoutException:
        print(f"❌ Timeout - Le serveur n'a pas répondu")
    except Exception as e:
        print(f"❌ Exception: {e}")


if __name__ == "__main__":
    print("\n" + "=" * 100)
    print("🔍 TEST MANUEL DU MODULE DE SCRAPING")
    print("=" * 100)

    # Exemples de sites à tester
    test_sites = [
        ("https://books.toscrape.com/", False),
        ("https://scrapeme.live/shop/", False),
        ("https://news.ycombinator.com/", False),
    ]

    print("\n📝 Sites de test disponibles:")
    for i, (url, _) in enumerate(test_sites, 1):
        print(f"   {i}. {url}")

    print("\n" + "-" * 100)

    # Tester chaque site
    for url, use_js in test_sites:
        test_url(url, use_js)
        print("\n")

    print("\n" + "=" * 100)
    print("💡 POUR TESTER VOS PROPRES URLs:")
    print("=" * 100)
    print(
        """
Modifiez ce script et ajoutez vos URLs dans la liste test_sites:

    test_sites = [
        ("https://votre-site.com/", False),  # False = HTTP classique
        ("https://site-js.com/", True),      # True = Playwright (JavaScript)
    ]

Ou utilisez l'interface Swagger: http://localhost:8000/docs
    """
    )
