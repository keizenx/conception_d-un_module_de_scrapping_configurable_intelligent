# backend/src/core/page_detector.py
# Détection intelligente de pages avec screenshot
# Utilise Playwright pour rapidité + rendu JS

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from typing import Dict, List, Set
import base64
import time


class PageDetector:
    """
    Détecte les pages d'un site + capture screenshots.
    Plus rapide que Selenium, supporte JavaScript.
    """
    
    def __init__(self, base_url: str, timeout: int = 30000):
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.domain = urlparse(base_url).netloc
        
    def analyze_with_screenshot(self, max_depth: int = 2) -> Dict:
        """
        Analyse le site + capture screenshot de la homepage.
        
        Returns:
            {
                'screenshot': str (base64),
                'pages_found': List[str],
                'total_pages': int,
                'navigation_links': List[Dict],
                'stats': {...}
            }
        """
        result = {
            'screenshot': None,
            'pages_found': [],
            'navigation_links': [],
            'total_pages': 0,
            'stats': {}
        }
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            )
            page = context.new_page()
            
            try:
                # 1. Charger homepage + screenshot
                try:
                    page.goto(self.base_url, timeout=self.timeout, wait_until='networkidle')
                except PlaywrightTimeout:
                    # Fallback si networkidle est trop long
                    page.goto(self.base_url, timeout=self.timeout, wait_until='domcontentloaded')
                
                # Screenshot full page (peut échouer sur certains sites très longs, donc on fallback sur viewport si besoin)
                try:
                    screenshot_bytes = page.screenshot(full_page=False, type='png') # Viewport seulement pour la rapidité
                except:
                    screenshot_bytes = None

                if screenshot_bytes:
                    result['screenshot'] = base64.b64encode(screenshot_bytes).decode()
                
                # 2. Extraire les liens (après rendu JS)
                page.wait_for_timeout(2000)  # Attendre animations/lazy loading
                
                html = page.content()
                soup = BeautifulSoup(html, 'html.parser')
                
                # 3. Analyser navigation principale
                nav_links = self._extract_navigation(soup)
                result['navigation_links'] = nav_links
                
                # 4. Crawler léger (max_depth pages)
                visited = set()
                to_visit = {self.base_url}
                all_pages = set()
                
                # Ajouter les liens de navigation à visiter
                for nav in nav_links:
                    to_visit.add(nav['url'])
                
                depth = 0
                while to_visit and depth < max_depth:
                    current_batch = list(to_visit)[:10]  # Limiter à 10 pages par niveau
                    to_visit -= set(current_batch)
                    
                    for url in current_batch:
                        if url in visited:
                            continue
                            
                        visited.add(url)
                        all_pages.add(url) # Ajouter la page visitée
                        
                        # Ne pas crawler profondément pour l'instant, juste la homepage et ses liens directs
                        # Pour l'estimation rapide, on se contente des liens trouvés sur la home
                        if depth > 0: 
                            continue

                        # Si on est sur la home (depth 0), on extrait les liens
                        if url == self.base_url:
                            new_links = self._extract_internal_links(soup, url)
                            all_pages.update(new_links)
                            # On n'ajoute pas forcément tout à to_visit pour rester rapide
                    
                    depth += 1
                
                result['pages_found'] = sorted(list(all_pages))
                result['total_pages'] = len(all_pages)
                
                # 5. Stats
                result['stats'] = {
                    'images_count': len(soup.find_all('img')),
                    'forms_count': len(soup.find_all('form')),
                    'external_links': len(soup.find_all('a', href=lambda h: h and not self._is_internal(h))),
                    'has_pagination': self._detect_pagination(soup)
                }
                
            except Exception as e:
                print(f"Erreur PageDetector: {e}")
                result['error'] = str(e)
            finally:
                browser.close()
        
        return result
    
    def _extract_navigation(self, soup: BeautifulSoup) -> List[Dict]:
        """Extrait les liens de navigation principale."""
        nav_links = []
        
        # Chercher <nav>, <header>, ou class="nav"/"menu"
        nav_elements = soup.find_all(['nav', 'header']) + \
                      soup.find_all(class_=lambda c: c and any(x in str(c).lower() for x in ['nav', 'menu']))
        
        for nav in nav_elements[:3]:  # Max 3 navs
            for link in nav.find_all('a', href=True):
                href = link['href']
                if self._is_internal(href):
                    full_url = urljoin(self.base_url, href)
                    # Éviter doublons
                    if not any(nl['url'] == full_url for nl in nav_links):
                        nav_links.append({
                            'text': link.get_text(strip=True)[:30],
                            'url': full_url
                        })
        
        return nav_links[:15]  # Max 15 liens nav
    
    def _extract_internal_links(self, soup: BeautifulSoup, base_url: str) -> Set[str]:
        """Extrait tous les liens internes."""
        links = set()
        
        for link in soup.find_all('a', href=True):
            href = link['href']
            if self._is_internal(href):
                full_url = urljoin(base_url, href)
                # Nettoyer (enlever #, ?)
                clean_url = full_url.split('#')[0].split('?')[0]
                if clean_url and clean_url != self.base_url.rstrip('/') and clean_url != self.base_url.rstrip('/') + '/':
                    links.add(clean_url)
        
        return links
    
    def _is_internal(self, href: str) -> bool:
        """Vérifie si le lien est interne."""
        if not href or href.startswith(('#', 'javascript:', 'mailto:', 'tel:')):
            return False
        
        try:
            parsed = urlparse(urljoin(self.base_url, href))
            return parsed.netloc == self.domain or parsed.netloc == ''
        except:
            return False
    
    def _detect_pagination(self, soup: BeautifulSoup) -> bool:
        """Détecte la pagination."""
        pagination_patterns = ['pagination', 'pager', 'page-nav', 'next', 'prev']
        return bool(soup.find_all(class_=lambda c: c and any(p in str(c).lower() for p in pagination_patterns)))


# Test
if __name__ == "__main__":
    import sys
    url = sys.argv[1] if len(sys.argv) > 1 else "https://example.com"
    detector = PageDetector(url)
    result = detector.analyze_with_screenshot(max_depth=1)
    
    print(f"✅ Screenshot: {'Oui' if result['screenshot'] else 'Non'}")
    print(f"📄 Pages trouvées: {result['total_pages']}")
    print(f"🧭 Liens navigation: {len(result['navigation_links'])}")
    print(f"\n📊 Stats:")
    for k, v in result['stats'].items():
        print(f"  • {k}: {v}")
