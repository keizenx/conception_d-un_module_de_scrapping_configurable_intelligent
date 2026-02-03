# backend/tests/test_content_detector.py
# Test du détecteur de contenus avec un vrai site
# Vérifie qu'on détecte bien articles, produits, etc.
# RELEVANT FILES: content_detector.py, analyzer.py

import sys
sys.path.insert(0, '..')

from src.core.content_detector import ContentDetector
from src.core.fetcher import fetch_html

def test_real_site():
    """Test avec un vrai site e-commerce"""
    print("\n" + "="*60)
    print("TEST: Détection de contenus sur Amazon")
    print("="*60)
    
    url = "https://www.amazon.com/s?k=laptop"
    print(f"\nURL: {url}")
    
    # Récupérer le HTML
    print("\nRécupération du HTML...")
    html = fetch_html(url)
    
    if not html:
        print("❌ Impossible de récupérer le HTML")
        return
    
    print(f"✓ HTML récupéré ({len(html)} caractères)")
    
    # Détecter les contenus
    print("\nAnalyse des contenus...")
    detector = ContentDetector()
    result = detector.detect_content_types(html, url)
    
    print(f"\n{'='*60}")
    print(f"RÉSULTATS")
    print(f"{'='*60}")
    print(f"\nTotal de types détectés: {result['total_types']}")
    print(f"Recommandation: {result['recommended_action']}")
    print(f"Complexité: {result['structure_complexity']}")
    print(f"Pagination: {'Oui' if result['has_pagination'] else 'Non'}")
    print(f"Pages estimées: {result['total_pages_estimate']}")
    
    print(f"\n{'='*60}")
    print(f"TYPES DE CONTENU DÉTECTÉS")
    print(f"{'='*60}")
    
    for content in result['detected_types'][:10]:  # Top 10
        print(f"\n{content['icon']} {content['name']}")
        print(f"   Type: {content['type']}")
        print(f"   Quantité: {content['count']} éléments")
        print(f"   Confiance: {content['confidence']:.0%}")
        print(f"   Champs: {', '.join(content['fields'][:5])}...")
        if content['sample']:
            print(f"   Échantillon:")
            for key, value in list(content['sample'].items())[:2]:
                print(f"      {key}: {value[:50]}...")

def test_blog_site():
    """Test avec un site de blog"""
    print("\n\n" + "="*60)
    print("TEST: Détection de contenus sur un blog")
    print("="*60)
    
    url = "https://techcrunch.com/"
    print(f"\nURL: {url}")
    
    # Récupérer le HTML
    print("\nRécupération du HTML...")
    html = fetch_html(url)
    
    if not html:
        print("❌ Impossible de récupérer le HTML")
        return
    
    print(f"✓ HTML récupéré ({len(html)} caractères)")
    
    # Détecter les contenus
    print("\nAnalyse des contenus...")
    detector = ContentDetector()
    result = detector.detect_content_types(html, url)
    
    print(f"\n{'='*60}")
    print(f"RÉSULTATS")
    print(f"{'='*60}")
    print(f"\nTotal de types détectés: {result['total_types']}")
    print(f"Recommandation: {result['recommended_action']}")
    
    print(f"\n{'='*60}")
    print(f"TYPES DE CONTENU DÉTECTÉS")
    print(f"{'='*60}")
    
    for content in result['detected_types'][:5]:  # Top 5
        print(f"\n{content['icon']} {content['name']}")
        print(f"   Quantité: {content['count']} éléments")
        print(f"   Confiance: {content['confidence']:.0%}")

if __name__ == "__main__":
    test_real_site()
    test_blog_site()
