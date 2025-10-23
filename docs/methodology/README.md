# MCP Server Development Methodology

**Version:** v0.4.2
**Framework:** Decision-Driven Delivery with Portable State Management

A decision-driven delivery framework for building Model Context Protocol (MCP) servers with evidence-based validation, transparent decision accountability, and team collaboration through portable state files.

## 🎯 Overview

This methodology shifts from static checklists to a decision-driven approach:

- **From:** Phase compliance → **To:** Decision evidence flow
- **From:** Prescriptive steps → **To:** Typed decisions with clear reversibility
- **From:** Documentation after build → **To:** Evidence before build

## 📂 Files

### Core Application
- **`index.html`** - Interactive web interface (v0.4.2) with state management
- **`data.json`** - Catalog (immutable): phases, decision nodes, gates, evidence requirements
- **`state.json`** - State (mutable): your progress, decisions, evidence (git-ignored by default)
- **`state.example.json`** - Example state file showing all features

### Documentation
- **`development.html`** - Visual timeline of methodology evolution (v0.1.0 → v0.4.2)
- **`schema-v0.3.0-proposal.yaml`** - Schema documentation and transformation guide
- **`schema-gate-predicates.yaml`** - Structured gate predicate types
- **`tag-canonicalization.yaml`** - Canonical tag set and mapping rules

### Architecture (v0.4.0+)
The methodology now separates **immutable catalog** (data.json) from **mutable state** (state.json):
- **Catalog** defines the structure: what decisions exist, what evidence is needed
- **State** tracks your progress: which nodes are done, decisions made, evidence collected
- **Portable** state files enable team collaboration and version control

## 🔢 Version Strategy

This methodology uses **three independent versions** that evolve separately:

| Version | Current | What | When to Bump |
|---------|---------|------|--------------|
| **Frontend** | v0.4.2 | UI/UX features (HTML/JS/CSS) | New UI features, styling, UX improvements |
| **Catalog Schema** | 0.3.0 | data.json structure | Changes to catalog JSON schema |
| **State Schema** | 0.4.0 | state.json structure | Changes to state JSON schema |

**Current Compatibility:** Frontend v0.4.2 works with Catalog 0.3.0 and State 0.4.0

This allows the frontend to evolve independently of data schemas. For example, v0.4.1 added decision input fields (frontend change) without requiring catalog or state schema changes.

For detailed version update guidelines, see `VERSION` file.

## 🚪 Decision Door Types

### One-Way Door
Irreversible or very costly to reverse. **Requires:** ADR, spike validation, careful consideration.

**Examples:** Database choice, API design patterns, authentication architecture

### Two-Way Door
Easily reversible with minimal cost.

**Examples:** UI layouts, configuration values, internal utilities

### Guardrail
Constraints that prevent bad outcomes.

**Examples:** Input validation, rate limits, security policies

### Operational
Runtime tuning and operational decisions.

**Examples:** Timeout values, observability settings, performance limits

## 🎯 Decision Levels

- **Required:** Must complete for production readiness (core architecture, security)
- **Recommended:** Strongly suggested for quality (should complete unless good reason to skip)
- **Optional:** Nice-to-have enhancements (advanced features for mature implementations)

## 📊 Evidence Types

| Type | Description | Example |
|------|-------------|---------|
| **spike** | Time-boxed experiment to validate technical approach | OAuth library compatibility test |
| **test_report** | Test coverage and quality assurance results | Unit/integration test outcomes |
| **security** | Security reviews and compliance checks | OWASP Top 10 compliance, vulnerability scans |
| **perf** | Performance benchmarks and load tests | Latency measurements, resource usage |
| **ops_runbook** | Operational procedures and deployment guides | Incident response docs, deployment steps |

### Evidence Timing

- **@gate** - Required before passing phase gate (must complete to proceed)
- **@completion** - Required when marking decision node done (final validation)
- **@always** - Must be maintained continuously throughout lifecycle

## 📋 Phases

1. **Getting Started** - Foundational architectural decisions
2. **Core Features** - Essential functionality and contracts
3. **Production Ready** - Security, performance, testing
4. **Advanced** - Operational excellence and discovery

## 🏷️ Canonical Tags

- **naming** - Naming conventions and patterns
- **architecture** - Structural decisions
- **security** - Auth, validation, encryption
- **performance** - Optimization, caching, limits
- **testing** - Quality assurance strategies
- **observability** - Logging, monitoring, metrics
- **tooling** - Tool design and contracts
- **formats** - Data formats and schemas
- **transport** - Network protocols
- **integration** - APIs and interoperability
- **ops** - Deployment and operations
- **ux** - Developer experience

