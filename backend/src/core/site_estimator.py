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
        
        # Stratégie 2: Robots.txt + échantillonnage
        robots_result = self._check_robots()
        sample_result = self._sample_homepage()
        
        # Combiner les résultats
        if sample_result and sample_result.get('links_count', 0) > 0:
            # Estimation basique: nombre de liens trouvés * facteur de profondeur
            links_count = sample_result['links_count']
            depth_factor = 2.5  # Estimation moyenne de pages par niveau
            
            estimated = int(links_count * depth_factor)
            
            # Ajuster avec robots.txt si disponible
            if robots_result and robots_result.get('crawl_delay'):
                # Site avec crawl_delay = généralement plus gros
                estimated = int(estimated * 1.5)
            
            return {
                'estimated_pages': estimated,
                'confidence': 'medium',
                'method': 'sampling',
                'details': {
                    'homepage_links': links_count,
                    'depth_factor': depth_factor,
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
