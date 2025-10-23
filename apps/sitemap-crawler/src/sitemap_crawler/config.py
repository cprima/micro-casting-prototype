"""Configuration loading and management."""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, List
from urllib.parse import urlparse


class Config:
    """Configuration manager for sitemap crawler."""

    def __init__(self, config_path: str = "config.yaml"):
        """
        Load configuration from YAML file.

        Args:
            config_path: Path to config.yaml file
        """
        self.config_path = Path(config_path)
        self.data = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """Load and parse YAML config file."""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Config file not found: {self.config_path}")

        with open(self.config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)

        # Expand environment variables in config
        config = self._expand_env_vars(config)

        return config

    def _expand_env_vars(self, obj: Any) -> Any:
        """
        Recursively expand environment variables in config.

        Supports ${VAR_NAME} syntax.
        """
        if isinstance(obj, dict):
            return {k: self._expand_env_vars(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._expand_env_vars(item) for item in obj]
        elif isinstance(obj, str):
            # Expand ${VAR} patterns
            if "${" in obj:
                import re
                pattern = r'\$\{([^}]+)\}'
                matches = re.findall(pattern, obj)
                for var_name in matches:
                    var_value = os.environ.get(var_name, "")
                    obj = obj.replace(f"${{{var_name}}}", var_value)
            return obj
        else:
            return obj

    def _auto_detect_type(self, source: str) -> str:
        """
        Auto-detect sitemap type from source URL.

        Args:
            source: Source URL or content

        Returns:
            Detected type: llms.txt, xml_sitemap, or direct_url
        """
        source_lower = source.lower().strip()

        # Check for llms.txt
        if source_lower.endswith(".txt") or "llms.txt" in source_lower:
            return "llms.txt"

        # Check for XML sitemap
        if source_lower.endswith(".xml") or "sitemap" in source_lower:
            return "xml_sitemap"

        # Default: treat as direct URL(s)
        return "direct_url"

    def _auto_extract_domain(self, source: str) -> str:
        """
        Auto-extract domain from source URL.

        Args:
            source: Source URL (single or multiline)

        Returns:
            Extracted domain name
        """
        # Get first non-empty line
        first_url = None
        for line in source.splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                first_url = line
                break

        if not first_url:
            return "unknown"

        # Parse domain from URL
        try:
            parsed = urlparse(first_url)
            return parsed.netloc
        except Exception:
            return "unknown"

    def get_base_output_dir(self) -> str:
        """
        Get base output directory.

        Checks environment variable BASE_OUTPUT_DIR first,
        falls back to config file setting.
        """
        # Environment variable takes precedence
        env_dir = os.environ.get("BASE_OUTPUT_DIR")
        if env_dir:
            return env_dir

        # Fall back to config file
        return self.data.get("settings", {}).get("base_output_dir", "./docs")

    def get_sites(self) -> List[Dict[str, Any]]:
        """
        Get list of configured sites with auto-detection applied.

        Auto-fills missing 'type' and 'domain' fields:
        - type: auto-detected from source URL
        - domain: auto-extracted from first URL in source
        """
        sites = self.data.get("sites", [])

        # Apply auto-detection to each site
        for site in sites:
            source = site.get("source", "")

            # Auto-detect type if not specified
            if "type" not in site and source:
                site["type"] = self._auto_detect_type(source)

            # Auto-extract domain if not specified
            if "domain" not in site and source:
                site["domain"] = self._auto_extract_domain(source)

        return sites

    def get_site_by_name(self, name: str) -> Dict[str, Any]:
        """
        Get site configuration by name.

        Args:
            name: Site name

        Returns:
            Site configuration dict

        Raises:
            ValueError: If site not found
        """
        sites = self.get_sites()
        for site in sites:
            if site.get("name") == name:
                return site

        raise ValueError(f"Site not found: {name}")

    def get_storage_backend(self) -> str:
        """Get configured storage backend type."""
        return self.data.get("settings", {}).get("storage_backend", "local")

    def get_site_base_dir(self, site_config: Dict[str, Any]) -> str:
        """
        Get base output directory for a specific site.

        Checks in this order:
        1. Site's base_dir field (highest priority)
        2. BASE_OUTPUT_DIR environment variable
        3. Global base_output_dir setting (fallback)

        Args:
            site_config: Site configuration dictionary

        Returns:
            Base directory path for this site
        """
        # Check if site has its own base_dir override
        if "base_dir" in site_config:
            return site_config["base_dir"]

        # Fall back to global base output dir (which checks env var)
        return self.get_base_output_dir()

    def get_retry_config(self) -> Dict[str, Any]:
        """
        Get retry configuration.

        Returns:
            Retry configuration dict with defaults
        """
        defaults = {
            "max_retries": 3,
            "initial_backoff": 1.0,
            "backoff_multiplier": 2.0,
            "max_backoff": 60.0,
            "retry_on_status": [500, 502, 503, 504, 429]
        }
        settings = self.data.get("settings", {})
        retry = settings.get("retry", {})

        # Merge with defaults
        return {**defaults, **retry}

    def get_rate_limit_config(self) -> Dict[str, Any]:
        """
        Get rate limiting configuration.

        Returns:
            Rate limit configuration dict with defaults
        """
        defaults = {
            "requests_per_second": 1.0,
            "delay_between_requests": 1.0,
            "respect_429": True
        }
        settings = self.data.get("settings", {})
        rate_limit = settings.get("rate_limit", {})

        # Merge with defaults
        return {**defaults, **rate_limit}

    def get_http_config(self) -> Dict[str, Any]:
        """
        Get HTTP configuration.

        Returns:
            HTTP configuration dict with defaults
        """
        defaults = {
            "user_agent": "sitemap-crawler/0.2.0",
            "timeout": {
                "connect": 10.0,
                "read": 30.0,
                "total": 60.0
            }
        }
        settings = self.data.get("settings", {})
        http = settings.get("http", {})

        # Merge with defaults
        result = {**defaults, **http}

        # Ensure timeout dict is merged properly
        if "timeout" in http:
            result["timeout"] = {**defaults["timeout"], **http["timeout"]}

        return result

    def get_limits_config(self) -> Dict[str, Any]:
        """
        Get resource limits configuration.

        Returns:
            Resource limits configuration dict with defaults
        """
        defaults = {
            "max_urls_per_site": 50000,
            "max_file_size_mb": 10.0,
            "max_total_size_mb": 5000.0,
            "max_crawl_duration": 0,
            "min_content_chars": 100
        }
        settings = self.data.get("settings", {})
        limits = settings.get("limits", {})

        # Merge with defaults
        return {**defaults, **limits}

    def get_robots_config(self) -> Dict[str, Any]:
        """
        Get robots.txt compliance configuration.

        Returns:
            robots.txt configuration dict with defaults
        """
        defaults = {
            "enabled": True,
            "respect_crawl_delay": True,
            "cache_duration": 3600
        }
        settings = self.data.get("settings", {})
        robots = settings.get("robots", {})

        # Merge with defaults
        return {**defaults, **robots}

    def get_browser_config(self):
        """
        Get BrowserConfig for crawl4ai.

        Returns:
            BrowserConfig instance configured from settings
        """
        from crawling import BrowserConfig

        defaults = {
            "headless": True,
            "verbose": False,
            "user_agent": None,
            "viewport_width": 1080,
            "viewport_height": 600
        }
        settings = self.data.get("settings", {})
        browser = settings.get("browser", {})

        # Merge with defaults
        config = {**defaults, **browser}

        # Build BrowserConfig
        return BrowserConfig(
            headless=config["headless"],
            verbose=config["verbose"],
            user_agent=config.get("user_agent"),
            viewport_width=config["viewport_width"],
            viewport_height=config["viewport_height"]
        )

    def get_run_config(self, site_config: Dict[str, Any]):
        """
        Get CrawlerRunConfig for a specific site.

        Combines global crawl_defaults with per-site crawl4ai overrides.

        Args:
            site_config: Site configuration dictionary

        Returns:
            CrawlerRunConfig instance
        """
        from crawling import CrawlerRunConfig, CacheMode
        from crawl4ai.content_filter_strategy import PruningContentFilter
        from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator

        # Get global defaults
        settings = self.data.get("settings", {})
        crawl_defaults = settings.get("crawl_defaults", {})

        # Get site-specific overrides
        site_crawl_config = site_config.get("crawl4ai", {})

        # Merge: site overrides take precedence
        merged = {**crawl_defaults, **site_crawl_config}

        # Parse cache_mode
        cache_mode_str = merged.get("cache_mode", "enabled").upper()
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

        # Build pruning filter from config
        pruning_config = merged.get("pruning", {})
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
            css_selector=merged.get("css_selector"),
            target_elements=merged.get("target_elements"),
            # Content filtering
            excluded_tags=merged.get("excluded_tags"),
            word_count_threshold=merged.get("word_count_threshold"),
            exclude_external_links=merged.get("exclude_external_links", False),
            exclude_social_media_links=merged.get("exclude_social_media_links", False),
            exclude_external_images=merged.get("exclude_external_images", False)
        )
