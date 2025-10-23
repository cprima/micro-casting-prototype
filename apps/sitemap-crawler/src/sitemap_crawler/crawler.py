"""Main crawler orchestration."""

import requests
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List
from urllib.parse import urlparse
from tqdm import tqdm

from crawling import fetch_sync
from .parsers import LlmsTxtParser, XmlSitemapParser, DirectUrlParser
from .storage import LocalStorage
from .logging_config import get_logger, bind_context, unbind_context
from .correlation import set_correlation_id
from .metrics import CrawlMetrics, track_request, track_operation
from .resilience import RetryHandler, RateLimiter
from .robots import RobotsHandler

logger = get_logger(__name__)


class SitemapCrawler:
    """Main crawler that orchestrates sitemap parsing and content fetching."""

    def __init__(
        self,
        config: Dict[str, Any],
        storage: LocalStorage,
        dry_run: bool = False,
        retry_config: Dict[str, Any] = None,
        rate_limit_config: Dict[str, Any] = None,
        http_config: Dict[str, Any] = None,
        limits_config: Dict[str, Any] = None,
        robots_config: Dict[str, Any] = None,
        browser_config = None
    ):
        """
        Initialize crawler.

        Args:
            config: Site configuration dictionary
            storage: Storage backend
            dry_run: If True, only list URLs without crawling
            retry_config: Retry configuration
            rate_limit_config: Rate limiting configuration
            http_config: HTTP configuration (user-agent, timeouts)
            limits_config: Resource limits configuration
            robots_config: robots.txt compliance configuration
            browser_config: BrowserConfig instance for crawl4ai
        """
        self.config = config
        self.storage = storage
        self.dry_run = dry_run
        self.metrics = CrawlMetrics()

        # Initialize resilience components
        self.retry_handler = RetryHandler(retry_config or {})
        self.rate_limiter = RateLimiter(rate_limit_config or {})
        self.http_config = http_config or {}
        self.limits_config = limits_config or {}

        # Initialize robots.txt handler
        user_agent = http_config.get("user_agent", "sitemap-crawler/0.2.0") if http_config else "sitemap-crawler/0.2.0"
        self.robots_handler = RobotsHandler(robots_config or {}, user_agent=user_agent)

        # Store browser config for crawl4ai
        self.browser_config = browser_config

        # Track resource usage
        self.crawl_start_time = None
        self.total_bytes_downloaded = 0

        # Track filename collisions
        self.used_filenames: Dict[str, int] = {}

    def crawl(self) -> Dict[str, int]:
        """
        Execute the crawl for the configured site.

        Returns:
            Statistics dictionary
        """
        site_name = self.config.get('name')

        # Set correlation ID for this crawl session
        correlation_id = set_correlation_id()
        bind_context(site=site_name)

        # Track start time for duration limits
        self.crawl_start_time = datetime.now()

        logger.info("crawl_started", site=site_name, dry_run=self.dry_run)

        try:
            # Fetch and parse sitemap
            urls = self._get_urls()

            # Apply max URLs limit
            max_urls = self.limits_config.get("max_urls_per_site", 0)
            if max_urls > 0 and len(urls) > max_urls:
                logger.warning(
                    "url_limit_exceeded",
                    total_urls=len(urls),
                    max_urls=max_urls,
                    urls_kept=max_urls
                )
                urls = urls[:max_urls]

            self.metrics.urls_total = len(urls)

            if self.dry_run:
                logger.info("dry_run_urls_found", url_count=len(urls))
                for url in urls:
                    print(f"  - {url}")
                return self.metrics.to_dict()

            # Crawl each URL with progress bar
            progress_bar = tqdm(
                urls,
                desc=f"Crawling {site_name}",
                unit="url",
                bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]'
            )

            for url in progress_bar:
                # Check duration limit
                if self._check_duration_limit():
                    logger.warning("crawl_duration_limit_reached")
                    break

                # Check total size limit
                if self._check_size_limit():
                    logger.warning("crawl_size_limit_reached")
                    break

                # Check robots.txt compliance
                if not self.robots_handler.is_allowed(url):
                    logger.info("url_skipped_robots_disallow", url=url)
                    self.metrics.urls_skipped += 1
                    continue

                # Update progress bar description with current URL
                short_url = url[:60] + "..." if len(url) > 60 else url
                progress_bar.set_postfix_str(short_url, refresh=False)

                logger.info("crawling_url", url=url)
                try:
                    self._crawl_url(url)
                except Exception as e:
                    logger.error("url_crawl_failed", url=url, error=str(e), exc_info=True)
                    self.metrics.record_failure()

            self.metrics.finish()
            self.metrics.log_summary()

            logger.info("crawl_completed", site=site_name)
            return self.metrics.to_dict()

        finally:
            unbind_context("site")

    def _get_urls(self) -> List[str]:
        """Fetch sitemap and extract URLs."""
        source_url = self.config.get("source")
        sitemap_type = self.config.get("type")
        filters = self.config.get("filters", [])

        # For direct URLs, no fetch needed - source IS the content
        if sitemap_type == "direct_url":
            logger.info("parsing_direct_urls", type=sitemap_type)
            parser = DirectUrlParser(filters=filters)
            urls = parser.parse(source_url)  # source_url is the actual URL(s), not a URL to fetch
            logger.info("urls_extracted", url_count=len(urls), sitemap_type=sitemap_type)
            return urls

        # For sitemaps, fetch the content
        logger.info("fetching_sitemap", url=source_url, type=sitemap_type)

        with track_request(source_url) as metrics:
            # Rate limiting
            self.rate_limiter.wait_if_needed()

            # Fetch with retry logic
            def fetch_sitemap():
                response = requests.get(
                    source_url,
                    headers=self._get_request_headers(),
                    timeout=self._get_request_timeout()
                )
                response.raise_for_status()
                return response

            response = self.retry_handler.execute_with_retry(fetch_sitemap)
            metrics["status_code"] = response.status_code
            metrics["content_length"] = len(response.content)

        content = response.text

        # Save the raw sitemap
        self._save_sitemap(content)

        # Parse based on type
        if sitemap_type == "llms.txt":
            parser = LlmsTxtParser(filters=filters)
            urls = parser.parse(content)
        elif sitemap_type == "xml_sitemap":
            urls = self._parse_xml_sitemap_recursive(source_url, content, filters)
        else:
            raise ValueError(f"Unknown sitemap type: {sitemap_type}")

        logger.info("urls_extracted", url_count=len(urls), sitemap_type=sitemap_type)
        return urls

    def _parse_xml_sitemap_recursive(self, url: str, content: str, filters: List[Dict[str, Any]]) -> List[str]:
        """
        Recursively parse XML sitemap, handling sitemap indexes.

        Args:
            url: URL of the sitemap
            content: Sitemap content
            filters: URL filters (applied only to sitemap indexes, not page URLs)

        Returns:
            List of page URLs
        """
        parser = XmlSitemapParser(filters=filters)
        urls = parser.parse(content)

        # Check if these are sub-sitemaps or final URLs
        if urls and self._is_sitemap_url(urls[0]):
            logger.info("sitemap_index_found", sub_sitemap_count=len(urls))
            all_urls = []

            for i, sub_url in enumerate(urls, 1):
                logger.info("fetching_sub_sitemap", url=sub_url, progress=f"{i}/{len(urls)}")
                try:
                    with track_request(sub_url) as metrics:
                        # Rate limiting
                        self.rate_limiter.wait_if_needed()

                        # Fetch with retry logic
                        def fetch_sub_sitemap():
                            response = requests.get(
                                sub_url,
                                headers=self._get_request_headers(),
                                timeout=self._get_request_timeout()
                            )
                            response.raise_for_status()
                            return response

                        response = self.retry_handler.execute_with_retry(fetch_sub_sitemap)
                        metrics["status_code"] = response.status_code
                        metrics["content_length"] = len(response.content)

                    # Don't pass filters to sub-sitemaps - filters only apply to sitemap index
                    sub_urls = self._parse_xml_sitemap_recursive(sub_url, response.text, filters=[])
                    all_urls.extend(sub_urls)
                    logger.debug("sub_sitemap_parsed", url=sub_url, url_count=len(sub_urls))
                except Exception as e:
                    logger.error("sub_sitemap_fetch_failed", url=sub_url, error=str(e), exc_info=True)

            return all_urls
        else:
            return urls

    def _is_sitemap_url(self, url: str) -> bool:
        """Check if a URL points to a sitemap file."""
        return "sitemap" in url.lower() and url.endswith(".xml")

    def _save_sitemap(self, content: str) -> None:
        """Save the raw sitemap file."""
        output_pattern = self.config.get("output_pattern", "{domain}")
        domain = self.config.get("domain")

        # Expand pattern
        output_dir = output_pattern.format(
            domain=domain,
            date=datetime.now().strftime("%Y-%m-%d")
        )

        # Determine filename based on type
        sitemap_type = self.config.get("type")
        if sitemap_type == "llms.txt":
            filename = "llms.txt"
        else:
            filename = "sitemap.xml"

        path = f"{output_dir}/{filename}"
        self.storage.write(path, content)
        logger.info("sitemap_saved", path=path, size_bytes=len(content))

    def _crawl_url(self, url: str) -> None:
        """
        Crawl a single URL and save its content.

        Args:
            url: URL to crawl
        """
        import time

        with track_operation("crawl_url", url=url):
            # Check for robots.txt crawl-delay directive
            robots_delay = self.robots_handler.get_crawl_delay(url)
            if robots_delay is not None:
                # robots.txt crawl-delay takes precedence over configured rate limit
                logger.debug(
                    "using_robots_crawl_delay",
                    url=url,
                    delay_seconds=robots_delay
                )
                time.sleep(robots_delay)
            else:
                # Use configured rate limiting
                self.rate_limiter.wait_if_needed()

            # Build CrawlerRunConfig for this site
            run_config = self._build_run_config()

            # Fetch content using crawling library (returns full CrawlResult)
            result = fetch_sync(url, self.browser_config, run_config)

            # Extract markdown from result
            markdown = str(result.markdown) if result.markdown else ""

            # Validate content
            if not self._validate_content(markdown, url):
                self.metrics.record_failure()
                return

            # Generate filename from URL
            filename = self._url_to_filename(url)

            # Get output directory
            output_pattern = self.config.get("output_pattern", "{domain}")
            domain = self.config.get("domain")
            output_dir = output_pattern.format(
                domain=domain,
                date=datetime.now().strftime("%Y-%m-%d")
            )

            # Save content
            path = f"{output_dir}/{filename}"
            self.storage.write(path, markdown)

            # Record metrics and track total bytes
            content_size = len(markdown)
            self.total_bytes_downloaded += content_size
            self.metrics.record_success(content_size)

            logger.debug("url_saved", url=url, path=path, size_bytes=content_size)

    def _url_to_filename(self, url: str) -> str:
        """
        Convert URL to a safe filename with collision detection and path length handling.

        Args:
            url: URL to convert

        Returns:
            Safe, unique filename
        """
        parsed = urlparse(url)
        path = parsed.path.strip("/")

        # Generate base filename
        if not path:
            base_filename = "index"
        else:
            # Replace slashes with underscores
            base_filename = path.replace("/", "_")

        # Remove .md extension if present (we'll add it later)
        if base_filename.endswith(".md"):
            base_filename = base_filename[:-3]

        # Sanitize the filename (remove special characters)
        base_filename = self.storage.sanitize_filename(base_filename)

        # Handle extremely long filenames (Windows MAX_PATH = 260, leave room for path)
        # Typical pattern: base_dir/domain/filename.md
        # Reserve ~200 chars for base path, leaving ~60 for filename
        max_filename_length = 60

        if len(base_filename) > max_filename_length:
            # Use hash-based filename for very long URLs
            url_hash = hashlib.md5(url.encode()).hexdigest()[:8]
            # Keep first part of filename + hash
            truncated = base_filename[:40]
            base_filename = f"{truncated}_{url_hash}"
            logger.debug(
                "filename_truncated",
                url=url,
                original_length=len(path),
                new_filename=base_filename
            )

        # Handle filename collisions
        filename = base_filename
        if filename in self.used_filenames:
            # Collision detected
            self.used_filenames[filename] += 1
            counter = self.used_filenames[filename]
            filename = f"{base_filename}-{counter}"
            logger.debug(
                "filename_collision",
                original=base_filename,
                new_filename=filename,
                collision_count=counter
            )
        else:
            self.used_filenames[filename] = 0

        # Add .md extension
        filename += ".md"

        return filename

    def _get_request_headers(self) -> Dict[str, str]:
        """
        Get HTTP request headers.

        Returns:
            Headers dictionary
        """
        user_agent = self.http_config.get("user_agent", "sitemap-crawler/0.2.0")
        return {
            "User-Agent": user_agent,
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate"
        }

    def _get_request_timeout(self) -> float:
        """
        Get HTTP request timeout.

        Returns:
            Timeout in seconds
        """
        timeout_config = self.http_config.get("timeout", {})
        return timeout_config.get("total", 60.0)

    def _check_duration_limit(self) -> bool:
        """
        Check if crawl duration limit has been exceeded.

        Returns:
            True if limit exceeded, False otherwise
        """
        max_duration = self.limits_config.get("max_crawl_duration", 0)
        if max_duration <= 0 or self.crawl_start_time is None:
            return False

        elapsed = (datetime.now() - self.crawl_start_time).total_seconds()
        return elapsed >= max_duration

    def _check_size_limit(self) -> bool:
        """
        Check if total size limit has been exceeded.

        Returns:
            True if limit exceeded, False otherwise
        """
        max_size_mb = self.limits_config.get("max_total_size_mb", 0)
        if max_size_mb <= 0:
            return False

        current_mb = self.total_bytes_downloaded / (1024 * 1024)
        return current_mb >= max_size_mb

    def _validate_content(self, content: str, url: str) -> bool:
        """
        Validate content before saving.

        Args:
            content: Content to validate
            url: URL of the content (for logging)

        Returns:
            True if content is valid, False otherwise
        """
        # Check minimum content length
        min_chars = self.limits_config.get("min_content_chars", 100)
        if len(content) < min_chars:
            logger.warning(
                "content_too_short",
                url=url,
                content_length=len(content),
                min_required=min_chars
            )
            return False

        # Check if content appears to be empty/minimal
        stripped = content.strip()
        if not stripped:
            logger.warning("content_empty", url=url)
            return False

        return True

    def _build_run_config(self):
        """
        Build CrawlerRunConfig from site configuration.

        Uses site-specific crawl4ai settings with defaults.

        Returns:
            CrawlerRunConfig instance
        """
        from crawling import CrawlerRunConfig, CacheMode
        from crawl4ai.content_filter_strategy import PruningContentFilter
        from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator

        # Get site-specific crawl4ai config
        site_crawl_config = self.config.get("crawl4ai", {})

        # Parse cache_mode
        cache_mode_str = site_crawl_config.get("cache_mode", "enabled").upper()
        if cache_mode_str == "BYPASS":
            cache_mode = CacheMode.BYPASS
        elif cache_mode_str == "DISABLED":
            cache_mode = CacheMode.DISABLED
        elif cache_mode_str == "READ_ONLY":
            cache_mode = CacheMode.READ_ONLY
        elif cache_mode_str == "WRITE_ONLY":
            cache_mode = CacheMode.WRITE_ONLY
        else:
            cache_mode = CacheMode.ENABLED

        # Build pruning filter from config (if specified)
        pruning_config = site_crawl_config.get("pruning")
        if pruning_config:
            prune_filter = PruningContentFilter(
                threshold=pruning_config.get("threshold", 0.48),
                threshold_type=pruning_config.get("threshold_type", "dynamic"),
                min_word_threshold=pruning_config.get("min_word_threshold", 5)
            )
            md_generator = DefaultMarkdownGenerator(content_filter=prune_filter)
        else:
            # No pruning configured - use simple markdown generator
            md_generator = DefaultMarkdownGenerator()

        # Build CrawlerRunConfig
        return CrawlerRunConfig(
            cache_mode=cache_mode,
            markdown_generator=md_generator,
            # CSS selection
            css_selector=site_crawl_config.get("css_selector"),
            target_elements=site_crawl_config.get("target_elements"),
            # Content filtering
            excluded_tags=site_crawl_config.get("excluded_tags"),
            word_count_threshold=site_crawl_config.get("word_count_threshold"),
            exclude_external_links=site_crawl_config.get("exclude_external_links", False),
            exclude_social_media_links=site_crawl_config.get("exclude_social_media_links", False),
            exclude_external_images=site_crawl_config.get("exclude_external_images", False)
        )
