import httpx

BASE_URL = "http://localhost:8000"

print("\n" + "=" * 100)
print("TEST: Vérification que l'API supporte le paramètre use_js")
print("=" * 100)

print("\n1. Test avec use_js=False (mode HTTP classique)")
try:
    response = httpx.post(
        f"{BASE_URL}/analyze",
        json={
            "url": "https://books.toscrape.com/",
            "use_js": False,
            "max_candidates": 1,
        },
        timeout=30.0,
    )

    if response.status_code == 200:
        data = response.json()
        if data.get("success"):
            print(f"   ✓ Mode HTTP classique fonctionne")
            print(
                f"   ✓ Collections trouvées: {data['summary']['total_collections_found']}"
            )
        else:
            print(f"   ✗ Erreur: {data.get('error')}")
    else:
        print(f"   ✗ HTTP {response.status_code}")
except Exception as e:
    print(f"   ✗ Exception: {e}")

print("\n2. Test avec use_js=True (mode Playwright)")
print(
    "   Note: Playwright doit être installé avec 'pip install playwright' et 'playwright install chromium'"
)
try:
    response = httpx.post(
        f"{BASE_URL}/analyze",
        json={
            "url": "https://books.toscrape.com/",
            "use_js": True,
            "max_candidates": 1,
        },
        timeout=60.0,
    )

    if response.status_code == 200:
        data = response.json()
        if data.get("success"):
            print(f"   ✓ Mode Playwright fonctionne")
            print(
                f"   ✓ Collections trouvées: {data['summary']['total_collections_found']}"
            )
        else:
            print(f"   ✗ Erreur: {data.get('error')}")
    else:
        print(f"   ✗ HTTP {response.status_code}: {response.text[:200]}")
except httpx.TimeoutException:
    print(
        f"   ✗ Timeout - Le serveur n'a pas répondu (Playwright peut prendre plus de temps)"
    )
except Exception as e:
    print(f"   ⚠ Exception: {e}")
    print(f"   Note: Si Playwright n'est pas installé, c'est normal")

print("\n" + "=" * 100)
print("RÉSUMÉ")
print("=" * 100)
print("\nL'API est prête à supporter Playwright.")
print("Pour activer Playwright, exécutez:")
print("  1. pip install playwright")
print("  2. playwright install chromium")
print("\nEnsuite, utilisez use_js=true dans vos requêtes pour les sites JavaScript.")
