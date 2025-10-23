# MCP Server Development Methodology - Schema Documentation

**Co-located with data.json** for version traceability and relative `$ref` resolution.

## Architecture

This directory contains a **modular, reusable schema structure** that avoids duplication and supports clean version evolution.

### Modular Structure

```
schema/
├── core.schema.json          # Shared $defs (Program, Phase, Node, Gate, etc.)
├── predicate.schema.json     # Locked predicate grammar (5 kinds)
├── advisory.schema.json      # Phase/Node advisory types (v0.4.0-alpha+)
├── v0.3.0.schema.json        # Frozen: core + predicate only
└── v0.4.0-alpha.schema.json  # Prerelease: core + predicate + advisory
```

### Design Principles

1. **Core + Overlay Pattern**
   - `core.schema.json` contains shared definitions used across all versions
   - Version-specific schemas import core and add/constrain as needed
   - v0.3.0 = core only (no advisory)
   - v0.4.0-alpha = core + advisory overlay

2. **Externalized $defs**
   - Shared types defined once in core.schema.json
   - Version schemas use `$ref: "core.schema.json#/$defs/Type"`
   - Eliminates duplication and drift between versions

3. **Predicate as Separate Module**
   - `predicate.schema.json` defines locked grammar
   - Only 5 predicate kinds allowed (enforced at schema level)
   - Both versions reference this module
   - Future versions can extend if needed

4. **Advisory as Separate Module**
   - `advisory.schema.json` contains PhaseAdvisory/NodeAdvisory types
   - v0.3.0: No advisory reference
   - v0.4.0-alpha: Optional advisory at phase/node level
   - Future versions inherit same structure

5. **Version Pinning**
   - Each version schema has `const` for `program.version`
   - v0.3.0: `status` enum limited to `frozen|active|previous`
   - v0.4.0-alpha: `status` enum adds `prerelease`

## Schemas

### core.schema.json

**Purpose:** Shared type definitions used across all methodology versions

**Exports:**
- `ProgramBase` - Program metadata (id, title, version, status, fingerprint, supersedes)
  - Note: `last_updated` must be in `YYYY-MM-DD` format (not full timestamp)
- `PhaseBase` - Phase structure (id, title, description, color, nodes, gate)
- `NodeBase` - Node structure (id, title, summary, why, door, level, tags, effort, status, etc.)
  - Note: `_search_stemmed` is a **derived field** (computed, optional) - stripped by ingest transform
- `Effort` - Effort estimation (min, max, confidence)
- `EvidencePolicy` - Evidence requirements (type, required_at, criteria)
- `DecisionInput` - User input specifications (label, placeholder, pattern, help)
- `Block` - Dependency blocking (on, reason)
- `NodeStatus` - Node state tracking (state, cause)
- `Gate` - Phase gate definition (id, purpose, applies_to, checks, approvers, outcomes)
- `GateCheck` - Individual gate check (id, description, predicate)
- `GlobalGate` - Cross-phase gate (id, purpose, applies_to, checks, approvers, outcomes)
- `Level` - Priority level definition (id, label, description)
- `Source` - Transformation metadata (transformation_version, transformation_date, from_version, changes)

**Usage:**
```json
{
  "$ref": "core.schema.json#/$defs/ProgramBase"
}
```

### predicate.schema.json

**Purpose:** Locked predicate grammar for gate evaluation

**Locked Grammar (5 kinds):**
1. `node-field-present` - Check if node field exists/matches value
2. `evidence-meets` - Check if evidence type/result is present
3. `all-of` - All targets must meet condition
4. `adr-has-section` - ADR contains required section
5. `artifact-exists` - Artifact of type exists

**Condition Tokens (3 patterns):**
- `status.state == done` - Node completion check
- `has_evidence:<type>[:result]` - Evidence presence/result check
- `has_contract` - Contract definition check

**Convention:**
- Schema allows both `target` (string) and `targets` (array), but the compiler **always outputs `targets`** (even for singletons) to avoid branching logic

**Exports:**
- `Predicate` - Predicate structure with locked kind enum

**Usage:**
```json
{
  "$ref": "predicate.schema.json#/$defs/Predicate"
}
```

### advisory.schema.json

**Purpose:** Phase and node-level advisory structures (v0.4.0-alpha+)

