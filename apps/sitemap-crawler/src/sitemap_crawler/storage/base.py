"""Base storage interface for crawled content."""

from abc import ABC, abstractmethod
from pathlib import Path


class BaseStorage(ABC):
    """Abstract base class for storage backends."""

    @abstractmethod
    def write(self, path: str, content: str) -> None:
        """
        Write content to storage.

        Args:
            path: Relative path where content should be stored
            content: Content to write
        """
        pass

    @abstractmethod
    def exists(self, path: str) -> bool:
        """
        Check if a path exists in storage.

        Args:
            path: Relative path to check

        Returns:
            True if path exists, False otherwise
        """
        pass

    @abstractmethod
    def read(self, path: str) -> str:
        """
        Read content from storage.

        Args:
            path: Relative path to read from

        Returns:
            Content from the path

        Raises:
            FileNotFoundError: If path doesn't exist
        """
        pass

    @staticmethod
    def sanitize_filename(filename: str, max_length: int = 200) -> str:
        """
        Sanitize a filename to be safe for filesystems.

        Args:
            filename: Original filename
            max_length: Maximum length for the filename

        Returns:
            Sanitized filename
        """
        # Replace unsafe characters
        unsafe_chars = '<>:"/\\|?*'
        for char in unsafe_chars:
            filename = filename.replace(char, '_')

        # Remove leading/trailing spaces and dots
        filename = filename.strip('. ')

        # Truncate if too long
        if len(filename) > max_length:
            filename = filename[:max_length]

        # Ensure it's not empty
        if not filename:
            filename = "unnamed"

        return filename
