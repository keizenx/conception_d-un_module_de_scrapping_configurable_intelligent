import asyncio
import random
import time
import warnings
from typing import Optional, Dict, Any, List
import httpx
from playwright.async_api import async_playwright

# Suppress pkg_resources deprecation warning from playwright-stealth
warnings.filterwarnings("ignore", category=UserWarning, module='pkg_resources')
warnings.filterwarnings("ignore", category=DeprecationWarning, module='pkg_resources')

# Imports conditionnels pour techniques anti-détection avancées
try:
    from playwright_stealth import stealth_async
    STEALTH_AVAILABLE = True
except ImportError:
    STEALTH_AVAILABLE = False
    print("⚠️ playwright-stealth non disponible - techniques basiques utilisées")

try:
    from fake_useragent import UserAgent
    UA_AVAILABLE = True
except ImportError:
    UA_AVAILABLE = False
    print("⚠️ fake-useragent non disponible - user agents statiques utilisés")

# =================== CONFIGURATIONS OPTIMALES DE SCRAPING ===================

# Configuration Anti-Détection basée sur les meilleures pratiques
OPTIMAL_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-User': '?1',
    'Cache-Control': 'max-age=0',
    'DNT': '1'
}

# Pool d'User-Agents rotatifs pour éviter la détection - ÉTENDU POUR ANTI-DÉTECTION
USER_AGENTS_POOL = [
    # Chrome (le plus commun)
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    # Firefox (moins détecté)
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:122.0) Gecko/20100101 Firefox/122.0',
    # Safari
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2.1 Safari/605.1.15',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Version/17.1.2 Safari/605.1.15'
]

# User-Agent dynamique avec fake-useragent si disponible
def get_dynamic_user_agent() -> str:
    """Obtenir un User-Agent ultra-réaliste et récent"""
    if UA_AVAILABLE:
        try:
            ua = UserAgent()
            return ua.random
        except:
            return random.choice(USER_AGENTS_POOL)
    else:
        return random.choice(USER_AGENTS_POOL)

# Configuration Playwright optimale basée sur la documentation officielle + ANTI-DÉTECTION AVANCÉ
PLAYWRIGHT_CONFIG = {
    'headless': True,  # Plus rapide pour la production
    'args': [
        # === MASQUAGE AUTOMATION ===
        '--disable-blink-features=AutomationControlled',
        '--exclude-switches=enable-automation',
        '--disable-extensions-except=',
        '--disable-extensions',
        '--no-first-run',
        '--no-default-browser-check',
        
        # === SÉCURITÉ ET SANDBOX ===
        '--no-sandbox',
        '--disable-setuid-sandbox', 
        '--disable-dev-shm-usage',
        '--disable-gpu-sandbox',
        
        # === ANTI-DÉTECTION AVANCÉ ===
        '--disable-web-security',
        '--disable-features=VizDisplayCompositor',
        '--disable-features=IsolateOrigins,site-per-process',
        '--disable-site-isolation-trials',
        '--disable-features=TranslateUI',
        '--disable-ipc-flooding-protection',
        
        # === PERFORMANCE ===
        '--disable-background-networking',
        '--disable-background-timer-throttling',
        '--disable-backgrounding-occluded-windows',
        '--disable-renderer-backgrounding',
        '--enable-features=NetworkService,NetworkServiceInProcess',
        
        # === FINGERPRINTING PROTECTION ===
        '--disable-canvas-aa',
        '--disable-2d-canvas-clip-aa',
        '--disable-accelerated-2d-canvas',
        
        # === APPARENCE RÉALISTE ===
        '--force-color-profile=srgb',
        '--hide-scrollbars',
        '--mute-audio',
        '--disable-logging',
        '--disable-notifications',
        
        # Anciens args conservés
        '--disable-infobars',
        '--disable-default-apps',
        '--disable-sync'
    ],
    'viewport': {'width': 1366, 'height': 768},
    'ignore_https_errors': True,
    'java_script_enabled': True,
    'accept_downloads': False,
    'has_touch': False,
    'is_mobile': False,
    'locale': 'fr-FR',
    'timezone_id': 'Europe/Paris',
    'color_scheme': 'light'
}

# Configuration des délais adaptatifs
DELAY_CONFIG = {
    'min_delay': 0.5,          # Délai minimum entre requêtes
    'max_delay': 2.0,          # Délai maximum 
    'nginx_rate_limit': 1.13,  # Respect du rate limiting Nginx (1 req/sec)
    'adaptive_delay': True     # Délai adaptatif selon la charge serveur
}

# Configuration de retry intelligente
RETRY_CONFIG = {
    'max_retries': 3,
    'backoff_factor': 0.3,
    'retry_status_codes': [429, 500, 502, 503, 504],
    'timeout_retry': 2
}

# ==============================================================================

def get_random_user_agent() -> str:
    """Retourne un User-Agent aléatoire optimisé pour anti-détection"""
    # Utiliser le User-Agent dynamique si disponible
    if UA_AVAILABLE:
        return get_dynamic_user_agent()
    else:
        return random.choice(USER_AGENTS_POOL)

def get_optimal_headers() -> dict:
    """
    Génère des headers optimisés avec rotation pour anti-détection
    """
    user_agent = get_random_user_agent()
    
    # Headers de base ultra-réalistes
    headers = {
        'User-Agent': user_agent,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': random.choice([
            'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
            'en-US,en;q=0.9,fr;q=0.8',
            'fr-FR,fr;q=0.8,en-US;q=0.5,en;q=0.3'
        ]),
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate', 
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Cache-Control': random.choice(['max-age=0', 'no-cache']),
        'DNT': '1'
    }
    
    # Ajouter headers Chrome si User-Agent Chrome
    if 'Chrome' in user_agent:
        headers.update({
            'sec-ch-ua': '"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"'
        })
    
    return headers

