# Sitemap Crawler Roadmap

Version-based feature roadmap showing implemented vs planned features.

---

## Current Status: v0.1.0 ✅ COMPLETE

**Release Date**: 2025-01-22

### ✅ Implemented Features

**Core Functionality:**
- ✅ Basic app structure under `apps/sitemap-crawler/`
- ✅ llms.txt parser with markdown link support
- ✅ XML sitemap parser with recursive sitemap index support
- ✅ Local filesystem storage with `BaseStorage` interface
- ✅ Integration with `crawling` library (Crawl4AI) for markdown conversion
- ✅ Synchronous crawling (one URL at a time)

**CLI Commands:**
- ✅ `sitemap-crawler list` - Show configured sites
- ✅ `sitemap-crawler crawl <name>` - Crawl single site
- ✅ `sitemap-crawler crawl-all` - Crawl all sites
- ✅ `--dry-run` - Preview URLs without crawling
- ✅ `--verbose` - Enable debug logging

**Configuration:**
- ✅ config.yaml with 2 example sites (modelcontextprotocol.io, docs.uipath.com)
- ✅ URL filtering (pattern matching, contains)
- ✅ Per-site base_dir configuration (different output locations per site)
- ✅ Environment variable expansion (`${VAR}`)
- ✅ Output path templates (`{domain}`, `{date}`)

**File Handling:**
- ✅ File naming safety (sanitize special characters)
- ✅ Cross-platform path support (Windows/Linux/Mac)
- ✅ Automatic parent directory creation

**Logging:**
- ✅ Basic console logging
- ✅ Detailed filter logging (shows before/after counts)
- ✅ Sitemap index vs regular sitemap differentiation
- ✅ Per-URL crawl progress

**Documentation:**
- ✅ Comprehensive README.md
- ✅ Example config.yaml with comments
- ✅ ROADMAP.md (this file)
- ✅ CC-BY 4.0 LICENSE

### 🎯 Success Criteria Met
- ✅ Successfully crawl https://modelcontextprotocol.io/llms.txt (43 URLs)
- ✅ Successfully crawl English URLs from https://docs.uipath.com/sitemap.xml (~32K URLs)
- ✅ Output markdown files to configurable directories
- ✅ Per-site storage configuration working

---

## Next: v0.2.0 - Production Ready ✅ COMPLETE

**Goal**: Add resilience, observability, and production-grade features

**Completed**: 2025-10-22

### 🚧 Recommended Priority Order

#### **Phase 1: Best-in-Class Logging** 📊 ✅ COMPLETE

**Why First**: Essential for debugging large crawls, understanding performance bottlenecks

- ✅ **Structured logging with `structlog`**
  - JSON output format for machine parsing
  - Human-readable console output for development
  - Correlation IDs to trace requests across components
  - Context binding (site name, URL, crawl session)

- ✅ **Performance metrics**
  - Request duration tracking
  - Bytes downloaded per request
  - Average speed (URLs/second, MB/second)
  - Crawl session metrics with summary

- ✅ **Log levels properly implemented**
  - DEBUG: Filter details, parser internals, HTTP requests
  - INFO: Crawl progress, major operations, filtering results
  - WARNING: Skipped URLs, retries
  - ERROR: Failed requests, exceptions with stack traces
  - Configurable via `--log-level` CLI option

- ✅ **Configurable log outputs**
  - Console (human-readable with colors via structlog.dev.ConsoleRenderer)
  - File (JSON lines for log aggregation at logs/sitemap-crawler.log)
  - Rotation policy (10MB files, 5 backups)
  - Configurable via `--log-file` CLI option

#### **Phase 2: Progress Tracking** 📈 ✅ COMPLETE

**Why Next**: User feedback for long-running crawls

- ✅ **Progress bar with `tqdm`**
  - Visual progress for URL fetching
  - Nested progress bars (sites → URLs)
  - ETA calculation
  - Speed indicator (URLs/s)

