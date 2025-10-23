"""Parser for llms.txt format files."""

import re
from typing import List
from .base import BaseParser


class LlmsTxtParser(BaseParser):
    """Parser for llms.txt format (newline-separated URLs or markdown links)."""

    def parse(self, content: str) -> List[str]:
        """
        Parse llms.txt content and extract URLs.

        The llms.txt format supports:
        - Simple URLs: one URL per line
        - Markdown links: - [Title](URL)
        - Comments starting with # (but not markdown headers)

        Args:
            content: Raw llms.txt content

        Returns:
            List of URLs found in the file
        """
        urls = []

        for line in content.splitlines():
            line = line.strip()

            # Skip empty lines
            if not line:
                continue

            # Skip comment lines (but allow markdown headers for structure)
            if line.startswith("#") and not line.startswith("##"):
                continue

            # Extract URLs from markdown links: [text](url)
            markdown_links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', line)
            for title, url in markdown_links:
                if url.startswith("http://") or url.startswith("https://"):
                    urls.append(url)

            # Also check if line starts with a plain URL
            if line.startswith("http://") or line.startswith("https://"):
                urls.append(line)

        # Apply filters if configured
        return self.apply_filters(urls)
