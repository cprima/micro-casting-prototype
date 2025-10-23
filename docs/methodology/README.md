# MCP Server Development Methodology

**Version:** v0.3.2
**Framework:** Decision-Driven Delivery

A decision-driven delivery framework for building Model Context Protocol (MCP) servers with evidence-based validation and transparent decision accountability.

## 🎯 Overview

This methodology shifts from static checklists to a decision-driven approach:

- **From:** Phase compliance → **To:** Decision evidence flow
- **From:** Prescriptive steps → **To:** Typed decisions with clear reversibility
- **From:** Documentation after build → **To:** Evidence before build

## 📂 Files

- **`index.html`** - Interactive web interface for tracking methodology progress
- **`data.json`** - Methodology data (phases, decision nodes, gates, evidence requirements)
- **`schema-v0.3.0-proposal.yaml`** - Schema documentation and transformation guide
- **`schema-gate-predicates.yaml`** - Structured gate predicate types
- **`tag-canonicalization.yaml`** - Canonical tag set and mapping rules

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
- Filter by level (required/recommended/optional) and door type
- View evidence requirements and block dependencies
- Mark nodes as completed (progress saved to localStorage)

### Local Development

```bash
# Serve locally
python -m http.server 8000
# Visit http://localhost:8000
```

### GitHub Pages

This methodology is designed to work seamlessly with GitHub Pages. The `.nojekyll` file in the docs directory ensures proper rendering.

## 📊 Data Structure (v0.3.2)

Key improvements in v0.3.2:

- **Sparse encoding** - Omit null/empty fields (38% size reduction)
- **Semantic IDs** - Human-readable like `auth-oauth21` vs `pr-3`
- **Evidence policy** - Requirements instead of pre-filled stubs
- **Blocks with reasons** - Explicit dependency explanations
- **Effort ranges** - Honest uncertainty with confidence levels
- **Tag reduction** - 20 → 12 canonical tags
- **Computed types** - Derived from tags at render time

## 🎨 Styling

Uses **Solarized Light** color scheme for comfortable reading:

- Base background: `#fdf6e3` (warm cream)
- Content panels: `#eee8d5` (light beige)
- Primary text: `#657b83` (blue-gray)
- Headings: `#073642` (dark blue-gray)
- Accent: `#268bd2` (blue), `#859900` (green)

## 🔄 Version History

- **v0.3.2** - Solarized Light theme, comprehensive footer with reference documentation
- **v0.3.0** - Schema v0.3.0 with semantic IDs, sparse encoding, evidence policy
- **v0.2.1** - Initial transformation-based schema
- **v0.2.0** - Original checklist-based model

## 🤝 Contributing

This methodology is designed for iterative improvement. Feedback and enhancements welcome!

## 📄 License

See project root LICENSE file.
