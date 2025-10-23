# Sitemap Crawler

A Python application for crawling documentation sites using sitemaps and llms.txt files, extracting content as markdown.

## Features

- **Multiple sitemap formats**: llms.txt and XML sitemaps
- **Sitemap index support**: Recursively crawls nested sitemaps
- **URL filtering**: Filter by pattern, language, or custom rules
- **Markdown extraction**: Uses the `crawling` library (Crawl4AI) for clean markdown output
- **Configurable storage**: Local filesystem (SMB/network in future)
- **CLI interface**: Easy-to-use commands for crawling
- **Environment variable support**: Override output directory via `$BASE_OUTPUT_DIR`

## Adding Sites (Quick Reference)

### Option 1: Single URL (Simplest)

Just add the URL to `config.yaml`:

```yaml
sites:
  - name: my-article
    source: https://example.com/blog/article/
```

That's it! The crawler auto-detects:
- `type: direct_url` (from URL format)
- `domain: example.com` (extracted from URL)

**Run:** `sitemap-crawler crawl my-article`

### Option 2: Multiple URLs

```yaml
sites:
  - name: my-articles
    source: |
      https://example.com/blog/article-1/
      https://example.com/blog/article-2/
      https://example.com/blog/article-3/
```

**Run:** `sitemap-crawler crawl my-articles`

### Option 3: Full Documentation Site (Sitemap/llms.txt)

```yaml
sites:
  - name: example-docs
    source: https://example.com/sitemap.xml
    # OR
    source: https://example.com/llms.txt
```

**Run:** `sitemap-crawler crawl example-docs`

**Output location:** `docs/{domain}/` (e.g., `docs/example.com/`)