- ✅ **Crawl statistics**
  - Real-time counters (success/fail/skipped)
  - Total bytes downloaded
  - Total duration
  - Summary report at end

#### **Phase 3: Resilience & Politeness** 🛡️ ✅ COMPLETE

**Why Next**: Required for production use on real sites

- ✅ **Retry logic with exponential backoff**
  - Configurable max retries (default: 3)
  - Exponential backoff (1s, 2s, 4s, 8s...)
  - Retry on network errors, HTTP 5xx
  - Don't retry on HTTP 4xx (client errors)

- ✅ **Rate limiting**
  - Configurable delay between requests (default: 1s)
  - Per-domain rate limiting
  - Respect HTTP 429 (Too Many Requests)
  - Adaptive rate limiting

- ✅ **Custom User-Agent**
  - Configurable User-Agent string
  - Default: `sitemap-crawler/0.2.0 (+https://github.com/...)`
  - Per-site override

- ✅ **Timeouts from config**
  - Request timeout (default: 30s)
  - Connection timeout (default: 10s)
  - Per-site override

- ❌ **Config reload on signal (SIGHUP)** (Deferred to v0.5.0)
  - Reload config.yaml without stopping crawl
  - Update settings for queued URLs (not in-progress)
  - Useful for long-running crawls with many sites
  - Handle config errors gracefully (keep old config on error)

#### **Phase 4: Resource Limits** ⚙️ ✅ COMPLETE

**Why Next**: Safety constraints for production

- ✅ **Configurable limits**
  - Max URLs per site (default: 50000)
  - Max file size (default: 10MB, skip larger)
  - Max total size per crawl (default: 5000MB)
  - Max crawl duration (timeout, default: unlimited)

- ✅ **Content validation**
  - Empty page detection (skip if < 100 chars)
  - Minimum content threshold (configurable)
  - HTML error page detection (404/500 saved as HTML)

#### **Phase 5: Enhanced File Handling** 📁 ✅ COMPLETE

- ✅ **Collision detection**
  - Detect duplicate filenames
  - Append counter: `page.md`, `page-1.md`, `page-2.md`
  - Log collisions

- ✅ **Improved path sanitization**
  - Handle extremely long URLs (> 260 chars on Windows)
  - Hash-based filenames for very long URLs (MD5 hash truncated to 8 chars)
  - Preserve URL structure option

### ❌ Not Implemented (Deferred to v0.5.0)

- ❌ SMBStorage implementation (BaseStorage interface exists, implementation deferred)
- ❌ Config reload on signal (SIGHUP)

### 📋 Success Criteria for v0.2.0

- ✅ Crawl 1000+ URLs from docs.uipath.com with retry logic
- ✅ Handle network failures gracefully (exponential backoff)
- ✅ JSON-structured logs available for analysis
- ✅ Progress bar shows ETA and speed
- ✅ Rate limiting prevents server overload
- ✅ All logs include correlation IDs for tracing
- ✅ Resource limits enforced (max URLs, file size, content validation)
- ✅ Filename collision detection working

---

## v0.2.1 - robots.txt Compliance ✅ COMPLETE

**Goal**: Respect website robots.txt policies (from v0.5.0 roadmap, implemented early)

**Completed**: 2025-10-23

### ✅ Implemented Features

**robots.txt Compliance:**
- ✅ Automatic robots.txt fetching per domain
- ✅ URL filtering based on disallow rules
- ✅ crawl-delay directive support (overrides configured rate limit)
- ✅ Per-domain caching (1 hour default, configurable)
- ✅ Configurable enable/disable via config.yaml
- ✅ Graceful fallback on fetch errors (allows by default)
- ✅ Proper User-Agent identification

### 📋 Success Criteria for v0.2.1

- ✅ Fetch and parse robots.txt successfully
- ✅ Respect disallow directives
- ✅ Honor crawl-delay when specified
- ✅ Cache robots.txt to avoid repeated fetches
- ✅ Gracefully handle missing robots.txt (404)

---

