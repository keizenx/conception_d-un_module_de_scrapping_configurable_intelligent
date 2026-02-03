# backend/src/core/site_checker.py
# Module de vérification de sites web et détection de protections anti-scraping
# Inspiré de httpx de ProjectDiscovery
# RELEVANT FILES: subdomain_finder.py, analyzer.py, fetcher.py

import httpx
import re
from typing import Dict, List, Optional, Tuple
from urllib.parse import urlparse
import time


class SiteChecker:
    """
    Vérifie l'accessibilité des sites et détecte les protections anti-scraping.
    """
    
    # Signatures des protections anti-bot
    PROTECTION_SIGNATURES = {
        'cloudflare': [
            'cloudflare',
            'cf-ray',
            '__cf_bm',
            'cf-cache-status',
            'cloudflare-nginx',
            'Just a moment...',
            'Checking your browser',
        ],
        'akamai': [
            'akamai',
            'akamaighost',
            'akamai-ghost',
            'x-akamai',
        ],
        'imperva': [
            'imperva',
            'incapsula',
            '_incap_ses',
            'visid_incap',
        ],
        'cloudfront': [
            'cloudfront',
            'x-amz-cf-id',
            'x-amz-cf-pop',
        ],
        'fastly': [
            'fastly',
            'x-fastly',
            'x-served-by',
        ],
        'sucuri': [
            'sucuri',
            'x-sucuri-id',
            'x-sucuri-cache',
        ],
        'ddos-guard': [
            'ddos-guard',
            'x-ddos-protection',
        ],
        'vercel': [
            'vercel',
            'x-vercel-id',
            'x-vercel-cache',
        ],
        'recaptcha': [
            'recaptcha',
            'grecaptcha',
            'g-recaptcha',
        ],
        'datadome': [
            'datadome',
            'x-datadome',
        ]
    }
    
    def __init__(self, timeout: int = 10, follow_redirects: bool = True):
        self.timeout = timeout
        self.follow_redirects = follow_redirects
        self.user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    
    def normalize_url(self, url: str) -> str:
        """Normalise l'URL pour les tests."""
        if not url.startswith(('http://', 'https://')):
            url = f'https://{url}'
        return url
    
    def get_status_info(self, status_code: int) -> Dict[str, str]:
        """Retourne les informations sur le code de statut HTTP."""
        if status_code == 200:
            return {
                'level': 'success',
                'emoji': '✅',
                'message': 'OK - Site accessible',
                'scrapable': True
            }
        elif status_code in [301, 302, 303, 307, 308]:
            return {
                'level': 'warning',
                'emoji': '⚠️',
                'message': 'Redirection détectée',
                'scrapable': True
            }
        elif status_code == 403:
            return {
                'level': 'warning',
                'emoji': '⚠️',
                'message': 'Accès refusé (403) - Peut être contournable',
                'scrapable': True  # On essaie quand même
            }
        elif status_code == 429:
            return {
                'level': 'danger',
                'emoji': '🚨',
                'message': 'Rate limit atteint',
                'scrapable': False
            }
        elif status_code in [401, 407]:
            return {
                'level': 'warning',
                'emoji': '🔐',
                'message': 'Authentication requise',
                'scrapable': True  # Certaines pages peuvent être accessibles
            }
        elif 500 <= status_code < 600:
            return {
                'level': 'warning',
                'emoji': '⚠️',
                'message': 'Erreur serveur temporaire',
                'scrapable': True  # L'erreur peut être temporaire
            }
        elif status_code == 404:
            return {
                'level': 'error',
                'emoji': '❓',
                'message': 'Page non trouvée',
                'scrapable': False
            }
        else:
            return {
                'level': 'info',
                'emoji': 'ℹ️',
                'message': f'Code inhabituel: {status_code}',
                'scrapable': False
            }
    
    def detect_protection(self, headers: dict, content: str) -> List[str]:
        """Détecte les protections anti-scraping présentes."""
        detected = []
        
        # Convertir headers et content en lowercase pour la recherche
        headers_str = str(headers).lower()
        content_lower = content.lower()
        
        for protection, signatures in self.PROTECTION_SIGNATURES.items():
            for signature in signatures:
                if signature.lower() in headers_str or signature.lower() in content_lower[:5000]:
                    if protection not in detected:
                        detected.append(protection)
                    break
        
        return detected
    
    def extract_title(self, html: str) -> Optional[str]:
        """Extrait le titre de la page HTML."""
        match = re.search(r'<title[^>]*>(.*?)</title>', html, re.IGNORECASE | re.DOTALL)
        if match:
            title = match.group(1).strip()
            # Nettoyer le titre
            title = re.sub(r'\s+', ' ', title)
            return title[:200]  # Limiter à 200 caractères
        return None
    
    def extract_tech_stack(self, headers: dict, content: str) -> List[str]:
        """Détecte les technologies utilisées."""
        tech = []
        
        # Headers
        headers_str = str(headers).lower()
        
        # Serveurs web
        server = headers.get('server', '').lower()
        if 'nginx' in server:
            tech.append('nginx')
        if 'apache' in server:
            tech.append('Apache')
        if 'iis' in server or 'microsoft' in server:
            tech.append('IIS')
        if 'litespeed' in server:
            tech.append('LiteSpeed')
        if 'caddy' in server:
            tech.append('Caddy')
        if 'tomcat' in server:
            tech.append('Tomcat')
        if 'gunicorn' in server:
            tech.append('Gunicorn')
        if 'uwsgi' in server:
            tech.append('uWSGI')
        if 'passenger' in server or 'phusion' in server:
            tech.append('Passenger')
        
        # Frameworks backend via headers
        if 'x-powered-by' in headers:
            powered = headers['x-powered-by'].lower()
            if 'php' in powered:
                tech.append('PHP')
            if 'asp.net' in powered:
                tech.append('ASP.NET')
            if 'express' in powered:
                tech.append('Express.js')
            if 'laravel' in powered:
                tech.append('Laravel')
            if 'django' in powered:
                tech.append('Django')
            if 'flask' in powered:
                tech.append('Flask')
            if 'rails' in powered or 'ruby' in powered:
                tech.append('Ruby on Rails')
        
        # Headers spécifiques
        if 'x-aspnet-version' in headers_str:
            tech.append('ASP.NET')
        if 'x-drupal-cache' in headers_str or 'x-generator' in headers_str:
            generator = headers.get('x-generator', '').lower()
            if 'drupal' in generator:
                tech.append('Drupal')
        
        # CMS & Frameworks depuis le contenu
        content_lower = content.lower()[:15000]  # Premiers 15KB
        
        # CMS populaires
        if 'wp-content' in content_lower or 'wordpress' in content_lower or 'wp-includes' in content_lower:
            tech.append('WordPress')
        if 'joomla' in content_lower or 'joomla!' in content_lower:
            tech.append('Joomla')
        if 'drupal' in content_lower:
            tech.append('Drupal')
        if 'shopify' in content_lower or 'cdn.shopify.com' in content_lower:
            tech.append('Shopify')
        if 'woocommerce' in content_lower:
            tech.append('WooCommerce')
        if 'magento' in content_lower or 'mage/' in content_lower:
            tech.append('Magento')
        if 'prestashop' in content_lower:
            tech.append('PrestaShop')
        if 'squarespace' in content_lower or 'squarespace.com' in content_lower:
            tech.append('Squarespace')
        if 'wix.com' in content_lower or 'wixstatic' in content_lower:
            tech.append('Wix')
        if 'webflow' in content_lower or 'webflow.com' in content_lower:
            tech.append('Webflow')
        if 'ghost' in content_lower and 'ghost-' in content_lower:
            tech.append('Ghost')
        if 'bigcommerce' in content_lower:
            tech.append('BigCommerce')
        
        # Frameworks frontend
        if 'react' in content_lower or '__react' in content_lower or 'reactjs' in content_lower:
            tech.append('React')
        if '_next' in content_lower or 'next.js' in content_lower or '__next' in content_lower:
            tech.append('Next.js')
        if 'vue' in content_lower and ('__vue' in content_lower or 'vue.js' in content_lower):
            tech.append('Vue.js')
        if '__nuxt' in content_lower or 'nuxt.js' in content_lower:
            tech.append('Nuxt.js')
        if 'angular' in content_lower or 'ng-' in content_lower or 'ng-app' in content_lower:
            tech.append('Angular')
        if 'svelte' in content_lower or '_svelte' in content_lower:
            tech.append('Svelte')
        if 'sveltekit' in content_lower:
            tech.append('SvelteKit')
        if 'solid' in content_lower and 'solidjs' in content_lower:
            tech.append('Solid.js')
        if 'ember' in content_lower and 'ember.js' in content_lower:
            tech.append('Ember.js')
        if 'backbone' in content_lower and 'backbone.js' in content_lower:
            tech.append('Backbone.js')
        if 'alpine' in content_lower and 'alpinejs' in content_lower:
            tech.append('Alpine.js')
        if 'htmx' in content_lower:
            tech.append('HTMX')
        
        # Frameworks backend (via métadonnées dans HTML)
        if 'django' in content_lower and ('csrfmiddlewaretoken' in content_lower or 'django-' in content_lower):
            tech.append('Django')
        if 'laravel' in content_lower or 'laravel_session' in content_lower:
            tech.append('Laravel')
        if 'symfony' in content_lower:
            tech.append('Symfony')
        if 'flask' in content_lower and 'flask-' in content_lower:
            tech.append('Flask')
        if 'fastapi' in content_lower:
            tech.append('FastAPI')
        if 'spring' in content_lower and ('spring-boot' in content_lower or 'springboot' in content_lower):
            tech.append('Spring Boot')
        if 'nestjs' in content_lower or '@nestjs' in content_lower:
            tech.append('NestJS')
        if 'express' in content_lower and 'express.js' in content_lower:
            tech.append('Express.js')
        
        # UI Frameworks & Libraries
        if 'bootstrap' in content_lower or 'bootstrap.min' in content_lower:
            tech.append('Bootstrap')
        if 'tailwind' in content_lower or 'tailwindcss' in content_lower:
            tech.append('Tailwind CSS')
        if 'material-ui' in content_lower or '@mui' in content_lower or 'mui.com' in content_lower:
            tech.append('Material UI')
        if 'ant-design' in content_lower or 'antd' in content_lower:
            tech.append('Ant Design')
        if 'chakra-ui' in content_lower or 'chakra' in content_lower and 'ui' in content_lower:
            tech.append('Chakra UI')
        if 'bulma' in content_lower and 'bulma.css' in content_lower:
            tech.append('Bulma')
        if 'foundation' in content_lower and 'foundation.css' in content_lower:
            tech.append('Foundation')
        if 'semantic-ui' in content_lower or 'semantic.min' in content_lower:
            tech.append('Semantic UI')
        
        # Build tools & Bundlers (via source maps ou mentions)
        if 'webpack' in content_lower or 'webpack://' in content_lower:
            tech.append('Webpack')
        if 'vite' in content_lower and ('@vite' in content_lower or 'vite.config' in content_lower):
            tech.append('Vite')
        if 'parcel' in content_lower and 'parcel-bundler' in content_lower:
            tech.append('Parcel')
        if 'rollup' in content_lower:
            tech.append('Rollup')
        if 'turbopack' in content_lower:
            tech.append('Turbopack')
        
        # Analytics & Tracking
        if 'google-analytics' in content_lower or 'gtag' in content_lower or 'ga.js' in content_lower:
            tech.append('Google Analytics')
        if 'googletagmanager' in content_lower or 'gtm.js' in content_lower:
            tech.append('Google Tag Manager')
        if 'hotjar' in content_lower:
            tech.append('Hotjar')
        if 'mixpanel' in content_lower:
            tech.append('Mixpanel')
        if 'segment' in content_lower and 'segment.com' in content_lower:
            tech.append('Segment')
        if 'plausible' in content_lower:
            tech.append('Plausible')
        if 'matomo' in content_lower or 'piwik' in content_lower:
            tech.append('Matomo')
        
        # Payment & E-commerce
        if 'stripe' in content_lower and 'stripe.com' in content_lower:
            tech.append('Stripe')
        if 'paypal' in content_lower:
            tech.append('PayPal')
        if 'klarna' in content_lower:
            tech.append('Klarna')
        if 'square' in content_lower and 'squareup.com' in content_lower:
            tech.append('Square')
        
        # CDN & Hosting
        if 'cloudflare' in content_lower or 'cf-ray' in headers_str:
            tech.append('Cloudflare')
        if 'vercel' in headers_str or 'vercel.app' in content_lower:
            tech.append('Vercel')
        if 'netlify' in headers_str or 'netlify.app' in content_lower:
            tech.append('Netlify')
        if 'aws' in content_lower or 'amazonaws.com' in content_lower:
            tech.append('AWS')
        if 'cloudfront' in headers_str:
            tech.append('CloudFront')
        if 'fastly' in headers_str:
            tech.append('Fastly CDN')
        if 'akamai' in headers_str:
            tech.append('Akamai')
        
        # JavaScript Libraries populaires
        if 'jquery' in content_lower:
            tech.append('jQuery')
        if 'lodash' in content_lower or 'underscore' in content_lower:
            tech.append('Lodash')
        if 'd3.js' in content_lower or 'd3.min.js' in content_lower:
            tech.append('D3.js')
        if 'three.js' in content_lower or 'threejs' in content_lower:
            tech.append('Three.js')
        if 'gsap' in content_lower:
            tech.append('GSAP')
        if 'chart.js' in content_lower:
            tech.append('Chart.js')
        
        # CMS Headless
        if 'contentful' in content_lower:
            tech.append('Contentful')
        if 'sanity' in content_lower and 'sanity.io' in content_lower:
            tech.append('Sanity')
        if 'strapi' in content_lower:
            tech.append('Strapi')
        if 'prismic' in content_lower:
            tech.append('Prismic')
        
        # Testing & Development
        if 'sentry' in content_lower and 'sentry.io' in content_lower:
            tech.append('Sentry')
        if 'datadog' in content_lower:
            tech.append('Datadog')
        if 'new relic' in content_lower or 'newrelic' in content_lower:
            tech.append('New Relic')
        
        return list(set(tech))
    
    def check_site(self, url: str) -> Dict:
        """
        Vérifie un site web et retourne des informations détaillées.
        
        Returns:
            dict avec status, protections, scrapabilité, titre, tech, etc.
        """
        url = self.normalize_url(url)
        start_time = time.time()
        
        result = {
            'url': url,
            'accessible': False,
            'scrapable': False,
            'status_code': None,
            'response_time': None,
            'title': None,
            'protections': [],
            'tech_stack': [],
            'server': None,
            'content_type': None,
            'content_length': None,
            'redirect_chain': [],
            'error': None
        }
        
        try:
            with httpx.Client(
                timeout=self.timeout,
                follow_redirects=self.follow_redirects,
                headers={'User-Agent': self.user_agent}
            ) as client:
                response = client.get(url)
                
                # Temps de réponse
                result['response_time'] = round(time.time() - start_time, 2)
                
                # Status
                result['status_code'] = response.status_code
                result['accessible'] = response.status_code < 400
                
                # Informations du statut
                status_info = self.get_status_info(response.status_code)
                result['status_info'] = status_info
                result['scrapable'] = status_info['scrapable']
                
                # Headers
                result['server'] = response.headers.get('server', 'Unknown')
                result['content_type'] = response.headers.get('content-type', 'Unknown')
                result['content_length'] = response.headers.get('content-length')
                
                # Chaîne de redirections
                if len(response.history) > 0:
                    result['redirect_chain'] = [
                        {'url': r.url.unicode_string(), 'status': r.status_code} 
                        for r in response.history
                    ]
                
                # Analyser le contenu si HTML
                if 'text/html' in result['content_type']:
                    content = response.text
                    
                    # Titre
                    result['title'] = self.extract_title(content)
                    
                    # Protections anti-scraping
                    result['protections'] = self.detect_protection(
                        dict(response.headers), 
                        content
                    )
                    
                    # Stack technologique
                    result['tech_stack'] = self.extract_tech_stack(
                        dict(response.headers),
                        content
                    )
                    
                    # Si protections détectées, marquer comme non scrapable
                    if result['protections']:
                        result['scrapable'] = False
                        result['status_info']['message'] += f" - Protection détectée: {', '.join(result['protections'])}"
                
        except httpx.TimeoutException:
            result['error'] = 'Timeout - Site trop lent ou injoignable'
            result['status_info'] = {
                'level': 'error',
                'emoji': '⏱️',
                'message': 'Timeout',
                'scrapable': False
            }
        except httpx.ConnectError:
            result['error'] = 'Connexion impossible - Site down ou DNS invalide'
            result['status_info'] = {
                'level': 'error',
                'emoji': '💀',
                'message': 'Site inaccessible',
                'scrapable': False
            }
        except Exception as e:
            result['error'] = f'Erreur: {str(e)}'
            result['status_info'] = {
                'level': 'error',
                'emoji': '⚠️',
                'message': str(e),
                'scrapable': False
            }
        
        return result
    
    def check_multiple(self, urls: List[str]) -> Dict[str, Dict]:
        """
        Vérifie plusieurs URLs en séquence.
        
        Returns:
            dict avec url comme clé et résultat comme valeur
        """
        results = {}
        
        for url in urls:
            print(f"[*] Vérification de {url}...")
            result = self.check_site(url)
            results[url] = result
            
            # Afficher le résultat
            emoji = result.get('status_info', {}).get('emoji', '?')
            status = result.get('status_code', 'ERR')
            message = result.get('status_info', {}).get('message', 'Erreur')
            scrapable = '✓ SCRAPABLE' if result['scrapable'] else '✗ NON SCRAPABLE'
            
            print(f"    └─ {emoji} [{status}] {message} - {scrapable}")
            
            if result.get('protections'):
                print(f"       Protections: {', '.join(result['protections'])}")
            if result.get('tech_stack'):
                print(f"       Tech: {', '.join(result['tech_stack'][:5])}")
        
        return results


