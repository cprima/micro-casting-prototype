# Micro Casting Prototype

A Python monorepo exploring the Model Context Protocol (MCP) with web scraping capabilities powered by Crawl4AI.

## Overview

This repository is organized as a **uv workspace** with shared libraries and applications:

- **`libs/`**: Reusable libraries shared across applications
  - `crawling`: Crawl4AI-based web scraping client
- **`apps/`**: Application projects
  - `uipac/ingestor`: Content ingestion service

## Features

- 🚀 **Fast dependency management** with [uv](https://github.com/astral-sh/uv)
- 🕷️ **Advanced web scraping** via [Crawl4AI](https://github.com/unclecode/crawl4ai) (0.7.6)
- 📦 **Monorepo workspace** for code sharing and consistency
- 🔧 **Makefile** for repeatable development workflows
- 🎭 **Playwright integration** for headless browser automation

## Repository Structure

```
micro-casting-prototype/
├── pyproject.toml              # Root workspace configuration
├── Makefile                    # Development automation
├── README.md                   # This file
├── .venv/                      # Virtual environment (created on setup)
├── libs/                       # Shared libraries
│   └── crawling/               # Web scraping library
│       ├── pyproject.toml      # Crawl4AI dependency (0.7.6)
│       ├── README.md           # Library documentation
│       └── src/
│           └── crawling/
│               ├── __init__.py
│               └── client.py   # Main crawling implementation
└── apps/                       # Application projects
    └── uipac/
        └── ingestor/           # Content ingestion app
            └── pyproject.toml  # Depends on "crawling"
```

## Quick Start

### Prerequisites

- **Python 3.10+**
- **uv** package manager ([installation guide](https://github.com/astral-sh/uv#installation))

```bash
# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh
# or on Windows:
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### Setup

```bash
# Clone the repository
git clone <repository-url>
cd micro-casting-prototype

# Complete setup: sync dependencies, install packages, setup playwright
make setup

# Verify installation
make verify
```

### Test the Crawling Library

```bash
# Test web scraping with example.com
make test-crawling

# Or run manually
uv run python -c "from crawling.client import fetch_markdown_sync; print(fetch_markdown_sync('https://example.com'))"
```

## Available Commands

Run `make help` to see all available commands:

| Command | Description |
|---------|-------------|
| `make setup` | Complete setup: sync dependencies, install packages, and set up playwright |
| `make sync` | Sync and resolve workspace dependencies |
| `make install` | Install workspace packages in editable mode |
| `make playwright` | Install Playwright chromium browser |
| `make test-crawling` | Test the crawling library with example.com |
| `make verify` | Verify installation |
| `make clean` | Remove virtual environment and cache |
| `make reinstall` | Clean and reinstall everything |

## Libraries

### Crawling Library

Located in `libs/crawling/`, this library provides a simple interface for web scraping.

**Features:**
- Async and sync APIs
- Built-in caching
- Headless browser automation
- Markdown output

**Usage:**

```python
from crawling.client import fetch_markdown_sync

# Scrape a web page and get markdown
content = fetch_markdown_sync('https://example.com')
print(content)
```

📖 **[Full Documentation](libs/crawling/README.md)**

## Applications

### UIPAC Ingestor

Located in `apps/uipac/ingestor/`, this application handles content ingestion.

**Dependencies:**
- `crawling` library (for web scraping)

## Development

### Adding a New Library

1. Create a new directory in `libs/`:
   ```bash
   mkdir -p libs/mylib/src/mylib
   ```

2. Create `libs/mylib/pyproject.toml`:
   ```toml
   [project]
   name = "mylib"
   version = "0.0.1"
   requires-python = ">=3.10"
   dependencies = []

   [build-system]
   requires = ["hatchling"]
   build-backend = "hatchling.build"
   ```

3. Install in editable mode:
   ```bash
   uv pip install -e libs/mylib
   ```

### Adding a New Application

1. Create a new directory in `apps/`:
   ```bash
   mkdir -p apps/myapp
   ```

2. Create `apps/myapp/pyproject.toml`:
   ```toml
   [project]
   name = "myapp"
   version = "0.0.1"
   requires-python = ">=3.10"
   dependencies = ["crawling"]  # Add dependencies
   ```

3. Install in editable mode:
   ```bash
   uv pip install -e apps/myapp
   ```

### Workspace Configuration

The root `pyproject.toml` defines workspace members:

```toml
[tool.uv.workspace]
members = ["libs/*", "apps/*", "apps/*/*"]
```

This allows:
- **Shared dependencies**: Pin versions once, use everywhere
- **Editable installs**: Changes reflect immediately
- **Cross-project imports**: Import from `crawling`, `uipac`, etc.

### Dependency Management

```bash
# Add a dependency to a specific package
cd libs/crawling
uv add requests

# Update all dependencies
uv sync --upgrade

# Lock dependencies without installing
uv lock
```

## Key Technologies

- **[uv](https://github.com/astral-sh/uv)**: Fast Python package manager (Rust-based)
- **[Crawl4AI](https://github.com/unclecode/crawl4ai)**: AI-powered web scraping
- **[Playwright](https://playwright.dev/python/)**: Browser automation
- **[hatchling](https://hatch.pypa.io/)**: Modern Python build backend

## Workspace Benefits

✅ **Unified dependency management**: One lockfile, consistent versions
✅ **Code reuse**: Shared libraries across apps
✅ **Fast installations**: uv's parallel downloads and caching
✅ **Editable mode**: Changes propagate instantly
✅ **Simplified CI/CD**: Single `make setup` command

## Troubleshooting

### Package not found

```bash
# Reinstall in editable mode
uv pip install -e libs/crawling
```

### Playwright browser missing

```bash
make playwright
# or
uv run playwright install chromium
```

### Import errors

```bash
# Verify workspace members
uv sync --verbose

# Check installed packages
uv pip list
```

### Clean install

```bash
make reinstall
```

## Notes

- `uv sync` reads the workspace and installs both libs and apps in editable mode
- `crawl4ai` is pinned once in `libs/crawling/pyproject.toml`; other apps just depend on `crawling`
- Keep each subproject's `pyproject.toml` minimal; `uv` handles linking automatically

## Resources

- [uv Documentation](https://github.com/astral-sh/uv)
- [Crawl4AI Documentation](https://github.com/unclecode/crawl4ai)
- [Playwright Python Docs](https://playwright.dev/python/)
- [Model Context Protocol](https://modelcontextprotocol.io/)

## License

[Your License Here]

## Contributing

[Contribution guidelines, if applicable]