**Next steps:** See [Quick Start](#quick-start) below for installation, or [Configuration](#configuration) for advanced options (filtering, custom output paths, per-site configuration).

---

## Installation

From the repository root:

```bash
# Install in editable mode
uv pip install -e apps/sitemap-crawler

# Or use the Makefile (recommended)
make install
```

## Quick Start

**New to sitemap-crawler?** See [Adding Sites (Quick Reference)](#adding-sites-quick-reference) above for copy-paste examples.

### 1. Configure Sites

Edit `apps/sitemap-crawler/config.yaml` to add sites:

```yaml
settings:
  base_output_dir: ../../docs

sites:
  - name: modelcontextprotocol
    domain: modelcontextprotocol.io
    source: https://modelcontextprotocol.io/llms.txt
    type: llms.txt
    output_pattern: "{domain}"
```

### 2. List Configured Sites

```bash
sitemap-crawler list
```

### 3. Crawl a Site

```bash
# Dry run (preview URLs)
sitemap-crawler crawl modelcontextprotocol --dry-run

# Actual crawl
sitemap-crawler crawl modelcontextprotocol

# Verbose logging
sitemap-crawler crawl modelcontextprotocol --verbose
```

### 4. Crawl All Sites

```bash
sitemap-crawler crawl-all
```

## Configuration

### Settings

| Setting | Description | Default |
|---------|-------------|---------|
| `base_output_dir` | Root directory for crawled content | `./docs` |
| `storage_backend` | Storage type (local, smb) | `local` |

### Site Configuration

Each site configuration requires:

| Field | Description | Required | Auto-detected |
|-------|-------------|----------|---------------|
| `name` | Unique site identifier | Yes | No |
| `source` | URL to sitemap, llms.txt, or direct URL | Yes | No |
| `type` | Format: `llms.txt`, `xml_sitemap`, or `direct_url` | No | ✅ Yes |
| `domain` | Domain name | No | ✅ Yes |
| `base_dir` | Override output directory for this site | No | No |
| `output_pattern` | Output path template | No | No |
| `filters` | List of URL filters | No | No |

**Auto-detection:**
- `type`: Auto-detected from source URL (`.txt` → llms.txt, `.xml`/`sitemap` → xml_sitemap, otherwise → direct_url)
- `domain`: Auto-extracted from first URL in source

### Direct URLs (Minimal Config)

For single URLs or small URL lists, use direct URLs with auto-detection:

```yaml
sites:
  # Single URL - minimal config
  - name: semgrep-guide
    source: https://semgrep.dev/blog/2025/a-security-engineers-guide-to-mcp/
    # type: auto-detected as direct_url
    # domain: auto-extracted as semgrep.dev

  # Multiple URLs from same domain
  - name: semgrep-articles
    source: |
      https://semgrep.dev/blog/2025/article-one/
      https://semgrep.dev/blog/2024/article-two/
    # type: auto-detected as direct_url
    # domain: auto-extracted as semgrep.dev
```

**Output:** `docs/semgrep.dev/blog_2025_article-one.md`

### Per-Site Output Directories

Each site can specify its own `base_dir` to control where content is saved. This is useful for:
- **Large datasets**: Store on external drives
- **Network shares**: Direct output to SMB/NFS mounts
- **Performance**: SSD for small sites, HDD for large archives

**Priority order:**
1. Site's `base_dir` field (highest)
2. `$BASE_OUTPUT_DIR` environment variable
3. Global `settings.base_output_dir` (default)

**Example:**

```yaml
sites:
  - name: modelcontextprotocol
    domain: modelcontextprotocol.io
    source: https://modelcontextprotocol.io/llms.txt
    type: llms.txt
    output_pattern: "{domain}"
    # Uses global base_output_dir (../../docs)

  - name: uipath-docs
    domain: docs.uipath.com
    source: https://docs.uipath.com/sitemap.xml
    type: xml_sitemap
    output_pattern: "{domain}/en"
    base_dir: /mnt/external-drive/docs  # Linux/Mac
    # base_dir: M:/docs.uipath.com      # Windows (forward slashes recommended)
    # base_dir: 'M:\docs.uipath.com'    # Windows (backslash, must quote)
    filters: [...]
```

**Windows Path Syntax:**
- ✅ **Recommended**: Use forward slashes: `M:/docs.uipath.com`
- ✅ **Alternative**: Quote backslashes: `'M:\docs.uipath.com'`
- ✅ **Parent directories created automatically** if they don't exist

Result:
- MCP docs → `../../docs/modelcontextprotocol.io/`
- UIPath docs → `M:/docs.uipath.com/docs.uipath.com/en/`

### Output Patterns

Customize where content is saved using template variables:

- `{domain}` - Site domain
- `{date}` - Current date (YYYY-MM-DD)

Example:
```yaml
output_pattern: "{domain}/{date}"
# Results in: docs/example.com/2025-01-22/
```

### URL Filters

Filter URLs by pattern:

```yaml
filters:
  - type: url_pattern
    pattern: "/en/"        # Only URLs containing "/en/"

  - type: url_contains
    value: "documentation"  # Only URLs with "documentation"
```

## CLI Commands

### `sitemap-crawler list`

List all configured sites.

```bash
sitemap-crawler list
```

### `sitemap-crawler crawl <name>`

Crawl a single site.

**Options:**
- `--dry-run` - Preview URLs without crawling
- `--verbose` - Enable debug logging
- `--config PATH` - Use alternative config file

**Example:**
```bash
sitemap-crawler crawl modelcontextprotocol --dry-run
```

### `sitemap-crawler crawl-all`

Crawl all configured sites.

**Options:**
- `--dry-run` - Preview URLs without crawling
- `--verbose` - Enable debug logging

**Example:**
```bash
sitemap-crawler crawl-all
```

## Environment Variables

### `BASE_OUTPUT_DIR`

Override the output directory from config:

```bash
BASE_OUTPUT_DIR=/mnt/external sitemap-crawler crawl-all
```

This is useful for:
- Moving content to external drives
- Using network shares (pre-mounted)
- Testing with different output locations

## Examples

### Example 1: Crawl MCP Documentation

```bash
sitemap-crawler crawl modelcontextprotocol
```

Output:
```
docs/modelcontextprotocol.io/
├── llms.txt
├── index.md
├── introduction.md
└── ...
```

### Example 2: Crawl UIPath Docs (English Only)

```bash
sitemap-crawler crawl uipath-docs --verbose
```

With filtering configured, this will:
1. Fetch the main sitemap index
2. Filter for `/sitemaps/en/` sub-sitemaps
3. Recursively fetch English sub-sitemaps
4. Filter individual URLs for `/en/`
5. Crawl and save as markdown

### Example 3: Preview All Sites

```bash
sitemap-crawler crawl-all --dry-run
```

Shows all URLs that would be crawled without actually fetching them.

### Example 4: Use External Drive

```bash
BASE_OUTPUT_DIR=/mnt/external-drive/docs sitemap-crawler crawl-all
```

## Architecture

```
apps/sitemap-crawler/
├── src/sitemap_crawler/
│   ├── parsers/          # Sitemap format parsers
│   │   ├── base.py       # BaseParser interface
│   │   ├── llms_txt.py   # llms.txt parser
│   │   └── xml_sitemap.py # XML sitemap parser
│   ├── storage/          # Storage backends
│   │   ├── base.py       # BaseStorage interface
│   │   └── local.py      # Local filesystem
│   ├── config.py         # Configuration loader
│   ├── crawler.py        # Main crawler logic
│   └── cli.py            # Click CLI
├── config.yaml           # Site configuration
├── pyproject.toml        # Package definition
├── README.md             # This file
└── ROADMAP.md            # Feature roadmap
```

## Extending

### Adding a New Parser

1. Create `src/sitemap_crawler/parsers/my_format.py`
2. Extend `BaseParser`
3. Implement `parse(content: str) -> List[str]`
4. Register in `parsers/__init__.py`

### Adding a New Storage Backend

1. Create `src/sitemap_crawler/storage/my_backend.py`
2. Extend `BaseStorage`
3. Implement `write()`, `read()`, `exists()`
4. Register in `storage/__init__.py`

## Troubleshooting

### No sites configured

**Error:** `No sites configured.`

**Solution:** Create or check `config.yaml` in the current directory or specify with `--config`.

### Site not found

**Error:** `Site not found: xyz`

**Solution:** Run `sitemap-crawler list` to see available site names.

### Permission denied writing files

**Error:** `PermissionError: ...`

**Solution:** Check write permissions on output directory or use `BASE_OUTPUT_DIR` to change location.

### XML parsing errors

**Error:** `Failed to parse XML sitemap`

**Solution:**
- Check if the URL returns valid XML
- Use `--verbose` to see detailed error
- Verify sitemap URL in browser

## Roadmap

See [ROADMAP.md](ROADMAP.md) for planned features:

- **v0.1.0**: Basic functionality (current)
- **v0.2.0**: Production features (retry logic, rate limiting, progress tracking)
- **v0.5.0**: Advanced features (incremental updates, async crawling, robots.txt)
- **v0.9.0**: Experimental features (post-processing, webhooks, distributed crawling)

## Dependencies

- `crawling` - Existing crawling library (Crawl4AI wrapper)
- `click` - CLI framework
- `pyyaml` - YAML configuration
- `lxml` - XML parsing
- `requests` - HTTP requests

## Author

**Christian Prior-Mamulyan**
Email: cprior@gmail.com

## License

This work is licensed under the [Creative Commons Attribution 4.0 International License (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/).

You are free to:
- **Share** — copy and redistribute the material in any medium or format
- **Adapt** — remix, transform, and build upon the material for any purpose, even commercially

Under the following terms:
- **Attribution** — You must give appropriate credit, provide a link to the license, and indicate if changes were made.

See the [LICENSE](../../LICENSE) file for full details.
