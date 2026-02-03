import httpx


def fetch_html(url: str, timeout_seconds: float = 20.0) -> str:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    }

    with httpx.Client(
        follow_redirects=True, timeout=timeout_seconds, headers=headers
    ) as client:
        resp = client.get(url)
        resp.raise_for_status()
        return resp.text
