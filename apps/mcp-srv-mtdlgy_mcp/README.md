# MCP Server: Methodology Advisory

**Stateless, read-only MCP server** providing advisory, validation, and migration services for the MCP Server Development Methodology.

## Architecture

This server implements a **strict separation** between presentation and logic:

- **HTML page** (`docs/methodology/`) - Dumb renderer, no validation, offline-capable
- **data.json** - Multi-version catalog, immutable database snapshot
- **MCP server** - All complexity: validation, gate evaluation, migrations, advisory

See [ADR-004](../../docs/adr/ADR-004_methodology_mcp_separation.md) for detailed rationale.

## Data Transformation Pipeline

The server uses a **3-stage transformation pipeline** that runs at startup:

### Stage 1: Ingest
Pick active (first non-frozen) and previous (via supersedes) catalog versions, strip runtime bloat (`_search_stemmed`).

**Output:** `var/catalog.current.json`, `var/catalog.previous.json`

### Stage 2: Validate
Fail-fast checks: invariants (current is canonical), fingerprint format (hex-64 SHA-256), gate ID uniqueness.

**Output:** Validation pass/fail (no files)

### Stage 3: Compile
Build indices (node→phase, phase→nodes, tags, door/level buckets), partially compile predicates, create advisory registry.

**Output:** `var/compiled.rules.json`

## Running Transforms

```bash
# From repository root
make mcp-transform-all       # Run all 3 stages
make mcp-transform-ingest    # Stage 1 only
make mcp-transform-validate  # Stage 2 only
make mcp-transform-compile   # Stage 3 only
make mcp-transform-clean     # Remove var/ outputs
```

## Data Structure

**Input:** `../../docs/methodology/data.json` (multi-version array)

**Outputs:**
- `var/catalog.current.json` - Active catalog (e.g., v0.4.0-alpha)
- `var/catalog.previous.json` - Previous catalog (e.g., v0.3.0)
- `var/compiled.rules.json` - Indices, compiled gates, advisory registry

## Predicate Grammar (Locked)

Only 3 condition types are supported:

1. **`status.state == done`** - Node completion check
2. **`has_evidence:<type>[:result]`** - Evidence presence/result check (e.g., `has_evidence:test_report`, `has_evidence:security:meets`)
3. **`has_contract`** - Contract definition check

## MCP Server (Future)

**Framework:** FastMCP (Python, stdio transport)

**Tools (Planned):**
- `gate.evaluate(gate_id, state)` → GateEvaluation
- `state.migrate(from_version, to_version, state)` → MigrationReport
- `catalog.diff(from_version, to_version)` → CatalogDiff
- `advisor.suggest(context, state)` → Suggestions

**Resources (Planned):**
- `methodology://catalog/{version}` - Full catalog access
- `methodology://phase/{phase_id}` - Phase details
- `methodology://node/{node_id}` - Node details

## Design Principles

1. **Stateless** - Server doesn't track client state; client provides state overlay
2. **Read-only** - No mutations, no persistence layer
3. **Advisory** - Server suggests, client decides
4. **Fail-fast** - Validation errors caught at startup, not runtime
5. **Minimal** - Stdlib-only transforms, FastMCP for server runtime

## Dependencies

**Transforms:** Python 3.10+ stdlib only (no external packages)

**Server (future):** FastMCP

## File Structure

```
apps/mcp-srv-mtdlgy_mcp/
├── transforms/          # 3-stage pipeline
│   ├── utils.py        # Shared utilities (8 functions)
│   ├── ingest.py       # Stage 1: Pick versions, strip bloat
│   ├── validate.py     # Stage 2: Fail-fast checks
│   └── compile.py      # Stage 3: Build indices, compile predicates
├── var/                # Generated outputs (gitignored)
│   ├── catalog.current.json
│   ├── catalog.previous.json
│   └── compiled.rules.json
├── pyproject.toml      # Package metadata
└── README.md           # This file
```

## References

- [Multi-Version Catalog](../../docs/methodology/data.json)
- [Catalog Schemas](../../docs/schema/)
- [ADR-004: Separation of Presentation and Logic](../../docs/adr/ADR-004_methodology_mcp_separation.md)
- [ADR-001: Monorepo Layout](../../docs/adr/ADR-001_monorepo.md)
- [ADR-003: pyproject.toml Standardization](../../docs/adr/ADR-003_pyproject_standardization.md)
