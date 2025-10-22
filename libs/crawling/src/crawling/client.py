# libs/crawling/src/crawling/client.py
import asyncio
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode

_browser_cfg = BrowserConfig(headless=True, verbose=False)
_run_cfg = CrawlerRunConfig(cache_mode=CacheMode.ENABLED, word_count_threshold=1)

async def fetch_markdown(url: str) -> str:
    async with AsyncWebCrawler(config=_browser_cfg) as crawler:
        r = await crawler.arun(url=url, config=_run_cfg)
        return r.markdown  # or r.markdown.fit_markdown

def fetch_markdown_sync(url: str) -> str:
    return asyncio.run(fetch_markdown(url))
