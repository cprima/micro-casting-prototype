# libs/crawling/src/crawling/client.py
"""
Minimal wrapper around crawl4ai for version pinning.

This library's ONLY purpose is to pin crawl4ai to a specific version (0.7.6).
All configuration should be done by the calling application, NOT hardcoded here.
"""
import asyncio
import logging
import os
from contextlib import redirect_stderr, redirect_stdout

# Re-export crawl4ai types for applications to use
from crawl4ai import (
    AsyncWebCrawler,
    BrowserConfig,
    CrawlerRunConfig,
    CacheMode,
    CrawlResult
)

# Suppress Crawl4AI's internal logger to avoid Windows encoding issues
logging.getLogger("crawl4ai").setLevel(logging.CRITICAL)


async def fetch(
    url: str,
    browser_config: BrowserConfig,
    run_config: CrawlerRunConfig
) -> CrawlResult:
    """
    Fetch content from URL using Crawl4AI.

    Args:
        url: URL to fetch
        browser_config: BrowserConfig instance (configured by application)
        run_config: CrawlerRunConfig instance (configured by application)

    Returns:
        CrawlResult with full metadata (markdown, response_headers, status_code, etc.)
    """
    # Suppress all output from Crawl4AI to avoid Windows Unicode errors
    devnull = open(os.devnull, 'w', encoding='utf-8')
    try:
        with redirect_stdout(devnull), redirect_stderr(devnull):
            async with AsyncWebCrawler(config=browser_config) as crawler:
                result = await crawler.arun(url=url, config=run_config)
        return result
    finally:
        devnull.close()


def fetch_sync(
    url: str,
    browser_config: BrowserConfig,
    run_config: CrawlerRunConfig
) -> CrawlResult:
    """
    Synchronous wrapper for fetch().

    Args:
        url: URL to fetch
        browser_config: BrowserConfig instance (configured by application)
        run_config: CrawlerRunConfig instance (configured by application)

    Returns:
        CrawlResult with full metadata (markdown, response_headers, status_code, etc.)
    """
    return asyncio.run(fetch(url, browser_config, run_config))
