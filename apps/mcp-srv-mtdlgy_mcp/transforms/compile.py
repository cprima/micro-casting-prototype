"""
Stage 3: Compile

Build indices, partially compile predicates, create advisory registry
"""
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from utils import load_json, save_json, build_indices, compile_predicate


def build_advisory_registry(catalog: dict) -> dict:
    """Build advisory registry preserving present/absent semantics."""
    registry = {
        "phase_advisory": {},
        "node_advisory": {}
    }

    for phase in catalog.get("phases", []):
        phase_id = phase["id"]

        # Check if advisory key present
        if "advisory" in phase:
            advisory = phase["advisory"]
            counts = {
                key: len(advisory.get(key, []))
                for key in ["examples", "templates", "anti_patterns", "success_criteria",
                           "decision_trees", "tool_recommendations", "related_resources",
                           "conversation_starters"]
            }
            registry["phase_advisory"][phase_id] = {
                "present": True,
                "counts": counts
            }
        else:
            registry["phase_advisory"][phase_id] = {
                "present": False
            }

        # Node advisory
        for node in phase.get("nodes", []):
            node_id = node["id"]

            if "advisory" in node:
                advisory = node["advisory"]
                counts = {
                    key: len(advisory.get(key, []))
                    for key in ["examples", "templates", "anti_patterns", "success_criteria"]
                }
                registry["node_advisory"][node_id] = {
                    "present": True,
                    "counts": counts
                }
            else:
                registry["node_advisory"][node_id] = {
                    "present": False
                }

    return registry


def main():
    try:
        var_dir = Path(__file__).parent.parent / "var"

        # Load current catalog only
        print("Loading current catalog...")
        current = load_json(var_dir / "catalog.current.json")
        print(f"  Version: {current['program']['version']}")

        # Build indices
        print("Building indices...")
        indices = build_indices(current)
        print(f"  [OK] Nodes indexed: {len(indices['node_to_phase'])}")
        print(f"  [OK] Phases indexed: {len(indices['phase_to_nodes'])}")
        print(f"  [OK] Tags indexed: {len(indices['tag_to_nodes'])}")
        print(f"  [OK] Door/level buckets: {len(indices['door_level_buckets'])}")

        # Compile gates
        print("Compiling gate predicates...")
        gates_compiled = []

        # Phase gates
        for phase in current.get("phases", []):
            gate = phase.get("gate", {})
            gate_id = gate.get("id")

            for check in gate.get("checks", []):
                check_id = check["id"]
                try:
                    compiled = compile_predicate(
                        check["predicate"],
                        current,
                        check_id,
                        indices
                    )
                    compiled["gate_id"] = gate_id
                    compiled["gate_type"] = "phase"
                    compiled["description"] = check.get("description", "")
                    gates_compiled.append(compiled)
                except ValueError as e:
                    print(f"  ERROR in phase gate {gate_id}, check {check_id}: {e}", file=sys.stderr)
                    raise

        # Global gates
        for global_gate in current.get("global_gates", []):
            gate_id = global_gate["id"]

            for check in global_gate.get("checks", []):
                check_id = check["id"]
                try:
                    compiled = compile_predicate(
                        check["predicate"],
                        current,
                        check_id,
                        indices
                    )
                    compiled["gate_id"] = gate_id
                    compiled["gate_type"] = "global"
                    compiled["applies_to"] = global_gate.get("applies_to", "")
                    compiled["description"] = check.get("description", "")
                    gates_compiled.append(compiled)
                except ValueError as e:
                    print(f"  ERROR in global gate {gate_id}, check {check_id}: {e}", file=sys.stderr)
                    raise

        print(f"  [OK] Compiled {len(gates_compiled)} gate checks")

        # Build advisory registry
        print("Building advisory registry...")
        advisory = build_advisory_registry(current)
        phase_count = sum(1 for v in advisory["phase_advisory"].values() if v["present"])
        node_count = sum(1 for v in advisory["node_advisory"].values() if v["present"])
        print(f"  [OK] Phases with advisory: {phase_count}/{len(advisory['phase_advisory'])}")
        print(f"  [OK] Nodes with advisory: {node_count}/{len(advisory['node_advisory'])}")

        # Save compiled rules
        compiled_path = var_dir / "compiled.rules.json"
        print(f"Writing: {compiled_path}")

        compiled = {
            "indices": indices,
            "gates": gates_compiled,
            "advisory": advisory
        }

        save_json(compiled_path, compiled)

        print("[OK] Compilation complete")
        return 0

    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
