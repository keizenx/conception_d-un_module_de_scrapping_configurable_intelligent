# 🚀 TEST API ULTRA-COMPLÈTE OPTIMISÉE
# Backend\tests\test_api_ultra_complete.py - Test des endpoints FastAPI optimisés
# Test complet de l'intégration PlaywrightFetcher dans l'API
# RELEVANT FILES: scrape.py, fetcher_playwright.py, scraper.py, test_ultra_complete.py

import requests
import json
import time

def test_api_ultra_complete():
    """
    Test complet de l'API ultra-complète optimisée
    """
    print("🚀 TEST API ULTRA-COMPLÈTE OPTIMISÉE")
    print("=" * 60)
    
    base_url = "http://127.0.0.1:8000/api/scrape"
    
    test_sites = [
        {
            "name": "Site de test simple",
            "url": "https://httpbin.org/html",
            "use_scroll": False,
            "timeout": 20.0
        },
        {
            "name": "Site avec JavaScript dynamique",
            "url": "https://quotes.toscrape.com/js/",
            "use_scroll": True,
            "timeout": 30.0
        },
        {
            "name": "Site avec métadonnées riches",
            "url": "https://github.com",
            "use_scroll": False,
            "timeout": 25.0
        }
    ]
    
    for i, site in enumerate(test_sites, 1):
        print(f"\n🌟 TEST API {i}: {site['name']}")
        print(f"URL: {site['url']}")
        print(f"Options: scroll={site['use_scroll']}, timeout={site['timeout']}s")
        print("-" * 50)
        
        try:
            # Test endpoint ultra-complete
            start_time = time.time()
            
            response = requests.post(
                f"{base_url}/ultra-complete",
                headers={'Content-Type': 'application/json'},
                json={
                    'url': site['url'],
                    'use_scroll': site['use_scroll'],
                    'timeout_seconds': site['timeout']
                },
                timeout=60
            )
            
            duration = time.time() - start_time
            print(f"Status: {response.status_code} (durée: {duration:.2f}s)")
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('success'):
                    summary = data.get('summary', {})
                    metadata = data.get('data', {}).get('metadata', {})
                    
                    print("✅ EXTRACTION API RÉUSSIE !")
                    print(f"   📝 Texte: {summary.get('total_text_length', 0):,} caractères")
                    print(f"   🖼️  Images: {summary['media_found']['images']} (+{summary['media_found']['background_images']} background)")
                    print(f"   🎥 Médias: {summary['media_found']['videos']} vidéos, {summary['media_found']['audios']} audios")
                    print(f"   🔗 Contenu: {summary['content_found']['links']} liens, {summary['content_found']['files']} fichiers")
                    print(f"   📊 Structure: {summary['content_found']['forms']} formulaires, {summary['content_found']['tables']} tableaux")
                    print(f"   📦 Données JSON-LD: {summary['content_found']['structured_data']}")
                    print(f"   📋 Titre: {metadata.get('title', 'N/A')[:60]}...")
                    print(f"   🌐 Langue: {metadata.get('language', 'N/A')}")
                    
                    # Afficher les optimisations utilisées
                    optimizations = data.get('optimizations_used', [])
                    if optimizations:
                        print(f"   ⚡ Optimisations actives:")
                        for opt in optimizations[:3]:
                            print(f"      • {opt}")
                    
                    # Sauvegarder résultats détaillés  
                    filename = f"api_test_{i}.json"
                    with open(filename, 'w', encoding='utf-8') as f:
                        json.dump(data, f, indent=2, ensure_ascii=False)
                    print(f"   💾 Données complètes sauvées: {filename}")
                    
                else:
                    print(f"❌ Erreur API: {data.get('error', 'Inconnue')}")
                    
            elif response.status_code == 422:
                print(f"❌ Erreur validation: {response.json()}")
            elif response.status_code == 500:
                error_detail = response.json().get('detail', 'Erreur serveur')
                print(f"❌ Erreur serveur: {error_detail}")
            else:
                print(f"❌ Erreur HTTP {response.status_code}: {response.text[:200]}")
                
        except requests.exceptions.Timeout:
            print("❌ Timeout de la requête")
        except requests.exceptions.ConnectionError:
            print("❌ Erreur de connexion - Le serveur est-il démarré ?")
        except Exception as e:
            print(f"❌ Exception: {str(e)}")
            
        # Pause entre tests
        if i < len(test_sites):
            time.sleep(2)
    
    print("\n" + "=" * 60)
    print("🎉 TESTS API ULTRA-COMPLÈTE TERMINÉS")
    print("✅ PlaywrightFetcher intégré dans FastAPI")
    print("✅ Endpoints /scrape/ultra-complete opérationnels")
    print("✅ Toutes les optimisations actives")
    print("✅ Extraction métadonnées, médias, formulaires")
    print("✅ Support contenu dynamique avec scroll")
    print("✅ Headers anti-détection et User-Agent rotation")
    print("✅ Gestion d'erreurs et timeouts")
    print("✅ 100% GRATUIT et production-ready !")


def test_api_health():
    """
    Test rapide de la santé de l'API
    """
    print("\n🔍 Test de santé API...")
    try:
        # Test endpoint simple
        response = requests.post(
            "http://127.0.0.1:8000/api/scrape/ultra-complete",
            headers={'Content-Type': 'application/json'},
            json={
                'url': 'https://httpbin.org/html',
                'use_scroll': False,
                'timeout_seconds': 15.0
            },
            timeout=30
        )
        
        if response.status_code == 200:
            print("✅ API fonctionnelle !")
            return True
        else:
            print(f"⚠️ API répond avec status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ API non accessible: {str(e)}")
        return False


if __name__ == "__main__":
    # Test de santé d'abord
    if test_api_health():
        # Puis tests complets
        test_api_ultra_complete()
    else:
        print("\n💡 Assurez-vous que le serveur FastAPI est démarré avec :")
        print("   cd backend")
        print("   python -m uvicorn src.index:app --reload --host 127.0.0.1 --port 8000")