## v0.3.0 - Architecture Cleanup ✅ COMPLETE

**Release Date**: 2025-10-23

**Goal**: Clean separation of concerns between libs/crawling and apps/sitemap-crawler

**Status**: Complete

### ✅ Implemented Features

**libs/crawling Refactoring:**
- ✅ Minimal wrapper library (pinning crawl4ai==0.7.6 only)
- ✅ Re-exports crawl4ai types (BrowserConfig, CrawlerRunConfig, CacheMode, CrawlResult)
- ✅ Returns full CrawlResult (not just markdown string)
- ✅ No hardcoded configuration decisions
- ✅ Updated documentation reflecting Unix philosophy: "Do one thing well"

**apps/sitemap-crawler Configuration:**
- ✅ Global `browser:` settings in config.yaml (headless, viewport, user_agent)
- ✅ Global `crawl_defaults:` settings with pruning configuration
- ✅ Per-site `crawl4ai:` overrides continue to work
- ✅ Config class builds BrowserConfig and CrawlerRunConfig from YAML

**Future-Proofing:**
- ✅ Access to response_headers (enables Last-Modified/ETag for incremental updates)
- ✅ Access to status_code and full CrawlResult metadata
- ✅ Clean foundation for v0.5.0 advanced features

### 🎯 Success Criteria Met
- ✅ Clean separation: libs = pinning only, apps = all configuration
- ✅ No hardcoded browser/run config in library layer
- ✅ Existing crawls work unchanged with new architecture
- ✅ Full CrawlResult available for future features

---

## v0.4.0 - Distributed Work Queue 💭 PLANNED

**Goal**: Filesystem-based distributed crawling with resumable state and incremental updates

**Status**: Design phase

### Problem Statement

**Current Limitations:**
- No persistent state → cannot resume failed crawls
- No work distribution → single process only
- No incremental updates → re-crawls everything
- Doesn't scale for large sites (34K+ URLs like UIPath)

**Why Not SQLite:**
- Single writer bottleneck defeats concurrency
- Network filesystem corruption risk (SMB/NFS + SQLite = bad)
- Lock contention when multiple workers compete

### Core Architecture

**State lives in output directory:**
```
{base_output_dir}/.crawl-state/{site_name}/
├── tickets/
│   ├── pending/
│   │   ├── 0001.json    # URLs 0-99
│   │   ├── 0002.json    # URLs 100-199
│   │   └── ...
│   ├── claimed/
│   │   └── 0003.json    # Worker-1 processing
│   ├── completed/
│   │   └── 0001.json    # Done
│   └── failed/
│       └── 0042.json    # Failed after retries
├── manifest.json        # Crawl metadata
├── url-index.json       # URL → {last_modified, etag, hash, status}
└── workers/
    ├── worker-1.lock    # Heartbeat file
    └── worker-2.lock
```

### Features

**Phase 1: Ticket-Based Work Distribution**
- [ ] Split URL list into tickets (default: 100 URLs per ticket)
- [ ] Atomic ticket claiming via filesystem rename()
- [ ] Worker heartbeat mechanism (detect dead workers)
- [ ] Automatic stale ticket recovery
- [ ] Progress tracking per ticket

**Phase 2: Incremental Updates**
- [ ] URL index tracking (Last-Modified, ETag, content hash)
- [ ] Conditional HTTP requests (If-Modified-Since, If-None-Match)
- [ ] Skip unchanged content (HTTP 304 or matching hash)
- [ ] Detect removed URLs (delete from output)
- [ ] Access to CrawlResult.response_headers (implemented in v0.3.0)

**Phase 3: Distributed Workers**
- [ ] Multi-process workers on same machine
- [ ] Multi-machine workers (shared network filesystem)
- [ ] No central coordinator required
- [ ] Automatic load balancing via ticket claiming

### Ticket Format

