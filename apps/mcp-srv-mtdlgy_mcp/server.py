#!/usr/bin/env python3
"""
MCP Server: Methodology Advisory

Stateless, read-only MCP server providing advisory, validation, and migration services
for the MCP Server Development Methodology.

Transport: stdio (default) + HTTP (via --transport http)
Framework: FastMCP
"""
import json
import sys
from pathlib import Path
from typing import Any, Literal

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, ConfigDict, Field

# Module-level constants
VAR_DIR = Path(__file__).parent / "var"
COMPILED_RULES_PATH = VAR_DIR / "compiled.rules.json"
CATALOG_CURRENT_PATH = VAR_DIR / "catalog.current.json"
CATALOG_PREVIOUS_PATH = VAR_DIR / "catalog.previous.json"

# Type aliases
ResponseFormat = Literal["json", "markdown"]

# Initialize MCP server
mcp = FastMCP("cprima_mcp-srv-mtdlgy_mcp")

# Global state: loaded at startup
compiled_rules: dict[str, Any] = {}
catalog_current: dict[str, Any] = {}
catalog_previous: dict[str, Any] = {}


# =============================================================================
# Pydantic Models (Strict Validation)
# =============================================================================


class Evidence(BaseModel):
    """Evidence item attached to a node."""

    model_config = ConfigDict(extra="forbid")

    type: Literal["spike", "test_report", "security", "perf", "ops_runbook"]
    result: str | None = None
    details: str


class NodeStatus(BaseModel):
    """Node completion status."""

    model_config = ConfigDict(extra="forbid")

    state: Literal["todo", "in_progress", "done"]
    cause: str | None = None


class NodeState(BaseModel):
    """State for a single node in client overlay."""

    model_config = ConfigDict(extra="forbid")

    status: NodeStatus
    decision_input: dict[str, Any] | None = None
    evidence: list[Evidence] = Field(default_factory=list)


class ClientState(BaseModel):
    """Client state overlay for gate evaluation."""

    model_config = ConfigDict(extra="forbid")

    nodes: dict[str, NodeState] = Field(default_factory=dict)


# =============================================================================
# Server Lifecycle
# =============================================================================


def load_data() -> None:
    """Load compiled rules and catalogs at server startup."""
    global compiled_rules, catalog_current, catalog_previous

    print("Loading compiled data...", file=sys.stderr)

    compiled_rules = json.loads(COMPILED_RULES_PATH.read_text(encoding="utf-8"))
    print(
        f"  [OK] Loaded {len(compiled_rules.get('gates', []))} gates",
        file=sys.stderr,
    )

    catalog_current = json.loads(CATALOG_CURRENT_PATH.read_text(encoding="utf-8"))
    print(
        f"  [OK] Loaded current catalog: {catalog_current['program']['version']}",
        file=sys.stderr,
    )

    catalog_previous = json.loads(CATALOG_PREVIOUS_PATH.read_text(encoding="utf-8"))
    print(
        f"  [OK] Loaded previous catalog: {catalog_previous['program']['version']}",
        file=sys.stderr,
    )


# =============================================================================
# Markdown Formatting Utilities
# =============================================================================


def format_gate_evaluation_markdown(result: dict[str, Any]) -> str:
    """Format gate evaluation as plain text Markdown (no colors, no symbols)."""
    md = f"# Gate Evaluation: {result['gate_id']}\n\n"

    status = "PASS" if result["pass"] else "FAIL"
    md += f"Status: {status}\n"
    md += f"Checks: {result['passed']}/{result['total_checks']} passed\n\n"

    for check in result["checks"]:
        check_status = "PASS" if check["pass"] else "FAIL"
        md += f"## {check_status} {check['check_id']}\n"
        md += f"- Gate: {check['gate_id']}\n"
        md += f"- Message: {check['message']}\n"
        md += f"- Targets: {', '.join(check['targets'])}\n"

        if check["failures"]:
            md += f"- Failed nodes: {', '.join(check['failures'])}\n"

        md += "\n"

    return md


