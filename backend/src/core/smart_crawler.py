# backend/src/core/smart_crawler.py
# Crawler intelligent utilisant Playwright pour découvrir la structure d'un site
# Similaire à Web Scraper, ParseHub, Octoparse - ouvre le site réel et détecte les patterns
# RELEVANT FILES: fetcher_playwright.py, path_finder.py, analyzer.py

from playwright.sync_api import sync_playwright, Page, Browser
from urllib.parse import urlparse, urljoin
from typing import Dict, List, Set, Tuple
import re
import time


class SmartCrawler:
    """
    Crawler intelligent qui ouvre un site avec Playwright et découvre automatiquement:
    - Les menus de navigation
    - Les liens importants
    - La structure des pages
    - Les répertoires et chemins
    """
    
    def __init__(self, base_url: str, max_pages: int = 30, timeout: int = 30000):
        self.base_url = base_url
        self.max_pages = max_pages
        self.timeout = timeout
        self.parsed_base = urlparse(base_url)
        self.visited_urls = set()
        self.discovered_paths = set()
        self.navigation_links = {}
        
    def is_same_domain(self, url: str) -> bool:
        """Vérifie si l'URL appartient au même domaine."""
        parsed = urlparse(url)
        return parsed.netloc == self.parsed_base.netloc or parsed.netloc == ''
    
    def normalize_url(self, url: str) -> str:
        """Normalise une URL."""
        # Construire l'URL absolue
        absolute_url = urljoin(self.base_url, url)
        parsed = urlparse(absolute_url)
        
        # Retirer le fragment (#)
        url_without_fragment = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
        
        # Retirer le trailing slash sauf pour la racine
        if parsed.path != '/' and url_without_fragment.endswith('/'):
            url_without_fragment = url_without_fragment.rstrip('/')
        
        return url_without_fragment
    
    def is_valid_page(self, url: str) -> bool:
        """Vérifie si l'URL est une page valide à crawler."""
        # Ignorer les fichiers statiques
        ignored_extensions = [
            '.jpg', '.jpeg', '.png', '.gif', '.svg', '.ico', '.webp',
            '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.zip', '.rar',
            '.css', '.js', '.woff', '.woff2', '.ttf', '.eot',
            '.mp4', '.avi', '.mov', '.mp3', '.wav'
        ]
        
        url_lower = url.lower()
        
        # Ignorer les extensions de fichiers
        if any(url_lower.endswith(ext) for ext in ignored_extensions):
            return False
        
        # Ignorer les liens mailto, tel, etc.
        if any(url_lower.startswith(prefix) for prefix in ['mailto:', 'tel:', 'javascript:', '#']):
            return False
        
        return True
    
    def extract_page_preview(self, page: Page) -> Dict:
        """
        Extrait une prévisualisation du contenu de la page :
        - Images principales
        - Texte principal
        - Meta description
        - Nombre d'éléments (liens, images, formulaires)
        """
        preview = {
            'meta': {},
            'images': [],
            'text_preview': '',
            'stats': {
                'total_links': 0,
                'total_images': 0,
                'total_forms': 0,
                'total_tables': 0,
                'total_lists': 0
            }
        }
        
        try:
            # Meta tags
            meta_selectors = {
                'description': 'meta[name="description"]',
                'keywords': 'meta[name="keywords"]',
                'og:title': 'meta[property="og:title"]',
                'og:description': 'meta[property="og:description"]',
                'og:image': 'meta[property="og:image"]'
            }
            
            for key, selector in meta_selectors.items():
                try:
                    element = page.query_selector(selector)
                    if element:
                        content = element.get_attribute('content')
                        if content:
                            preview['meta'][key] = content[:200]
                except:
                    pass
            
            # Images principales (seulement les grandes images, pas les icônes)
            try:
                images = page.query_selector_all('img')
                for img in images[:10]:  # Max 10 images
                    try:
                        src = img.get_attribute('src')
                        alt = img.get_attribute('alt') or ''
                        width = img.get_attribute('width') or '0'
                        height = img.get_attribute('height') or '0'
                        
                        if src:
                            # Normaliser l'URL de l'image
                            if src.startswith('//'):
                                src = 'https:' + src
                            elif src.startswith('/'):
                                src = self.base_url.rstrip('/') + src
                            elif not src.startswith('http'):
                                src = self.base_url.rstrip('/') + '/' + src
                            
                            # Filtrer les petites images (icônes, logos)
                            try:
                                w = int(width) if width.isdigit() else 999
                                h = int(height) if height.isdigit() else 999
                                if w > 100 or h > 100:  # Images de taille raisonnable
                                    preview['images'].append({
                                        'src': src,
                                        'alt': alt[:100],
                                        'width': width,
                                        'height': height
                                    })
                            except:
                                # Si pas de dimensions, on garde quand même
                                preview['images'].append({
                                    'src': src,
                                    'alt': alt[:100]
                                })
                    except:
                        continue
            except:
                pass
            
            # Texte principal (extrait du corps de la page)
            try:
                # Chercher le contenu principal
                main_selectors = [
                    'main',
                    'article',
                    '.content',
                    '.main-content',
                    '#content',
                    '[role="main"]',
                    'body'
                ]
                
                for selector in main_selectors:
                    try:
                        main_element = page.query_selector(selector)
                        if main_element:
                            text = main_element.inner_text()
                            # Nettoyer et limiter
                            text = ' '.join(text.split())  # Normaliser les espaces
                            preview['text_preview'] = text[:300] + '...' if len(text) > 300 else text
                            break
                    except:
                        continue
            except:
                pass
            
            # Statistiques
            try:
                preview['stats']['total_links'] = len(page.query_selector_all('a[href]'))
                preview['stats']['total_images'] = len(page.query_selector_all('img'))
                preview['stats']['total_forms'] = len(page.query_selector_all('form'))
                preview['stats']['total_tables'] = len(page.query_selector_all('table'))
                preview['stats']['total_lists'] = len(page.query_selector_all('ul, ol'))
            except:
                pass
            
        except Exception as e:
            print(f"    └─ Erreur extraction preview: {e}")
        
        return preview
    
    def extract_navigation_links(self, page: Page) -> Dict[str, List[Dict]]:
        """
        Extrait les liens de navigation depuis les zones clés du site.
        Similaire à la détection automatique de Web Scraper/Octoparse.
        """
        navigation_data = {
            'header': [],
            'nav': [],
            'menu': [],
            'footer': [],
            'sidebar': [],
            'other': []
        }
        
        # Sélecteurs pour les zones de navigation communes
        selectors = {
            'header': 'header a, .header a, #header a, [class*="header"] a',
            'nav': 'nav a, .nav a, .navbar a, .navigation a, [role="navigation"] a',
            'menu': '.menu a, #menu a, [class*="menu"] a',
            'footer': 'footer a, .footer a, #footer a, [class*="footer"] a',
            'sidebar': 'aside a, .sidebar a, #sidebar a, [class*="sidebar"] a'
        }
        
        for zone, selector in selectors.items():
            try:
                links = page.query_selector_all(selector)
                
                for link in links[:50]:  # Limiter pour éviter les surcharges
                    try:
                        href = link.get_attribute('href')
                        text = link.inner_text().strip()
                        
                        if href and self.is_valid_page(href):
                            normalized = self.normalize_url(href)
                            
                            if self.is_same_domain(normalized):
                                navigation_data[zone].append({
                                    'url': normalized,
                                    'text': text,
                                    'href': href
                                })
                    except:
                        continue
            except:
                continue
        
        # Extraire tous les autres liens de la page
        try:
            all_links = page.query_selector_all('a[href]')
            
            for link in all_links[:100]:  # Limiter
                try:
                    href = link.get_attribute('href')
                    text = link.inner_text().strip()
                    
                    if href and self.is_valid_page(href):
                        normalized = self.normalize_url(href)
                        
                        if self.is_same_domain(normalized):
                            # Vérifier si déjà dans une zone spécifique
                            already_added = any(
                                normalized in [item['url'] for item in zone_links]
                                for zone_links in navigation_data.values()
                            )
                            
                            if not already_added:
                                navigation_data['other'].append({
                                    'url': normalized,
                                    'text': text,
                                    'href': href
                                })
                except:
                    continue
        except:
            pass
        
        return navigation_data
    
    def detect_pagination(self, page: Page) -> List[str]:
        """Détecte les liens de pagination."""
        pagination_urls = []
        
        # Sélecteurs communs pour la pagination
        pagination_selectors = [
            '.pagination a',
            '.pager a',
            '[class*="page"] a',
            'a[rel="next"]',
            'a[rel="prev"]',
            'nav[aria-label*="pagination"] a',
            'nav[aria-label*="Pagination"] a'
        ]
        
        for selector in pagination_selectors:
            try:
                links = page.query_selector_all(selector)
                for link in links:
                    href = link.get_attribute('href')
                    if href:
                        normalized = self.normalize_url(href)
                        if self.is_same_domain(normalized):
                            pagination_urls.append(normalized)
            except:
                continue
        
        return list(set(pagination_urls))
    
    def crawl_page(self, page: Page, url: str) -> Dict:
        """Crawl une page et extrait toutes les informations."""
        print(f"[*] Crawling: {url}")
        
        response = None
        try:
            # Essai 1: Chargement standard (domcontentloaded)
            try:
                response = page.goto(url, wait_until='domcontentloaded', timeout=self.timeout)
            except Exception as e:
                print(f"    ⚠️ Timeout sur domcontentloaded, tentative en mode 'commit' (plus rapide)...")
                # Essai 2: Mode dégradé (commit) - on veut juste le HTML
                response = page.goto(url, wait_until='commit', timeout=self.timeout)
                # On attend un peu manuellement pour laisser une chance au contenu de s'afficher
                page.wait_for_timeout(2000)
            
            # Attendre un peu pour que le JavaScript s'exécute
            page.wait_for_timeout(1000)
            
            # Extraire les informations + preview du contenu
            page_data = {
                'url': url,
                'status': response.status if response else None,
                'title': page.title(),
                'path': urlparse(url).path,
                'navigation': self.extract_navigation_links(page),
                'pagination': self.detect_pagination(page),
                'preview': self.extract_page_preview(page)
            }
            
            return page_data
            
        except Exception as e:
            print(f"    └─ Erreur: {e}")
            return None
    
    def crawl(self) -> Dict:
        """
        Crawl le site en commençant par la page d'accueil.
        Découvre automatiquement la structure comme Web Scraper/Octoparse.
        """
        print(f"\n{'='*60}")
        print(f"SMART CRAWLER - Analyse de {self.base_url}")
        print(f"{'='*60}\n")
        
        all_navigation = {}
        urls_to_visit = [self.base_url]
        pages_data = []
        
        with sync_playwright() as p:
            # Lancer le navigateur en mode headless
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                viewport={'width': 1920, 'height': 1080}
            )
            page = context.new_page()
            
            while urls_to_visit and len(self.visited_urls) < self.max_pages:
                current_url = urls_to_visit.pop(0)
                
                # Skip si déjà visité
                if current_url in self.visited_urls:
                    continue
                
                # Marquer comme visité
                self.visited_urls.add(current_url)
                
                # Crawler la page
                page_data = self.crawl_page(page, current_url)
                
                if page_data:
                    pages_data.append(page_data)
                    
                    # Ajouter le chemin découvert
                    path = page_data['path']
                    if path and path != '/':
                        self.discovered_paths.add(path.rstrip('/'))
                    
                    # Collecter les liens de navigation
                    for zone, links in page_data['navigation'].items():
                        if zone not in all_navigation:
                            all_navigation[zone] = []
                        
                        for link_data in links:
                            link_url = link_data['url']
                            
                            # Ajouter à la navigation globale
                            if link_data not in all_navigation[zone]:
                                all_navigation[zone].append(link_data)
                            
                            # Ajouter aux URLs à visiter
                            if link_url not in self.visited_urls and link_url not in urls_to_visit:
                                urls_to_visit.append(link_url)
                    
                    # Ajouter les pages de pagination
                    for pag_url in page_data['pagination']:
                        if pag_url not in self.visited_urls and pag_url not in urls_to_visit:
                            urls_to_visit.append(pag_url)
                
                # Petit délai pour éviter de surcharger le serveur
                time.sleep(0.5)
            
            browser.close()
        
        # Organiser les résultats
        unique_paths = sorted(list(self.discovered_paths))
        
        # Identifier les pages principales (dans le menu/nav)
        main_pages = []
        for link_data in all_navigation.get('nav', []) + all_navigation.get('menu', []) + all_navigation.get('header', []):
            if link_data not in main_pages:
                main_pages.append(link_data)
        
        print(f"\n{'='*60}")
        print(f"RÉSULTATS DU CRAWL")
        print(f"{'='*60}")
        print(f"Pages visitées: {len(self.visited_urls)}")
        print(f"Chemins découverts: {len(unique_paths)}")
        print(f"Pages principales: {len(main_pages)}")
        
        return {
            'success': True,
            'base_url': self.base_url,
            'pages_crawled': len(self.visited_urls),
            'total_paths': len(unique_paths),
            'paths': unique_paths,
            'main_pages': main_pages[:20],  # Top 20 pages principales
            'navigation': {
                zone: links[:10] for zone, links in all_navigation.items() if links
            },
            'all_pages': [
                {
                    'url': pd['url'],
                    'title': pd['title'],
                    'path': pd['path'],
                    'preview': pd.get('preview', {})
                }
                for pd in pages_data
            ][:50]  # Top 50 pages
        }


