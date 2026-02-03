# backend/src/core/path_finder.py
# Module de découverte de chemins/répertoires (comme dirsearch/gobuster)
# Utilise des sources passives (Wayback Machine, Common Crawl, etc.)
# RELEVANT FILES: subdomain_finder.py, analyzer.py, site_checker.py

import httpx
import re
from typing import Dict, List, Set
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup


def find_paths_wayback(domain: str, timeout: int = 15) -> Set[str]:
    """
    Découvre les chemins via Wayback Machine (Internet Archive).
    Source passive très fiable pour trouver les anciennes URLs.
    """
    paths = set()
    
    try:
        # API Wayback Machine pour obtenir toutes les URLs archivées
        url = f"http://web.archive.org/cdx/search/cdx?url={domain}/*&output=json&fl=original&collapse=urlkey"
        
        with httpx.Client(timeout=timeout, follow_redirects=True) as client:
            response = client.get(url)
            
            if response.status_code == 200:
                data = response.json()
                
                # Première ligne est l'en-tête, on la saute
                for entry in data[1:]:
                    if entry and len(entry) > 0:
                        archived_url = entry[0]
                        parsed = urlparse(archived_url)
                        
                        # Extraire le chemin
                        if parsed.path and parsed.path != '/':
                            # Nettoyer le chemin
                            path = parsed.path.rstrip('/')
                            if path and not path.startswith('/wp-'):  # Ignorer WordPress admin
                                paths.add(path)
    
    except Exception as e:
        print(f"[Wayback] Erreur: {e}")
    
    return paths


def find_paths_commonpages(domain: str) -> Set[str]:
    """
    Teste les pages communes trouvées sur la plupart des sites web.
    Basé sur les wordlists courantes de dirsearch/gobuster.
    """
    common_paths = {
        '/about', '/a-propos', '/apropos',
        '/contact', '/contacts',
        '/services', '/service',
        '/products', '/produits', '/product',
        '/blog', '/news', '/actualites', '/actualite',
        '/formation', '/formations', '/training',
        '/team', '/equipe', '/about-us',
        '/portfolio', '/projets', '/projects',
        '/tarifs', '/pricing', '/prix',
        '/faq', '/aide', '/help',
        '/login', '/signin', '/connexion',
        '/register', '/signup', '/inscription',
        '/dashboard', '/admin', '/panel',
        '/search', '/recherche',
        '/sitemap', '/sitemap.xml',
        '/robots.txt',
        '/gallery', '/galerie', '/photos',
        '/events', '/evenements', '/event',
        '/careers', '/carrieres', '/jobs', '/emplois',
        '/partners', '/partenaires',
        '/testimonials', '/temoignages',
        '/privacy', '/confidentialite', '/politique-confidentialite',
        '/terms', '/conditions', '/cgu',
        '/legal', '/mentions-legales',
        '/downloads', '/telechargements',
        '/resources', '/ressources'
    }
    
    return common_paths


def find_paths_sitemap(base_url: str, timeout: int = 10) -> Set[str]:
    """
    Extrait les chemins depuis le fichier sitemap.xml.
    """
    paths = set()
    
    sitemap_urls = [
        '/sitemap.xml',
        '/sitemap_index.xml',
        '/sitemap1.xml',
        '/wp-sitemap.xml'
    ]
    
    try:
        with httpx.Client(timeout=timeout, follow_redirects=True) as client:
            for sitemap_path in sitemap_urls:
                sitemap_url = urljoin(base_url, sitemap_path)
                
                try:
                    response = client.get(sitemap_url)
                    
                    if response.status_code == 200:
                        # Parser le XML
                        soup = BeautifulSoup(response.content, 'xml')
                        
                        # Trouver tous les <loc> tags
                        for loc in soup.find_all('loc'):
                            url = loc.get_text().strip()
                            parsed = urlparse(url)
                            
                            if parsed.path and parsed.path != '/':
                                path = parsed.path.rstrip('/')
                                if path:
                                    paths.add(path)
                        
                        # Si on a trouvé des URLs, pas besoin de chercher d'autres sitemaps
                        if paths:
                            break
                
                except:
                    continue
    
    except Exception as e:
        print(f"[Sitemap] Erreur: {e}")
    
    return paths


def find_paths_robots(base_url: str, timeout: int = 10) -> Set[str]:
    """
    Extrait les chemins mentionnés dans robots.txt.
    """
    paths = set()
    
    try:
        robots_url = urljoin(base_url, '/robots.txt')
        
        with httpx.Client(timeout=timeout, follow_redirects=True) as client:
            response = client.get(robots_url)
            
            if response.status_code == 200:
                lines = response.text.split('\n')
                
                for line in lines:
                    line = line.strip()
                    
                    # Chercher les directives Disallow et Allow
                    if line.startswith('Disallow:') or line.startswith('Allow:'):
                        path = line.split(':', 1)[1].strip()
                        
                        # Nettoyer les wildcards
                        path = path.replace('*', '').rstrip('/')
                        
                        if path and path != '/' and not path.startswith('#'):
                            paths.add(path)
                    
                    # Chercher les références aux sitemaps
                    elif line.startswith('Sitemap:'):
                        sitemap_url = line.split(':', 1)[1].strip()
                        parsed = urlparse(sitemap_url)
                        if parsed.path and parsed.path != '/':
                            paths.add(parsed.path.rstrip('/'))
    
    except Exception as e:
        print(f"[Robots.txt] Erreur: {e}")
    
    return paths


