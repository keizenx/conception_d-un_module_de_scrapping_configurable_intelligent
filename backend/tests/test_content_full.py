# backend/tests/test_content_full.py
# Test complet d'analyse de contenu
# Simule ce que l'utilisateur verra dans l'UI
# RELEVANT FILES: analyzer.py, content_detector.py

import sys
sys.path.insert(0, '..')

import json
from src.core.analyzer import analyze_url

def test_full_analysis():
    """Test de l'analyse complète avec détection de contenus"""
    print("\n" + "="*70)
    print("TEST COMPLET: Analyse de page avec détection de contenus")
    print("="*70)
    
    # Test avec un site éducatif
    url = "https://www.iit.ci/"
    print(f"\nAnalyse de: {url}")
    print("-" * 70)
    
    result = analyze_url(url)
    
    if not result.get('success'):
        print("❌ Échec de l'analyse")
        print(json.dumps(result, indent=2))
        return
    
    print(f"\n✓ Page analysée: {result['page_title']}")
    
    # Afficher les contenus scrapables détectés
    if 'scrapable_content' in result:
        content = result['scrapable_content']
        
        print(f"\n{'='*70}")
        print(f"CONTENUS SCRAPABLES DÉTECTÉS")
        print(f"{'='*70}")
        
        print(f"\nStatistiques:")
        print(f"  • Total de types: {content['total_types']}")
        print(f"  • Recommandation: {content['recommended_action']}")
        print(f"  • Complexité: {content['structure_complexity']}")
        print(f"  • Pagination: {'Oui' if content.get('has_pagination') else 'Non'}")
        
        if content['detected_types']:
            print(f"\n{'='*70}")
            print(f"TYPES DISPONIBLES POUR LE SCRAPING")
            print(f"{'='*70}")
            
            for item in content['detected_types']:
                print(f"\n  {item['icon']} {item['name']}")
                print(f"     Type: {item['type']}")
                print(f"     Éléments trouvés: {item['count']}")
                print(f"     Confiance: {item['confidence']:.0%}")
                print(f"     Description: {item['description']}")
                print(f"     Champs disponibles: {', '.join(item['fields'])}")
                
                if item.get('sample'):
                    print(f"     Échantillon:")
                    for key, val in item['sample'].items():
                        preview = str(val)[:60] + '...' if len(str(val)) > 60 else str(val)
                        print(f"       - {key}: {preview}")
        
        # Simulation de sélection utilisateur
        print(f"\n{'='*70}")
        print(f"SIMULATION: Options de scraping")
        print(f"{'='*70}")
        
        print("\nL'utilisateur peut choisir:")
        print("  1. ✓ Tout scraper (tous les types)")
        print("  2. ✓ Scraper seulement:")
        
        for item in content['detected_types']:
            print(f"     • {item['name']} ({item['count']} éléments)")
        
        print("\n  3. ✓ Combinaison personnalisée")
        print("     Exemple: Articles + Images + Navigation seulement")

if __name__ == "__main__":
    test_full_analysis()
