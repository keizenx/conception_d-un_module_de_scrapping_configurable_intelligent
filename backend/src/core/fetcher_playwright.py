import asyncio
from typing import Optional
import httpx
from playwright.async_api import async_playwright, Browser, Page


_browser: Optional[Browser] = None


async def _get_browser() -> Browser:
    global _browser
    if _browser is None:
        playwright = await async_playwright().start()
        _browser = await playwright.chromium.launch(headless=True)
    return _browser


async def fetch_html_playwright(url: str, wait_for_selector: Optional[str] = None, timeout_seconds: float = 20.0) -> str:
    browser = await _get_browser()
    page: Page = await browser.new_page()
    
    try:
        await page.goto(url, wait_until="networkidle", timeout=int(timeout_seconds * 1000))
        
        if wait_for_selector:
            await page.wait_for_selector(wait_for_selector, timeout=int(timeout_seconds * 1000))
        else:
            await asyncio.sleep(2)
        
        html = await page.content()
        return html
    finally:
        await page.close()


def fetch_html_with_js(url: str, wait_for_selector: Optional[str] = None, timeout_seconds: float = 20.0) -> str:
    return asyncio.run(fetch_html_playwright(url, wait_for_selector, timeout_seconds))


def fetch_html_smart(url: str, use_js: bool = False, wait_for_selector: Optional[str] = None, timeout_seconds: float = 20.0) -> str:
    if use_js:
        return fetch_html_with_js(url, wait_for_selector, timeout_seconds)
    else:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        }
        
        with httpx.Client(follow_redirects=True, timeout=timeout_seconds, headers=headers) as client:
            resp = client.get(url)
            resp.raise_for_status()
            return resp.text
