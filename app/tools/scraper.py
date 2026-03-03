import hashlib
from playwright.async_api import async_playwright
from app.tools.cache import get_cache, set_cache

MAX_CONTENT_LENGTH = 4000  # ~1k tokens per page, keeps total context manageable
MIN_USEFUL_LENGTH = 100  # skip pages that return errors / near-empty content


async def scrape_page(url: str) -> str:
    cache_key = "scrape:" + hashlib.md5(url.encode()).hexdigest()

    cached = await get_cache(cache_key)
    if cached:
        return cached

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        try:
            resp = await page.goto(url, timeout=15_000, wait_until="domcontentloaded")
            status = resp.status if resp else 0
            if status >= 400:
                content = ""
            else:
                content = await page.inner_text("body")
        except Exception:
            content = ""
        finally:
            await browser.close()

    content = content[:MAX_CONTENT_LENGTH]

    # Don't cache error pages or near-empty responses
    if len(content) >= MIN_USEFUL_LENGTH:
        await set_cache(cache_key, content, ttl=86400)
    else:
        content = ""

    return content
