"""Parser for XML sitemap files."""

from typing import List
from lxml import etree
from .base import BaseParser
from ..logging_config import get_logger

logger = get_logger(__name__)


class XmlSitemapParser(BaseParser):
    """Parser for XML sitemap files with sitemap index support."""

    def parse(self, content: str) -> List[str]:
        """
        Parse XML sitemap content and extract URLs.

        Handles both regular sitemaps and sitemap indexes.
        For sitemap indexes, returns the list of sub-sitemaps.

        Args:
            content: Raw XML content

        Returns:
            List of URLs or sub-sitemap URLs
        """
        try:
            root = etree.fromstring(content.encode('utf-8'))
        except etree.XMLSyntaxError as e:
            logger.error("xml_parse_failed", error=str(e), exc_info=True)
            return []

        # Get namespace if present
        nsmap = root.nsmap
        default_ns = nsmap.get(None)

        urls = []

        # Check if this is a sitemap index
        if self._is_sitemap_index(root, default_ns):
            logger.info("parsing_sitemap_index", has_filters=bool(self.filters))
            urls = self._parse_sitemap_index(root, default_ns)
            if self.filters:
                logger.debug("filters_apply_to_subsitemaps", url_count=len(urls))
        else:
            logger.info("parsing_regular_sitemap", has_filters=bool(self.filters))
            urls = self._parse_regular_sitemap(root, default_ns)
            if self.filters:
                logger.debug("filters_apply_to_pages", url_count=len(urls))

        # Apply filters if configured
        return self.apply_filters(urls)

    def _is_sitemap_index(self, root, namespace: str = None) -> bool:
        """Check if XML is a sitemap index."""
        if namespace:
            sitemaps = root.findall(f"{{{namespace}}}sitemap")
        else:
            sitemaps = root.findall("sitemap")

        return len(sitemaps) > 0

    def _parse_sitemap_index(self, root, namespace: str = None) -> List[str]:
        """Parse a sitemap index and return sub-sitemap URLs."""
        urls = []

        if namespace:
            sitemaps = root.findall(f"{{{namespace}}}sitemap")
            for sitemap in sitemaps:
                loc = sitemap.find(f"{{{namespace}}}loc")
                if loc is not None and loc.text:
                    urls.append(loc.text.strip())
        else:
            sitemaps = root.findall("sitemap")
            for sitemap in sitemaps:
                loc = sitemap.find("loc")
                if loc is not None and loc.text:
                    urls.append(loc.text.strip())

        logger.debug("extracted_subsitemaps", count=len(urls), has_namespace=bool(namespace))
        return urls

    def _parse_regular_sitemap(self, root, namespace: str = None) -> List[str]:
        """Parse a regular sitemap and return page URLs."""
        urls = []

        if namespace:
            url_elements = root.findall(f"{{{namespace}}}url")
            for url_elem in url_elements:
                loc = url_elem.find(f"{{{namespace}}}loc")
                if loc is not None and loc.text:
                    urls.append(loc.text.strip())
        else:
            url_elements = root.findall("url")
            for url_elem in url_elements:
                loc = url_elem.find("loc")
                if loc is not None and loc.text:
                    urls.append(loc.text.strip())

        logger.debug("extracted_page_urls", count=len(urls), has_namespace=bool(namespace))
        return urls