def format_migration_report_markdown(report: dict[str, Any]) -> str:
    """Format migration report as plain text Markdown."""
    md = f"# Migration Report: {report['from_version']} -> {report['to_version']}\n\n"

    compat = "COMPATIBLE" if report["compatible"] else "INCOMPATIBLE"
    md += f"## Compatibility: {compat}\n\n"

    md += "## Changes\n\n"

    # Added nodes
    md += "### Added Nodes\n"
    if report["changes"]["added_nodes"]:
        for node in report["changes"]["added_nodes"]:
            md += f"- {node['id']}\n"
    else:
        md += "No nodes added.\n"
    md += "\n"

    # Removed nodes
    md += "### Removed Nodes\n"
    if report["changes"]["removed_nodes"]:
        for node in report["changes"]["removed_nodes"]:
            md += f"- {node}\n"
    else:
        md += "No nodes removed.\n"
    md += "\n"

    # New features
    if report["changes"]["new_advisory"]:
        md += "### New Features\n"
        md += "- Advisory content now available (examples, templates, anti-patterns, success criteria)\n\n"

    # State updates
    md += "## State Updates\n\n"

    md += "### Nodes to Add\n"
    if report["state_updates"]["nodes_to_add"]:
        for node in report["state_updates"]["nodes_to_add"]:
            md += f"- {node}\n"
    else:
        md += "No new nodes to add to state.\n"
    md += "\n"

    md += "### Advisory Available\n"
    if report["state_updates"]["advisory_available"]:
        md += "The following nodes now have advisory content:\n"
        for node in report["state_updates"]["advisory_available"]:
            md += f"- {node}\n"
    else:
        md += "No advisory content available.\n"
    md += "\n"

    # Warnings
    md += "## Warnings\n"
    if report["warnings"]:
        for warning in report["warnings"]:
            md += f"- {warning}\n"
    else:
        md += "No warnings.\n"

    return md


def format_catalog_diff_markdown(diff: dict[str, Any]) -> str:
    """Format catalog diff as plain text Markdown."""
    md = f"# Catalog Diff: {diff['from_version']} -> {diff['to_version']}\n\n"

    # Fingerprints
    md += "## Fingerprints\n"
    md += f"- From: {diff['fingerprints']['from']}\n"
    md += f"- To: {diff['fingerprints']['to']}\n\n"

    # Phases
    md += "## Phases\n\n"
    md += f"Added: {len(diff['phases']['added'])}\n"
    md += f"Removed: {len(diff['phases']['removed'])}\n"
    md += f"Unchanged: {len(diff['phases']['unchanged'])}\n\n"

    # Nodes
    md += "## Nodes\n\n"

    if diff["nodes"]["added"]:
        md += "### Added Nodes\n"
        for node in diff["nodes"]["added"]:
            md += f"- {node['id']} (phase: {node['phase']}, door: {node['door']}, level: {node['level']})\n"
        md += "\n"

    if diff["nodes"]["removed"]:
        md += "### Removed Nodes\n"
        for node in diff["nodes"]["removed"]:
            md += f"- {node['id']} (phase: {node['phase']})\n"
        md += "\n"

    md += f"### Unchanged Nodes\n"
    md += f"Count: {len(diff['nodes']['unchanged'])}\n\n"

    # Gates
    md += "## Gates\n"
    md += f"{diff['gates']['info']}\n"
    md += f"Total compiled: {diff['gates']['total_compiled']}\n\n"

    # Advisory
    md += "## Advisory\n"
    md += f"- Available in {diff['from_version']}: {'Yes' if diff['advisory']['available_in_from'] else 'No'}\n"
    md += f"- Available in {diff['to_version']}: {'Yes' if diff['advisory']['available_in_to'] else 'No'}\n\n"

    if diff["advisory"]["nodes_with_new_advisory"]:
        md += "Nodes with new advisory:\n"
        for node in diff["advisory"]["nodes_with_new_advisory"]:
            md += f"- {node}\n"

    return md