def discover_paths_smart(url: str, max_pages: int = 30) -> Dict:
    """
    Découvre les chemins d'un site en utilisant un crawler intelligent avec Playwright.
    Similaire à Web Scraper, ParseHub, Octoparse.
    
    Args:
        url: URL du site à crawler
        max_pages: Nombre maximum de pages à visiter
    
    Returns:
        dict avec les chemins découverts et la structure du site
    """
    crawler = SmartCrawler(url, max_pages=max_pages)
    return crawler.crawl()


if __name__ == "__main__":
    # Test du module
    import sys
    
    test_url = sys.argv[1] if len(sys.argv) > 1 else "https://example.com"
    max_pages = int(sys.argv[2]) if len(sys.argv) > 2 else 20
    
    result = discover_paths_smart(test_url, max_pages=max_pages)
    
    print(f"\n{'='*60}")
    print(f"CHEMINS DÉCOUVERTS")
    print(f"{'='*60}")
    for path in result['paths'][:30]:
        print(f"  📄 {path}")
    
    if len(result['paths']) > 30:
        print(f"  ... et {len(result['paths']) - 30} autres")
    
    print(f"\n{'='*60}")
    print(f"PAGES PRINCIPALES")
    print(f"{'='*60}")
    for page in result['main_pages']:
        print(f"  🔗 {page['text']}: {page['url']}")