def adaptive_delay():
    """Calcule un délai adaptatif basé sur la configuration"""
    if DELAY_CONFIG['adaptive_delay']:
        return random.uniform(DELAY_CONFIG['min_delay'], DELAY_CONFIG['max_delay'])
    return DELAY_CONFIG['min_delay']


async def fetch_html_playwright(
    url: str, wait_for_selector: Optional[str] = None, timeout_seconds: float = 60.0
) -> str:
    """
    Récupère le HTML d'une page avec Playwright optimisé (chaque appel crée un nouveau browser).
    Intègre les meilleures pratiques anti-détection et optimisations de performance.
    """
    async with async_playwright() as p:
        # Configuration browser optimale
        browser = await p.chromium.launch(
            headless=PLAYWRIGHT_CONFIG['headless'],
            args=PLAYWRIGHT_CONFIG['args']
        )
        
        # Contexte optimisé avec headers réalistes
        context = await browser.new_context(
            viewport=PLAYWRIGHT_CONFIG['viewport'],
            user_agent=get_random_user_agent(),
            ignore_https_errors=PLAYWRIGHT_CONFIG['ignore_https_errors'],
            java_script_enabled=PLAYWRIGHT_CONFIG['java_script_enabled'],
            accept_downloads=PLAYWRIGHT_CONFIG['accept_downloads'],
            has_touch=PLAYWRIGHT_CONFIG['has_touch'],
            is_mobile=PLAYWRIGHT_CONFIG['is_mobile'],
            locale=PLAYWRIGHT_CONFIG['locale'],
            timezone_id=PLAYWRIGHT_CONFIG['timezone_id'],
            color_scheme=PLAYWRIGHT_CONFIG['color_scheme'],
            extra_http_headers=get_optimal_headers()
        )
        
        page = await context.new_page()

        try:
            # Optimisations de performance - bloquer images et ressources inutiles
            await page.route("**/*.{png,jpg,jpeg,gif,svg,ico,webp}", lambda route: route.abort())
            await page.route("**/*.{woff,woff2,ttf,eot}", lambda route: route.abort())
            await page.route("**/*.{css}", lambda route: route.abort())
            
            # Navigation optimisée avec stratégie de fallback
            try:
                await page.goto(
                    url, 
                    wait_until="domcontentloaded",  # Plus rapide que networkidle
                    timeout=int(timeout_seconds * 1000)
                )
            except Exception as e:
                if "Timeout" in str(e):
                    print(f"⚠️ Timeout sur domcontentloaded, tentative en mode 'commit' (plus rapide)...")
                    # Fallback: on veut juste le HTML, même si tout n'est pas chargé
                    await page.goto(
                        url, 
                        wait_until="commit",
                        timeout=int(timeout_seconds * 1000)
                    )
                    # On attend un peu manuellement
                    await asyncio.sleep(2)
                else:
                    raise e

            if wait_for_selector:
                await page.wait_for_selector(
                    wait_for_selector, timeout=int(timeout_seconds * 1000)
                )
            else:
                # Attendre un court délai pour le contenu dynamique
                await asyncio.sleep(1)

            html = await page.content()
            
            # Délai adaptatif pour éviter la détection
            delay = adaptive_delay()
            await asyncio.sleep(delay)
            
            return html
            
        except Exception as e:
            print(f"⚠️ Erreur lors du fetch Playwright: {str(e)}")
            # En cas d'erreur, on peut retry avec des paramètres plus conservateurs
            raise e
            
        finally:
            await page.close()
            await context.close()
            await browser.close()