```json
{
  "ticket_id": "0001",
  "site": "uipath-docs",
  "created_at": "2025-10-23T12:00:00Z",
  "urls": [
    {
      "url": "https://docs.uipath.com/page1",
      "last_seen": "2025-10-23T12:00:00Z"
    }
  ],
  "size": 100,
  "claimed_by": null,
  "claimed_at": null,
  "completed_at": null,
  "progress": {
    "total": 100,
    "success": 0,
    "failed": 0,
    "skipped": 0
  }
}
```

### URL Index Format

```json
{
  "https://docs.uipath.com/page1": {
    "last_modified": "2025-10-20T10:00:00Z",
    "etag": "\"abc123\"",
    "content_hash": "sha256:...",
    "status_code": 200,
    "last_crawled": "2025-10-23T12:00:00Z",
    "file_path": "docs/uipath.com/en/page1.md"
  }
}
```

### Atomic Operations

**Ticket State Transitions (using filesystem rename):**
```
pending/0001.json → claimed/0001.json    # Atomic claim
claimed/0001.json → completed/0001.json  # Atomic complete
claimed/0001.json → failed/0001.json     # Atomic fail
```

**Worker Coordination:**
- Heartbeat files updated every 5 seconds
- Workers declared dead after 60s without heartbeat
- Stale tickets automatically reclaimed to pending/

### CLI Commands

```bash
# Prepare tickets for a site
sitemap-crawler prepare uipath-docs

# Work on tickets (single worker)
sitemap-crawler work uipath-docs

# Work with multiple processes
sitemap-crawler work uipath-docs --workers 4

# Resume failed crawl
sitemap-crawler resume uipath-docs

# Show progress
sitemap-crawler status uipath-docs
```

### Configuration

```yaml
settings:
  crawl_state:
    enabled: true                    # Enable ticket system
    ticket_size: 100                 # URLs per ticket
    heartbeat_interval: 5            # Seconds
    heartbeat_timeout: 60            # Declare worker dead after 60s
    incremental: true                # Enable incremental updates

sites:
  - name: uipath-docs
    source: https://docs.uipath.com/sitemap.xml
    crawl_state:
      ticket_size: 500               # Override for large sites
```

### Benefits

✅ **Distributed**: Multiple workers, multiple machines
✅ **Resumable**: Pickup where left off after crash
✅ **Incremental**: Only crawl changed content
✅ **Observable**: Clear progress via ticket status
✅ **No Database**: Pure filesystem, works on SMB/NFS
✅ **Atomic**: Filesystem rename provides coordination
✅ **Scalable**: 34K URLs → 340 tickets (@ 100 URLs/ticket)
✅ **State with Data**: Travels with output directory

### Success Criteria

- [ ] Prepare 34K UIPath URLs into ~340 tickets
- [ ] 4 workers claim tickets concurrently without conflicts
- [ ] Kill worker-2 mid-crawl, tickets reclaimed automatically
- [ ] Resume crawl after crash (only pending tickets re-crawled)
- [ ] Incremental re-crawl skips unchanged URLs (via Last-Modified/ETag)
- [ ] Network filesystem test (SMB mount, multiple machines)

---

## Backlog: v1.9.0 - Future Ideas 🔮

**Status**: Ideas only, not committed

**Note**: Incremental updates and distributed crawling moved to v0.4.0

### Async/Concurrent Crawling (within single process)
- Async implementation using `asyncio` + crawl4ai's arun_many()
- Concurrent URL fetching (configurable max workers)
- Connection pooling (reuse HTTP connections)
- 5-10x performance improvement for large crawls

### Advanced Sitemap Support
- Compressed sitemaps (.xml.gz)
- RSS/Atom feed parsing
- Custom sitemap formats (extensible parser system)

### Crawl Manifest
- JSON manifest per crawl: `manifest.json`
- Contains: timestamp, URL list, status codes, hashes
- Enable auditing and debugging

### Enhanced Filtering
- Regex pattern matching
- Multiple filter types (AND/OR logic)
- Domain whitelist/blacklist
- Content-type filtering

