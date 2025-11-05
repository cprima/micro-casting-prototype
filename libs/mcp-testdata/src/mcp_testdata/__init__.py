"""
MCP Test Data - Realistic test databases for MCP server development.

Provides:
- Pre-generated SQLite databases (library, ecommerce, logistics, finance)
- Database generation scripts
- Database access utilities
"""

from pathlib import Path

__version__ = "0.1.0"

# Database locations
DATA_DIR = Path(__file__).parent / "data"
DATA_DIR.mkdir(exist_ok=True)

def get_database_path(name: str) -> Path:
    """
    Get path to a test database.

    Args:
        name: Database name without extension (e.g., 'library', 'ecommerce')

    Returns:
        Path to the database file.
    """
    return DATA_DIR / f"{name}.db"


__all__ = ["get_database_path", "DATA_DIR"]