def filter_scrapable_sites(urls: List[str]) -> Tuple[List[str], List[str], Dict]:
    """
    Filtre une liste d'URLs pour ne garder que celles qui sont scrapables.
    
    Returns:
        (scrapable_urls, non_scrapable_urls, details)
    """
    checker = SiteChecker(timeout=8)
    
    scrapable = []
    non_scrapable = []
    details = {}
    
    print(f"\n{'='*60}")
    print(f"VÉRIFICATION DE {len(urls)} SITES")
    print(f"{'='*60}\n")
    
    results = checker.check_multiple(urls)
    
    for url, result in results.items():
        details[url] = result
        
        if result['scrapable']:
            scrapable.append(url)
        else:
            non_scrapable.append(url)
    
    print(f"\n{'='*60}")
    print(f"RÉSUMÉ")
    print(f"{'='*60}")
    print(f"✅ Scrapable: {len(scrapable)}")
    print(f"❌ Non scrapable: {len(non_scrapable)}")
    print(f"📊 Total vérifié: {len(urls)}")
    
    return scrapable, non_scrapable, details


if __name__ == "__main__":
    # Test du module
    import sys
    
    test_urls = [
        "https://example.com",
        "https://google.com",
        "https://github.com",
        "https://reddit.com"
    ]
    
    if len(sys.argv) > 1:
        test_urls = sys.argv[1:]
    
    scrapable, non_scrapable, details = filter_scrapable_sites(test_urls)
    
    print(f"\n✅ SITES SCRAPABLES:")
    for url in scrapable:
        print(f"  • {url}")
    
    print(f"\n❌ SITES NON SCRAPABLES:")
    for url in non_scrapable:
        info = details[url]
        reason = info.get('status_info', {}).get('message', 'Raison inconnue')
        print(f"  • {url} - {reason}")
