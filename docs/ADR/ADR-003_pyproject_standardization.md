# **ADR 003 – pyproject.toml Standardization**

## Status

Accepted

## Context

* Workspace contains multiple packages (libs/*, apps/*)
* Inconsistent metadata across pyproject.toml files caused drift
* `libs/crawling` lacked readme, authors, license fields
* Version strategy unclear (0.0.1 vs 0.1.0)
* Future packages need clear template to follow

## Decision

Standardize all workspace packages with full metadata:

```toml
[project]
name = "package-name"
version = "0.x.y"                    # Semantic versioning
description = "One-line purpose"
readme = "README.md"
authors = [
    {name = "Christian Prior-Mamulyan", email = "cprior@gmail.com"}
]
license = {file = "../../LICENSE"}   # Relative path to root LICENSE
requires-python = ">=3.10"
dependencies = [...]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/package_name"]
```

**Version strategy**: Semantic versioning for all packages (0.x.y for pre-1.0)

**Exception**: Root `pyproject.toml` stays minimal (workspace coordinator, not published)

## Rationale

| Goal / Requirement           | How the decision addresses it                        |
| ---------------------------- | ---------------------------------------------------- |
| Package discoverability      | Full metadata enables PyPI publishing if needed      |
| Consistent attribution       | All packages reference same authors                  |
| License clarity              | Explicit license reference from each package         |
| Documentation link           | README declared in package metadata                  |
| Version semantics            | 0.1.0 = working features, 0.0.1 = experimental       |
| Build reproducibility        | Consistent hatchling configuration                   |
| Future scalability           | Clear template for new packages                      |

## Implementation Rules

**Required fields for all workspace packages:**
1. `name` - Package name (matches directory)
2. `version` - Semantic versioning (0.x.y)
3. `description` - One-line purpose
4. `readme` - Path to README.md
5. `authors` - Consistent workspace attribution
6. `license = {file = "../../LICENSE"}` - Reference root license
7. `requires-python = ">=3.10"` - Python version constraint
8. `[build-system]` - hatchling backend
9. `[tool.hatch.build.targets.wheel]` - Package location

**Version semantics:**
- `0.0.x` - Experimental, unstable API
- `0.x.0` - Working features, pre-1.0 stability
- `1.0.0+` - Stable public API

## Alternatives Considered

1. **Minimal metadata for libs** – Rejected: Limits future publishing options
2. **All versions at 0.0.1** – Rejected: Doesn't reflect functional maturity
3. **Per-package licenses** – Rejected: Adds maintenance overhead
4. **No version enforcement** – Rejected: Allows drift to return

## Consequences

### Positive

* Consistent metadata across all packages
* Clear template for future package creation
* Publishing-ready packages (PyPI compatible)
* Version numbers reflect maturity level

### Negative

* More verbose pyproject.toml files
* Version bumps require manual coordination
* License path assumes consistent directory structure

### Neutral

* Root workspace stays minimal (0.0.1 version)
* Authors field duplicated across packages
* All packages share CC-BY 4.0 license

## Related

* Implementation:
  - `libs/crawling/pyproject.toml:1-18`
  - `apps/sitemap-crawler/pyproject.toml:1-32`
  - `pyproject.toml:1-11`
* ADR-001: uv Workspaces for Monorepo Layout
* License: `LICENSE` (CC-BY 4.0)
