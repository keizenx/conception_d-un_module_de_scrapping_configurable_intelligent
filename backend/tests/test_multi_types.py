import httpx
import json

BASE_URL = "http://localhost:8000"

test_sites = {
    "E-commerce": [
        "https://books.toscrape.com/",
        "https://scrapeme.live/shop/",
    ],
    "Blog/Articles": [
        "https://blog.python.org/",
        "https://realpython.com/",
    ],
    "Actualités": [
        "https://news.ycombinator.com/",
        "https://www.reddit.com/r/programming/",
    ],
    "Documentation": [
        "https://docs.python.org/3/library/",
    ],
}


def test_analyze_site(url: str, category: str):
    print(f"\n{'='*100}")
    print(f"CATÉGORIE: {category}")
    print(f"URL: {url}")
    print("=" * 100)

    try:
        response = httpx.post(
            f"{BASE_URL}/analyze",
            json={"url": url, "max_candidates": 3, "max_items_preview": 3},
            timeout=30.0,
        )

        if response.status_code != 200:
            print(f"✗ Erreur HTTP {response.status_code}")
            return None

        data = response.json()

        if data.get("success"):
            print(f"\n✓ Page Title: {data.get('page_title', 'N/A')[:80]}")
            print(f"\n✓ Résumé:")
            print(
                f"  - Collections trouvées: {data['summary']['total_collections_found']}"
            )

            if data["summary"]["total_collections_found"] > 0:
                print(
                    f"  - Types de champs détectés: {', '.join(data['summary']['detected_field_types'])}"
                )

                print(f"\n✓ Collections détectées:")
                for i, collection in enumerate(data.get("collections", [])):
                    print(f"\n  [{i}] Collection:")
                    print(f"      - Container: {collection['container_selector_hint']}")
                    print(f"      - Item tag: {collection['item_tag']}")
                    print(f"      - Items estimés: {collection['estimated_items']}")
                    print(f"      - Confiance: {collection['confidence']}")
                    print(
                        f"      - Champs moyens/item: {collection['avg_fields_per_item']}"
                    )

                    if collection["items_preview"]:
                        print(f"\n      Aperçu du premier item:")
                        first_item = collection["items_preview"][0]
                        for field in first_item["fields"][:4]:
                            if field["type"] == "title":
                                print(
                                    f"        - {field['type']}: {field['text'][:60]}"
                                )
                            elif field["type"] == "price":
                                print(f"        - {field['type']}: {field['text']}")
                            elif field["type"] == "link":
                                print(
                                    f"        - {field['type']}: {field['text'][:40]}"
                                )
                            elif field["type"] == "image":
                                print(
                                    f"        - {field['type']}: {field.get('src', '')[:50]}"
                                )
                            elif field["type"] == "description":
                                print(
                                    f"        - {field['type']}: {field['text'][:50]}..."
                                )
                            elif field["type"] == "date":
                                print(f"        - {field['type']}: {field['text']}")
                            elif field["type"] == "author":
                                print(f"        - {field['type']}: {field['text']}")

                print(f"\n  ✓ VALIDATION: Détection réussie pour {category}")
            else:
                print(f"\n  ✗ ÉCHEC: Aucune collection détectée pour {category}")
        else:
            print(f"\n✗ Erreur: {data.get('error')}")
            return None

        return data

    except httpx.TimeoutException:
        print(f"\n✗ Timeout: Le site n'a pas répondu dans les 30 secondes")
        return None
    except Exception as e:
        print(f"\n✗ Exception: {e}")
        return None


if __name__ == "__main__":
    print("\n" + "=" * 100)
    print("TEST DE VALIDATION: ANALYSE SUR DIFFÉRENTS TYPES DE PAGES WEB")
    print("=" * 100)

    results = {}

    for category, urls in test_sites.items():
        results[category] = []
        for url in urls:
            result = test_analyze_site(url, category)
            results[category].append(
                {
                    "url": url,
                    "success": result is not None and result.get("success", False),
                    "collections_found": result["summary"]["total_collections_found"]
                    if result and result.get("success")
                    else 0,
                }
            )
            print("\n")

    print("\n" + "=" * 100)
    print("RÉSUMÉ DES RÉSULTATS")
    print("=" * 100)

    for category, category_results in results.items():
        total = len(category_results)
        success = sum(
            1 for r in category_results if r["success"] and r["collections_found"] > 0
        )
        print(f"\n{category}: {success}/{total} sites validés")
        for r in category_results:
            status = "✓" if r["success"] and r["collections_found"] > 0 else "✗"
            print(f"  {status} {r['url']} - {r['collections_found']} collection(s)")
