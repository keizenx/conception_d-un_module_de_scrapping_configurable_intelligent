# backend/src/core/subdomain_finder.py
# Module de découverte de sous-domaines similaire à subfinder
# Utilise des sources passives (Certificate Transparency, DNS, etc.)
# RELEVANT FILES: analyzer.py, fetcher.py

import re
import json
from typing import List, Set
from urllib.parse import urlparse
import httpx


def extract_domain(url: str) -> str:
    """Extrait le domaine principal d'une URL."""
    parsed = urlparse(url if url.startswith('http') else f'https://{url}')
    domain = parsed.netloc or parsed.path
    # Enlever www. si présent
    if domain.startswith('www.'):
        domain = domain[4:]
    return domain


def find_subdomains_crtsh(domain: str, timeout: int = 10) -> Set[str]:
    """
    Découvre les sous-domaines via Certificate Transparency (crt.sh).
    Source gratuite et fiable sans API key requise.
    """
    subdomains = set()
    
    try:
        url = f"https://crt.sh/?q=%.{domain}&output=json"
        
        with httpx.Client(timeout=timeout, follow_redirects=True) as client:
            response = client.get(url)
            
            if response.status_code == 200:
                data = response.json()
                
                for entry in data:
                    name_value = entry.get('name_value', '')
                    # Peut contenir plusieurs noms séparés par des retours à la ligne
                    names = name_value.split('\n')
                    
                    for name in names:
                        name = name.strip().lower()
                        # Enlever les wildcards
                        name = name.replace('*.', '')
                        
                        # Vérifier que c'est bien un sous-domaine du domaine cible
                        if name.endswith(domain) and name != domain:
                            # Valider que c'est un nom de domaine valide
                            if re.match(r'^[a-z0-9.-]+$', name):
                                subdomains.add(name)
                
    except Exception as e:
        print(f"Erreur crt.sh pour {domain}: {e}")
    
    return subdomains


def find_subdomains_hackertarget(domain: str, timeout: int = 10) -> Set[str]:
    """
    Découvre les sous-domaines via HackerTarget API (gratuit, limité).
    """
    subdomains = set()
    
    try:
        url = f"https://api.hackertarget.com/hostsearch/?q={domain}"
        
        with httpx.Client(timeout=timeout) as client:
            response = client.get(url)
            
            if response.status_code == 200:
                lines = response.text.strip().split('\n')
                
                for line in lines:
                    if ',' in line:
                        subdomain = line.split(',')[0].strip().lower()
                        if subdomain.endswith(domain) and re.match(r'^[a-z0-9.-]+$', subdomain):
                            subdomains.add(subdomain)
                
    except Exception as e:
        print(f"Erreur HackerTarget pour {domain}: {e}")
    
    return subdomains


def find_subdomains_alienvault(domain: str, timeout: int = 10) -> Set[str]:
    """
    Découvre les sous-domaines via AlienVault OTX (Open Threat Exchange).
    Source passive gratuite similaire à subfinder.
    """
    subdomains = set()
    
    try:
        url = f"https://otx.alienvault.com/api/v1/indicators/domain/{domain}/passive_dns"
        
        with httpx.Client(timeout=timeout, follow_redirects=True) as client:
            response = client.get(url)
            
            if response.status_code == 200:
                data = response.json()
                
                for entry in data.get('passive_dns', []):
                    hostname = entry.get('hostname', '').strip().lower()
                    if hostname and hostname.endswith(domain):
                        subdomains.add(hostname)
    
    except Exception as e:
        print(f"[AlienVault] Erreur: {e}")
    
    return subdomains


def find_subdomains_threatcrowd(domain: str, timeout: int = 10) -> Set[str]:
    """
    Découvre les sous-domaines via ThreatCrowd API.
    Source passive gratuite.
    """
    subdomains = set()
    
    try:
        url = f"https://www.threatcrowd.org/searchApi/v2/domain/report/?domain={domain}"
        
        with httpx.Client(timeout=timeout, follow_redirects=True) as client:
            response = client.get(url)
            
            if response.status_code == 200:
                data = response.json()
                
                for subdomain in data.get('subdomains', []):
                    subdomain = subdomain.strip().lower()
                    if subdomain and subdomain.endswith(domain):
                        subdomains.add(subdomain)
    
    except Exception as e:
        print(f"[ThreatCrowd] Erreur: {e}")
    
    return subdomains


