"""
Performance metrics tracking for crawl operations.

Tracks:
- Request duration
- Bytes downloaded/uploaded
- URLs per second
- Success/failure counts
- Memory usage
"""

import time
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Optional

from .logging_config import get_logger

logger = get_logger(__name__)


@dataclass
class CrawlMetrics:
    """Metrics for a crawl session."""

    # Counters
    urls_total: int = 0
    urls_success: int = 0
    urls_failed: int = 0
    urls_skipped: int = 0

    # Bytes
    bytes_downloaded: int = 0

    # Timing
    start_time: float = field(default_factory=time.time)
    end_time: Optional[float] = None

    def record_success(self, content_size: int = 0) -> None:
        """Record a successful URL fetch."""
        self.urls_success += 1
        self.bytes_downloaded += content_size

    def record_failure(self) -> None:
        """Record a failed URL fetch."""
        self.urls_failed += 1

    def record_skip(self) -> None:
        """Record a skipped URL."""
        self.urls_skipped += 1

    def finish(self) -> None:
        """Mark the crawl as finished."""
        self.end_time = time.time()

    @property
    def duration(self) -> float:
        """Get duration in seconds."""
        end = self.end_time if self.end_time else time.time()
        return end - self.start_time

    @property
    def urls_per_second(self) -> float:
        """Calculate URLs processed per second."""
        duration = self.duration
        if duration == 0:
            return 0.0
        return self.urls_success / duration

    @property
    def bytes_per_second(self) -> float:
        """Calculate bytes downloaded per second."""
        duration = self.duration
        if duration == 0:
            return 0.0
        return self.bytes_downloaded / duration

    @property
    def mb_downloaded(self) -> float:
        """Get megabytes downloaded."""
        return self.bytes_downloaded / (1024 * 1024)

    def to_dict(self) -> dict:
        """Convert metrics to dictionary for logging."""
        return {
            "urls_total": self.urls_total,
            "urls_success": self.urls_success,
            "urls_failed": self.urls_failed,
            "urls_skipped": self.urls_skipped,
            "bytes_downloaded": self.bytes_downloaded,
            "mb_downloaded": round(self.mb_downloaded, 2),
            "duration_seconds": round(self.duration, 2),
            "urls_per_second": round(self.urls_per_second, 2),
            "mb_per_second": round(self.bytes_per_second / (1024 * 1024), 2),
        }

    def log_summary(self) -> None:
        """Log a summary of the metrics."""
        logger.info(
            "crawl_metrics_summary",
            **self.to_dict()
        )


@contextmanager
def track_operation(operation_name: str, **context):
    """
    Context manager to track operation duration.

    Usage:
        with track_operation("fetch_sitemap", url="https://example.com"):
            # ... operation code ...
    """
    start = time.time()
    logger.debug(
        f"{operation_name}_started",
        **context
    )

    try:
        yield
        duration = time.time() - start
        logger.info(
            f"{operation_name}_completed",
            duration_seconds=round(duration, 3),
            **context
        )
    except Exception as e:
        duration = time.time() - start
        logger.error(
            f"{operation_name}_failed",
            duration_seconds=round(duration, 3),
            error=str(e),
            **context
        )
        raise


@contextmanager
def track_request(url: str):
    """
    Context manager to track HTTP request metrics.

    Usage:
        with track_request("https://example.com") as metrics:
            response = requests.get(url)
            metrics["status_code"] = response.status_code
            metrics["content_length"] = len(response.content)
    """
    metrics = {}
    start = time.time()

    logger.debug("http_request_started", url=url)

    try:
        yield metrics
        duration = time.time() - start

        logger.info(
            "http_request_completed",
            url=url,
            duration_seconds=round(duration, 3),
            **metrics
        )
    except Exception as e:
        duration = time.time() - start

        logger.error(
            "http_request_failed",
            url=url,
            duration_seconds=round(duration, 3),
            error=str(e),
            **metrics
        )
        raise