def format_advisory_suggestions_markdown(result: dict[str, Any]) -> str:
    """Format advisory suggestions as plain text Markdown with code language hints."""
    md = f"# Advisory Suggestions\n\n"
    md += f"Context: {result['context']}\n\n"

    for suggestion in result["suggestions"]:
        source = suggestion["source"]
        adv_type = suggestion["type"]
        items = suggestion["items"]

        md += f"## {source.replace(':', ': ').title()}\n\n"
        md += f"### {adv_type.replace('_', ' ').title()}\n\n"

        for item in items:
            if adv_type == "examples":
                md += f"#### {item['title']}\n"
                md += f"{item['description']}\n\n"

                if "code" in item and item["code"]:
                    lang = _detect_language(item["code"])
                    md += f"```{lang}\n"
                    md += f"{item['code']}\n"
                    md += f"```\n\n"

                if "context" in item and item["context"]:
                    md += f"Context: {item['context']}\n\n"

            elif adv_type == "templates":
                md += f"#### {item['name']}\n\n"
                lang = item.get("format", "text")
                md += f"```{lang}\n"
                md += f"{item['content']}\n"
                md += f"```\n\n"

            elif adv_type == "anti_patterns":
                md += f"#### {item['title']}\n"
                md += f"Problem: {item['problem']}\n\n"
                md += f"Solution: {item['solution']}\n\n"

                if "example" in item and item["example"]:
                    md += f"Example: {item['example']}\n\n"

            elif adv_type == "success_criteria":
                md += f"#### {item['criterion']}\n"
                md += f"Verification: {item['verification']}\n\n"

                if "evidence" in item and item["evidence"]:
                    md += f"Evidence: {item['evidence']}\n\n"

    md += f"Total items: {result['total_items']}\n"

    return md


def _detect_language(code: str) -> str:
    """Detect programming language from code content for syntax highlighting."""
    code_lower = code.lower()

    if "def " in code or "import " in code or "@" in code:
        return "python"
    elif "{" in code and ('"name"' in code or '"version"' in code):
        return "json"
    elif "[project]" in code or "[tool." in code:
        return "toml"
    elif "function" in code or "const" in code or "=>" in code:
        return "javascript"
    elif "```" in code:
        return "markdown"
    else:
        return "text"


# =============================================================================
# Helper Functions
# =============================================================================


def _evaluate_check(
    gate: dict[str, Any], state: ClientState
) -> tuple[bool, str, list[str]]:
    """Evaluate a single gate check against client state."""
    kind = gate["kind"]
    targets = gate.get("targets", [])
    condition = gate.get("condition_token")
    evidence_spec = gate.get("evidence_spec")
    nodes = state.nodes

    failures = []

    if kind == "all-of":
        # All targets must satisfy condition
        for target in targets:
            node_state = nodes.get(target)

            if not node_state:
                failures.append(target)
                continue

            if condition == "status.state == done":
                if node_state.status.state != "done":
                    failures.append(target)

            elif condition and condition.startswith("has_evidence:"):
                # Parse: has_evidence:<type>[:result]
                parts = condition.split(":")
                ev_type = parts[1]
                ev_result = parts[2] if len(parts) > 2 else None

                evidence_list = node_state.evidence
                found = False
                for ev in evidence_list:
                    if ev.type == ev_type:
                        if ev_result is None or ev.result == ev_result:
                            found = True
                            break

                if not found:
                    failures.append(target)

            elif condition == "has_contract":
                if node_state.decision_input is None:
                    failures.append(target)

        if failures:
            return False, f"Failed for: {', '.join(failures)}", failures
        return True, "All targets satisfy condition", []

    elif kind == "node-field-present":
        # Check if field present in target nodes
        field = gate.get("field", "decision_input")
        for target in targets:
            node_state = nodes.get(target)
            if not node_state:
                failures.append(target)
                continue

            if field == "decision_input" and node_state.decision_input is None:
                failures.append(target)

        if failures:
            return False, f"Missing field '{field}' in: {', '.join(failures)}", failures
        return True, f"Field '{field}' present in all targets", []

    elif kind == "evidence-meets":
        # Check evidence meets criteria
        for target in targets:
            node_state = nodes.get(target)
            if not node_state:
                failures.append(target)
                continue

            evidence_list = node_state.evidence

            if evidence_spec:
                ev_type = evidence_spec.get("type")
                ev_result = evidence_spec.get("result")

                found = False
                for ev in evidence_list:
                    if ev.type == ev_type:
                        if ev_result is None or ev.result == ev_result:
                            found = True
                            break

                if not found:
                    failures.append(target)

        if failures:
            return (
                False,
                f"Evidence not found for: {', '.join(failures)}",
                failures,
            )
        return True, "Evidence meets criteria", []

    elif kind in ("adr-has-section", "artifact-exists"):
        # These require external artifact inspection - return advisory
        return True, f"Check '{kind}' requires external validation", []

    return True, f"Check kind '{kind}' not fully implemented", []