### Additional Storage Backends
- SMBStorage implementation (smbprotocol)
- S3/MinIO storage backend
- WebDAV storage backend

### Observability
- Prometheus metrics export
- Crawl history database (past runs)
- Error report generation

### Post-processing & Integration
- Post-crawl hooks (run arbitrary scripts)
- Index generation (SUMMARY.md, index.json)
- Vector embedding preparation
- Full-text search index (Elasticsearch/Meilisearch)

### Advanced Content Extraction
- CSS/XPath selectors for specific content sections
- Readability mode (extract main content only)
- Table extraction and conversion
- Image downloading and local storage

### Scheduling & Automation
- Built-in scheduler (cron-like)
- Watch mode (re-crawl on sitemap changes)
- Webhook triggers
- GitHub Actions integration

### Authentication
- HTTP Basic/Digest auth support
- OAuth2 flow support
- Cookie-based session handling
- API key authentication

### UI/Dashboard
- Web UI for monitoring crawls
- Real-time progress dashboard
- Crawl configuration editor
- Historical analytics

### Content Transformation
- Pandoc integration for multiple output formats
- HTML → PDF conversion
- Archive format support (.warc, .har)

### Notification System
- Email notifications on completion
- Slack/Discord webhooks
- Error alerting

---

## Version History

| Version | Status | Date | Notes |
|---------|--------|------|-------|
| 0.1.0 | ✅ **Released** | 2025-01-22 | Initial prototype with basic crawling |
| 0.2.0 | ✅ **Released** | 2025-10-22 | Production-ready features (logging, retry, limits, progress, validation) |
| 0.2.1 | ✅ **Released** | 2025-10-23 | robots.txt compliance (from v0.5.0 roadmap) |
| 0.3.0 | ✅ **Released** | 2025-10-23 | Architecture cleanup (libs/crawling minimal wrapper, config separation) |
| 0.4.0 | 💭 Planned | TBD | Distributed work queue (filesystem-based tickets, incremental updates) |
| 1.9.0 | 🔮 Backlog | TBD | Future ideas |

---

## Immediate Next Steps (Recommended Order)

1. ✅ ~~**Implement structured logging with `structlog`**~~ (COMPLETE)
   - ✅ JSON output format
   - ✅ Correlation IDs
   - ✅ Performance metrics
   - ✅ Multiple output targets (console + file)

2. ✅ ~~**Add progress tracking with `tqdm`**~~ (COMPLETE)
   - ✅ Visual progress bars
   - ✅ Speed indicators
   - ✅ ETA calculation

3. ✅ ~~**Implement retry logic**~~ (COMPLETE)
   - ✅ Exponential backoff
   - ✅ Configurable max retries
   - ✅ Smart retry (only on network/5xx errors)

4. ✅ ~~**Add rate limiting**~~ (COMPLETE)
   - ✅ Configurable delays
   - ✅ Per-domain limits
   - ✅ HTTP 429 handling

5. ✅ ~~**Resource limits from config**~~ (COMPLETE)
   - ✅ Max URLs, file size, duration
   - ✅ Content validation
   - ✅ Graceful limit handling
   - ✅ Filename collision detection
   - ✅ Long URL handling

**Next: v0.4.0 - Distributed Work Queue**
- Filesystem-based ticket system for work distribution
- Incremental updates via Last-Modified/ETag headers
- Multi-worker support (multi-process, multi-machine)
- Resumable crawls after crashes
- State lives with data in output directory

---

## Contributing

Features are prioritized based on:
1. **User demand** - What users actually need
2. **Implementation complexity** - Low-hanging fruit first
3. **Dependencies** - Foundation features before advanced ones
4. **Maintenance burden** - Sustainable long-term

To propose a feature:
1. Check if it's already in the backlog
2. Open an issue describing the use case
3. Discuss implementation approach
4. Submit PR if approved

---

## Author

Christian Prior-Mamulyan (cprior@gmail.com)

## License

CC-BY 4.0 - See [LICENSE](../../LICENSE)
