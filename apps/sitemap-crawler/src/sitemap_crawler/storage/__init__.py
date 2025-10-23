"""Storage backends for crawled content."""

from .base import BaseStorage
from .local import LocalStorage

__all__ = ["BaseStorage", "LocalStorage"]
