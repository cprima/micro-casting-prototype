# **ADR 002 – Crawl4AI Wrapper for Documentation Retrieval**

## Status

Accepted

## Context

* Need web documentation in markdown format for LLM context
* Manual doc collection is slow and blocks MCP development iteration
* Require headless browser capabilities for JavaScript-heavy documentation sites
* Windows development environment compatibility needed

## Decision

Build minimal wrapper library for Crawl4AI:

```toml
# libs/crawling/pyproject.toml
dependencies = ["crawl4ai==0.7.6"]
```

* Pin crawl4ai to version 0.7.6
* Provide thin wrappers: `fetch()` (async), `fetch_sync()` (sync)
* Re-export types: `BrowserConfig`, `CrawlerRunConfig`, `CacheMode`, `CrawlResult`
* Applications provide all configuration (browser settings, caching, filtering)
* Makefile automation for setup: `make setup` → `uv sync + playwright install`

## Rationale

| Goal / Requirement           | How the decision addresses it                        |
| ---------------------------- | ---------------------------------------------------- |
| Simple RAG pattern           | Fetch → markdown → LLM context (no vector DB)        |
| Fast doc retrieval           | AI-powered extraction handles complex sites          |
| Stability                    | Pinned version prevents breaking changes             |
| Flexibility                  | Apps access full Crawl4AI API via re-exports         |
| Windows compatibility        | Logging suppression avoids encoding errors           |
| Reusability                  | Minimal wrapper = apps define own defaults           |
| Low maintenance              | 44-line wrapper vs. complex abstraction              |

## Implementation Rules

**Library responsibilities** (`libs/crawling/src/crawling/client.py:1-70`):
* Version pinning only
* Type re-exports for discoverability
* Windows logging workaround (suppress to CRITICAL)
* Stdout/stderr redirection to avoid Unicode errors

**Application responsibilities** (`apps/sitemap-crawler/src/sitemap_crawler/config.py:298-394`):
* Build `BrowserConfig` (headless mode, viewport, user-agent)
* Build `CrawlerRunConfig` (caching, CSS selectors, content filtering)
* Merge global defaults with per-site overrides
* Handle business logic (retries, rate limiting, robots.txt)

**Setup automation** (`Makefile:7-18`):
```bash
make setup
  ├─ uv sync                              # Resolve dependencies
  ├─ uv pip install -e libs/crawling      # Editable install
  └─ uv run playwright install chromium   # Browser setup
```

## Alternatives Considered

1. **Vector database RAG** – Unnecessary complexity for doc fetching use case
2. **BeautifulSoup/lxml** – Cannot handle JavaScript-rendered content
3. **Default configurations in lib** – Couples apps, reduces flexibility
4. **Convenience methods** – Hides metadata apps might need

## Consequences

### Positive

* Fast markdown extraction from any documentation site
* Simple RAG workflow without vector DB overhead
* Stable dependency (pinned version)
* Full Crawl4AI API available to applications

### Negative

* Playwright browser must be installed manually (`make playwright`)
* Requires understanding of BrowserConfig/CrawlerRunConfig
* Windows-specific workarounds increase code complexity

### Neutral

* Applications own configuration complexity
* Wrapper library stays minimal (44 lines)
* Transitive Playwright dependency (~200MB browser download)

## Related

* Implementation: `libs/crawling/pyproject.toml:6`
* Client wrapper: `libs/crawling/src/crawling/client.py:26-69`
* App config example: `apps/sitemap-crawler/src/sitemap_crawler/config.py:298-394`
* Automation: `Makefile:7-18`
* Crawl4AI docs: https://docs.crawl4ai.com/
* ADR-001: uv Workspaces for Monorepo Layout
