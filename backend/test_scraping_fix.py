# Test du scraping direct
import sys
import os
import django

# Configuration de Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from api.models import ScrapingSession, ScrapedData, User
from src.core.analyzer import analyze_url

def test_scraping_logic():
    """
    Test direct de la logique de scraping sans passer par l'API
    """
    print("=== TEST DIRECT DU SCRAPING ===")
    
    # Créer un utilisateur de test
    user, created = User.objects.get_or_create(
        username='test_user',
        defaults={'email': 'test@test.com'}
    )
    
    # Créer une session de scraping
    session = ScrapingSession.objects.create(
        user=user,
        url='https://babiloc.com',
        configuration={
            'content_types': ['media', 'text_content'],
            'depth': 1,
            'delay': 1000
        },
        status='pending'
    )
    
    print(f"Session créée: #{session.id}")
    
    try:
        session.status = 'in_progress'
        session.save()
        
        # Test de l'import analyze_url
        print("Test de l'import analyze_url...")
        result = analyze_url('https://babiloc.com', max_candidates=10, max_items_preview=10, use_js=True)
        
        if not result or not result.get('scrapable_content'):
            print("❌ Analyse échouée - pas de contenu scrapable")
            return
            
        print("✅ Analyse réussie")
        
        scrapable = result['scrapable_content']
        detected_types = scrapable.get('detected_types', [])
        selected_types = session.configuration.get('content_types', [])
        
        print(f"Types détectés: {[t.get('type') for t in detected_types]}")
        print(f"Types sélectionnés: {selected_types}")
        
        # Simulation du scraping
        scraped_count = 0
        for detected_type in detected_types:
            type_name = detected_type.get('type', '')
            type_display_name = detected_type.get('name', '')
            
            # Vérifier si ce type est sélectionné
            if type_name in selected_types or not selected_types:
                element_count = min(detected_type.get('count', 0), 5)  # Limiter à 5 pour le test
                
                print(f"Extraction de {type_display_name} ({element_count} éléments)...")
                
                for i in range(element_count):
                    data_item = {
                        'titre': f'Test {type_display_name} {i+1}',
                        'contenu': f'Contenu test de type {type_name}',
                        'url_source': session.url
                    }
                    
                    # Créer ScrapedData
                    ScrapedData.objects.create(
                        session=session,
                        data=data_item,
                        element_type=type_name,
                        source_url=session.url
                    )
                    scraped_count += 1
        
        # Finaliser la session
        session.status = 'completed'
        session.success_count = scraped_count
        session.total_items = scraped_count
        session.save()
        
        print(f"✅ Scraping terminé avec succès!")
        print(f"   Session #{session.id} - {scraped_count} éléments extraits")
        
        # Vérifier les données créées
        scraped_objects = session.scraped_data.all()
        print(f"   Vérification DB: {scraped_objects.count()} objets ScrapedData")
        
        if scraped_objects.count() > 0:
            first_item = scraped_objects.first()
            print(f"   Premier item: {first_item.element_type} - {first_item.data}")
            
        # Test de l'export
        print("\n=== TEST DE L'EXPORT ===")
        scraped_data = [obj.data for obj in scraped_objects]
        print(f"Données pour export: {len(scraped_data)} items")
        
        if scraped_data:
            print("Premier item d'export:", scraped_data[0])
            print("✅ Export fonctionne!")
        else:
            print("❌ Pas de données pour l'export")
            
    except Exception as e:
        print(f"❌ Erreur lors du scraping: {e}")
        session.status = 'failed' 
        session.error_message = str(e)
        session.save()

if __name__ == "__main__":
    test_scraping_logic()