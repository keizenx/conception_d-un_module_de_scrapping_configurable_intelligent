# backend/src/core/site_estimator.py
# Estimation du nombre de pages d'un site avant le crawl complet
# Utilise sitemap.xml, robots.txt, et échantillonnage intelligent
# RELEVANT FILES: smart_crawler.py, views.py

import httpx
from bs4 import BeautifulSoup
from typing import Dict, Optional
from urllib.parse import urljoin, urlparse
import re


class SiteEstimator:
    """
    Estime le nombre de pages d'un site web avant de lancer le crawl complet.
    Stratégies: sitemap, robots.txt, échantillonnage, patterns d'URL.
    """
    
    def __init__(self, base_url: str, timeout: int = 20):
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        }
    
    def estimate_total_pages(self) -> Dict:
        """
        Estime le nombre total de pages du site.
        
        Returns:
            {
                'estimated_pages': int,
                'confidence': 'high' | 'medium' | 'low',
                'method': str,
                'details': {...},
                'recommended_max_crawl': int
            }
        """
        # Stratégie 1: Sitemap.xml (plus fiable)
        sitemap_result = self._check_sitemap()
        if sitemap_result and sitemap_result['count'] > 0:
            return {
                'estimated_pages': sitemap_result['count'],
                'confidence': 'high',
                'method': 'sitemap.xml',
                'details': sitemap_result,
                'recommended_max_crawl': min(sitemap_result['count'], 100)
            }
        
        # Stratégie 1.5: OSINT (Wayback Machine, URLScan)
        osint_result = self._check_osint()
        if osint_result and osint_result['count'] > 0:
            return {
                'estimated_pages': osint_result['count'],
                'confidence': 'medium',
                'method': f"OSINT ({osint_result['source']})",
                'details': osint_result,
                'recommended_max_crawl': min(osint_result['count'], 100)
            }

        # Stratégie 2: PageDetector (Playwright) pour sites JS/SPA
        # C'est plus lent mais beaucoup plus précis pour les sites modernes comme babiloc.com
        try:
            from .page_detector import PageDetector
            print(f"[*] PageDetector (Playwright) scanning: {self.base_url}")
            detector = PageDetector(self.base_url, timeout=self.timeout * 1000)
            detector_result = detector.analyze_with_screenshot(max_depth=1)
            
            pages_found = detector_result['total_pages']
            stats = detector_result.get('stats', {})
            print(f"[+] PageDetector result: found {pages_found} pages, stats: {stats}")
            
            if pages_found > 0:
                # Si on trouve des pages via Playwright, c'est très fiable
                estimated = pages_found
                
                # Si pagination détectée, on multiplie
                if stats.get('has_pagination'):
                    estimated = int(estimated * 3)
                    print(f"[+] Pagination detected, multiplying estimation to {estimated}")
                
                return {
                    'estimated_pages': estimated,
                    'confidence': 'high',
                    'method': 'Playwright Scan (JS detected)',
                    'details': {
                        'pages_found': pages_found,
                        'stats': stats
                    },
                    'recommended_max_crawl': min(estimated, 100)
                }
        except Exception as e:
            print(f"[-] PageDetector failed: {e}")
            import traceback
            print(traceback.format_exc())

        # Stratégie 3: Robots.txt + échantillonnage (Fallback statique)
        robots_result = self._check_robots()
        sample_result = self._sample_homepage()
        
        # Combiner les résultats
        if sample_result and sample_result.get('links_count', 0) > 0:
            # Estimation basique: nombre de liens trouvés * facteur de profondeur
            links_count = sample_result['links_count']
            
            # Si peu de liens (< 5), on suppose que le site est plat/petit (Landing page)
            if links_count < 5:
                # CORRECTION: Ne pas ajouter +1 artificiellement si on veut être strict sur les liens trouvés
                # Si links_count = 2 (home + contact), on estime à 2.
                estimated = max(links_count, 1) 
                confidence = 'high'
            else:
                depth_factor = 2.5  # Estimation moyenne de pages par niveau
                estimated = int(links_count * depth_factor)
                confidence = 'medium'
            
            # Ajuster avec robots.txt si disponible
            if robots_result and robots_result.get('crawl_delay'):
                # Site avec crawl_delay = généralement plus gros
                estimated = int(estimated * 1.5)
            
            return {
                'estimated_pages': estimated,
                'confidence': confidence,
                'method': 'sampling (analyse page d\'accueil)',
                'details': {
                    'homepage_links': links_count,
                    'robots_info': robots_result
                },
                'recommended_max_crawl': min(estimated, 100)
            }
        
        # Stratégie 3: Estimation par défaut
        return {
            'estimated_pages': 50,
            'confidence': 'low',
            'method': 'default',
            'details': {'reason': 'Aucune donnée disponible'},
            'recommended_max_crawl': 50
        }
    
    def _check_osint(self) -> Optional[Dict]:
        """
        Utilise des sources OSINT (Wayback Machine, URLScan) pour estimer le nombre de pages.
        Inspiré de la logique subfinder/passive discovery.
        """
        domain = urlparse(self.base_url).netloc
        
        # 1. URLScan.io
        try:
            url = f"https://urlscan.io/api/v1/search/?q=domain:{domain}"
            with httpx.Client(timeout=10, follow_redirects=True) as client:
                response = client.get(url)
                if response.status_code == 200:
                    data = response.json()
                    total = data.get('total', 0)
                    if total > 0:
                        return {
                            'count': total,
                            'source': 'urlscan.io',
                            'type': 'passive_scan'
                        }
        except:
            pass

        # 2. Wayback Machine (Archive.org)
        try:
            # CDX API pour compter les URLs uniques (collapse=urlkey)
            # On limite à 500 pour ne pas surcharger, mais si on atteint 500 c'est qu'il y en a bcp
            url = f"http://web.archive.org/cdx/search/cdx?url={domain}/*&output=json&fl=original&collapse=urlkey&limit=500"
            with httpx.Client(timeout=15, follow_redirects=True) as client:
                response = client.get(url)
                if response.status_code == 200:
                    data = response.json()
                    # Le premier élément est le header ["original"], on l'enlève
                    if len(data) > 1:
                        count = len(data) - 1
                        return {
                            'count': count if count < 500 else 500, # Si 500, c'est probablement plus
                            'source': 'wayback_machine',
                            'type': 'historical_index'
                        }
        except:
            pass
            
        return None

    def _check_sitemap(self) -> Optional[Dict]:
        """
        Vérifie sitemap.xml pour compter les URLs.
        """
        sitemap_urls = [
            f"{self.base_url}/sitemap.xml",
            f"{self.base_url}/sitemap_index.xml",
            f"{self.base_url}/sitemap1.xml"
        ]
        
        for sitemap_url in sitemap_urls:
            try:
                response = httpx.get(sitemap_url, headers=self.headers, timeout=self.timeout, follow_redirects=True)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'xml')
                    
                    # Compter les <url> ou <sitemap>
                    urls = soup.find_all('url')
                    sitemaps = soup.find_all('sitemap')
                    
                    if urls:
                        return {
                            'count': len(urls),
                            'sitemap_url': sitemap_url,
                            'type': 'direct'
                        }
                    elif sitemaps:
                        # Sitemap index - compter dans chaque sous-sitemap
                        total_urls = 0
                        for sitemap in sitemaps[:5]:  # Limiter à 5 sous-sitemaps
                            loc = sitemap.find('loc')
                            if loc:
                                sub_count = self._count_sitemap_urls(loc.text)
                                total_urls += sub_count
                        
                        return {
                            'count': total_urls,
                            'sitemap_url': sitemap_url,
                            'type': 'index',
                            'sub_sitemaps': len(sitemaps)
                        }
            except:
                continue
        
        return None
    
    def _count_sitemap_urls(self, sitemap_url: str) -> int:
        """Compte les URLs dans un sitemap spécifique."""
        try:
            response = httpx.get(sitemap_url, headers=self.headers, timeout=self.timeout)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'xml')
                return len(soup.find_all('url'))
        except:
            pass
        return 0
    
    def _check_robots(self) -> Optional[Dict]:
        """
        Analyse robots.txt pour obtenir des indices.
        """
        try:
            robots_url = f"{self.base_url}/robots.txt"
            response = httpx.get(robots_url, headers=self.headers, timeout=self.timeout)
            
            if response.status_code == 200:
                content = response.text
                
                # Chercher Crawl-delay (indique un gros site)
                crawl_delay = re.search(r'Crawl-delay:\s*(\d+)', content, re.IGNORECASE)
                
                # Chercher Sitemap
                sitemap_refs = re.findall(r'Sitemap:\s*(.+)', content, re.IGNORECASE)
                
                # Compter les Disallow (beaucoup = site complexe)
                disallow_count = len(re.findall(r'Disallow:', content, re.IGNORECASE))
                
                return {
                    'has_robots': True,
                    'crawl_delay': int(crawl_delay.group(1)) if crawl_delay else None,
                    'sitemap_refs': sitemap_refs,
                    'disallow_count': disallow_count
                }
        except:
            pass
        
        return None
    
    def _sample_homepage(self) -> Optional[Dict]:
        """
        Échantillonne la page d'accueil pour estimer la taille du site.
        """
        try:
            response = httpx.get(
                self.base_url, 
                headers=self.headers, 
                timeout=self.timeout, 
                follow_redirects=True,
                verify=False  # Ignorer SSL pour certains sites
            )
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Compter les liens internes
                base_domain = urlparse(self.base_url).netloc
                internal_links = set()
                
                for link in soup.find_all('a', href=True):
                    href = link['href']
                    try:
                        full_url = urljoin(self.base_url, href)
                        parsed = urlparse(full_url)
                        
                        if parsed.netloc == base_domain or parsed.netloc == '':
                            # Nettoyer l'URL (enlever fragments, paramètres)
                            clean_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
                            if clean_url and clean_url != f"{parsed.scheme}://{parsed.netloc}/":
                                internal_links.add(clean_url)
                    except:
                        continue
                
                # Détecter pagination
                has_pagination = bool(soup.find_all(['a', 'div'], class_=re.compile(r'pag', re.I)))
                
                # Détecter blog/news (indique beaucoup de pages)
                is_blog = bool(soup.find_all(['article', 'div'], class_=re.compile(r'post|article|blog', re.I)))
                
                return {
                    'links_count': len(internal_links),
                    'has_pagination': has_pagination,
                    'is_blog': is_blog,
                    'total_links': len(soup.find_all('a'))
                }
        except Exception as e:
            print(f"Erreur lors de l'échantillonnage: {e}")
        
        return None


if __name__ == "__main__":
    # Test
    import sys
    
    test_url = sys.argv[1] if len(sys.argv) > 1 else "https://example.com"
    
    print(f"\n{'='*60}")
    print(f"ESTIMATION DU NOMBRE DE PAGES")
    print(f"{'='*60}\n")
    print(f"URL: {test_url}\n")
    
    estimator = SiteEstimator(test_url)
    result = estimator.estimate_total_pages()
    
    print(f"Estimation: {result['estimated_pages']} pages")
    print(f"Confiance: {result['confidence']}")
    print(f"Méthode: {result['method']}")
    print(f"Crawl recommandé: {result['recommended_max_crawl']} pages max")
    print(f"\nDétails:")
    for key, value in result['details'].items():
        print(f"  • {key}: {value}")
