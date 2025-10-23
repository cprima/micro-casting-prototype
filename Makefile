.PHONY: setup install sync playwright test clean help serve

help: ## Show this help message
	@echo "Available targets:"
	@echo ""
	@echo "Setup & Installation:"
	@echo "  setup                - Complete setup: sync dependencies, install packages, and set up playwright"
	@echo "  sync                 - Sync and resolve workspace dependencies"
	@echo "  install              - Install workspace packages in editable mode"
	@echo "  playwright           - Install Playwright chromium browser"
	@echo "  verify               - Verify installation"
	@echo "  reinstall            - Clean and reinstall everything"
	@echo ""
	@echo "Testing:"
	@echo "  test-crawling        - Test the crawling library with example.com"
	@echo ""
	@echo "Maintenance:"
	@echo "  clean                - Remove virtual environment and cache"
	@echo ""
	@echo "Sitemap Crawler:"
	@echo "  crawl-list           - List configured sitemap crawler sites"
	@echo "  crawl-mcp            - Crawl modelcontextprotocol.io"
	@echo "  crawl-uipath         - Crawl docs.uipath.com (English only)"
	@echo "  crawl-all            - Crawl all configured sites"
	@echo "  crawl-dry-run        - Preview what would be crawled"
	@echo ""
	@echo "Documentation:"
	@echo "  serve                - Serve documentation on http://localhost:8001"
	@echo ""
	@echo "MCP Server Methodology - Data Transformation:"
	@echo "  mcp-transform-ingest    - Stage 1: Ingest - Pick active/previous versions"
	@echo "  mcp-transform-validate  - Stage 2: Validate - Fail-fast invariant checks"
	@echo "  mcp-transform-compile   - Stage 3: Compile - Build indices and rules"
	@echo "  mcp-transform-all       - Run all 3 transformation stages"
	@echo "  mcp-transform-clean     - Remove generated var/ files"

setup: sync install playwright ## Complete setup: sync dependencies, install packages, and set up playwright

sync: ## Sync and resolve workspace dependencies
	uv sync

install: ## Install workspace packages in editable mode
	uv pip install -e libs/crawling
	uv pip install -e apps/uipac/ingestor
	uv pip install -e apps/sitemap-crawler

playwright: ## Install Playwright chromium browser
	uv run playwright install chromium

test-crawling: ## Test the crawling library with example.com
	uv run python -c "from crawling.client import fetch_markdown_sync; print(fetch_markdown_sync('https://example.com')[:200] + '...')"

verify: ## Verify installation
	@echo "Verifying crawling library..."
	@uv run python -c "from crawling.client import fetch_markdown_sync; print('✓ Crawling library is working')" || echo "✗ Crawling library import failed"
	@echo "Verifying playwright..."
	@uv run python -c "import playwright; print('✓ Playwright is installed')" || echo "✗ Playwright import failed"

clean: ## Remove virtual environment and cache
	rm -rf .venv
	rm -rf .uv
	rm -rf libs/crawling/dist
	rm -rf libs/crawling/build
	rm -rf libs/crawling/*.egg-info

reinstall: clean setup ## Clean and reinstall everything

# Sitemap Crawler commands
crawl-list: ## List configured sitemap crawler sites
	cd apps/sitemap-crawler && uv run sitemap-crawler list

crawl-mcp: ## Crawl modelcontextprotocol.io
	cd apps/sitemap-crawler && uv run sitemap-crawler crawl modelcontextprotocol

crawl-uipath: ## Crawl docs.uipath.com (English only)
	cd apps/sitemap-crawler && uv run sitemap-crawler crawl uipath-docs

crawl-all: ## Crawl all configured sites
	cd apps/sitemap-crawler && uv run sitemap-crawler crawl-all

crawl-dry-run: ## Preview what would be crawled
	cd apps/sitemap-crawler && uv run sitemap-crawler crawl-all --dry-run

crawl-fastmc: ## Crawl fastmc-site
	cd apps/sitemap-crawler && uv run sitemap-crawler crawl fastmc-site

serve: ## Serve documentation on http://localhost:8001
	cd docs && python -m http.server 8001

# MCP Server Methodology - Data Transformation
mcp-transform-ingest: ## Stage 1: Ingest - Pick active/previous versions
	cd apps/mcp-srv-mtdlgy_mcp && uv run python transforms/ingest.py

mcp-transform-validate: ## Stage 2: Validate - Fail-fast invariant checks
	cd apps/mcp-srv-mtdlgy_mcp && uv run python transforms/validate.py

mcp-transform-compile: ## Stage 3: Compile - Build indices and rules
	cd apps/mcp-srv-mtdlgy_mcp && uv run python transforms/compile.py

mcp-transform-all: ## Run all 3 transformation stages
	cd apps/mcp-srv-mtdlgy_mcp && uv run python transforms/ingest.py && uv run python transforms/validate.py && uv run python transforms/compile.py

mcp-transform-clean: ## Remove generated var/ files
	rm -rf apps/mcp-srv-mtdlgy_mcp/var/*.json
