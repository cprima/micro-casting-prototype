.PHONY: setup install sync playwright test clean help serve

help: ## Show this help message
	@echo "Available targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

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

serve: ## Serve documentation on http://localhost:8001
	cd docs && python -m http.server 8001
