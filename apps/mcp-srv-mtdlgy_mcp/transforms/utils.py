"""Core utilities for methodology catalog transformation pipeline."""
import json
import re
from pathlib import Path
from typing import Any


# ============================================================================
# I/O Functions
# ============================================================================

def load_json(path: str | Path) -> dict[str, Any]:
    """Load JSON from file with UTF-8 encoding."""
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_json(path: str | Path, data: dict[str, Any]) -> None:
    """Save JSON to file with UTF-8 encoding, stable key order, indent=2."""
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False, sort_keys=True)


# ============================================================================
# Version Selection
# ============================================================================

def pick_versions(catalogs: list[dict]) -> tuple[dict, dict]:
    """
    Pick active and previous catalogs from array.

    Active: First catalog where status != "frozen" (highest version)
    Previous: Catalog where version == active.program.supersedes

    Raises:
        ValueError: If active or previous not found, or supersedes missing
    """
    # Find active (first non-frozen, assuming array is sorted by version desc)
    active = None
    for catalog in catalogs:
        if catalog["program"]["status"] != "frozen":
            active = catalog
            break

    if not active:
        raise ValueError("No active catalog found (all catalogs are frozen)")

    # Check supersedes present
    supersedes = active["program"].get("supersedes")
    if not supersedes:
        raise ValueError(f"Active catalog {active['program']['version']} missing 'supersedes' field")

    # Find previous
    previous = None
    for catalog in catalogs:
        if catalog["program"]["version"] == supersedes:
            previous = catalog
            break

    if not previous:
        raise ValueError(f"Previous catalog {supersedes} not found (referenced by active)")

    return active, previous


# ============================================================================
# Validation Functions
# ============================================================================

def assert_invariants(current: dict, previous: dict) -> None:
    """
    Assert that shared dictionaries are identical across versions.
    Current is canonical; previous must match.

    Checks: levels, tags, global_gates

    Raises:
        ValueError: On first mismatch with diagnostic path
    """
    # Check levels
    curr_levels = current.get("levels", [])
    prev_levels = previous.get("levels", [])
    if curr_levels != prev_levels:
        # Find first difference
        for i, (curr, prev) in enumerate(zip(curr_levels, prev_levels)):
            if curr != prev:
                raise ValueError(f"levels[{i}] differs: current={curr} vs previous={prev}")
        if len(curr_levels) != len(prev_levels):
            raise ValueError(f"levels length differs: current={len(curr_levels)} vs previous={len(prev_levels)}")

    # Check tags
    curr_tags = current.get("tags", [])
    prev_tags = previous.get("tags", [])
    if curr_tags != prev_tags:
        raise ValueError(f"tags differ: current={curr_tags} vs previous={prev_tags}")

    # Check global_gates
    curr_gg = current.get("global_gates", [])
    prev_gg = previous.get("global_gates", [])

    if len(curr_gg) != len(prev_gg):
        raise ValueError(f"global_gates length differs: current={len(curr_gg)} vs previous={len(prev_gg)}")

    for i, (curr, prev) in enumerate(zip(curr_gg, prev_gg)):
        if curr.get("id") != prev.get("id"):
            raise ValueError(f"global_gates[{i}].id differs: '{curr.get('id')}' vs '{prev.get('id')}'")
        if curr != prev:
            raise ValueError(f"global_gates[{i}] content differs")


def validate_fingerprint(fp: Any) -> None:
    """
    Validate fingerprint format: exactly 64 lowercase hex chars (SHA-256).

    Raises:
        ValueError: If invalid format
    """
    if not isinstance(fp, str):
        raise ValueError(f"Fingerprint must be string, got {type(fp)}")

    if not re.match(r'^[a-f0-9]{64}$', fp):
        raise ValueError(f"Fingerprint must be 64 lowercase hex chars, got: {fp}")


def check_gate_ids_unique(catalog: dict) -> None:
    """
    Check that all gate IDs are unique across phase gates + global gates.

    Raises:
        ValueError: If duplicate gate ID found
    """
    seen_ids = set()

    # Phase gates
    for phase in catalog.get("phases", []):
        gate = phase.get("gate", {})
        gate_id = gate.get("id")
        if gate_id:
            if gate_id in seen_ids:
                raise ValueError(f"Duplicate gate ID: {gate_id}")
            seen_ids.add(gate_id)

    # Global gates
    for global_gate in catalog.get("global_gates", []):
        gate_id = global_gate.get("id")
        if gate_id:
            if gate_id in seen_ids:
                raise ValueError(f"Duplicate gate ID: {gate_id}")
            seen_ids.add(gate_id)


