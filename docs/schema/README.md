# Methodology JSON Schemas

JSON Schema definitions for the MCP Server Development Methodology multi-version catalog.

## Schema Files

### v0.3.0.schema.json
Schema for **frozen** v0.3.0 catalog:
- No advisory blocks (neither phase nor node level)
- Status: `frozen`
- Supersedes: v0.2.1

### v0.4.0-alpha.schema.json
Schema for **prerelease** v0.4.0-alpha catalog:
- **Phase-level advisory**: 8 fields (examples, templates, anti_patterns, success_criteria, decision_trees, tool_recommendations, related_resources, conversation_starters)
- **Node-level advisory**: 4 fields (examples, templates, anti_patterns, success_criteria)
- Status: `prerelease`
- Supersedes: v0.3.0

## Schema Features

### 1. Root $schema per Catalog
Each embedded catalog in the array has its own `$schema` reference:
```json
[
  {
    "$schema": "file:///docs/schema/v0.3.0.schema.json",
    "program": {...}
  },
  {
    "$schema": "file:///docs/schema/v0.4.0-alpha.schema.json",
    "program": {...}
  }
]
```

### 2. Advisory with Explicit Item Types
**Advisory is optional** - not present in required arrays. JS code must guard against undefined.

When present, advisory arrays contain typed objects (no `"n/a"` sentinels):

**Phase Advisory (v0.4.0-alpha only - optional):**
- `examples`: `AdvisoryExample[]` - Concrete usage examples
- `templates`: `AdvisoryTemplate[]` - Reusable templates (ADRs, evidence)
- `anti_patterns`: `AdvisoryAntiPattern[]` - Common mistakes to avoid
- `success_criteria`: `AdvisoryCriteria[]` - How to know you're done well
- `decision_trees`: `AdvisoryDecisionTree[]` - "If X, then Y" branching logic
- `tool_recommendations`: `AdvisoryToolRecommendation[]` - Relevant tools
- `related_resources`: `AdvisoryResource[]` - Documentation, articles, examples
- `conversation_starters`: `string[]` - Questions an advisor would ask

**Node Advisory (v0.4.0-alpha only - optional):**
- `examples`: `AdvisoryExample[]`
- `templates`: `AdvisoryTemplate[]`
- `anti_patterns`: `AdvisoryAntiPattern[]`
- `success_criteria`: `AdvisoryCriteria[]`

**Important:** Check for `advisory?.examples` or use optional chaining in JS/TS.

### 3. Program Metadata
Each catalog's `program` object includes:
- `version`: Semantic version string
- `status`: `"frozen" | "active" | "previous" | "prerelease"`
- `fingerprint`: SHA-256 hash of `program.id + ":" + version` (deterministic)
  - v0.3.0: `00432378056df2da0d46ade26c18f6c90104c5908290d941a7759015619367a9`
  - v0.4.0-alpha: `4813d14478eac5169c699b6e3c67600ae261bd3fe600522107fafae5077b6bd7`
- `supersedes`: Version this catalog replaces
  - v0.3.0 supersedes: `"0.2.1"`
  - v0.4.0-alpha supersedes: `"0.3.0"`

### 4. Shared Definitions
`$defs` section includes reusable types:
- Core: `Program`, `Phase`, `Node`, `Gate`, `GlobalGate`
- Supporting: `Effort`, `EvidencePolicy`, `Block`, `Predicate`, `NodeStatus`
- Advisory Types: `AdvisoryExample`, `AdvisoryTemplate`, `AdvisoryAntiPattern`, etc.
- Metadata: `Level`, `Source`

### 5. Derived vs Source Fields
- **Derived fields** (computed): `_search_stemmed`
- **Source fields** (provenance): `_source` object with transformation history

## Validation

### Using Python jsonschema
```python
import json
from jsonschema import validate

# Load schema
with open('docs/schema/v0.4.0-alpha.schema.json') as f:
    schema = json.load(f)

# Load catalog
with open('docs/methodology/data.json') as f:
    catalogs = json.load(f)

# Validate v0.4.0-alpha catalog
catalog_v040 = next(c for c in catalogs if c['program']['version'] == '0.4.0-alpha')
validate(instance=catalog_v040, schema=schema)
```

## Advisory Item Types

### AdvisoryExample
```json
{
  "title": "Example Title",
  "description": "Detailed explanation",
  "code": "Optional code snippet",
  "context": "When/why to use this"
}
```

### AdvisoryTemplate
```json
{
  "name": "Template Name",
  "content": "Template content (Markdown, JSON, etc.)",
  "format": "markdown" | "text" | "json"
}
```

### AdvisoryAntiPattern
```json
{
  "title": "Anti-pattern Title",
  "problem": "What goes wrong",
  "solution": "How to do it right",
  "example": "Optional concrete example"
}
```

### AdvisoryCriteria
```json
{
  "criterion": "What should be true",
  "verification": "How to verify it",
  "evidence": "What evidence to collect"
}
```

### AdvisoryDecisionTree
```json
{
  "question": "What to consider?",
  "branches": [
    {
      "condition": "If this is true",
      "recommendation": "Then do this",
      "next": {...}  // Optional nested tree
    }
  ]
}
```

### AdvisoryToolRecommendation
```json
{
  "tool": "Tool Name",
  "purpose": "What it helps with",
  "url": "https://example.com/tool"
}
```

### AdvisoryResource
```json
{
  "title": "Resource Title",
  "url": "https://example.com/resource",
  "type": "documentation" | "article" | "video" | "example" | "tool"
}
```

## Notes

- **Fingerprints**: Computed deterministically as `SHA-256(program.id + ":" + version)`. Used for client state validation.
- **Advisory optional**: Not required by schema. JS/TS code must use optional chaining (`advisory?.examples`) or existence checks.
- **Empty arrays**: Advisory blocks have empty arrays `[]` by default, not `null` or `undefined`. Check parent object existence.
- **Shared dictionaries**: `levels` and `tags` arrays are defined at catalog root level and referenced throughout.
- **Version evolution**: v0.3.0 is frozen; v0.4.0-alpha will stabilize and freeze when ready, then v0.5.0 begins.
