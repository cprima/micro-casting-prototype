"""Local filesystem storage backend."""

from pathlib import Path
from .base import BaseStorage
from ..logging_config import get_logger

logger = get_logger(__name__)


class LocalStorage(BaseStorage):
    """Local filesystem storage backend."""

    def __init__(self, base_dir: str):
        """
        Initialize local storage.

        Args:
            base_dir: Base directory for storage
        """
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        logger.info("local_storage_initialized", base_dir=str(self.base_dir))

    def write(self, path: str, content: str) -> None:
        """Write content to a file."""
        full_path = self.base_dir / path
        full_path.parent.mkdir(parents=True, exist_ok=True)

        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)

        logger.debug("file_written", path=str(full_path), size_bytes=len(content))

    def exists(self, path: str) -> bool:
        """Check if a file exists."""
        full_path = self.base_dir / path
        return full_path.exists()

    def read(self, path: str) -> str:
        """Read content from a file."""
        full_path = self.base_dir / path

        if not full_path.exists():
            raise FileNotFoundError(f"File not found: {full_path}")

        with open(full_path, 'r', encoding='utf-8') as f:
            return f.read()