def find_subdomains_urlscan(domain: str, timeout: int = 10) -> Set[str]:
    """
    Découvre les sous-domaines via URLScan.io API.
    Source passive gratuite.
    """
    subdomains = set()
    
    try:
        url = f"https://urlscan.io/api/v1/search/?q=domain:{domain}"
        
        with httpx.Client(timeout=timeout, follow_redirects=True) as client:
            response = client.get(url)
            
            if response.status_code == 200:
                data = response.json()
                
                for result in data.get('results', []):
                    page_domain = result.get('page', {}).get('domain', '').strip().lower()
                    if page_domain and page_domain.endswith(domain):
                        subdomains.add(page_domain)
                    
                    # Aussi extraire du task.domain
                    task_domain = result.get('task', {}).get('domain', '').strip().lower()
                    if task_domain and task_domain.endswith(domain):
                        subdomains.add(task_domain)
    
    except Exception as e:
        print(f"[URLScan] Erreur: {e}")
    
    return subdomains


def find_subdomains_dnsrepo(domain: str, timeout: int = 10) -> Set[str]:
    """
    Découvre les sous-domaines via DNSRepo (gardé pour compatibilité).
    """
    subdomains = set()
    
    try:
        url = f"https://dnsrepo.noc.org/?domain={domain}"
        
        with httpx.Client(timeout=timeout, follow_redirects=True) as client:
            response = client.get(url, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            
            if response.status_code == 200:
                # Parser le HTML pour extraire les sous-domaines
                # Simple regex pour trouver les patterns de sous-domaines
                pattern = r'([a-z0-9.-]+\.' + re.escape(domain) + r')'
                matches = re.findall(pattern, response.text.lower())
                
                for match in matches:
                    if match != domain and re.match(r'^[a-z0-9.-]+$', match):
                        subdomains.add(match)
                
    except Exception as e:
        print(f"Erreur DNSRepo pour {domain}: {e}")
    
    return subdomains


def find_subdomains_common(domain: str) -> Set[str]:
    """
    Génère une liste de sous-domaines communs à tester.
    """
    common_prefixes = [
        'www', 'mail', 'ftp', 'localhost', 'webmail', 'smtp', 'pop', 'ns1', 'ns2',
        'webdisk', 'ns', 'test', 'blog', 'pop3', 'dev', 'www2', 'admin', 'forum',
        'news', 'vpn', 'ns3', 'm', 'secure', 'api', 'www3', 'mail2', 'new',
        'mysql', 'old', 'lists', 'support', 'mobile', 'mx', 'static', 'docs', 'beta',
        'shop', 'sql', 'secure', 'demo', 'cp', 'calendar', 'wiki', 'web', 'media',
        'email', 'images', 'img', 'www1', 'intranet', 'portal', 'video', 'sip',
        'dns2', 'api2', 'cdn', 'ns4', 'ww1', 'host', 'ww42', 'mx1', 'dns1',
        'dns', 'remote', 'exchange', 'router', 'help', 'status', 'server', 'ns5',
        'mx2', 'mx3', 'admin2', 'store', 'app', 'staging', 'backup'
    ]
    
    return {f"{prefix}.{domain}" for prefix in common_prefixes}


def discover_subdomains(
    url: str,
    use_crtsh: bool = True,
    use_hackertarget: bool = True,
    use_dnsrepo: bool = False,
    use_common: bool = True,
    max_subdomains: int = 100
) -> dict:
    """
    Découvre les sous-domaines d'un domaine en utilisant plusieurs sources passives.
    
    Args:
        url: URL ou domaine à analyser
        use_crtsh: Utiliser Certificate Transparency (recommandé)
        use_hackertarget: Utiliser HackerTarget API
        use_dnsrepo: Utiliser DNSRepo (peut être lent)
        use_common: Tester les sous-domaines communs
        max_subdomains: Nombre maximum de sous-domaines à retourner
    
    Returns:
        dict avec les sous-domaines découverts et les statistiques
    """
    domain = extract_domain(url)
    all_subdomains = set()
    sources_used = []
    
    # Certificate Transparency (crt.sh) - Source la plus fiable
    if use_crtsh:
        print(f"[*] Recherche via Certificate Transparency (crt.sh)...")
        crtsh_results = find_subdomains_crtsh(domain)
        all_subdomains.update(crtsh_results)
        sources_used.append({
            'name': 'crt.sh',
            'count': len(crtsh_results),
            'type': 'Certificate Transparency'
        })
        print(f"    └─ {len(crtsh_results)} sous-domaines trouvés")
    
    # HackerTarget API
    if use_hackertarget:
        print(f"[*] Recherche via HackerTarget API...")
        ht_results = find_subdomains_hackertarget(domain)
        all_subdomains.update(ht_results)
        sources_used.append({
            'name': 'hackertarget',
            'count': len(ht_results),
            'type': 'DNS Records'
        })
        print(f"    └─ {len(ht_results)} sous-domaines trouvés")
    
    # AlienVault OTX
    print(f"[*] Recherche via AlienVault OTX...")
    av_results = find_subdomains_alienvault(domain)
    all_subdomains.update(av_results)
    if av_results:
        sources_used.append({
            'name': 'alienvault',
            'count': len(av_results),
            'type': 'Threat Intelligence'
        })
        print(f"    └─ {len(av_results)} sous-domaines trouvés")
    
    # ThreatCrowd
    print(f"[*] Recherche via ThreatCrowd...")
    tc_results = find_subdomains_threatcrowd(domain)
    all_subdomains.update(tc_results)
    if tc_results:
        sources_used.append({
            'name': 'threatcrowd',
            'count': len(tc_results),
            'type': 'Threat Intelligence'
        })
        print(f"    └─ {len(tc_results)} sous-domaines trouvés")
    
    # URLScan.io
    print(f"[*] Recherche via URLScan.io...")
    us_results = find_subdomains_urlscan(domain)
    all_subdomains.update(us_results)
    if us_results:
        sources_used.append({
            'name': 'urlscan',
            'count': len(us_results),
            'type': 'Web Scanner'
        })
        print(f"    └─ {len(us_results)} sous-domaines trouvés")
        print(f"    └─ {len(ht_results)} sous-domaines trouvés")
    
    # DNSRepo (optionnel, peut être lent)
    if use_dnsrepo:
        print(f"[*] Recherche via DNSRepo...")
        dns_results = find_subdomains_dnsrepo(domain)
        all_subdomains.update(dns_results)
        sources_used.append({
            'name': 'dnsrepo',
            'count': len(dns_results),
            'type': 'DNS Database'
        })
        print(f"    └─ {len(dns_results)} sous-domaines trouvés")
    
    # Sous-domaines communs
    if use_common:
        print(f"[*] Génération de sous-domaines communs...")
        common_results = find_subdomains_common(domain)
        # Ne pas les ajouter tous, juste les marquer comme "à vérifier"
        sources_used.append({
            'name': 'common',
            'count': len(common_results),
            'type': 'Common Subdomains (unverified)'
        })
    
    # Ajouter le domaine principal
    all_subdomains.add(domain)
    all_subdomains.add(f"www.{domain}")
    
    # Trier et limiter
    subdomains_list = sorted(list(all_subdomains))[:max_subdomains]
    
    return {
        'success': True,
        'domain': domain,
        'total_found': len(all_subdomains),
        'returned': len(subdomains_list),
        'subdomains': subdomains_list,
        'sources': sources_used,
        'metadata': {
            'note': 'Sous-domaines découverts via sources passives',
            'verification': 'Les sous-domaines communs ne sont pas vérifiés (DNS check requis)'
        }
    }


if __name__ == "__main__":
    # Test du module
    import sys
    
    test_domain = sys.argv[1] if len(sys.argv) > 1 else "example.com"
    
    print(f"\n{'='*60}")
    print(f"SUBDOMAIN FINDER - Test pour: {test_domain}")
    print(f"{'='*60}\n")
    
    result = discover_subdomains(test_domain)
    
    print(f"\n{'='*60}")
    print(f"RÉSULTATS")
    print(f"{'='*60}")
    print(f"Domaine: {result['domain']}")
    print(f"Total trouvé: {result['total_found']}")
    print(f"\nSous-domaines découverts:")
    for sd in result['subdomains'][:20]:
        print(f"  • {sd}")
    
    if result['total_found'] > 20:
        print(f"  ... et {result['total_found'] - 20} autres")
    
    print(f"\nSources utilisées:")
    for source in result['sources']:
        print(f"  • {source['name']}: {source['count']} ({source['type']})")
