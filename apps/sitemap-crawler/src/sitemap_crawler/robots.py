"""robots.txt compliance handler."""

import time
from typing import Dict, Optional
from urllib.parse import urlparse, urljoin
from urllib.robotparser import RobotFileParser
import requests
from .logging_config import get_logger

logger = get_logger(__name__)


class RobotsHandler:
    """Handle robots.txt fetching, parsing, and compliance checking."""

    def __init__(self, config: Dict[str, any], user_agent: str = "sitemap-crawler/0.2.0"):
        """
        Initialize robots.txt handler.

        Args:
            config: robots.txt configuration dict
            user_agent: User-Agent string to use for robots.txt checks
        """
        self.enabled = config.get("enabled", True)
        self.user_agent = user_agent
        self.cache_duration = config.get("cache_duration", 3600)  # 1 hour default
        self.respect_crawl_delay = config.get("respect_crawl_delay", True)

        # Cache: domain -> (parser, fetch_time)
        self._cache: Dict[str, tuple[RobotFileParser, float]] = {}

    def is_allowed(self, url: str) -> bool:
        """
        Check if URL is allowed by robots.txt.

        Args:
            url: URL to check

        Returns:
            True if allowed, False if disallowed
        """
        if not self.enabled:
            return True

        try:
            parser = self._get_parser_for_url(url)
            if parser is None:
                # If no robots.txt or error fetching, allow by default
                return True

            allowed = parser.can_fetch(self.user_agent, url)

            if not allowed:
                logger.info(
                    "url_disallowed_by_robots",
                    url=url,
                    user_agent=self.user_agent
                )

            return allowed

        except Exception as e:
            logger.warning(
                "robots_check_error",
                url=url,
                error=str(e)
            )
            # On error, allow by default
            return True

    def get_crawl_delay(self, url: str) -> Optional[float]:
        """
        Get crawl-delay directive from robots.txt.

        Args:
            url: URL to get crawl delay for

        Returns:
            Crawl delay in seconds, or None if not specified
        """
        if not self.enabled or not self.respect_crawl_delay:
            return None

        try:
            parser = self._get_parser_for_url(url)
            if parser is None:
                return None

            # Get crawl delay for our user agent
            delay = parser.crawl_delay(self.user_agent)

            if delay is not None:
                logger.debug(
                    "robots_crawl_delay",
                    url=url,
                    delay_seconds=delay
                )

            return delay

        except Exception as e:
            logger.warning(
                "robots_crawl_delay_error",
                url=url,
                error=str(e)
            )
            return None

    def _get_parser_for_url(self, url: str) -> Optional[RobotFileParser]:
        """
        Get (cached) robots.txt parser for URL's domain.

        Args:
            url: URL to get parser for

        Returns:
            RobotFileParser or None if unavailable
        """
        parsed = urlparse(url)
        domain = f"{parsed.scheme}://{parsed.netloc}"

        # Check cache
        if domain in self._cache:
            parser, fetch_time = self._cache[domain]

            # Check if cache is still valid
            if time.time() - fetch_time < self.cache_duration:
                return parser
            else:
                logger.debug("robots_cache_expired", domain=domain)

        # Fetch and parse robots.txt
        robots_url = urljoin(domain, "/robots.txt")
        parser = self._fetch_robots(robots_url, domain)

        if parser is not None:
            self._cache[domain] = (parser, time.time())

        return parser

    def _fetch_robots(self, robots_url: str, domain: str) -> Optional[RobotFileParser]:
        """
        Fetch and parse robots.txt file.

        Args:
            robots_url: URL of robots.txt
            domain: Domain name (for logging)

        Returns:
            RobotFileParser or None if unavailable
        """
        try:
            logger.debug("fetching_robots_txt", url=robots_url)

            response = requests.get(
                robots_url,
                timeout=10,
                headers={"User-Agent": self.user_agent}
            )

            # 404 is acceptable - means no robots.txt
            if response.status_code == 404:
                logger.debug("robots_txt_not_found", domain=domain)
                # Create empty parser (allows everything)
                parser = RobotFileParser()
                parser.parse([])
                return parser

            response.raise_for_status()

            # Parse robots.txt content
            parser = RobotFileParser()
            parser.parse(response.text.splitlines())

            logger.info(
                "robots_txt_fetched",
                domain=domain,
                size_bytes=len(response.content)
            )

            return parser

        except requests.RequestException as e:
            logger.warning(
                "robots_txt_fetch_failed",
                domain=domain,
                error=str(e)
            )
            return None
        except Exception as e:
            logger.error(
                "robots_txt_parse_error",
                domain=domain,
                error=str(e),
                exc_info=True
            )
            return None

    def clear_cache(self):
        """Clear robots.txt cache."""
        self._cache.clear()
        logger.debug("robots_cache_cleared")