def _extract_node_ids(catalog: dict[str, Any]) -> set[str]:
    """Extract all node IDs from a catalog."""
    node_ids = set()
    for phase in catalog.get("phases", []):
        for node in phase.get("nodes", []):
            node_ids.add(node["id"])
    return node_ids


def _get_node_details(catalog: dict[str, Any]) -> list[dict[str, Any]]:
    """Extract node details from catalog."""
    nodes = []
    for phase in catalog.get("phases", []):
        phase_id = phase["id"]
        for node in phase.get("nodes", []):
            nodes.append(
                {
                    "id": node["id"],
                    "phase": phase_id,
                    "door": node.get("door", ""),
                    "level": node.get("level", ""),
                }
            )
    return nodes


def _find_node_in_catalog(
    catalog: dict[str, Any], node_id: str
) -> dict[str, Any] | None:
    """Find a node by ID in a catalog."""
    for phase in catalog.get("phases", []):
        for node in phase.get("nodes", []):
            if node["id"] == node_id:
                return node
    return None


def _find_phase_in_catalog(
    catalog: dict[str, Any], phase_id: str
) -> dict[str, Any] | None:
    """Find a phase by ID in a catalog."""
    for phase in catalog.get("phases", []):
        if phase["id"] == phase_id:
            return phase
    return None


# =============================================================================
# MCP Tools
# =============================================================================


@mcp.tool(
    annotations={
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    }
)
def evaluate_gate(
    gate_id: str | None = None,
    state: dict[str, Any] | None = None,
    format: ResponseFormat = "markdown",
) -> str | dict[str, Any]:
    """
    Check if a client state satisfies a specific gate or all gates.

    Args:
        gate_id: Gate ID to evaluate (e.g., "core-features-gate", "G-Risk").
                 If None, evaluates all gates.
        state: Client state object with node statuses and evidence.
               Format: {"nodes": {"node-id": {"status": {"state": "done"}, "evidence": [...]}}}
        format: Response format - "json" (default) or "markdown"

    Returns:
        GateEvaluation object with pass/fail status and diagnostics for each check.
        Format varies based on 'format' parameter.

    Example:
        evaluate_gate("core-features-gate", {"nodes": {"tool-atomicity": {"status": {"state": "done"}}}})

    Errors:
        - Unknown gate_id: Returns error with list of valid gate IDs
        - Invalid state format: Returns Pydantic validation error
    """
    try:
        # Validate state with Pydantic
        validated_state = ClientState(**state) if state else ClientState()
    except Exception as e:
        return {"error": "Validation error", "details": str(e)}

    gates = compiled_rules.get("gates", [])

    # Filter gates
    if gate_id:
        target_gates = [g for g in gates if g["gate_id"] == gate_id]
        if not target_gates:
            valid_gates = sorted(set(g["gate_id"] for g in gates))
            return {"error": f"Unknown gate_id: {gate_id}", "valid_gates": valid_gates}
    else:
        target_gates = gates
        gate_id = "all"

    # Evaluate checks
    checks = []
    all_pass = True

    for gate in target_gates:
        check_pass, message, failures = _evaluate_check(gate, validated_state)
        checks.append(
            {
                "check_id": gate["check_id"],
                "gate_id": gate["gate_id"],
                "pass": check_pass,
                "message": message,
                "targets": gate.get("targets", []),
                "failures": failures,
            }
        )
        if not check_pass:
            all_pass = False

    result = {
        "gate_id": gate_id,
        "pass": all_pass,
        "total_checks": len(checks),
        "passed": sum(1 for c in checks if c["pass"]),
        "failed": sum(1 for c in checks if not c["pass"]),
        "checks": checks,
    }

    if format == "markdown":
        return format_gate_evaluation_markdown(result)
    return result


