# **ADR 001 – uv Workspaces for Monorepo Layout**

## Status

Accepted

## Context

* Need to manage multiple applications and shared libraries in a single repository
* Require consistent dependency resolution across all projects
* Support both flat (`apps/*`) and nested (`apps/uipac/*`) project hierarchies
* Enable rapid development with editable installs for shared libraries

## Decision

Use **uv workspaces** with glob-based member discovery:

```toml
[tool.uv.workspace]
members = ["libs/*", "apps/*", "apps/uipac/*"]
```

* Single `uv.lock` file at repository root
* Shared libraries referenced via `{ workspace = true }`
* Root pyproject.toml defines common dependencies

## Rationale

| Goal / Requirement           | How the decision addresses it                        |
| ---------------------------- | ---------------------------------------------------- |
| Dependency consistency       | Single lock file ensures identical versions          |
| Rapid development            | Editable installs - no rebuild for lib changes       |
| Auto-discovery               | Glob patterns find projects automatically            |
| Hierarchical organization    | Support both flat and nested app structures          |
| Shared workflow              | Single `uv sync` command for entire monorepo         |
| Future scalability           | Pre-configured for `apps/uipac/*` (not yet created)  |

## Alternatives Considered

1. **Poetry workspaces** – Less mature workspace support, slower resolver
2. **pip-tools with constraints files** – Manual coordination, no auto-discovery
3. **Separate repos** – Increases friction, version skew, complex CI/CD

## Consequences

### Positive

* Zero-configuration discoverability for new projects
* Fast dependency resolution (Rust-based uv)
* Native workspace dependency references
* Consistent Python >=3.10 across all projects

### Negative

* uv is newer tooling (adoption risk)
* Team must learn uv-specific patterns
* Glob patterns must be updated for new hierarchy levels

### Neutral

* Requires hatchling as build backend across all projects
* Single lock file grows with monorepo size

## Related

* Implementation: `pyproject.toml:9-10`
* Example workspace ref: `apps/sitemap-crawler/pyproject.toml:21-22`
* uv docs: https://docs.astral.sh/uv/concepts/workspaces/