## 📝 ADR (Architecture Decision Record)

Documents irreversible (one-way door) decisions with:

- **Context** - What situation prompted this decision?
- **Decision** - What did we choose and why?
- **Consequences** - What are the trade-offs and implications?
- **Rollback Plan** - How can we reverse this if needed?

## 🚀 Usage

### View Online

Open `index.html` in a web browser to:

- Track progress across all decision nodes
- Enter decision values (e.g., server naming pattern)
- Filter by level (required/recommended/optional) and door type
- View evidence requirements and block dependencies
- Mark nodes as completed
- **Export** state to shareable JSON file
- **Import** state from teammates

### State Management Workflow (v0.4.0+)

```bash
# 1. Work Locally
# - Progress auto-saves to browser localStorage
# - Enter decision values in input fields (e.g., "analytics_mcp" for server name)

# 2. Export Your Progress
# - Click "Export State" button
# - Downloads: analytics_mcp-state-2025-10-23.json
# - Filename uses your server naming decision!

# 3. Share with Team
git add docs/methodology/analytics_mcp-state-2025-10-23.json
git commit -m "chore: update methodology progress"
git push

# 4. Import Teammate's Progress
# - Click "Import State" button
# - Select their state.json file
# - Review reconciliation summary
# - Confirm import → progress synchronized!

# 5. Collaborate
# - Both team members now have same progress
# - Decision values (like server name) shared
# - Evidence and notes synchronized
```

### Local Development

```bash
# Serve locally
python -m http.server 8000
# Visit http://localhost:8000
```

### GitHub Pages

This methodology is designed to work seamlessly with GitHub Pages. The `.nojekyll` file in the docs directory ensures proper rendering.

## 📊 Data Structure

### Catalog (data.json) - v0.3.0
Immutable structure defining the methodology:

- **Sparse encoding** - Omit null/empty fields (38% size reduction)
- **Semantic IDs** - Human-readable like `auth-oauth21` vs `pr-3`
- **Evidence policy** - Requirements instead of pre-filled stubs
- **Blocks with reasons** - Explicit dependency explanations
- **Effort ranges** - Honest uncertainty with confidence levels
- **Tag reduction** - 20 → 12 canonical tags
- **Computed types** - Derived from tags at render time
- **Decision inputs** (v0.4.1) - Metadata-driven input fields for capturing decisions

### State (state.json) - v0.4.0
Mutable progress tracking:

```json
{
  "state_version": "0.4.0",
  "program_id": "mcp-server-delivery",
  "catalog_version": "0.3.0",
  "catalog_fingerprint": "sha256:...",
  "metadata": {
    "created_at": "2025-10-23T14:30:00Z",
    "updated_at": "2025-10-23T16:45:00Z"
  },
  "nodes": {
    "server-naming": {
      "status": "done",
      "done_at": "2025-10-23T14:35:00Z",
      "decision_value": "analytics_mcp",
      "notes": "Chose Python convention",
      "artifacts": {
        "adr_ref": "docs/adr/001-server-naming.md"
      },
      "evidence": [...]
    }
  },
  "integrity": {
    "state_fingerprint": "sha256:...",
    "migrations_applied": []
  }
}
```

**Key features:**
- SHA-256 fingerprinting for integrity verification
- Sparse encoding (only meaningful state saved)
- Reconciliation support (handles catalog evolution)
- Backward compatible (auto-migrates from v0.3.x)

## 🎨 Styling

Uses **Solarized Light** color scheme for comfortable reading:

- Base background: `#fdf6e3` (warm cream)
- Content panels: `#eee8d5` (light beige)
- Primary text: `#657b83` (blue-gray)
- Headings: `#073642` (dark blue-gray)
- Accent: `#268bd2` (blue), `#859900` (green)

## 🔄 Version History

- **v0.4.2** - Checkbox repositioned to right side, version harmonization drill test
- **v0.4.1** - Decision input fields with metadata-driven architecture, scalable input system
- **v0.4.0** - State management revolution: portable state files, export/import, reconciliation, smart filename generation
- **v0.3.2** - Solarized Light theme, comprehensive footer with reference documentation
- **v0.3.0** - Schema v0.3.0 with semantic IDs, sparse encoding, evidence policy
- **v0.2.1** - Initial transformation-based schema
- **v0.2.0** - Original checklist-based model

## 🤝 Contributing

This methodology is designed for iterative improvement. Feedback and enhancements welcome!

## 📄 License

See project root LICENSE file.
