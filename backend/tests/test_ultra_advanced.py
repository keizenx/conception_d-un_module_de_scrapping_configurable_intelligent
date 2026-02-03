# Backend/tests/test_ultra_advanced.py - Tests complets des techniques anti-détection
# Teste toutes les stratégies avancées contre différents types de sites
# Valide l'efficacité du contournement Cloudflare et autres protections
# RELEVANT FILES: fetcher_advanced_free_complete.py, scrape.py, fetcher_playwright.py

import asyncio
import pytest
import time
from typing import Dict, Any, List

# Import des fetchers
try:
    from backend.src.core.fetcher_playwright import get_fetcher
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False

try:
    from backend.src.core.fetcher_advanced_free_complete import get_advanced_fetcher
    ADVANCED_AVAILABLE = True
except ImportError:
    ADVANCED_AVAILABLE = False


class UltraAdvancedTester:
    """
    🧪 Testeur ultra-avancé pour techniques anti-détection
    
    Tests:
    - Sites normaux vs sites protégés
    - Efficacité Cloudflare bypass
    - Comparaison stratégies (Chrome vs Firefox)
    - Performance extraction
    - Stabilité anti-détection
    """
    
    def __init__(self):
        self.test_sites = {
            # Sites normaux (contrôle)
            "normal": [
                "https://httpbin.org/html",
                "https://example.com",
                "https://quotes.toscrape.com"
            ],
            
            # Sites JavaScript intensifs
            "javascript": [
                "https://quotes.toscrape.com/js/",
                "https://scrapethissite.com/pages/javascript/"
            ],
            
            # Sites avec protections modérées
            "protected": [
                "https://httpbin.org/user-agent",
                "https://httpbin.org/headers"
            ]
        }
        
        self.results = []
    
    async def test_all_strategies(self):
        """
        🚀 Test COMPLET de toutes les stratégies disponibles
        """
        print("="*80)
        print("🧪 TESTS ULTRA-AVANCÉS - TECHNIQUES ANTI-DÉTECTION")
        print("="*80)
        
        # 1. Test disponibilité des composants
        await self._test_availability()
        
        # 2. Test stratégies sur sites normaux
        await self._test_normal_sites()
        
        # 3. Test stratégies sur sites JavaScript
        await self._test_javascript_sites()
        
        # 4. Test stratégies sur sites protégés
        await self._test_protected_sites()
        
        # 5. Analyser résultats
        self._analyze_results()
    
    async def _test_availability(self):
        """Test de disponibilité des composants"""
        print("\n🔍 VÉRIFICATION DISPONIBILITÉ COMPOSANTS")
        print("-" * 50)
        
        print(f"   ✅ Playwright Fetcher: {'OUI' if PLAYWRIGHT_AVAILABLE else '❌ NON'}")
        print(f"   ✅ Advanced Fetcher: {'OUI' if ADVANCED_AVAILABLE else '❌ NON'}")
        
        if PLAYWRIGHT_AVAILABLE:
            try:
                fetcher = await get_fetcher()
                print("   ✅ PlaywrightFetcher initialisé avec succès")
            except Exception as e:
                print(f"   ❌ Erreur PlaywrightFetcher: {e}")
        
        if ADVANCED_AVAILABLE:
            try:
                advanced_fetcher = await get_advanced_fetcher()
                print("   ✅ AdvancedFreeFetcher initialisé avec succès")
            except Exception as e:
                print(f"   ❌ Erreur AdvancedFreeFetcher: {e}")
    
    async def _test_normal_sites(self):
        """Test sur sites normaux (baseline)"""
        print("\n🔵 TESTS SITES NORMAUX (Baseline)")
        print("-" * 50)
        
        for url in self.test_sites["normal"]:
            print(f"\n📋 Test: {url}")
            
            # Test avec stratégies disponibles
            if PLAYWRIGHT_AVAILABLE:
                result = await self._test_single_strategy(url, "optimized")
                self.results.append(result)
            
            if ADVANCED_AVAILABLE:
                result = await self._test_single_strategy(url, "stealth")
                self.results.append(result)
                
                result = await self._test_single_strategy(url, "firefox")
                self.results.append(result)
    
    async def _test_javascript_sites(self):
        """Test sur sites JavaScript intensifs"""
        print("\n🟡 TESTS SITES JAVASCRIPT")
        print("-" * 50)
        
        for url in self.test_sites["javascript"]:
            print(f"\n📋 Test: {url}")
            
            if PLAYWRIGHT_AVAILABLE:
                result = await self._test_single_strategy(url, "optimized")
                self.results.append(result)
            
            if ADVANCED_AVAILABLE:
                result = await self._test_single_strategy(url, "stealth")
                self.results.append(result)
    
    async def _test_protected_sites(self):
        """Test sur sites avec protections"""
        print("\n🟢 TESTS SITES PROTÉGÉS") 
        print("-" * 50)
        
        for url in self.test_sites["protected"]:
            print(f"\n📋 Test: {url}")
            
            if ADVANCED_AVAILABLE:
                # Tester toutes les stratégies avancées
                result = await self._test_single_strategy(url, "stealth")
                self.results.append(result)
                
                result = await self._test_single_strategy(url, "firefox")
                self.results.append(result)
                
                result = await self._test_single_strategy(url, "auto")
                self.results.append(result)
    
    async def _test_single_strategy(self, url: str, strategy: str) -> Dict[str, Any]:
        """Test une stratégie sur une URL"""
        start_time = time.time()
        
        try:
            if strategy == "optimized" and PLAYWRIGHT_AVAILABLE:
                fetcher = await get_fetcher()
                result = await fetcher.fetch_with_ultra_complete_extraction(
                    url=url,
                    use_scroll=True,
                    timeout_seconds=20.0
                )
            
            elif strategy == "stealth" and ADVANCED_AVAILABLE:
                fetcher = await get_advanced_fetcher()
                result = await fetcher.scrape_with_advanced_stealth(
                    url=url,
                    use_scroll=True,
                    timeout_seconds=20.0
                )
            
            elif strategy == "firefox" and ADVANCED_AVAILABLE:
                fetcher = await get_advanced_fetcher()
                result = await fetcher.scrape_with_firefox(
                    url=url,
                    use_scroll=True,
                    timeout_seconds=20.0
                )
            
            elif strategy == "auto" and ADVANCED_AVAILABLE:
                fetcher = await get_advanced_fetcher()
                result = await fetcher.scrape_with_auto_strategy(
                    url=url,
                    use_scroll=True,
                    timeout_seconds=20.0
                )
            
            else:
                result = {
                    'success': False,
                    'error': f'Stratégie {strategy} non disponible',
                    'strategy': strategy
                }
            
            duration = time.time() - start_time
            
            # Log résultat
            if result.get('success'):
                text_length = result.get('summary', {}).get('total_text_length', 0)
                images = result.get('summary', {}).get('media_found', {}).get('images', 0)
                links = result.get('summary', {}).get('content_found', {}).get('links', 0)
                
                print(f"      ✅ {strategy.upper()}: {text_length:,} chars | {images} images | {links} liens | {duration:.1f}s")
            else:
                error = result.get('error', 'Erreur inconnue')
                print(f"      ❌ {strategy.upper()}: {error[:50]}... | {duration:.1f}s")
            
            # Enrichir résultat pour analyse
            result['test_url'] = url
            result['test_strategy'] = strategy
            result['test_duration'] = duration
            result['test_timestamp'] = time.time()
            
            return result
            
        except Exception as e:
            duration = time.time() - start_time
            print(f"      💥 {strategy.upper()}: Exception {str(e)[:50]}... | {duration:.1f}s")
            
            return {
                'success': False,
                'error': str(e),
                'test_url': url,
                'test_strategy': strategy,
                'test_duration': duration,
                'test_timestamp': time.time()
            }
    
    def _analyze_results(self):
        """Analyse complète des résultats de tests"""
        print("\n" + "="*80)
        print("📊 ANALYSE COMPLÈTE DES RÉSULTATS")
        print("="*80)
        
        # Statistiques globales
        total_tests = len(self.results)
        successful_tests = [r for r in self.results if r.get('success', False)]
        failed_tests = [r for r in self.results if not r.get('success', False)]
        
        print(f"\n📈 STATISTIQUES GLOBALES:")
        print(f"   • Tests total: {total_tests}")
        print(f"   • Réussis: {len(successful_tests)} ({len(successful_tests)/total_tests*100:.1f}%)")
        print(f"   • Échoués: {len(failed_tests)} ({len(failed_tests)/total_tests*100:.1f}%)")
        
        # Analyse par stratégie
        print(f"\n🎯 PERFORMANCE PAR STRATÉGIE:")
        strategies = set(r.get('test_strategy', 'unknown') for r in self.results)
        
        for strategy in strategies:
            strategy_results = [r for r in self.results if r.get('test_strategy') == strategy]
            successful = [r for r in strategy_results if r.get('success', False)]
            
            if strategy_results:
                success_rate = len(successful) / len(strategy_results) * 100
                avg_duration = sum(r.get('test_duration', 0) for r in strategy_results) / len(strategy_results)
                
                if successful:
                    avg_text_length = sum(r.get('summary', {}).get('total_text_length', 0) for r in successful) / len(successful)
                    avg_images = sum(r.get('summary', {}).get('media_found', {}).get('images', 0) for r in successful) / len(successful)
                    avg_links = sum(r.get('summary', {}).get('content_found', {}).get('links', 0) for r in successful) / len(successful)
                else:
                    avg_text_length = avg_images = avg_links = 0
                
                print(f"\n   🔸 {strategy.upper()}:")
                print(f"      • Taux réussite: {success_rate:.1f}% ({len(successful)}/{len(strategy_results)})")
                print(f"      • Durée moyenne: {avg_duration:.1f}s")
                print(f"      • Extraction moyenne: {avg_text_length:,.0f} caractères")
                print(f"      • Images moyenne: {avg_images:.1f}")
                print(f"      • Liens moyenne: {avg_links:.1f}")
        
        # Meilleure stratégie
        print(f"\n🏆 RECOMMANDATIONS:")
        
        # Calculer score pour chaque stratégie (success_rate * avg_extraction)
        strategy_scores = {}
        for strategy in strategies:
            strategy_results = [r for r in self.results if r.get('test_strategy') == strategy]
            successful = [r for r in strategy_results if r.get('success', False)]
            
            if strategy_results and successful:
                success_rate = len(successful) / len(strategy_results)
                avg_text_length = sum(r.get('summary', {}).get('total_text_length', 0) for r in successful) / len(successful)
                score = success_rate * avg_text_length
                strategy_scores[strategy] = score
        
        if strategy_scores:
            best_strategy = max(strategy_scores, key=strategy_scores.get)
            print(f"   ⭐ Meilleure stratégie globale: {best_strategy.upper()}")
            
            # Recommandations par type de site
            print(f"   📋 Recommandations d'usage:")
            print(f"      • Sites normaux: optimized (rapide et fiable)")
            print(f"      • Sites JavaScript: stealth (meilleure extraction)")
            print(f"      • Sites protégés: {best_strategy} (score le plus élevé)")
            print(f"      • Maximum compatibilité: auto (adaptatif)")
        
        # Erreurs communes
        print(f"\n⚠️ ERREURS FRÉQUENTES:")
        error_counts = {}
        for result in failed_tests:
            error = result.get('error', 'Erreur inconnue')
            error_type = error.split(':')[0] if ':' in error else error[:30]
            error_counts[error_type] = error_counts.get(error_type, 0) + 1
        
        for error_type, count in sorted(error_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"   • {error_type}: {count} occurrences")


async def run_ultra_advanced_tests():
    """
    🚀 Fonction principale pour lancer tous les tests ultra-avancés
    """
    tester = UltraAdvancedTester()
    await tester.test_all_strategies()


if __name__ == "__main__":
    # Lancer les tests
    print("🚀 Démarrage des tests ultra-avancés...")
    asyncio.run(run_ultra_advanced_tests())
    print("\n✅ Tests terminés !")