@mcp.tool(
    annotations={
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    }
)
def migrate_state(
    from_version: str,
    to_version: str,
    state: dict[str, Any],
    format: ResponseFormat = "markdown",
) -> str | dict[str, Any]:
    """
    Compare catalogs and suggest how to update an existing state for version transition.

    Args:
        from_version: Source catalog version (e.g., "0.3.0")
        to_version: Target catalog version (e.g., "0.4.0-alpha")
        state: Current client state object
        format: Response format - "json" or "markdown" (default)

    Returns:
        MigrationReport with structural changes and state update suggestions.

    Example:
        migrate_state("0.3.0", "0.4.0-alpha", {"nodes": {...}})

    Errors:
        - Unknown version: Returns error with available versions
        - Invalid state: Returns Pydantic validation error
    """
    try:
        # Validate state with Pydantic
        ClientState(**state)
    except Exception as e:
        return {"error": "Validation error", "details": str(e)}

    # Determine which catalogs to use
    available_versions = [
        catalog_previous["program"]["version"],
        catalog_current["program"]["version"],
    ]

    if from_version == catalog_previous["program"]["version"]:
        from_catalog = catalog_previous
    elif from_version == catalog_current["program"]["version"]:
        from_catalog = catalog_current
    else:
        return {
            "error": f"Unknown from_version: {from_version}",
            "available_versions": available_versions,
        }

    if to_version == catalog_current["program"]["version"]:
        to_catalog = catalog_current
    elif to_version == catalog_previous["program"]["version"]:
        to_catalog = catalog_previous
    else:
        return {
            "error": f"Unknown to_version: {to_version}",
            "available_versions": available_versions,
        }

    # Extract nodes from both catalogs
    from_nodes = _extract_node_ids(from_catalog)
    to_nodes = _extract_node_ids(to_catalog)

    added_nodes = to_nodes - from_nodes
    removed_nodes = from_nodes - to_nodes

    # Check advisory availability
    advisory_reg = compiled_rules.get("advisory", {}).get("node_advisory", {})
    nodes_with_advisory = [
        node_id
        for node_id in added_nodes
        if advisory_reg.get(node_id, {}).get("present")
    ]

    # Build migration report
    report = {
        "from_version": from_version,
        "to_version": to_version,
        "changes": {
            "added_nodes": [
                {"id": node_id, "info": "New node in target version"}
                for node_id in sorted(added_nodes)
            ],
            "removed_nodes": list(sorted(removed_nodes)),
            "new_advisory": to_version == catalog_current["program"]["version"],
        },
        "state_updates": {
            "nodes_to_add": list(sorted(added_nodes)),
            "nodes_to_review": [],  # Future: gate diff analysis
            "advisory_available": nodes_with_advisory,
        },
        "compatible": len(removed_nodes) == 0,
        "warnings": [
            f"Node '{node}' removed in target version" for node in removed_nodes
        ],
    }

    if format == "markdown":
        return format_migration_report_markdown(report)
    return report


