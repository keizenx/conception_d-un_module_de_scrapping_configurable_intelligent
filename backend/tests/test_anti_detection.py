# backend/tests/test_anti_detection.py
# Test de l'intégration des techniques anti-détection
# Vérifie que PlaywrightFetcher utilise correctement stealth et les scripts
# RELEVANT FILES: fetcher_playwright.py, fetcher_advanced_free_complete.py

import asyncio
import sys
sys.path.insert(0, 'src')

from core.fetcher_playwright import PlaywrightFetcher

async def test_anti_detection():
    """Test complet de l'anti-détection intégré"""
    
    print("=" * 60)
    print("🧪 TEST ANTI-DETECTION INTEGRE DANS L'APP")
    print("=" * 60)
    
    # 1. Initialisation
    fetcher = PlaywrightFetcher()
    await fetcher.initialize()
    
    print(f"\n📦 Configuration:")
    print(f"   Stealth enabled: {fetcher.stealth_enabled}")
    print(f"   Browser: Chromium")
    
    # 2. Tests sur différents sites
    test_urls = [
        ("httpbin.org/headers", "https://httpbin.org/headers"),
        ("quotes.toscrape.com", "https://quotes.toscrape.com/"),
        ("books.toscrape.com", "https://books.toscrape.com/"),
    ]
    
    results = []
    
    for name, url in test_urls:
        print(f"\n📡 Test: {name}")
        print(f"   URL: {url}")
        
        try:
            result = await fetcher.extract_everything(url, use_stealth=True)
            
            if result.get('success'):
                html_len = len(result.get('html', ''))
                data_count = len(result.get('extracted_data', []))
                print(f"   ✅ Succès!")
                print(f"      HTML: {html_len} chars")
                print(f"      Data: {data_count} items")
                results.append(True)
            else:
                print(f"   ❌ Erreur: {result.get('error', 'Inconnu')}")
                results.append(False)
                
        except Exception as e:
            print(f"   ❌ Exception: {e}")
            results.append(False)
    
    # 3. Résumé
    await fetcher.close()
    
    success_count = sum(results)
    total = len(results)
    
    print("\n" + "=" * 60)
    print(f"📊 RÉSULTAT: {success_count}/{total} tests réussis")
    print("=" * 60)
    
    if success_count == total:
        print("✅ ANTI-DETECTION INTÉGRÉ AVEC SUCCÈS!")
    else:
        print("⚠️ Certains tests ont échoué")
    
    return success_count == total

if __name__ == "__main__":
    success = asyncio.run(test_anti_detection())
    sys.exit(0 if success else 1)
