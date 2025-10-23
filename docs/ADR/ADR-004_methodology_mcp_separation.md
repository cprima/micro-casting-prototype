# ADR-004: Separation of Presentation (HTML) and Logic (MCP Server)

**Status:** Accepted
**Date:** 2025-10-23
**Context:** MCP Server Development Methodology - Architecture Decision

---

## Context

The methodology visualization system consists of:
- A **multi-version catalog** (`data.json`) with phases, nodes, gates, and evidence policies
- An **HTML/vanilla JS page** for visualization and user interaction
- An **MCP server** providing advisory, validation, and migration services

We need to decide how to distribute complexity between the presentation layer (HTML) and the logic layer (MCP server).

---

## Decision

**Adopt a strict separation:** HTML is a dumb renderer; MCP server carries all complexity.

### 1️⃣ Immutable Presentation Layer

The static **HTML + vanilla JS** page is a read-only renderer.

* **No schema validation, predicate parsing, or version logic in browser**
* Safe for GitHub Pages and offline use
* Any change to logic never forces UI rebuild
* HTML only:
  - Loads `data.json`
  - Displays phases/nodes/gates
  - Compares fingerprints (string equality only)
  - Manages local state (localStorage)

### 2️⃣ Data-at-Rest Contract

`data.json` is treated as a **database snapshot**, not executable code.

* Contains multiple catalog versions, frozen and human-readable
* Array structure: `[{version: "0.3.0", ...}, {version: "0.4.0-alpha", ...}]`
* HTML merely loads and displays it
* The MCP server ingests and compiles it at startup
* Each catalog has:
  - `$schema` reference for documentation only (not used by HTML)
  - `program.fingerprint` for state validation (string comparison)
  - `program.supersedes` for version lineage

### 3️⃣ Complexity Centralization

All reasoning, validation, and migration live in the **Python MCP server**.

* **Gate evaluation:** Interpret predicates, check state overlay, verify evidence
* **Evidence checks:** Match evidence policies with client-provided records
* **Predicate compilation:** Transform JSON predicates into executable rules
* **Easier testing, logging, and upgrades** in one language/runtime
* Keeps browser payload small and secure
* Tools provided:
  - `gate.evaluate(gate_id, state)` → pass/fail + diagnostics
  - `state.migrate(from_ver, to_ver, state)` → migration report
  - `catalog.diff(from_ver, to_ver)` → structural changes
  - `advisor.suggest(context, state)` → context-aware recommendations

### 4️⃣ Fail-Fast, Server-Side Validation

Version integrity, invariant checks, and fingerprint enforcement run once at server start.

* **Three-stage transformation pipeline:**
  1. `ingest.py` - Pick active/previous, strip bloat → `var/*.json`
  2. `validate.py` - Assert invariants, validate fingerprints, check gate ID uniqueness
  3. `compile.py` - Build indices, compile predicates, create advisory registry
* **Detects drift or malformed data** before exposure to clients
* Prevents inconsistent behavior between HTML views and backend logic
* **Current is canonical:** `levels`, `tags`, `global_gates` in previous must match current
* **Locked predicate grammar:** Only `status.state == done`, `has_evidence:<type>[:result]`, `has_contract`

### 5️⃣ Maintainability & Extensibility

The plain HTML stays stable for years; evolution happens in Python transforms and tools.

* **Lower maintenance cost** and minimal web-frontend expertise required
* Future complexity (advisor logic, schema enforcement, migrations) added only in server code paths
* **Clear boundaries:**
  - HTML: Presentation only
  - data.json: Immutable reference (versioned, fingerprinted)
  - MCP server: Business logic, validation, transformation

---

## Consequences

### Positive

✅ **HTML simplicity:** No complex JS libraries, no schema validation, no predicate parsing
✅ **Offline capable:** HTML works without MCP server for basic visualization
✅ **Security:** No eval(), no dynamic code generation in browser
✅ **Testing:** All logic testable in Python with full assertion/debugging tools
✅ **Versioning:** data.json evolution doesn't break HTML renderer
✅ **Fail-fast:** Errors caught at server startup, not at runtime in browser

### Negative

⚠️ **Duplication:** HTML shows structure; MCP server parses same structure
⚠️ **Round-trip:** Advanced features (gate evaluation, migration) require MCP server calls
⚠️ **Python dependency:** Full feature set needs Python MCP server running

### Neutral

➡️ **Data.json grows:** Multi-version array increases file size (~70KB for 2 versions)
➡️ **Transform scripts:** Adds 3 Python scripts (ingest/validate/compile) to maintain
➡️ **Cache layer:** `var/` directory with compiled outputs needs regeneration on data.json changes

---

## Alternatives Considered

### ❌ Embed logic in HTML/JavaScript
- **Rejected:** Would require duplicating validation, predicate parsing, and migration logic in JS
- Risk of HTML/Python logic divergence
- Harder to test, debug, and maintain

### ❌ Server-side rendered HTML
- **Rejected:** Loses offline capability and GitHub Pages compatibility
- Requires backend for every page view
- More infrastructure complexity

### ❌ Single-version catalog
- **Rejected:** Cannot support migration between versions
- Clients mid-project would be stranded on version transitions
- Loses version history and evolution tracking

---

## Implementation

### Data Structure
- Multi-version array in `data.json`
- Each catalog has: `$schema`, `program.fingerprint`, `program.supersedes`
- Schemas in `docs/schema/` for documentation (not runtime validation)

### Transformation Pipeline
```bash
make mcp-transform-all  # Runs all 3 stages
# Or individually:
make mcp-transform-ingest    # Stage 1
make mcp-transform-validate  # Stage 2
make mcp-transform-compile   # Stage 3
```

### MCP Server (Future)
- FastMCP (Python) with stdio transport
- Loads `var/*.json` files generated by transforms
- Provides 4 tools + resources (catalog/phase/node access)

---

## References

- [Methodology Data Schema](../schema/README.md)
- [Multi-Version Catalog Structure](../methodology/data.json)
- [Transformation Pipeline](../../apps/mcp-srv-mtdlgy_mcp/transforms/)
- [ADR-001: Monorepo Layout](./ADR-001_monorepo.md)