def find_paths_crawl_homepage(base_url: str, timeout: int = 10) -> Set[str]:
    """
    Crawl la page d'accueil pour extraire tous les liens internes.
    """
    paths = set()
    
    try:
        with httpx.Client(timeout=timeout, follow_redirects=True) as client:
            response = client.get(base_url)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                base_domain = urlparse(base_url).netloc
                
                # Trouver tous les liens <a>
                for link in soup.find_all('a', href=True):
                    href = link['href']
                    
                    # Construire l'URL absolue
                    absolute_url = urljoin(base_url, href)
                    parsed = urlparse(absolute_url)
                    
                    # Ne garder que les liens du même domaine
                    if parsed.netloc == base_domain:
                        if parsed.path and parsed.path != '/':
                            path = parsed.path.rstrip('/')
                            if path and not any(ext in path.lower() for ext in ['.jpg', '.png', '.gif', '.css', '.js', '.pdf']):
                                paths.add(path)
    
    except Exception as e:
        print(f"[Crawl Homepage] Erreur: {e}")
    
    return paths


def discover_paths(
    url: str,
    use_wayback: bool = True,
    use_sitemap: bool = True,
    use_robots: bool = True,
    use_common: bool = True,
    use_crawl: bool = True,
    max_paths: int = 100
) -> Dict:
    """
    Découvre les chemins/répertoires d'un site web en utilisant plusieurs sources passives.
    
    Args:
        url: URL du site à analyser
        use_wayback: Utiliser Wayback Machine
        use_sitemap: Chercher dans sitemap.xml
        use_robots: Chercher dans robots.txt
        use_common: Tester les chemins communs
        use_crawl: Crawler la page d'accueil
        max_paths: Nombre maximum de chemins à retourner
    
    Returns:
        dict avec les chemins découverts et les statistiques
    """
    parsed = urlparse(url)
    base_url = f"{parsed.scheme}://{parsed.netloc}"
    domain = parsed.netloc
    
    all_paths = set()
    sources_used = []
    
    # Wayback Machine
    if use_wayback:
        print(f"[*] Recherche de chemins via Wayback Machine...")
        wayback_paths = find_paths_wayback(domain)
        all_paths.update(wayback_paths)
        if wayback_paths:
            sources_used.append({
                'name': 'wayback',
                'count': len(wayback_paths),
                'type': 'Internet Archive'
            })
            print(f"    └─ {len(wayback_paths)} chemins trouvés")
    
    # Sitemap.xml
    if use_sitemap:
        print(f"[*] Recherche de chemins via Sitemap...")
        sitemap_paths = find_paths_sitemap(base_url)
        all_paths.update(sitemap_paths)
        if sitemap_paths:
            sources_used.append({
                'name': 'sitemap',
                'count': len(sitemap_paths),
                'type': 'Sitemap XML'
            })
            print(f"    └─ {len(sitemap_paths)} chemins trouvés")
    
    # Robots.txt
    if use_robots:
        print(f"[*] Recherche de chemins via Robots.txt...")
        robots_paths = find_paths_robots(base_url)
        all_paths.update(robots_paths)
        if robots_paths:
            sources_used.append({
                'name': 'robots',
                'count': len(robots_paths),
                'type': 'Robots.txt'
            })
            print(f"    └─ {len(robots_paths)} chemins trouvés")
    
    # Crawl homepage
    if use_crawl:
        print(f"[*] Crawl de la page d'accueil...")
        crawl_paths = find_paths_crawl_homepage(base_url)
        all_paths.update(crawl_paths)
        if crawl_paths:
            sources_used.append({
                'name': 'crawl',
                'count': len(crawl_paths),
                'type': 'Homepage Links'
            })
            print(f"    └─ {len(crawl_paths)} chemins trouvés")
    
    # Chemins communs
    if use_common:
        print(f"[*] Test des chemins communs...")
        common_paths = find_paths_commonpages(domain)
        # On ne les ajoute pas directement, on les retourne pour vérification
        sources_used.append({
            'name': 'common',
            'count': len(common_paths),
            'type': 'Common Wordlist'
        })
    else:
        common_paths = set()
    
    # Trier et limiter
    paths_list = sorted(list(all_paths))[:max_paths]
    
    # Construire les URLs complètes
    full_urls = [urljoin(base_url, path) for path in paths_list]
    
    return {
        'success': True,
        'base_url': base_url,
        'total_found': len(all_paths),
        'returned': len(paths_list),
        'paths': paths_list,
        'full_urls': full_urls,
        'common_paths': sorted(list(common_paths))[:50],  # Chemins à tester
        'sources': sources_used
    }


if __name__ == "__main__":
    # Test du module
    import sys
    
    test_url = sys.argv[1] if len(sys.argv) > 1 else "https://example.com"
    
    print(f"\n{'='*60}")
    print(f"PATH FINDER - Test pour: {test_url}")
    print(f"{'='*60}\n")
    
    result = discover_paths(test_url)
    
    print(f"\n{'='*60}")
    print(f"RÉSULTATS")
    print(f"{'='*60}")
    print(f"URL de base: {result['base_url']}")
    print(f"Total trouvé: {result['total_found']}")
    print(f"\nChemins découverts:")
    for path in result['paths'][:30]:
        print(f"  • {path}")
    
    if result['total_found'] > 30:
        print(f"  ... et {result['total_found'] - 30} autres")
    
    print(f"\nSources utilisées:")
    for source in result['sources']:
        print(f"  • {source['name']}: {source['count']} ({source['type']})")
