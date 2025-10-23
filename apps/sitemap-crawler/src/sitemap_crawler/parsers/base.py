"""Base parser interface for sitemap formats."""

from abc import ABC, abstractmethod
from typing import List, Dict, Any

from ..logging_config import get_logger

logger = get_logger(__name__)


class BaseParser(ABC):
    """Abstract base class for sitemap parsers."""

    def __init__(self, filters: List[Dict[str, Any]] = None):
        """
        Initialize parser with optional filters.

        Args:
            filters: List of filter dictionaries with 'type' and filter-specific keys
        """
        self.filters = filters or []

    @abstractmethod
    def parse(self, content: str) -> List[str]:
        """
        Parse sitemap content and return list of URLs.

        Args:
            content: Raw sitemap content

        Returns:
            List of URLs extracted from the sitemap
        """
        pass

    def apply_filters(self, urls: List[str]) -> List[str]:
        """
        Apply configured filters to URL list.

        Args:
            urls: List of URLs to filter

        Returns:
            Filtered list of URLs
        """
        if not self.filters:
            logger.debug("no_filters_configured", url_count=len(urls))
            return urls

        logger.info("applying_filters", filter_count=len(self.filters), url_count=len(urls))
        filtered = urls

        for i, filter_config in enumerate(self.filters, 1):
            filter_type = filter_config.get("type")
            before_count = len(filtered)

            if filter_type == "url_pattern":
                pattern = filter_config.get("pattern", "")
                filtered = [url for url in filtered if pattern in url]
                after_count = len(filtered)
                removed_count = before_count - after_count
                logger.info(
                    "filter_applied",
                    filter_index=i,
                    filter_total=len(self.filters),
                    filter_type="url_pattern",
                    pattern=pattern,
                    before=before_count,
                    after=after_count,
                    removed=removed_count
                )

            elif filter_type == "url_contains":
                value = filter_config.get("value", "")
                filtered = [url for url in filtered if value in url]
                after_count = len(filtered)
                removed_count = before_count - after_count
                logger.info(
                    "filter_applied",
                    filter_index=i,
                    filter_total=len(self.filters),
                    filter_type="url_contains",
                    value=value,
                    before=before_count,
                    after=after_count,
                    removed=removed_count
                )

        kept_count = len(filtered)
        removed_total = len(urls) - kept_count
        logger.info(
            "filtering_complete",
            original_count=len(urls),
            kept_count=kept_count,
            removed_total=removed_total
        )

        return filtered