# ============================================================================
# Compilation Functions
# ============================================================================

def build_indices(catalog: dict) -> dict:
    """
    Build index maps for fast lookups.

    Returns:
        dict with: node_to_phase, phase_to_nodes, tag_to_nodes, door_level_buckets
    """
    node_to_phase = {}
    phase_to_nodes = {}
    tag_to_nodes = {}
    door_level_buckets = {}

    for phase in catalog.get("phases", []):
        phase_id = phase["id"]
        phase_to_nodes[phase_id] = []

        for node in phase.get("nodes", []):
            node_id = node["id"]

            # node → phase
            node_to_phase[node_id] = phase_id

            # phase → nodes
            phase_to_nodes[phase_id].append(node_id)

            # tag → nodes
            for tag in node.get("tags", []):
                if tag not in tag_to_nodes:
                    tag_to_nodes[tag] = []
                tag_to_nodes[tag].append(node_id)

            # (door, level) → nodes
            door = node.get("door")
            level = node.get("level")
            if door and level:
                key = (door, level)
                if key not in door_level_buckets:
                    door_level_buckets[key] = []
                door_level_buckets[key].append(node_id)

    return {
        "node_to_phase": node_to_phase,
        "phase_to_nodes": phase_to_nodes,
        "tag_to_nodes": tag_to_nodes,
        "door_level_buckets": {f"{k[0]}:{k[1]}": v for k, v in door_level_buckets.items()}
    }


def compile_predicate(predicate: dict, catalog: dict, check_id: str, indices: dict) -> dict:
    """
    Partially compile a gate predicate.

    Locked grammar:
    - status.state == done
    - has_evidence:<type>[:result]
    - has_contract

    Pre-resolves:
    - Target node lists
    - Evidence requirements

    Raises:
        ValueError: If condition not in locked grammar
    """
    kind = predicate.get("kind")
    condition = predicate.get("condition", "")

    # Parse condition and validate grammar
    condition_token = None
    evidence_spec = None

    if condition == "status.state == done":
        condition_token = "status.state == done"
    elif condition.startswith("has_evidence:"):
        condition_token = condition
        # Parse evidence spec: has_evidence:type or has_evidence:type:result
        parts = condition.split(":")
        if len(parts) == 2:
            evidence_spec = {"type": parts[1], "result": None}
        elif len(parts) == 3:
            evidence_spec = {"type": parts[1], "result": parts[2]}
        else:
            raise ValueError(f"Invalid has_evidence condition in check {check_id}: {condition}")
    elif condition == "has_contract":
        condition_token = "has_contract"
    elif condition:  # Non-empty condition but not in grammar
        raise ValueError(f"Condition not in locked grammar in check {check_id}: {condition}")

    # Resolve targets
    targets = []

    if "target" in predicate:
        # Single target
        targets.append(predicate["target"])
    elif "targets" in predicate:
        # Multiple targets
        targets.extend(predicate["targets"])
    elif "query" in predicate:
        # Query-based target resolution
        query = predicate["query"]
        phase_id = query.get("phase")
        level = query.get("level")
        tags = query.get("tags")

        # Start with phase nodes if specified
        if phase_id:
            targets = indices["phase_to_nodes"].get(phase_id, [])
        else:
            targets = list(indices["node_to_phase"].keys())

        # Filter by level
        if level:
            targets = [n for n in targets if _get_node_level(catalog, n) == level]

        # Filter by tags
        if tags:
            targets = [n for n in targets if _node_has_tags(catalog, n, tags)]

    return {
        "check_id": check_id,
        "kind": kind,
        "targets": targets,
        "condition_token": condition_token,
        "evidence_spec": evidence_spec
    }


def _get_node_level(catalog: dict, node_id: str) -> str | None:
    """Helper: Get node level."""
    for phase in catalog.get("phases", []):
        for node in phase.get("nodes", []):
            if node["id"] == node_id:
                return node.get("level")
    return None


def _node_has_tags(catalog: dict, node_id: str, required_tags: list[str]) -> bool:
    """Helper: Check if node has all required tags."""
    for phase in catalog.get("phases", []):
        for node in phase.get("nodes", []):
            if node["id"] == node_id:
                node_tags = set(node.get("tags", []))
                return all(tag in node_tags for tag in required_tags)
    return False


# ============================================================================
# Cleanup Functions
# ============================================================================

def strip_runtime_bloat(catalog: dict) -> None:
    """
    Remove _search_stemmed from all nodes (mutates catalog in-place).
    """
    for phase in catalog.get("phases", []):
        for node in phase.get("nodes", []):
            node.pop("_search_stemmed", None)
