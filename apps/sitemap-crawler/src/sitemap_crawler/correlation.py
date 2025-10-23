"""
Correlation ID management for request tracing.

Provides unique identifiers for:
- Crawl sessions (entire crawl-all or single crawl run)
- Individual URL fetches
- Site operations

This allows tracing a request through the entire system across all components.
"""

import uuid
from typing import Optional

import structlog


def generate_correlation_id() -> str:
    """Generate a new correlation ID."""
    return str(uuid.uuid4())


def set_correlation_id(correlation_id: Optional[str] = None) -> str:
    """
    Set or generate a correlation ID in the context.

    Args:
        correlation_id: Existing ID to use, or None to generate new one

    Returns:
        The correlation ID that was set
    """
    if correlation_id is None:
        correlation_id = generate_correlation_id()

    structlog.contextvars.bind_contextvars(correlation_id=correlation_id)
    return correlation_id


def get_correlation_id() -> Optional[str]:
    """
    Get the current correlation ID from context.

    Returns:
        Current correlation ID, or None if not set
    """
    return structlog.contextvars.get_contextvars().get("correlation_id")


def clear_correlation_id() -> None:
    """Clear the correlation ID from context."""
    structlog.contextvars.unbind_contextvars("correlation_id")