**Exports:**
- `PhaseAdvisory` - Phase-level guidance (examples, templates, anti_patterns, success_criteria, decision_trees, tool_recommendations, related_resources, conversation_starters)
- `NodeAdvisory` - Node-level guidance (examples, templates, anti_patterns, success_criteria)
- `AdvisoryExample` - Example with code/context
- `AdvisoryTemplate` - Reusable template (markdown/text/json)
- `AdvisoryAntiPattern` - Problem/solution pair
- `AdvisoryCriteria` - Success criterion with verification
- `AdvisoryDecisionTree` - Decision tree with branches
- `AdvisoryToolRecommendation` - Tool suggestion with purpose/URL
- `AdvisoryResource` - External resource link

**Usage:**
```json
{
  "advisory": {
    "$ref": "advisory.schema.json#/$defs/PhaseAdvisory"
  }
}
```

### v0.3.0.schema.json

**Status:** Frozen
**Description:** Schema for frozen v0.3.0 catalog (no advisory blocks)

**Structure:**
- Imports: `core.schema.json`, `predicate.schema.json`
- Program: `version: "0.3.0"` (const), `status: frozen|active|previous`
- Phase: `PhaseBase` from core (no advisory)
- Node: `NodeBase` from core (no advisory)

**Usage in data.json:**
```json
{
  "$schema": "file:///docs/methodology/schema/v0.3.0.schema.json",
  "program": {
    "version": "0.3.0"
  }
}
```

### v0.4.0-alpha.schema.json

**Status:** Prerelease
**Description:** Schema for v0.4.0-alpha catalog with phase and node-level advisory blocks

**Structure:**
- Imports: `core.schema.json`, `predicate.schema.json`, `advisory.schema.json`
- Program: `version: "0.4.0-alpha"` (const), `status: frozen|active|previous|prerelease`
- Phase: `PhaseBase` + optional `advisory: PhaseAdvisory`
- Node: `NodeBase` + optional `advisory: NodeAdvisory`

**Usage in data.json:**
```json
{
  "$schema": "file:///docs/methodology/schema/v0.4.0-alpha.schema.json",
  "program": {
    "version": "0.4.0-alpha"
  },
  "phases": [
    {
      "advisory": {
        "examples": [],
        "templates": []
      }
    }
  ]
}
```

## Validation

### Browser (HTML Page)
**No validation.** The HTML page is a dumb renderer that:
- Loads `data.json`
- Displays phases/nodes/gates
- Compares fingerprints (string equality only)
- Manages local state (localStorage)

### Server (MCP Transform Pipeline)
**Optional validation.** The transformation pipeline can validate `data.json` entries against their referenced versioned schema during the ingest stage.

**Example (Python):**
```python
import json
import jsonschema
from pathlib import Path

schema_dir = Path("docs/methodology/schema")
data = json.loads(Path("docs/methodology/data.json").read_text())

for catalog in data:
    schema_ref = catalog.get("$schema", "")
    schema_file = schema_dir / Path(schema_ref).name
    schema = json.loads(schema_file.read_text())

    # Resolve $refs using custom resolver
    resolver = jsonschema.RefResolver(
        base_uri=f"file:///{schema_dir}/",
        referrer=schema
    )

    jsonschema.validate(catalog, schema, resolver=resolver)
```

## Evolution Strategy

### Adding a New Version (e.g., v0.5.0)

1. **If no new types needed:**
   ```json
   // v0.5.0.schema.json
   {
     "$ref": "core.schema.json#/$defs/...",
     "Program": {
       "version": { "const": "0.5.0" }
     }
   }
   ```

2. **If new advisory fields needed:**
   - Extend `advisory.schema.json` with new types
   - Import in v0.5.0 schema
   - Previous versions unaffected

3. **If new predicate kinds needed:**
   - Extend `predicate.schema.json` with new kinds
   - Update locked grammar documentation
   - Consider backward compatibility impact

### Deprecating a Version

1. Update version schema status to `frozen`
2. Document deprecation in schema description
3. Keep schema file for historical validation
4. MCP transform pipeline can skip frozen versions (except for migration support)

## References

- [Multi-Version Catalog](../data.json) - Database at rest
- [ADR-004: Separation of Presentation and Logic](../../adr/ADR-004_methodology_mcp_separation.md)
- [MCP Transform Pipeline](../../../apps/mcp-srv-mtdlgy_mcp/transforms/)
- [JSON Schema 2020-12 Spec](https://json-schema.org/draft/2020-12/json-schema-core.html)
