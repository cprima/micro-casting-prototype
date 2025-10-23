"""Resilience features: retry logic and rate limiting."""

import time
import requests
from typing import Dict, Any, Callable, Optional
from .logging_config import get_logger

logger = get_logger(__name__)


class RetryHandler:
    """Handles retry logic with exponential backoff."""

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize retry handler.

        Args:
            config: Retry configuration dict
        """
        self.max_retries = config.get("max_retries", 3)
        self.initial_backoff = config.get("initial_backoff", 1.0)
        self.backoff_multiplier = config.get("backoff_multiplier", 2.0)
        self.max_backoff = config.get("max_backoff", 60.0)
        self.retry_on_status = config.get("retry_on_status", [500, 502, 503, 504, 429])

    def should_retry(self, error: Exception, attempt: int) -> bool:
        """
        Determine if a request should be retried.

        Args:
            error: Exception that occurred
            attempt: Current attempt number (0-indexed)

        Returns:
            True if should retry, False otherwise
        """
        if attempt >= self.max_retries:
            return False

        # Retry on network errors
        if isinstance(error, (requests.ConnectionError, requests.Timeout)):
            return True

        # Retry on specific HTTP status codes
        if isinstance(error, requests.HTTPError):
            if hasattr(error.response, 'status_code'):
                return error.response.status_code in self.retry_on_status

        return False

    def get_backoff_delay(self, attempt: int, retry_after: Optional[int] = None) -> float:
        """
        Calculate backoff delay for retry.

        Args:
            attempt: Current attempt number (0-indexed)
            retry_after: Optional Retry-After header value (seconds)

        Returns:
            Delay in seconds before next retry
        """
        # If server specified Retry-After, respect it
        if retry_after is not None:
            return min(retry_after, self.max_backoff)

        # Calculate exponential backoff
        delay = self.initial_backoff * (self.backoff_multiplier ** attempt)
        return min(delay, self.max_backoff)

    def execute_with_retry(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute a function with retry logic.

        Args:
            func: Function to execute
            *args: Positional arguments for function
            **kwargs: Keyword arguments for function

        Returns:
            Function result

        Raises:
            Last exception if all retries exhausted
        """
        last_error = None

        for attempt in range(self.max_retries + 1):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                last_error = e

                if not self.should_retry(e, attempt):
                    logger.warning(
                        "request_not_retryable",
                        error=str(e),
                        attempt=attempt + 1,
                        max_retries=self.max_retries
                    )
                    raise

                # Extract Retry-After header if available
                retry_after = None
                if isinstance(e, requests.HTTPError) and hasattr(e, 'response'):
                    retry_after_header = e.response.headers.get('Retry-After')
                    if retry_after_header:
                        try:
                            retry_after = int(retry_after_header)
                        except ValueError:
                            pass

                delay = self.get_backoff_delay(attempt, retry_after)

                logger.warning(
                    "request_retry",
                    error=str(e),
                    attempt=attempt + 1,
                    max_retries=self.max_retries,
                    backoff_seconds=delay
                )

                time.sleep(delay)

        # All retries exhausted
        logger.error(
            "request_failed_all_retries",
            error=str(last_error),
            attempts=self.max_retries + 1
        )
        raise last_error


class RateLimiter:
    """Rate limiter to control request frequency."""

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize rate limiter.

        Args:
            config: Rate limit configuration dict
        """
        self.requests_per_second = config.get("requests_per_second", 1.0)
        self.delay_between_requests = config.get("delay_between_requests", 1.0)
        self.respect_429 = config.get("respect_429", True)
        self.last_request_time = 0.0

    def wait_if_needed(self):
        """Wait if necessary to respect rate limit."""
        if self.delay_between_requests <= 0:
            return

        elapsed = time.time() - self.last_request_time
        required_delay = self.delay_between_requests

        if elapsed < required_delay:
            sleep_time = required_delay - elapsed
            logger.debug("rate_limit_wait", sleep_seconds=sleep_time)
            time.sleep(sleep_time)

        self.last_request_time = time.time()

    def handle_429(self, response: requests.Response):
        """
        Handle HTTP 429 (Too Many Requests) response.

        Args:
            response: HTTP response object
        """
        if not self.respect_429:
            return

        if response.status_code == 429:
            retry_after = response.headers.get('Retry-After')
            if retry_after:
                try:
                    wait_time = int(retry_after)
                    logger.warning(
                        "rate_limit_429",
                        retry_after_seconds=wait_time
                    )
                    time.sleep(wait_time)
                except ValueError:
                    # Retry-After might be a date, just use default delay
                    logger.warning("rate_limit_429", retry_after_invalid=retry_after)
                    time.sleep(self.delay_between_requests)
            else:
                # No Retry-After header, use default delay
                logger.warning("rate_limit_429_no_header")
                time.sleep(self.delay_between_requests)
