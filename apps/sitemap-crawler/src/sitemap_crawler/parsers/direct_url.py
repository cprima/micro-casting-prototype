"""Parser for direct URL lists."""

from typing import List
from .base import BaseParser
from ..logging_config import get_logger

logger = get_logger(__name__)


class DirectUrlParser(BaseParser):
    """
    Parser for direct URL input (not sitemaps).

    Supports:
    - Single URL: "https://example.com/page"
    - Multiple URLs: newline-separated list
    """

    def parse(self, content: str) -> List[str]:
        """
        Parse direct URL content.

        Args:
            content: Single URL or newline-separated URLs

        Returns:
            List of URLs found
        """
        urls = []

        for line in content.splitlines():
            line = line.strip()

            # Skip empty lines
            if not line:
                continue

            # Skip comments
            if line.startswith("#"):
                continue

            # Validate it looks like a URL
            if line.startswith("http://") or line.startswith("https://"):
                urls.append(line)
            else:
                logger.warning("invalid_url_skipped", url=line, reason="Does not start with http:// or https://")

        logger.info("direct_urls_parsed", url_count=len(urls))

        # Apply filters if configured
        return self.apply_filters(urls)
