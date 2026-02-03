# 🌟 DÉMONSTRATION EXTRACTION ULTRA-COMPLÈTE
# Backend\tests\demo_ultra_complete.py - Test des nouvelles fonctionnalités
# Démonstration des optimisations gratuites intégrées dans notre scraper
# RELEVANT FILES: fetcher_playwright.py, scraper.py, test_manual.py, CONFIGURATIONS_OPTIMALES.md

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.fetcher_playwright import extract_complete_content_sync
import json

def demo_ultra_complete():
    """
    🚀 DÉMONSTRATION : Extraction ULTRA-COMPLÈTE
    """
    print("🌟" + "="*70)
    print("🚀 DÉMONSTRATION EXTRACTION ULTRA-COMPLÈTE")
    print("🌟 Toutes les optimisations gratuites intégrées !")
    print("="*70)
    
    test_sites = [
        {
            "name": "Site avec JavaScript dynamique",
            "url": "https://quotes.toscrape.com/js/",
            "features": "Contenu dynamique, scroll automatique"
        },
        {
            "name": "Site avec métadonnées riches", 
            "url": "https://github.com",
            "features": "OpenGraph, JSON-LD, images background"
        },
        {
            "name": "Site de base",
            "url": "https://httpbin.org/html",
            "features": "HTML simple, test de référence"
        }
    ]
    
    for i, site in enumerate(test_sites, 1):
        print(f"\n🌟 TEST {i}: {site['name']}")
        print(f"URL: {site['url']}")
        print(f"Fonctionnalités: {site['features']}")
        print("-" * 50)
        
        try:
            # Extraction ultra-complète
            use_scroll = site['url'].endswith('/js/')  # Scroll pour contenu JS
            result = extract_complete_content_sync(
                url=site['url'],
                timeout_seconds=25.0,
                scroll_for_dynamic=use_scroll
            )
            
            stats = result.get('extraction_stats', {})
            metadata = result.get('metadata', {})
            
            print("✅ EXTRACTION RÉUSSIE !")
            print(f"   📝 Texte: {stats.get('text_length', 0):,} caractères")
            print(f"   🖼️  Images: {stats.get('images', 0)} (+{stats.get('background_images', 0)} background CSS)")
            print(f"   🎥 Vidéos: {stats.get('videos', 0)}, Audios: {stats.get('audios', 0)}, iFrames: {stats.get('iframes', 0)}")
            print(f"   🔗 Liens: {stats.get('links', 0)}, Fichiers: {stats.get('files', 0)}")
            print(f"   📊 Formulaires: {stats.get('forms', 0)}, Tableaux: {stats.get('tables', 0)}")
            print(f"   📦 Données structurées JSON-LD: {stats.get('structured_data', 0)}")
            print(f"   📋 Titre: {metadata.get('title', 'N/A')[:60]}...")
            print(f"   📄 Description: {metadata.get('description', 'N/A')[:80]}...")
            print(f"   🌐 Langue: {metadata.get('language', 'N/A')}")
            
            # Montrer quelques extraits de contenu
            text_data = result.get('text', {})
            if text_data.get('headings', {}).get('h1'):
                print(f"   📌 H1 trouvés: {len(text_data['headings']['h1'])}")
                for h1 in text_data['headings']['h1'][:2]:
                    print(f"      • {h1[:50]}...")
                    
            if result.get('media', {}).get('images'):
                images = result['media']['images']
                print(f"   🎨 Premières images:")
                for img in images[:3]:
                    print(f"      • {img.get('alt', 'Sans alt')} - {img.get('src', '')[:60]}")
            
            # Sauvegarder résultats détaillés
            filename = f"demo_ultra_complete_{i}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            print(f"   💾 Détails complets sauvés: {filename}")
            
        except Exception as e:
            print(f"❌ Erreur: {str(e)}")
            import traceback
            traceback.print_exc()
        
        print()
    
    print("🎉" + "="*70)
    print("🚀 DÉMONSTRATION TERMINÉE - TOUTES LES OPTIMISATIONS INTÉGRÉES !")
    print("="*70)
    print("✅ Headers anti-détection avancés (12 champs)")
    print("✅ User-Agent rotation automatique (5 agents)")
    print("✅ Délais adaptatifs intelligents")
    print("✅ Retry logic avec backoff exponentiel")
    print("✅ Optimisations Playwright (block images/fonts)")
    print("✅ Scroll automatique pour contenu dynamique")
    print("✅ Extraction métadonnées complètes (OpenGraph)")
    print("✅ Images background CSS détectées")
    print("✅ Données structurées JSON-LD extraites")
    print("✅ Formulaires et tableaux structurés")
    print("✅ Support vidéos, audios, iframes (YouTube/Vimeo)")
    print("✅ 100% GRATUIT - Aucune API payante requise !")
    print("="*70)


if __name__ == "__main__":
    demo_ultra_complete()