@mcp.tool(
    annotations={
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    }
)
def diff_catalogs(
    from_version: str, to_version: str, format: ResponseFormat = "markdown"
) -> str | dict[str, Any]:
    """
    Inspect structural differences between two catalog versions.

    Args:
        from_version: Source catalog version (e.g., "0.3.0")
        to_version: Target catalog version (e.g., "0.4.0-alpha")
        format: Response format - "json" or "markdown" (default)

    Returns:
        CatalogDiff object with structural changes.

    Example:
        diff_catalogs("0.3.0", "0.4.0-alpha")

    Errors:
        - Unknown version: Returns error with available versions
    """
    available_versions = [
        catalog_previous["program"]["version"],
        catalog_current["program"]["version"],
    ]

    # Load catalogs
    if from_version == catalog_previous["program"]["version"]:
        from_catalog = catalog_previous
    elif from_version == catalog_current["program"]["version"]:
        from_catalog = catalog_current
    else:
        return {
            "error": f"Unknown from_version: {from_version}",
            "available_versions": available_versions,
        }

    if to_version == catalog_current["program"]["version"]:
        to_catalog = catalog_current
    elif to_version == catalog_previous["program"]["version"]:
        to_catalog = catalog_previous
    else:
        return {
            "error": f"Unknown to_version: {to_version}",
            "available_versions": available_versions,
        }

    # Extract structures
    from_phases = {p["id"] for p in from_catalog.get("phases", [])}
    to_phases = {p["id"] for p in to_catalog.get("phases", [])}

    from_nodes = _get_node_details(from_catalog)
    to_nodes = _get_node_details(to_catalog)

    from_node_ids = {n["id"] for n in from_nodes}
    to_node_ids = {n["id"] for n in to_nodes}

    # Advisory check
    from_has_advisory = (
        "advisory" in next(iter(from_catalog.get("phases", [])), {})
        if from_catalog.get("phases")
        else False
    )
    to_has_advisory = (
        "advisory" in next(iter(to_catalog.get("phases", [])), {})
        if to_catalog.get("phases")
        else False
    )

    advisory_reg = compiled_rules.get("advisory", {}).get("node_advisory", {})
    nodes_with_new_advisory = [
        node_id
        for node_id in (to_node_ids - from_node_ids)
        if advisory_reg.get(node_id, {}).get("present")
    ]

    diff = {
        "from_version": from_version,
        "to_version": to_version,
        "fingerprints": {
            "from": from_catalog["program"]["fingerprint"],
            "to": to_catalog["program"]["fingerprint"],
        },
        "phases": {
            "added": list(sorted(to_phases - from_phases)),
            "removed": list(sorted(from_phases - to_phases)),
            "unchanged": list(sorted(from_phases & to_phases)),
        },
        "nodes": {
            "added": [
                {
                    "id": n["id"],
                    "phase": n["phase"],
                    "door": n["door"],
                    "level": n["level"],
                }
                for n in to_nodes
                if n["id"] in (to_node_ids - from_node_ids)
            ],
            "removed": [
                {"id": n["id"], "phase": n["phase"]}
                for n in from_nodes
                if n["id"] in (from_node_ids - to_node_ids)
            ],
            "unchanged": list(sorted(from_node_ids & to_node_ids)),
        },
        "gates": {
            "info": "Gate diff requires compiled gate comparison",
            "total_compiled": len(compiled_rules.get("gates", [])),
        },
        "advisory": {
            "available_in_from": from_has_advisory,
            "available_in_to": to_has_advisory,
            "nodes_with_new_advisory": nodes_with_new_advisory,
        },
    }

    if format == "markdown":
        return format_catalog_diff_markdown(diff)
    return diff


