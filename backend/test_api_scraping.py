# Test API scraping pour babiloc.com
import requests
import json
import time
import sys
import os

# Configuration
API_BASE_URL = "http://127.0.0.1:8000"

def test_api_scraping():
    """Test complet de l'API de scraping"""
    print("=== TEST API SCRAPING BABILOC.COM ===")
    
    # Configuration du scraping
    scraping_data = {
        'url': 'https://babiloc.com',
        'options': {
            'content_types': ['media', 'text_content', 'tables'],
            'depth': 1,
            'delay': 1000,
            'user_agent': 'Chrome (Desktop)',
            'timeout': 30
        }
    }
    
    try:
        # 1. Lancer le scraping
        print("1. Lancement du scraping...")
        start_url = f"{API_BASE_URL}/api/scraping/start/"
        response = requests.post(start_url, json=scraping_data, timeout=10)
        
        print(f"   Status: {response.status_code}")
        if response.status_code != 201:
            print(f"   Erreur: {response.text}")
            return False
            
        result = response.json()
        session_id = result.get('session_id')
        print(f"   Session ID: {session_id}")
        
        if not session_id:
            print("   ❌ Pas de session ID retourné")
            return False
        
        # 2. Attendre le scraping (avec polling)
        print("2. Attente du scraping...")
        max_wait = 20  # 20 secondes max
        check_interval = 2  # Vérifier toutes les 2 secondes
        
        for i in range(0, max_wait, check_interval):
            time.sleep(check_interval)
            
            results_url = f"{API_BASE_URL}/api/results/{session_id}/"
            try:
                results_response = requests.get(results_url, timeout=10)
                if results_response.status_code == 200:
                    results = results_response.json()
                    status = results.get('status')
                    print(f"   Temps: {i+check_interval}s - Status: {status}")
                    
                    if status == 'completed':
                        break
                    elif status == 'failed':
                        error = results.get('error_message', 'Erreur inconnue')
                        print(f"   ❌ Scraping échoué: {error}")
                        return False
                else:
                    print(f"   ⚠️ Erreur lors de la vérification: {results_response.status_code}")
            except Exception as e:
                print(f"   ⚠️ Erreur réseau: {e}")
        
        # 3. Récupérer les résultats finaux
        print("3. Récupération des résultats...")
        try:
            final_results = requests.get(results_url, timeout=10).json()
            final_status = final_results.get('status')
            scraped_data = final_results.get('scraped_data', [])
            
            print(f"   Status final: {final_status}")
            print(f"   Éléments extraits: {len(scraped_data)}")
            
            if len(scraped_data) > 0:
                print("   ✅ Scraping réussi!")
                print(f"   Premier élément: {scraped_data[0]}")
                
                # 4. Test des exports
                print("4. Test des exports...")
                for export_format in ['csv', 'json']:
                    export_url = f"{API_BASE_URL}/api/results/{session_id}/export/?format={export_format}"
                    try:
                        export_response = requests.get(export_url, timeout=10)
                        print(f"   Export {export_format.upper()}: {export_response.status_code} - {len(export_response.content)} bytes")
                    except Exception as e:
                        print(f"   Export {export_format} échoué: {e}")
                
                return True
            else:
                print("   ❌ Aucun élément extrait")
                return False
                
        except Exception as e:
            print(f"   ❌ Erreur lors de la récupération: {e}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Impossible de se connecter au serveur Django")
        print("   Assurez-vous que le serveur tourne sur http://127.0.0.1:8000")
        return False
    except Exception as e:
        print(f"❌ Erreur inattendue: {e}")
        return False

def check_server():
    """Vérifier que le serveur Django est accessible"""
    try:
        response = requests.get(f"{API_BASE_URL}/api/", timeout=5)
        print(f"✅ Serveur accessible - Status: {response.status_code}")
        return True
    except:
        print("❌ Serveur non accessible")
        return False

if __name__ == "__main__":
    print("=== TEST API SCRAPING BABILOC.COM ===")
    
    if check_server():
        success = test_api_scraping()
        if success:
            print("\n🎉 TEST COMPLET RÉUSSI!")
        else:
            print("\n❌ TEST ÉCHOUÉ")
    else:
        print("\nDémarrez le serveur avec: python manage.py runserver")
        print("Puis relancez ce script.")