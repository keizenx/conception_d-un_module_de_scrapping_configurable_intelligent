# Backend/src/core/fetcher_playwright.py
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout
import asyncio
import json
from typing import Dict, Any, Optional, List
from urllib.parse import urljoin, urlparse
import re

class PlaywrightFetcher:
    """
    Scraper ultra-complet avec Playwright
    Extrait TOUT le contenu automatiquement : texte, images, vidéos, médias, etc.
    """
    
    def __init__(self):
        self.browser = None
        self.context = None
        
    async def initialize(self):
        """Initialiser le navigateur"""
        playwright = await async_playwright().start()
        self.browser = await playwright.chromium.launch(
            headless=True,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--no-sandbox'
            ]
        )
        # Context avec User-Agent réaliste
        self.context = await self.browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            viewport={'width': 1920, 'height': 1080},
            locale='fr-FR',
            timezone_id='Europe/Paris'
        )
        
    async def close(self):
        """Fermer le navigateur"""
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
            
    async def extract_everything(
        self, 
        url: str, 
        use_scroll: bool = True,
        timeout_seconds: float = 30.0,
        wait_for_selector: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Extrait TOUT le contenu d'une page automatiquement
        
        Args:
            url: URL à scraper
            use_scroll: Scroller pour charger le contenu lazy-loaded
            timeout_seconds: Timeout en secondes
            wait_for_selector: Sélecteur optionnel à attendre
            
        Returns:
            Dictionnaire avec tout le contenu extrait
        """
        if not self.browser:
            await self.initialize()
            
        page = await self.context.new_page()
        
        try:
            # Navigation vers la page
            await page.goto(
                url, 
                wait_until='networkidle',
                timeout=int(timeout_seconds * 1000)
            )
            
            # Attendre un sélecteur spécifique si demandé
            if wait_for_selector:
                await page.wait_for_selector(wait_for_selector, timeout=10000)
            
            # Attendre que le contenu dynamique se charge
            await asyncio.sleep(2)
            
            # Scroller pour charger le contenu lazy-loaded
            if use_scroll:
                await self._auto_scroll(page)
            
            # EXTRACTION COMPLÈTE
            full_content = await page.evaluate("""
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
                    
                    // ===== MÉTADONNÉES =====
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
                        
                        paragraphs: Array.from(document.querySelectorAll('p'))
                            .map(p => p.textContent.trim())
                            .filter(Boolean),
                        
                        lists: Array.from(document.querySelectorAll('ul, ol')).map(list => ({
                            type: list.tagName.toLowerCase(),
                            items: Array.from(list.querySelectorAll('li')).map(li => li.textContent.trim())
                        })),
                        
                        // Contenu principal (détection auto)
                        mainContent: (() => {
                            const main = 
                                document.querySelector('main') ||
                                document.querySelector('article') ||
                                document.querySelector('[role="main"]') ||
                                document.querySelector('.content') ||
                                document.querySelector('#content');
                            return main ? main.innerText : '';
                        })()
                    };
                    
                    // ===== IMAGES =====
                    result.media.images = Array.from(document.querySelectorAll('img')).map((img, index) => ({
                        src: img.src || '',
                        alt: img.alt || '',
                        title: img.title || '',
                        width: img.width || 0,
                        height: img.height || 0,
                        naturalWidth: img.naturalWidth || 0,
                        naturalHeight: img.naturalHeight || 0,
                        srcset: img.srcset || '',
                        loading: img.loading || '',
                        className: img.className || '',
                        id: img.id || '',
                        index
                    }));
                    
                    // Images en background CSS
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
                                className: el.className || '',
                                id: el.id || '',
                                index
                            };
                        });
                    
                    // ===== VIDÉOS =====
                    result.media.videos = Array.from(document.querySelectorAll('video')).map((video, index) => ({
                        src: video.src || video.currentSrc || '',
                        poster: video.poster || '',
                        sources: Array.from(video.querySelectorAll('source')).map(s => ({
                            src: s.src || '',
                            type: s.type || ''
                        })),
                        width: video.width || 0,
                        height: video.height || 0,
                        duration: video.duration || 0,
                        autoplay: video.autoplay,
                        controls: video.controls,
                        loop: video.loop,
                        muted: video.muted,
                        index
                    }));
                    
                    // iframes (YouTube, Vimeo, etc.)
                    result.media.iframes = Array.from(document.querySelectorAll('iframe')).map((iframe, index) => ({
                        src: iframe.src || '',
                        width: iframe.width || '',
                        height: iframe.height || '',
                        title: iframe.title || '',
                        allowFullscreen: iframe.allowFullscreen,
                        frameborder: iframe.frameBorder || '',
                        index
                    }));
                    
                    // ===== AUDIO =====
                    result.media.audios = Array.from(document.querySelectorAll('audio')).map((audio, index) => ({
                        src: audio.src || audio.currentSrc || '',
                        sources: Array.from(audio.querySelectorAll('source')).map(s => ({
                            src: s.src || '',
                            type: s.type || ''
                        })),
                        controls: audio.controls,
                        autoplay: audio.autoplay,
                        loop: audio.loop,
                        muted: audio.muted,
                        index
                    }));
                    
                    // ===== LIENS =====
                    result.links = Array.from(document.querySelectorAll('a')).map((a, index) => ({
                        href: a.href || '',
                        text: a.textContent.trim(),
                        title: a.title || '',
                        target: a.target || '',
                        rel: a.rel || '',
                        download: a.download || '',
                        index
                    }));
                    
                    // ===== FICHIERS TÉLÉCHARGEABLES =====
                    result.files = Array.from(document.querySelectorAll('a[href]'))
                        .filter(a => {
                            const href = (a.href || '').toLowerCase();
                            return /\\.(pdf|doc|docx|xls|xlsx|ppt|pptx|zip|rar|7z|tar|gz|csv|txt|json|xml)$/.test(href);
                        })
                        .map((a, index) => ({
                            href: a.href || '',
                            text: a.textContent.trim(),
                            type: (a.href || '').split('.').pop().toLowerCase(),
                            download: a.download || '',
                            index
                        }));
                    
                    // ===== FORMULAIRES =====
                    result.forms = Array.from(document.querySelectorAll('form')).map((form, index) => ({
                        action: form.action || '',
                        method: form.method || 'get',
                        id: form.id || '',
                        name: form.name || '',
                        enctype: form.enctype || '',
                        inputs: Array.from(form.querySelectorAll('input, textarea, select')).map(input => ({
                            type: input.type || input.tagName.toLowerCase(),
                            name: input.name || '',
                            id: input.id || '',
                            placeholder: input.placeholder || '',
                            value: input.value || '',
                            required: input.required || false,
                            disabled: input.disabled || false,
                            readonly: input.readOnly || false
                        })),
                        buttons: Array.from(form.querySelectorAll('button')).map(btn => ({
                            type: btn.type || '',
                            text: btn.textContent.trim()
                        })),
                        index
                    }));
                    
                    // ===== TABLEAUX =====
                    result.tables = Array.from(document.querySelectorAll('table')).map((table, index) => ({
                        headers: Array.from(table.querySelectorAll('th')).map(th => th.textContent.trim()),
                        rows: Array.from(table.querySelectorAll('tr')).map(tr => 
                            Array.from(tr.querySelectorAll('td')).map(td => td.textContent.trim())
                        ).filter(row => row.length > 0),
                        caption: table.querySelector('caption')?.textContent.trim() || '',
                        index
                    }));
                    
                    // ===== DONNÉES STRUCTURÉES (JSON-LD, Schema.org) =====
                    result.structuredData = Array.from(document.querySelectorAll('script[type="application/ld+json"]'))
                        .map(script => {
                            try {
                                return JSON.parse(script.textContent);
                            } catch {
                                return null;
                            }
                        })
                        .filter(Boolean);
                    
                    // ===== SCRIPTS ET STYLES =====
                    result.scripts = Array.from(document.querySelectorAll('script[src]')).map(s => s.src);
                    result.styles = Array.from(document.querySelectorAll('link[rel="stylesheet"]')).map(l => l.href);
                    
                    return result;
                }
            """)
            
            # Ajouter l'URL de base pour les URLs relatives
            full_content['base_url'] = url
            
            # Calculer des statistiques
            summary = self._calculate_summary(full_content)
            
            return {
                'success': True,
                'data': full_content,
                'summary': summary,
                'url': url,
                'timestamp': asyncio.get_event_loop().time()
            }
            
        except PlaywrightTimeout:
            return {
                'success': False,
                'error': f'Timeout après {timeout_seconds}s',
                'url': url
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'url': url
            }
        finally:
            await page.close()
    
    async def _auto_scroll(self, page):
        """
        Scroller automatiquement pour charger le contenu lazy-loaded
        """
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
                            window.scrollTo(0, 0); // Retour en haut
                            resolve();
                        }
                    }, 100);
                });
            }
        """)
        await asyncio.sleep(1)
    
    def _calculate_summary(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Calculer un résumé des données extraites"""
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


# ===== TEST D'EXÉCUTION =====
async def main():
    """
    Test principal de la classe PlaywrightFetcher
    """
    print("🚀 TEST ULTRA-COMPLET - PlaywrightFetcher")
    print("=" * 60)
    
    fetcher = PlaywrightFetcher()
    
    test_sites = [
        {
            "name": "Site de test simple",
            "url": "https://httpbin.org/html",
            "use_scroll": False
        },
        {
            "name": "Site avec JavaScript",
            "url": "https://quotes.toscrape.com/js/",
            "use_scroll": True
        },
        {
            "name": "Site avec métadonnées",
            "url": "https://github.com",
            "use_scroll": False
        }
    ]
    
    try:
        for i, site in enumerate(test_sites, 1):
            print(f"\n🌟 TEST {i}: {site['name']}")
            print(f"URL: {site['url']}")
            print("-" * 40)
            
            result = await fetcher.extract_everything(
                url=site['url'],
                use_scroll=site['use_scroll'],
                timeout_seconds=25.0
            )
            
            if result['success']:
                summary = result['summary']
                print("✅ EXTRACTION RÉUSSIE !")
                print(f"   📝 Texte: {summary['total_text_length']:,} caractères")
                print(f"   🖼️  Images: {summary['media_found']['images']} (+{summary['media_found']['background_images']} background)")
                print(f"   🎥 Médias: {summary['media_found']['videos']} vidéos, {summary['media_found']['audios']} audios")
                print(f"   🔗 Liens: {summary['content_found']['links']}, Fichiers: {summary['content_found']['files']}")
                print(f"   📊 Formulaires: {summary['content_found']['forms']}, Tableaux: {summary['content_found']['tables']}")
                print(f"   📦 Données JSON-LD: {summary['content_found']['structured_data']}")
                
                metadata = result['data']['metadata']
                print(f"   📋 Titre: {metadata['title'][:60]}...")
                print(f"   🌐 Langue: {metadata['language'] or 'N/A'}")
            else:
                print(f"❌ Erreur: {result.get('error', 'Inconnue')}")
                
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        await fetcher.close()
        print("\n🎉 Tests terminés !")


if __name__ == "__main__":
    asyncio.run(main())