async def take_screenshot(url: str, timeout_seconds: float = 30.0) -> str:
    """
    Prend une capture d'écran d'une page web et la retourne en base64.
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=PLAYWRIGHT_CONFIG['headless'],
            args=PLAYWRIGHT_CONFIG['args']
        )
        context = await browser.new_context(
            viewport=PLAYWRIGHT_CONFIG['viewport'],
            user_agent=get_random_user_agent(),
            ignore_https_errors=PLAYWRIGHT_CONFIG['ignore_https_errors'],
            java_script_enabled=PLAYWRIGHT_CONFIG['java_script_enabled'],
            extra_http_headers=get_optimal_headers()
        )
        page = await context.new_page()

        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=int(timeout_seconds * 1000))
            
            # Attendre un peu pour le rendu JS
            await asyncio.sleep(2)

            screenshot_bytes = await page.screenshot(full_page=True)
            
            return screenshot_bytes

        except Exception as e:
            print(f"⚠️ Erreur lors de la capture d'écran Playwright: {str(e)}")
            raise e
            
        finally:
            await page.close()
            await context.close()
            await browser.close()


def fetch_html_with_js(
    url: str, wait_for_selector: Optional[str] = None, timeout_seconds: float = 60.0
) -> str:
    return asyncio.run(fetch_html_playwright(url, wait_for_selector, timeout_seconds))


async def extract_complete_content_playwright(
    url: str, timeout_seconds: float = 60.0, scroll_for_dynamic: bool = True
) -> dict:
    """
    Extraction ULTRA-COMPLÈTE d'une page (basée sur les meilleures pratiques gratuites)
    Extrait : texte, images (y compris background CSS), vidéos, audio, formulaires, 
    tableaux, données structurées JSON-LD, métadonnées complètes
    """
    async with async_playwright() as p:
        # Configuration browser optimale
        browser = await p.chromium.launch(
            headless=PLAYWRIGHT_CONFIG['headless'],
            args=PLAYWRIGHT_CONFIG['args']
        )
        
        # Contexte optimisé avec headers réalistes
        context = await browser.new_context(
            viewport=PLAYWRIGHT_CONFIG['viewport'],
            user_agent=get_random_user_agent(),
            ignore_https_errors=PLAYWRIGHT_CONFIG['ignore_https_errors'],
            java_script_enabled=PLAYWRIGHT_CONFIG['java_script_enabled'],
            extra_http_headers=get_optimal_headers()
        )
        
        page = await context.new_page()

        try:
            print(f"🔍 Extraction ultra-complète : {url}")
            
            # Navigation optimisée avec fallback
            try:
                # On tente d'abord avec un timeout plus généreux (45s au lieu de 20s)
                timeout_ms = max(int(timeout_seconds * 1000), 45000)
                await page.goto(url, wait_until="domcontentloaded", timeout=timeout_ms)
            except Exception as e:
                if "Timeout" in str(e):
                    print(f"⚠️ Timeout sur domcontentloaded, tentative en mode 'commit'...")
                    # Fallback: on récupère dès que le serveur répond
                    await page.goto(url, wait_until="commit", timeout=30000)
                    # IMPORTANT: On attend 5s (au lieu de 2s) pour laisser le JS hydrater la page
                    print(f"⏳ Attente de 5s pour l'hydratation du contenu...")
                    await asyncio.sleep(5)
                else:
                    raise e
            
            # Pour le contenu dynamique - scroll automatique
            if scroll_for_dynamic:
                print(f"📋 Scroll automatique pour contenu dynamique...")
                await page.evaluate("""
                    async () => {
                        await new Promise((resolve) => {
                            let totalHeight = 0;
                            const distance = 100;
                            const timer = setInterval(() => {
                                const scrollHeight = document.body.scrollHeight;
                                window.scrollBy(0, distance);
                                totalHeight += distance;
                                if (totalHeight >= scrollHeight) {
                                    clearInterval(timer);
                                    resolve();
                                }
                            }, 100);
                        });
                    }
                """)
                await asyncio.sleep(2)  # Attendre le chargement après scroll
                
            # EXTRACTION ULTRA-COMPLÈTE
            full_content = await page.evaluate(r"""
                () => {
                    const result = {
                        metadata: {},
                        text: {},
                        media: {
                            images: [],
                            backgroundImages: [],
                            videos: [],
                            audios: [],
                            iframes: []
                        },
                        links: [],
                        files: [],
                        forms: [],
                        tables: [],
                        structuredData: [],
                        scripts: [],
                        styles: []
                    };
                    
                    // ===== MÉTADONNÉES COMPLÈTES =====
                    result.metadata = {
                        title: document.title,
                        url: window.location.href,
                        description: document.querySelector('meta[name="description"]')?.content || '',
                        keywords: document.querySelector('meta[name="keywords"]')?.content || '',
                        author: document.querySelector('meta[name="author"]')?.content || '',
                        ogTitle: document.querySelector('meta[property="og:title"]')?.content || '',
                        ogDescription: document.querySelector('meta[property="og:description"]')?.content || '',
                        ogImage: document.querySelector('meta[property="og:image"]')?.content || '',
                        canonical: document.querySelector('link[rel="canonical"]')?.href || '',
                        language: document.documentElement.lang || '',
                        favicon: document.querySelector('link[rel="icon"]')?.href || 
                                 document.querySelector('link[rel="shortcut icon"]')?.href || '',
                        charset: document.characterSet || '',
                        viewport: document.querySelector('meta[name="viewport"]')?.content || ''
                    };
                    
                    // ===== TEXTE STRUCTURÉ =====
                    result.text = {
                        fullText: document.body.innerText,
                        title: document.title,
                        headings: {
                            h1: [...document.querySelectorAll('h1')].map(h => h.textContent.trim()).filter(Boolean),
                            h2: [...document.querySelectorAll('h2')].map(h => h.textContent.trim()).filter(Boolean),
                            h3: [...document.querySelectorAll('h3')].map(h => h.textContent.trim()).filter(Boolean),
                            h4: [...document.querySelectorAll('h4')].map(h => h.textContent.trim()).filter(Boolean),
                            h5: [...document.querySelectorAll('h5')].map(h => h.textContent.trim()).filter(Boolean),
                            h6: [...document.querySelectorAll('h6')].map(h => h.textContent.trim()).filter(Boolean)
                        },
                        paragraphs: [...document.querySelectorAll('p')].map(p => p.textContent.trim()).filter(Boolean),
                        lists: [...document.querySelectorAll('ul, ol')].map(list => ({
                            type: list.tagName.toLowerCase(),
                            items: [...list.querySelectorAll('li')].map(li => li.textContent.trim()).filter(Boolean)
                        })),
                        quotes: [...document.querySelectorAll('blockquote')].map(q => q.textContent.trim()).filter(Boolean)
                    };
                    
                    // ===== IMAGES COMPLÈTES =====
                    result.media.images = [...document.querySelectorAll('img')].map((img, index) => ({
                        src: img.src,
                        alt: img.alt || '',
                        title: img.title || '',
                        width: img.width || 0,
                        height: img.height || 0,
                        naturalWidth: img.naturalWidth || 0,
                        naturalHeight: img.naturalHeight || 0,
                        srcset: img.srcset || '',
                        loading: img.loading || '',
                        index
                    })).filter(img => img.src);
                    
                    // Images en background CSS (technique avancée)
                    const elementsWithBg = [...document.querySelectorAll('*')].filter(el => {
                        const bg = window.getComputedStyle(el).backgroundImage;
                        return bg && bg !== 'none' && bg.includes('url(');
                    });
                    
                    result.media.backgroundImages = elementsWithBg.map((el, index) => ({
                        backgroundImage: window.getComputedStyle(el).backgroundImage,
                        element: el.tagName,
                        className: el.className,
                        index
                    }));
                    
                    // ===== VIDÉOS COMPLÈTES =====
                    result.media.videos = [...document.querySelectorAll('video')].map((video, index) => ({
                        src: video.src || video.currentSrc,
                        poster: video.poster,
                        sources: [...video.querySelectorAll('source')].map(s => ({
                            src: s.src,
                            type: s.type
                        })),
                        width: video.width || 0,
                        height: video.height || 0,
                        duration: video.duration || 0,
                        autoplay: video.autoplay,
                        controls: video.controls,
                        muted: video.muted,
                        index
                    })).filter(video => video.src);
                    
                    // YouTube, Vimeo, etc. (iframes)
                    result.media.iframes = [...document.querySelectorAll('iframe')].map((iframe, index) => ({
                        src: iframe.src,
                        width: iframe.width || 0,
                        height: iframe.height || 0,
                        title: iframe.title || '',
                        frameborder: iframe.frameBorder || '',
                        index
                    })).filter(iframe => iframe.src);
                    
                    // ===== AUDIO =====
                    result.media.audios = [...document.querySelectorAll('audio')].map((audio, index) => ({
                        src: audio.src || audio.currentSrc,
                        sources: [...audio.querySelectorAll('source')].map(s => ({
                            src: s.src,
                            type: s.type
                        })),
                        controls: audio.controls,
                        autoplay: audio.autoplay,
                        muted: audio.muted,
                        index
                    })).filter(audio => audio.src);
                    
                    // ===== LIENS OPTIMISÉS =====
                    result.links = [...document.querySelectorAll('a[href]')].map((a, index) => ({
                        href: a.href,
                        text: a.textContent.trim(),
                        title: a.title || '',
                        target: a.target || '',
                        rel: a.rel || '',
                        internal: a.href.includes(window.location.hostname),
                        index
                    })).filter(link => link.href && link.text);
                    
                    // ===== FICHIERS TÉLÉCHARGEABLES =====
                    result.files = [...document.querySelectorAll('a[href]')].filter(a => {
                        const href = a.href.toLowerCase();
                        return href.match(/\.(pdf|doc|docx|xls|xlsx|ppt|pptx|zip|rar|7z|tar|gz|mp3|mp4|avi|mov)$/);
                    }).map((a, index) => ({
                        href: a.href,
                        text: a.textContent.trim(),
                        type: a.href.split('.').pop().toLowerCase(),
                        size: a.getAttribute('data-size') || '',
                        index
                    }));
                    
                    // ===== FORMULAIRES COMPLETS =====
                    result.forms = [...document.querySelectorAll('form')].map((form, index) => ({
                        action: form.action,
                        method: form.method || 'get',
                        id: form.id || '',
                        name: form.name || '',
                        enctype: form.enctype || '',
                        inputs: [...form.querySelectorAll('input, textarea, select')].map(input => ({
                            type: input.type || input.tagName.toLowerCase(),
                            name: input.name || '',
                            id: input.id || '',
                            placeholder: input.placeholder || '',
                            value: input.value || '',
                            required: input.required,
                            label: input.labels?.[0]?.textContent?.trim() || ''
                        })),
                        index
                    }));
                    
                    // ===== TABLEAUX STRUCTURÉS =====
                    result.tables = [...document.querySelectorAll('table')].map((table, index) => ({
                        caption: table.querySelector('caption')?.textContent?.trim() || '',
                        headers: [...table.querySelectorAll('thead th, tr:first-child th')].map(th => th.textContent.trim()),
                        rows: [...table.querySelectorAll('tbody tr, tr')]
                            .filter(tr => !tr.querySelector('th'))
                            .map(tr => [...tr.querySelectorAll('td')].map(td => td.textContent.trim()))
                            .filter(row => row.length > 0),
                        index
                    })).filter(table => table.headers.length > 0 || table.rows.length > 0);
                    
                    // ===== DONNÉES STRUCTURÉES JSON-LD =====
                    result.structuredData = [...document.querySelectorAll('script[type="application/ld+json"]')]
                        .map((script, index) => {
                            try {
                                return {
                                    data: JSON.parse(script.textContent),
                                    index
                                };
                            } catch {
                                return null;
                            }
                        }).filter(Boolean);
                    
                    // ===== SCRIPTS ET STYLES =====
                    result.scripts = [...document.querySelectorAll('script[src]')].map(s => s.src).filter(Boolean);
                    result.styles = [...document.querySelectorAll('link[rel="stylesheet"]')].map(l => l.href).filter(Boolean);
                    
                    return result;
                }
            """)
            
            # Statistiques d'extraction
            stats = {
                'text_length': len(full_content['text']['fullText']),
                'images': len(full_content['media']['images']),
                'background_images': len(full_content['media']['backgroundImages']),
                'videos': len(full_content['media']['videos']),
                'audios': len(full_content['media']['audios']),
                'iframes': len(full_content['media']['iframes']),
                'links': len(full_content['links']),
                'files': len(full_content['files']),
                'forms': len(full_content['forms']),
                'tables': len(full_content['tables']),
                'structured_data': len(full_content['structuredData'])
            }
            
            print(f"✅ Extraction ultra-complète terminée !")
            print(f"   📝 Texte: {stats['text_length']} caractères")
            print(f"   🖼️ Images: {stats['images']} (+{stats['background_images']} background)")
            print(f"   🎥 Vidéos: {stats['videos']}, Audios: {stats['audios']}, iFrames: {stats['iframes']}")
            print(f"   🔗 Liens: {stats['links']}, Fichiers: {stats['files']}")
            print(f"   📊 Formulaires: {stats['forms']}, Tableaux: {stats['tables']}")
            print(f"   📦 Données structurées: {stats['structured_data']}")
            
            # Ajouter les statistiques
            full_content['extraction_stats'] = stats
            full_content['extraction_timestamp'] = int(time.time())
            full_content['extraction_url'] = url
            
            return full_content
            
        except Exception as e:
            print(f"❌ Erreur extraction complète: {str(e)}")
            raise e
            
        finally:
            await page.close()
            await context.close()
            await browser.close()
def fetch_html_smart(
    url: str,
    use_js: bool = False,
    wait_for_selector: Optional[str] = None,
    timeout_seconds: float = 20.0,
) -> str:
    """
    Fonction optimisée avec retry intelligent et configurations avancées
    Compatible avec l'extraction complète
    """
    max_attempts = RETRY_CONFIG['max_retries']
    
    for attempt in range(max_attempts):
        try:
            if use_js:
                # Utiliser Playwright pour contenu dynamique
                result = fetch_html_with_js(url, wait_for_selector, timeout_seconds)
                print(f"✅ Contenu récupéré avec Playwright (tentative {attempt + 1})")
                return result
            else:
                # Requête HTTP optimisée avec headers avancés
                headers = get_optimal_headers()
                
                with httpx.Client(
                    follow_redirects=True, 
                    timeout=timeout_seconds, 
                    headers=headers,
                    verify=False  # Pour éviter les erreurs SSL sur certains sites
                ) as client:
                    
                    # Délai adaptatif avant la requête
                    if attempt > 0:
                        delay = RETRY_CONFIG['backoff_factor'] * (2 ** attempt)
                        print(f"🔄 Retry dans {delay:.1f}s...")
                        time.sleep(delay)
                    
                    resp = client.get(url)
                    
                    # Vérifier si on doit retry basé sur le status code
                    if resp.status_code in RETRY_CONFIG['retry_status_codes']:
                        if attempt < max_attempts - 1:
                            print(f"⚠️ Status {resp.status_code} - retry tentative {attempt + 2}")
                            continue
                    
                    resp.raise_for_status()
                    
                    # Délai adaptatif après requête réussie
                    delay = adaptive_delay()
                    time.sleep(delay)
                    
                    print(f"✅ Contenu récupéré avec HTTP (tentative {attempt + 1})")
                    return resp.text
                    
        except Exception as e:
            error_msg = str(e).lower()
            print(f"⚠️ Tentative {attempt + 1} échouée: {str(e)}")
            
            # Conditions de retry
            should_retry = (
                attempt < max_attempts - 1 and (
                    "timeout" in error_msg or
                    "connection" in error_msg or
                    "network" in error_msg or
                    "502" in error_msg or
                    "503" in error_msg
                )
            )
            
            if should_retry:
                retry_delay = RETRY_CONFIG['backoff_factor'] * (2 ** attempt)
                print(f"🔄 Retry dans {retry_delay:.1f}s...")
                time.sleep(retry_delay)
                continue
            else:
                # Dernière tentative ou erreur non-retryable
                if attempt == max_attempts - 1:
                    print(f"❌ Échec après {max_attempts} tentatives")
                raise e
    
    # Ne devrait jamais arriver
    raise Exception(f"Échec de récupération après {max_attempts} tentatives")


def extract_complete_content_sync(url: str, timeout_seconds: float = 20.0, scroll_for_dynamic: bool = True) -> dict:
    """
    Version synchrone de l'extraction complète pour compatibilité
    """
    return asyncio.run(extract_complete_content_playwright(url, timeout_seconds, scroll_for_dynamic))


# =================== CLASSE PLAYWRIGHT FETCHER OPTIMISÉE ===================

class PlaywrightFetcher:
    """
    🚀 Scraper ultra-complet avec Playwright optimisé + ANTI-DÉTECTION AVANCÉ
    
    Intègre toutes les meilleures pratiques :
    - Headers anti-détection ultra-avancés
    - User-Agent rotation automatique avec fake-useragent
    - Scripts anti-fingerprinting (WebDriver, Chrome runtime, WebGL, Canvas)
    - Playwright-stealth si disponible
    - Scroll automatique pour contenu dynamique
    - Extraction complète : métadonnées, images, vidéos, formulaires, tableaux
    - Support JavaScript complet
    - Données structurées JSON-LD
    - Contournement Cloudflare niveau 1-2
    - 100% GRATUIT !
    """
    
    def __init__(self):
        self.browser = None
        self.context = None
        self.playwright = None
        self.stealth_enabled = STEALTH_AVAILABLE
        
    async def initialize(self, use_stealth: bool = True):
        """Initialiser le navigateur avec TOUTES les optimisations anti-détection"""
        if not self.browser:
            self.playwright = await async_playwright().start()
            
            # Configuration avec paramètres anti-détection étendus
            self.browser = await self.playwright.chromium.launch(
                headless=PLAYWRIGHT_CONFIG['headless'],
                args=PLAYWRIGHT_CONFIG['args'],
                ignore_default_args=['--enable-automation', '--enable-blink-features=AutomationControlled']
            )
            
            # Résolutions réalistes (rotation)
            viewports = [
                {'width': 1920, 'height': 1080},
                {'width': 1366, 'height': 768},
                {'width': 1536, 'height': 864},
                {'width': 1440, 'height': 900}
            ]
            viewport = random.choice(viewports)
            
            # Context ultra-réaliste avec headers optimaux
            self.context = await self.browser.new_context(
                viewport=viewport,
                user_agent=get_random_user_agent(),
                ignore_https_errors=PLAYWRIGHT_CONFIG['ignore_https_errors'],
                java_script_enabled=PLAYWRIGHT_CONFIG['java_script_enabled'],
                locale=random.choice(['fr-FR', 'en-US', 'en-GB']),
                timezone_id='Europe/Paris',
                color_scheme='light',
                extra_http_headers=get_optimal_headers(),
                device_scale_factor=random.choice([1, 1.25, 1.5])
            )
        
    async def close(self):
        """Fermer le navigateur proprement"""
        try:
            if self.context:
                await self.context.close()
                self.context = None
            if self.browser:
                await self.browser.close()
                self.browser = None
            if self.playwright:
                await self.playwright.stop()
                self.playwright = None
        except Exception as e:
            print(f"⚠️ Erreur fermeture navigateur: {e}")
            
    async def extract_everything(
        self, 
        url: str, 
        use_scroll: bool = True,
        timeout_seconds: float = 30.0,
        wait_for_selector: Optional[str] = None,
        use_stealth: bool = True
    ) -> dict:
        """
        🌟 EXTRACTION ULTRA-COMPLÈTE avec ANTI-DÉTECTION AVANCÉ intégré
        """
        await self.initialize(use_stealth=use_stealth)
        page = await self.context.new_page()
        
        try:
            print(f"🚀 Extraction ultra-complète optimisée: {url}")
            
            # Appliquer playwright-stealth si disponible et demandé
            if use_stealth and self.stealth_enabled:
                try:
                    await stealth_async(page)
                    print("   🛡️ Playwright-stealth activé")
                except Exception as e:
                    print(f"   ⚠️ Stealth non appliqué: {e}")
            
            # Injecter les scripts anti-détection avancés
            await self._inject_anti_detection_scripts(page)
            
            # Navigation avec optimisations et fallback
            try:
                await page.goto(
                    url, 
                    wait_until='domcontentloaded',
                    timeout=int(timeout_seconds * 1000)
                )
            except Exception as e:
                if "Timeout" in str(e):
                    print(f"⚠️ Timeout sur domcontentloaded, tentative en mode 'commit'...")
                    await page.goto(
                        url, 
                        wait_until='commit',
                        timeout=int(timeout_seconds * 1000)
                    )
                    await asyncio.sleep(2)
                else:
                    raise e
            
            # Attendre sélecteur spécifique si demandé
            if wait_for_selector:
                try:
                    await page.wait_for_selector(wait_for_selector, timeout=10000)
                except:
                    print(f"⚠️ Sélecteur '{wait_for_selector}' non trouvé")
            
            # Délai adaptatif pour le contenu dynamique
            await asyncio.sleep(adaptive_delay())
            
            # Scroll automatique pour contenu lazy-loaded
            if use_scroll:
                print("📋 Scroll automatique pour contenu dynamique...")
                await self._auto_scroll(page)
            
            # EXTRACTION COMPLÈTE DIRECTE (sans appel à la fonction externe)
            full_content = await page.evaluate(r"""
                () => {
                    const result = {
                        metadata: {},
                        text: {},
                        media: {
                            images: [],
                            backgroundImages: [],
                            videos: [],
                            audios: [],
                            iframes: []
                        },
                        links: [],
                        files: [],
                        forms: [],
                        tables: [],
                        structuredData: [],
                        scripts: [],
                        styles: []
                    };
                    
                    // ===== MÉTADONNÉES COMPLÈTES =====
                    result.metadata = {
                        title: document.title || '',
                        url: window.location.href,
                        description: document.querySelector('meta[name="description"]')?.content || '',
                        keywords: document.querySelector('meta[name="keywords"]')?.content || '',
                        author: document.querySelector('meta[name="author"]')?.content || '',
                        
                        // Open Graph
                        ogTitle: document.querySelector('meta[property="og:title"]')?.content || '',
                        ogDescription: document.querySelector('meta[property="og:description"]')?.content || '',
                        ogImage: document.querySelector('meta[property="og:image"]')?.content || '',
                        ogUrl: document.querySelector('meta[property="og:url"]')?.content || '',
                        ogType: document.querySelector('meta[property="og:type"]')?.content || '',
                        
                        // Twitter Card
                        twitterCard: document.querySelector('meta[name="twitter:card"]')?.content || '',
                        twitterTitle: document.querySelector('meta[name="twitter:title"]')?.content || '',
                        twitterDescription: document.querySelector('meta[name="twitter:description"]')?.content || '',
                        twitterImage: document.querySelector('meta[name="twitter:image"]')?.content || '',
                        
                        // Autres
                        canonical: document.querySelector('link[rel="canonical"]')?.href || '',
                        language: document.documentElement.lang || '',
                        favicon: document.querySelector('link[rel="icon"]')?.href || 
                                 document.querySelector('link[rel="shortcut icon"]')?.href || '',
                        charset: document.characterSet || '',
                        viewport: document.querySelector('meta[name="viewport"]')?.content || ''
                    };
                    
                    // ===== TEXTE =====
                    result.text = {
                        fullText: document.body.innerText || '',
                        html: document.documentElement.outerHTML,
                        headings: {
                            h1: Array.from(document.querySelectorAll('h1')).map(h => h.textContent.trim()).filter(Boolean),
                            h2: Array.from(document.querySelectorAll('h2')).map(h => h.textContent.trim()).filter(Boolean),
                            h3: Array.from(document.querySelectorAll('h3')).map(h => h.textContent.trim()).filter(Boolean),
                            h4: Array.from(document.querySelectorAll('h4')).map(h => h.textContent.trim()).filter(Boolean),
                            h5: Array.from(document.querySelectorAll('h5')).map(h => h.textContent.trim()).filter(Boolean),
                            h6: Array.from(document.querySelectorAll('h6')).map(h => h.textContent.trim()).filter(Boolean)
                        },
                        paragraphs: Array.from(document.querySelectorAll('p')).map(p => p.textContent.trim()).filter(Boolean),
                        lists: Array.from(document.querySelectorAll('ul, ol')).map(list => ({
                            type: list.tagName.toLowerCase(),
                            items: Array.from(list.querySelectorAll('li')).map(li => li.textContent.trim()).filter(Boolean)
                        }))
                    };
                    
                    // ===== IMAGES =====
                    result.media.images = Array.from(document.querySelectorAll('img')).map((img, index) => ({
                        src: img.src || '',
                        alt: img.alt || '',
                        title: img.title || '',
                        width: img.width || 0,
                        height: img.height || 0,
                        index
                    })).filter(img => img.src);
                    
                    // Images background CSS
                    result.media.backgroundImages = Array.from(document.querySelectorAll('*'))
                        .filter(el => {
                            const bg = window.getComputedStyle(el).backgroundImage;
                            return bg && bg !== 'none' && bg.includes('url');
                        })
                        .map((el, index) => {
                            const bg = window.getComputedStyle(el).backgroundImage;
                            const urlMatch = bg.match(/url\\(['"]?([^'"]+)['"]?\\)/);
                            return {
                                url: urlMatch ? urlMatch[1] : bg,
                                element: el.tagName,
                                index
                            };
                        });
                    
                    // ===== VIDÉOS =====
                    result.media.videos = Array.from(document.querySelectorAll('video')).map((video, index) => ({
                        src: video.src || video.currentSrc || '',
                        poster: video.poster || '',
                        width: video.width || 0,
                        height: video.height || 0,
                        index
                    })).filter(video => video.src);
                    
                    // ===== AUDIO =====
                    result.media.audios = Array.from(document.querySelectorAll('audio')).map((audio, index) => ({
                        src: audio.src || audio.currentSrc || '',
                        controls: audio.controls,
                        index
                    })).filter(audio => audio.src);
                    
                    // ===== IFRAMES =====
                    result.media.iframes = Array.from(document.querySelectorAll('iframe')).map((iframe, index) => ({
                        src: iframe.src || '',
                        title: iframe.title || '',
                        index
                    })).filter(iframe => iframe.src);
                    
                    // ===== LIENS =====
                    result.links = Array.from(document.querySelectorAll('a')).map((a, index) => ({
                        href: a.href || '',
                        text: a.textContent.trim(),
                        title: a.title || '',
                        index
                    })).filter(link => link.href && link.text);
                    
                    // ===== FICHIERS =====
                    result.files = Array.from(document.querySelectorAll('a[href]'))
                        .filter(a => {
                            const href = (a.href || '').toLowerCase();
                            return /\\.(pdf|doc|docx|xls|xlsx|ppt|pptx|zip|rar|7z|tar|gz|csv|txt|json|xml)$/.test(href);
                        })
                        .map((a, index) => ({
                            href: a.href || '',
                            text: a.textContent.trim(),
                            type: (a.href || '').split('.').pop().toLowerCase(),
                            index
                        }));
                    
                    // ===== FORMULAIRES =====
                    result.forms = Array.from(document.querySelectorAll('form')).map((form, index) => ({
                        action: form.action || '',
                        method: form.method || 'get',
                        id: form.id || '',
                        index
                    }));
                    
                    // ===== TABLEAUX =====
                    result.tables = Array.from(document.querySelectorAll('table')).map((table, index) => ({
                        headers: Array.from(table.querySelectorAll('th')).map(th => th.textContent.trim()),
                        rows: Array.from(table.querySelectorAll('tr')).map(tr => 
                            Array.from(tr.querySelectorAll('td')).map(td => td.textContent.trim())
                        ).filter(row => row.length > 0),
                        index
                    }));
                    
                    // ===== DONNÉES STRUCTURÉES =====
                    result.structuredData = Array.from(document.querySelectorAll('script[type="application/ld+json"]'))
                        .map(script => {
                            try {
                                return JSON.parse(script.textContent);
                            } catch {
                                return null;
                            }
                        })
                        .filter(Boolean);
                    
                    return result;
                }
            """)
            
            # Calculer statistiques
            summary = self._calculate_summary_direct(full_content)
            
            # Construire le résultat final
            result = {
                'success': True,
                'data': full_content,
                'summary': summary,
                'url': url,
                'extraction_type': 'ultra_complete',
                'extraction_method': 'playwright_fetcher_optimized',
                'optimizations_used': [
                    'Headers anti-détection avancés',
                    'User-Agent rotation automatique', 
                    'Délais adaptatifs intelligents',
                    'Retry logic avec backoff exponentiel',
                    'Optimisations Playwright (block resources)',
                    'Scroll automatique pour contenu dynamique'
                ],
                'timestamp': time.time()
            }
            
            print("✅ Extraction PlaywrightFetcher optimisée terminée !")
            print(f"   📝 Texte: {summary['total_text_length']:,} caractères")
            print(f"   🖼️ Images: {summary['media_found']['images']} (+{summary['media_found']['background_images']} background)")
            print(f"   🔗 Contenu: {summary['content_found']['links']} liens, {summary['content_found']['files']} fichiers")
            
            return result
            
        except Exception as e:
            print(f"❌ Erreur extraction: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'url': url,
                'extraction_method': 'playwright_fetcher_optimized'
            }
        finally:
            await page.close()
    
    async def _inject_anti_detection_scripts(self, page):
        """
        🛡️ Injection des scripts anti-détection ultra-avancés
        Couvre: WebDriver masking, Chrome runtime, fingerprinting, etc.
        """
        await page.add_init_script("""
            // =================== MASQUAGE WEBDRIVER ===================
            
            // 1. Masquer la propriété webdriver
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
            
            // 2. Supprimer les flags d'automation
            delete window.cdc_adoQpoasnfa76pfcZLmcfl_Array;
            delete window.cdc_adoQpoasnfa76pfcZLmcfl_Promise;
            delete window.cdc_adoQpoasnfa76pfcZLmcfl_Symbol;
            
            // =================== CHROME RUNTIME ===================
            
            // 3. Simuler l'objet Chrome (critique pour Cloudflare)
            window.chrome = {
                runtime: {
                    connect: () => {},
                    sendMessage: () => {},
                    onConnect: { addListener: () => {}, removeListener: () => {} },
                    onMessage: { addListener: () => {}, removeListener: () => {} }
                },
                loadTimes: function() {
                    return {
                        commitLoadTime: Math.random() * 1000 + 1000,
                        connectionInfo: 'h2',
                        finishDocumentLoadTime: Math.random() * 1000 + 2000,
                        finishLoadTime: Math.random() * 1000 + 2500,
                        navigationType: 'Navigation'
                    };
                },
                app: { isInstalled: false }
            };
            
            // =================== PLUGINS RÉALISTES ===================
            
            // 4. Simuler des plugins de navigateur réalistes
            Object.defineProperty(navigator, 'plugins', {
                get: () => {
                    const plugins = [
                        { name: 'Chrome PDF Plugin', filename: 'internal-pdf-viewer', length: 1 },
                        { name: 'Chrome PDF Viewer', filename: 'mhjfbmdgcfjbbpaeojofohoefgiehjai', length: 1 },
                        { name: 'Native Client', filename: 'internal-nacl-plugin', length: 2 }
                    ];
                    plugins.refresh = () => {};
                    return plugins;
                }
            });
            
            // =================== PERMISSIONS API ===================
            
            // 5. Mockup permissions réalistes
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) => {
                if (parameters.name === 'notifications') {
                    return Promise.resolve({ state: 'prompt' });
                }
                return Promise.resolve({ state: 'prompt' });
            };
            
            // =================== WEBGL PROTECTION ===================
            
            // 6. Masquer les infos GPU WebGL
            const getParameter = WebGLRenderingContext.prototype.getParameter;
            WebGLRenderingContext.prototype.getParameter = function(parameter) {
                const fakeValues = {
                    37445: 'Intel Inc.',
                    37446: 'Intel Iris OpenGL Engine'
                };
                return fakeValues[parameter] || getParameter.apply(this, [parameter]);
            };
            
            // =================== HARDWARE MASKING ===================
            
            // 7. Hardware concurrency réaliste
            Object.defineProperty(navigator, 'hardwareConcurrency', {
                get: () => [4, 8, 12, 16][Math.floor(Math.random() * 4)]
            });
            
            // 8. Device memory réaliste
            Object.defineProperty(navigator, 'deviceMemory', {
                get: () => [4, 8, 16][Math.floor(Math.random() * 3)]
            });
            
            // 9. Platform cohérent
            Object.defineProperty(navigator, 'platform', {
                get: () => 'Win32'
            });
            
            Object.defineProperty(navigator, 'vendor', {
                get: () => 'Google Inc.'
            });
            
            console.info('🛡️ Anti-detection scripts loaded');
        """)
        print("   🛡️ Scripts anti-détection injectés")
    
    async def _auto_scroll(self, page):
        """Scroll automatique optimisé"""
        await page.evaluate("""
            async () => {
                await new Promise((resolve) => {
                    let totalHeight = 0;
                    const distance = 100;
                    const timer = setInterval(() => {
                        const scrollHeight = document.body.scrollHeight;
                        window.scrollBy(0, distance);
                        totalHeight += distance;

                        if (totalHeight >= scrollHeight) {
                            clearInterval(timer);
                            window.scrollTo(0, 0);
                            resolve();
                        }
                    }, 100);
                });
            }
        """)
        await asyncio.sleep(1)
    
    def _calculate_summary_direct(self, content: dict) -> dict:
        """Calculer un résumé des données extraites directement"""
        text_data = content.get('text', {})
        media_data = content.get('media', {})
        
        return {
            'total_text_length': len(text_data.get('fullText', '')),
            'total_html_length': len(text_data.get('html', '')),
            'media_found': {
                'images': len(media_data.get('images', [])),
                'background_images': len(media_data.get('backgroundImages', [])),
                'videos': len(media_data.get('videos', [])),
                'audios': len(media_data.get('audios', [])),
                'iframes': len(media_data.get('iframes', []))
            },
            'content_found': {
                'links': len(content.get('links', [])),
                'files': len(content.get('files', [])),
                'forms': len(content.get('forms', [])),
                'tables': len(content.get('tables', [])),
                'structured_data': len(content.get('structuredData', [])),
                'headings': {
                    'h1': len(text_data.get('headings', {}).get('h1', [])),
                    'h2': len(text_data.get('headings', {}).get('h2', [])),
                    'h3': len(text_data.get('headings', {}).get('h3', [])),
                }
            }
        }


# Instance globale (singleton pattern)
_fetcher_instance = None

async def get_fetcher() -> PlaywrightFetcher:
    """Obtenir l'instance globale du fetcher (singleton)"""
    global _fetcher_instance
    if _fetcher_instance is None:
        _fetcher_instance = PlaywrightFetcher()
    return _fetcher_instance

async def cleanup_fetcher():
    """Nettoyer l'instance globale"""
    global _fetcher_instance
    if _fetcher_instance:
        await _fetcher_instance.close()
        _fetcher_instance = None