@mcp.tool(
    annotations={
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    }
)
def suggest_advisory(
    context: str,
    node_id: str | None = None,
    phase_id: str | None = None,
    advisory_type: Literal[
        "examples", "templates", "anti_patterns", "success_criteria"
    ]
    | None = None,
    format: ResponseFormat = "markdown",
) -> str | dict[str, Any]:
    """
    Retrieve phase/node-specific advisory content (examples, anti-patterns, templates, success criteria).

    Args:
        context: Description of situation or question (e.g., "naming a Python MCP server")
        node_id: Optional specific node ID (e.g., "server-naming", "tool-atomicity")
        phase_id: Optional specific phase ID (e.g., "getting-started", "core-features")
        advisory_type: Optional filter for specific advisory type
        format: Response format - "json" or "markdown" (default)

    Returns:
        AdvisorySuggestions object with relevant advisory content.

    Example:
        suggest_advisory("How to name tools?", node_id="tool-naming")
        suggest_advisory("Starting new server", phase_id="getting-started", advisory_type="examples")

    Errors:
        - Unknown node/phase: Returns error with valid IDs
        - No advisory available: Returns empty suggestions
    """
    suggestions = []

    # Load from current catalog (has advisory)
    advisory_types = ["examples", "templates", "anti_patterns", "success_criteria"]
    if advisory_type:
        advisory_types = [advisory_type]

    # Node-level advisory
    if node_id:
        node = _find_node_in_catalog(catalog_current, node_id)
        if not node:
            valid_nodes = (
                compiled_rules.get("indices", {}).get("node_to_phase", {}).keys()
            )
            return {
                "error": f"Unknown node_id: {node_id}",
                "valid_nodes": list(sorted(valid_nodes)),
            }

        node_advisory = node.get("advisory", {})
        for adv_type in advisory_types:
            items = node_advisory.get(adv_type, [])
            if items:
                suggestions.append(
                    {"source": f"node:{node_id}", "type": adv_type, "items": items}
                )

    # Phase-level advisory
    if phase_id:
        phase = _find_phase_in_catalog(catalog_current, phase_id)
        if not phase:
            valid_phases = [p["id"] for p in catalog_current.get("phases", [])]
            return {
                "error": f"Unknown phase_id: {phase_id}",
                "valid_phases": valid_phases,
            }

        phase_advisory = phase.get("advisory", {})
        for adv_type in advisory_types:
            items = phase_advisory.get(adv_type, [])
            if items:
                suggestions.append(
                    {"source": f"phase:{phase_id}", "type": adv_type, "items": items}
                )

        # Phase-specific types
        if advisory_type is None or advisory_type not in advisory_types:
            for extra_type in [
                "decision_trees",
                "tool_recommendations",
                "related_resources",
                "conversation_starters",
            ]:
                items = phase_advisory.get(extra_type, [])
                if items:
                    suggestions.append(
                        {
                            "source": f"phase:{phase_id}",
                            "type": extra_type,
                            "items": items,
                        }
                    )

    # If no specific node/phase, search by context
    if not node_id and not phase_id:
        # Simple keyword matching in advisory registry
        context_lower = context.lower()
        advisory_reg = compiled_rules.get("advisory", {})

        # Check nodes with advisory
        for nid, meta in advisory_reg.get("node_advisory", {}).items():
            if meta.get("present"):
                node = _find_node_in_catalog(catalog_current, nid)
                if node and any(
                    kw in node.get("title", "").lower() for kw in context_lower.split()
                ):
                    node_advisory = node.get("advisory", {})
                    for adv_type in advisory_types:
                        items = node_advisory.get(adv_type, [])
                        if items:
                            suggestions.append(
                                {
                                    "source": f"node:{nid}",
                                    "type": adv_type,
                                    "items": items,
                                }
                            )

    result = {
        "context": context,
        "suggestions": suggestions,
        "total_items": sum(len(s["items"]) for s in suggestions),
    }

    if format == "markdown":
        return format_advisory_suggestions_markdown(result)
    return result


# =============================================================================
# Main Entry Point
# =============================================================================

if __name__ == "__main__":
    # Load data at startup
    load_data()

    # Run server (stdio by default, HTTP via --transport http)
    mcp.run()
