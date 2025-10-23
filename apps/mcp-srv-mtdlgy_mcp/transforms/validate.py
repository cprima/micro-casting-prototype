"""
Stage 2: Validate

Fail-fast checks: invariants, fingerprints, gate ID uniqueness
"""
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from utils import load_json, assert_invariants, validate_fingerprint, check_gate_ids_unique


def main():
    try:
        var_dir = Path(__file__).parent.parent / "var"

        # Load catalogs
        print("Loading catalogs from var/...")
        current = load_json(var_dir / "catalog.current.json")
        previous = load_json(var_dir / "catalog.previous.json")

        print(f"  Current: {current['program']['version']}")
        print(f"  Previous: {previous['program']['version']}")

        # Check invariants (current is canonical)
        print("Checking invariants (levels/tags/global_gates)...")
        assert_invariants(current, previous)
        print("  [OK] Invariants match")

        # Validate fingerprints
        print("Validating fingerprints...")
        validate_fingerprint(current["program"]["fingerprint"])
        validate_fingerprint(previous["program"]["fingerprint"])
        print(f"  [OK] Current: {current['program']['fingerprint']}")
        print(f"  [OK] Previous: {previous['program']['fingerprint']}")

        # Check gate ID uniqueness
        print("Checking gate ID uniqueness...")
        check_gate_ids_unique(current)
        print("  [OK] All gate IDs unique")

        print("[OK] Validation complete")
        return 0

    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
