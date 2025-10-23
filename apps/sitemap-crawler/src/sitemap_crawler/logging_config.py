"""
Structured logging configuration using structlog.

Provides:
- JSON output to file for machine parsing
- Human-readable console output for development
- Correlation IDs for request tracing
- Performance metrics tracking
- Context binding (site, URL, session)
"""

import logging
import logging.handlers
import sys
from pathlib import Path
from typing import Any, Dict, Optional

import structlog
from structlog.typing import EventDict, Processor


def add_correlation_id(logger: logging.Logger, method_name: str, event_dict: EventDict) -> EventDict:
    """Add correlation ID from context if available."""
    correlation_id = structlog.contextvars.get_contextvars().get("correlation_id")
    if correlation_id:
        event_dict["correlation_id"] = correlation_id
    return event_dict


def add_timestamp(logger: logging.Logger, method_name: str, event_dict: EventDict) -> EventDict:
    """Add ISO timestamp to event."""
    import datetime
    event_dict["timestamp"] = datetime.datetime.utcnow().isoformat() + "Z"
    return event_dict


def configure_logging(
    log_level: str = "INFO",
    log_file: Optional[str] = None,
    enable_json_file: bool = True,
    enable_console: bool = True,
) -> None:
    """
    Configure structured logging with console and file outputs.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file (default: logs/sitemap-crawler.log)
        enable_json_file: Enable JSON file logging
        enable_console: Enable human-readable console logging
    """
    # Set up standard library logging
    logging.basicConfig(
        format="%(message)s",
        level=getattr(logging, log_level.upper()),
        stream=sys.stdout if enable_console else None,
    )

    # Shared processors for all outputs
    shared_processors: list[Processor] = [
        structlog.contextvars.merge_contextvars,
        add_correlation_id,
        add_timestamp,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]

    # Configure file logging if enabled
    if enable_json_file:
        if log_file is None:
            log_file = "logs/sitemap-crawler.log"

        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        # Rotating file handler (10MB per file, keep 5 backups)
        file_handler = logging.handlers.RotatingFileHandler(
            log_path,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding="utf-8",
        )
        file_handler.setLevel(getattr(logging, log_level.upper()))

        # JSON formatter for file
        file_handler.setFormatter(
            structlog.stdlib.ProcessorFormatter(
                processor=structlog.processors.JSONRenderer(),
                foreign_pre_chain=shared_processors,
            )
        )
        logging.root.addHandler(file_handler)

    # Configure console logging
    if enable_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, log_level.upper()))

        # Human-readable formatter for console
        console_handler.setFormatter(
            structlog.stdlib.ProcessorFormatter(
                processor=structlog.dev.ConsoleRenderer(colors=True),
                foreign_pre_chain=shared_processors,
            )
        )
        logging.root.handlers = [h for h in logging.root.handlers if not isinstance(h, logging.StreamHandler)]
        logging.root.addHandler(console_handler)

    # Configure structlog
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            add_correlation_id,
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_log_level,
            structlog.stdlib.add_logger_name,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """
    Get a configured structlog logger.

    Args:
        name: Logger name (typically __name__)

    Returns:
        Configured structlog logger
    """
    return structlog.get_logger(name)


def bind_context(**kwargs: Any) -> None:
    """
    Bind context variables that will be included in all log entries.

    Example:
        bind_context(site="modelcontextprotocol", session_id="abc123")
    """
    structlog.contextvars.bind_contextvars(**kwargs)


def unbind_context(*keys: str) -> None:
    """
    Unbind context variables.

    Example:
        unbind_context("site", "session_id")
    """
    structlog.contextvars.unbind_contextvars(*keys)


def clear_context() -> None:
    """Clear all context variables."""
    structlog.contextvars.clear_contextvars()
