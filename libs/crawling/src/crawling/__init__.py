"""
Minimal wrapper library for crawl4ai version pinning.

This library pins crawl4ai to version 0.7.6 and provides minimal wrappers.
All configuration is the responsibility of the calling application.
"""

from .client import (
    fetch,
    fetch_sync,
    # Re-export crawl4ai types
    AsyncWebCrawler,
    BrowserConfig,
    CrawlerRunConfig,
    CacheMode,
    CrawlResult
)

__all__ = [
    "fetch",
    "fetch_sync",
    "AsyncWebCrawler",
    "BrowserConfig",
    "CrawlerRunConfig",
    "CacheMode",
    "CrawlResult"
]
