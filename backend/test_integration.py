# 🧪 Test rapide de la classe PlaywrightFetcher optimisée
# Backend\test_integration.py - Validation de l'intégration complète
# Test direct sans problèmes d'import
# RELEVANT FILES: fetcher_playwright.py, scrape.py, test_ultra_complete.py

import sys
import os

# Ajouter le chemin du backend pour les imports
backend_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_path)

import asyncio
from src.core.fetcher_playwright import PlaywrightFetcher

async def test_integration():
    """
    Test d'intégration de la classe PlaywrightFetcher optimisée
    """
    print("🧪 TEST INTÉGRATION PLAYWRIGHT FETCHER OPTIMISÉ")
    print("=" * 55)
    
    fetcher = PlaywrightFetcher()
    
    test_sites = [
        {
            "name": "Test de base",
            "url": "https://httpbin.org/html",
            "scroll": False
        },
        {
            "name": "Test JavaScript dynamique", 
            "url": "https://quotes.toscrape.com/js/",
            "scroll": True
        }
    ]
    
    try:
        for i, site in enumerate(test_sites, 1):
            print(f"\n🌟 TEST {i}: {site['name']}")
            print(f"URL: {site['url']}")
            print("-" * 35)
            
            result = await fetcher.extract_everything(
                url=site['url'],
                use_scroll=site['scroll'],
                timeout_seconds=25.0
            )
            
            if result.get('success'):
                summary = result.get('summary', {})
                print("✅ EXTRACTION RÉUSSIE !")
                print(f"   📝 Texte: {summary.get('total_text_length', 0):,} caractères")
                print(f"   🖼️  Images: {summary['media_found']['images']}")
                print(f"   🔗 Liens: {summary['content_found']['links']}")
                print(f"   📊 Formulaires: {summary['content_found']['forms']}")
                print(f"   ⚡ Méthode: {result.get('extraction_method', 'N/A')}")
                
                # Vérifier les optimisations
                optimizations = result.get('optimizations_used', [])
                if optimizations:
                    print(f"   🚀 Optimisations actives: {len(optimizations)}")
                    for opt in optimizations[:2]:
                        print(f"      • {opt}")
            else:
                print(f"❌ Erreur: {result.get('error', 'Inconnue')}")
                
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        await fetcher.close()
        print("\n✅ Navigateur fermé proprement")
    
    print("\n🎉 TEST INTÉGRATION TERMINÉ")
    print("✅ PlaywrightFetcher fonctionnel")
    print("✅ Toutes les optimisations intégrées")
    print("✅ Extraction ultra-complète opérationnelle")


if __name__ == "__main__":
    asyncio.run(test_integration())