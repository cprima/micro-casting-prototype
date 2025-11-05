# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Monorepo Structure

This is a **Python monorepo** using **uv workspaces**. All packages share a single `uv.lock` file for unified dependency resolution.

**Workspace configuration:** Root `pyproject.toml` defines glob patterns:
```toml
[tool.uv.workspace]
members = ["libs/*", "apps/*", "apps/uipac/*"]
```

**Package organization:**
- `libs/` - Shared libraries (e.g., `crawling`: Crawl4AI-based web scraping)
- `apps/` - Applications (e.g., `sitemap-crawler`, `mcp-srv-mtdlgy_mcp`, `uipac/ingestor`)
- All packages use `hatchling` build backend and require Python >=3.10

**Workspace dependencies:** Apps reference libs via workspace sources:
```toml
# In apps/sitemap-crawler/pyproject.toml
dependencies = ["crawling"]

[tool.uv.sources]
crawling = { workspace = true }
```

## Development Commands

### Initial Setup
```bash
make setup          # Full setup: sync deps, install packages, setup Playwright
make verify         # Verify installation works
make reinstall      # Clean and reinstall from scratch
```

### Package Management
```bash
uv sync                           # Sync all workspace dependencies
uv pip install -e libs/crawling   # Install library in editable mode
uv add requests                   # Add dependency to current package
uv sync --upgrade                 # Update all dependencies
```

### Sitemap Crawler
```bash
sitemap-crawler list                        # List configured sites
sitemap-crawler crawl <name>                # Crawl a specific site
sitemap-crawler crawl <name> --dry-run      # Preview URLs without crawling
sitemap-crawler crawl-all                   # Crawl all configured sites
```

Configuration: `apps/sitemap-crawler/config.yaml`

### MCP Server Methodology - Transformation Pipeline
```bash
make mcp-transform-all         # Run all 3 stages (ingest → validate → compile)
make mcp-transform-ingest      # Stage 1: Pick versions, strip bloat
make mcp-transform-validate    # Stage 2: Fail-fast invariant checks
make mcp-transform-compile     # Stage 3: Build indices, compile predicates
make mcp-transform-clean       # Remove generated var/ files
```

**Pipeline outputs:** `apps/mcp-srv-mtdlgy_mcp/var/*.json`

### Testing
```bash
make test-crawling   # Test crawling library with example.com

# MCP server test (manual run)
cd apps/mcp-srv-mtdlgy_mcp && uv run python test_server.py
```

## Architecture & Design Patterns

### Monorepo Workspace (ADR-001)

**Decision:** Use uv workspaces with glob-based auto-discovery.

**Key benefits:**
- Single lockfile ensures version consistency
- Editable installs - changes to libs reflect instantly in apps
- Fast dependency resolution (Rust-based uv)
- Zero-config discovery for new packages

**Adding a new library:**
1. Create `libs/mylib/pyproject.toml` with `hatchling` build backend
2. Run `uv pip install -e libs/mylib`
3. Reference in apps via workspace dependency

**Adding a new app:**
1. Create `apps/myapp/pyproject.toml`
2. Add workspace dependencies (e.g., `crawling`)
3. Define workspace sources: `[tool.uv.sources]`
4. Run `uv pip install -e apps/myapp`

### MCP Server Architecture (ADR-004)

**Decision:** Strict separation of presentation (HTML) and logic (MCP server).

**HTML layer:**
- Static renderer, no validation, offline-capable
- Loads `data.json` (multi-version catalog array)
- String-only fingerprint comparison
- No schema validation or predicate parsing

**Data layer:**
- `docs/methodology/data.json` - Immutable multi-version catalog
- Each version: `$schema`, `program.fingerprint`, `program.supersedes`
- Array structure: `[{version: "0.3.0", ...}, {version: "0.4.0-alpha", ...}]`

**MCP server layer:**
- All complexity: gate evaluation, validation, migrations, advisory
- **3-stage transformation pipeline:**
  1. **Ingest** (`ingest.py`): Pick active/previous versions, strip bloat
  2. **Validate** (`validate.py`): Fail-fast invariant checks, fingerprint validation
  3. **Compile** (`compile.py`): Build indices, compile predicates, create advisory registry
- Stateless, read-only, advisory-only design
- Stdlib-only transforms (no external deps)

**Predicate grammar (locked):**
- `status.state == done` - Node completion
- `has_evidence:<type>[:result]` - Evidence checks
- `has_contract` - Contract presence

### Crawling Library

**Location:** `libs/crawling/`

**Purpose:** Shared Crawl4AI wrapper for web scraping.

**Features:**
- Async/sync APIs
- Markdown extraction
- Headless browser automation (Playwright)
- Built-in caching

**Usage:**
```python
from crawling.client import fetch_markdown_sync
content = fetch_markdown_sync('https://example.com')
```

**Requires:** Playwright chromium browser (`make playwright`)

### Sitemap Crawler

**Location:** `apps/sitemap-crawler/`

**Purpose:** Documentation crawler using sitemaps/llms.txt.

**Architecture:**
- `parsers/` - Format parsers (llms.txt, XML sitemap, direct URLs)
- `storage/` - Storage backends (local filesystem, future: SMB)
- `config.py` - YAML configuration loader
- `crawler.py` - Main crawling orchestration
- `cli.py` - Click-based CLI

**Extensibility:**
- New parsers: Extend `BaseParser` in `parsers/`
- New storage: Extend `BaseStorage` in `storage/`

**Configuration:** Auto-detects `type` and `domain` from source URL.

## Important Constraints

### Dependency Management
- **Never** force push to remote (`--force` or `--force-with-lease`)
- All packages must require `python = ">=3.10"`
- All packages must use `hatchling` build backend
- Pin `crawl4ai==0.7.6` only in `libs/crawling/pyproject.toml`

### MCP Server Transforms
- Transforms use **stdlib only** (no external packages)
- Validation is **fail-fast** - errors caught at startup, not runtime
- **Current catalog is canonical** - previous must match current's `levels`, `tags`, `global_gates`
- Fingerprints must be hex-64 SHA-256 format

### Package Structure
- Each package needs `pyproject.toml` with:
  - `[project]` section with name, version, dependencies
  - `[build-system]` using hatchling
  - `requires-python = ">=3.10"`
- Workspace dependencies use `[tool.uv.sources]` with `{ workspace = true }`

## File Locations

**Documentation:** `docs/`
- `docs/ADR/` - Architecture Decision Records
- `docs/methodology/` - Methodology catalog and HTML visualization
- `docs/schema/` - JSON schemas (documentation only, not runtime validation)

**Generated files (gitignored):**
- `apps/mcp-srv-mtdlgy_mcp/var/*.json` - Transform pipeline outputs
- `.venv/` - Virtual environment

**Configuration:**
- Root `pyproject.toml` - Workspace config
- `Makefile` - Development automation (105 lines, 30+ targets)
- `apps/sitemap-crawler/config.yaml` - Sitemap crawler sites
