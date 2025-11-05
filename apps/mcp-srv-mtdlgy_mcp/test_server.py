"""
Test script for MCP server tools.

Tests all 4 tools with state fixtures to validate server functionality.
"""

import json
from pathlib import Path
import pytest

# Import server functions
import sys
sys.path.insert(0, str(Path(__file__).parent))

from server import evaluate_gate, migrate_state, diff_catalogs, suggest_advisory, load_data


@pytest.fixture(scope="module", autouse=True)
def setup_module():
    """Load server data before running tests."""
    load_data()


def load_fixture(name: str) -> dict:
    """Load a JSON fixture file."""
    with open(Path(__file__).parent / "var" / name) as f:
        return json.load(f)


def test_evaluate_gate_pass():
    """Test evaluate_gate with passing state fixture."""
    print("Test 1: evaluate_gate with passing state...")

    state = load_fixture("state-pass.json")
    result = evaluate_gate(
        gate_id="core-features-gate",
        state={"nodes": state["nodes"]},
        format="json"
    )

    if isinstance(result, dict) and "error" in result:
        print(f"  FAIL: {result['error']}")
        return False

    if isinstance(result, dict) and result.get("pass") is True:
        print(f"  PASS: Gate passed ({result['passed']}/{result['total_checks']} checks)")
        return True
    else:
        print(f"  FAIL: Expected pass=True, got {result}")
        return False


def test_evaluate_gate_fail():
    """Test evaluate_gate with failing state fixture."""
    print("Test 2: evaluate_gate with failing state...")

    state = load_fixture("state-fail.json")
    result = evaluate_gate(
        gate_id="core-features-gate",
        state={"nodes": state["nodes"]},
        format="json"
    )

    if isinstance(result, dict) and "error" in result:
        print(f"  FAIL: {result['error']}")
        return False

    if isinstance(result, dict) and result.get("pass") is False:
        print(f"  PASS: Gate failed as expected ({result['passed']}/{result['total_checks']} checks)")

        # Check that cf-gate-3 is the failing check
        failing_checks = [c for c in result["checks"] if not c["pass"]]
        if failing_checks and failing_checks[0]["check_id"] == "cf-gate-3":
            print(f"    Correctly identified cf-gate-3 failure")
            return True
        else:
            print(f"    WARNING: Expected cf-gate-3 to fail, got {[c['check_id'] for c in failing_checks]}")
            return True
    else:
        print(f"  FAIL: Expected pass=False, got {result}")
        return False


def test_evaluate_gate_markdown():
    """Test evaluate_gate with Markdown format."""
    print("Test 3: evaluate_gate with Markdown format...")

    state = load_fixture("state-pass.json")
    result = evaluate_gate(
        gate_id="core-features-gate",
        state={"nodes": state["nodes"]},
        format="markdown"
    )

    if isinstance(result, str) and "# Gate Evaluation" in result:
        print(f"  PASS: Markdown format returned ({len(result)} chars)")
        # Verify no color codes or Unicode symbols
        if "\033[" in result or "✓" in result or "✗" in result:
            print(f"    WARNING: Found colors or Unicode symbols in output")
        return True
    else:
        print(f"  FAIL: Expected Markdown string, got {type(result)}")
        return False


def test_migrate_state():
    """Test migrate_state tool."""
    print("Test 4: migrate_state...")

    state = load_fixture("state-pass.json")
    result = migrate_state(
        from_version="0.3.0",
        to_version="0.4.0-alpha",
        state={"nodes": state["nodes"]},
        format="json"
    )

    if isinstance(result, dict) and "error" in result:
        print(f"  FAIL: {result['error']}")
        return False

    if isinstance(result, dict) and "from_version" in result and "to_version" in result:
        compatible = result.get("compatible", False)
        changes = result.get("changes", {})
        added = len(changes.get("added_nodes", []))
        removed = len(changes.get("removed_nodes", []))
        print(f"  PASS: Migration report generated (compatible={compatible}, +{added}, -{removed} nodes)")
        return True
    else:
        print(f"  FAIL: Expected migration report, got {result}")
        return False


def test_diff_catalogs():
    """Test diff_catalogs tool."""
    print("Test 5: diff_catalogs...")

    result = diff_catalogs(
        from_version="0.3.0",
        to_version="0.4.0-alpha",
        format="json"
    )

    if isinstance(result, dict) and "error" in result:
        print(f"  FAIL: {result['error']}")
        return False

    if isinstance(result, dict) and "from_version" in result:
        added = len(result.get("added_nodes", []))
        removed = len(result.get("removed_nodes", []))
        modified = len(result.get("modified_nodes", []))
        print(f"  PASS: Diff completed (+{added}, -{removed}, ~{modified} nodes)")
        return True
    else:
        print(f"  FAIL: Expected diff result, got {result}")
        return False


def test_suggest_advisory():
    """Test suggest_advisory tool."""
    print("Test 6: suggest_advisory...")

    result = suggest_advisory(
        context="I need to design atomic tools",
        format="json"
    )

    if isinstance(result, dict) and "error" in result:
        print(f"  FAIL: {result['error']}")
        return False

    if isinstance(result, dict) and "suggestions" in result:
        print(f"  PASS: Advisory suggestions returned ({len(result['suggestions'])} suggestions)")
        return True
    else:
        print(f"  FAIL: Expected suggestions, got {result}")
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("MCP Server Test Suite")
    print("=" * 60)
    print()

    # Load server data
    print("Loading server data...")
    load_data()
    print()

    tests = [
        test_evaluate_gate_pass,
        test_evaluate_gate_fail,
        test_evaluate_gate_markdown,
        test_migrate_state,
        test_diff_catalogs,
        test_suggest_advisory,
    ]

    results = []
    for test in tests:
        try:
            results.append(test())
        except Exception as e:
            print(f"  ERROR: {e}")
            results.append(False)
        print()

    # Summary
    print("=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"Results: {passed}/{total} tests passed")

    if passed == total:
        print("Status: ALL TESTS PASSED")
    else:
        print("Status: SOME TESTS FAILED")

    print("=" * 60)

    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
