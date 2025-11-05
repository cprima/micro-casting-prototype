#!/usr/bin/env python3
"""Run all MCP server tests and summarize results."""

import subprocess
from pathlib import Path
import re

apps_dir = Path("/home/user/micro-casting-prototype/apps")
total_tests = 0
total_passed = 0
total_failed = 0

servers_tested = []

for server_dir in sorted(apps_dir.glob("mcp-*")):
    test_file = server_dir / "test_server.py"
    if not test_file.exists():
        continue

    print(f"=== Testing {server_dir.name} ===")

    try:
        result = subprocess.run(
            ["uv", "run", "pytest", "test_server.py", "-q"],
            cwd=server_dir,
            capture_output=True,
            text=True,
            timeout=30
        )

        output = result.stdout + result.stderr
        print(output)

        # Parse results
        passed_match = re.search(r'(\d+) passed', output)
        failed_match = re.search(r'(\d+) failed', output)

        passed = int(passed_match.group(1)) if passed_match else 0
        failed = int(failed_match.group(1)) if failed_match else 0

        total_tests += passed + failed
        total_passed += passed
        total_failed += failed

        servers_tested.append({
            'name': server_dir.name,
            'passed': passed,
            'failed': failed
        })

    except subprocess.TimeoutExpired:
        print("TIMEOUT")
        servers_tested.append({
            'name': server_dir.name,
            'passed': 0,
            'failed': 1
        })
        total_tests += 1
        total_failed += 1
    except Exception as e:
        print(f"ERROR: {e}")

print("\n" + "="*60)
print("FINAL RESULTS")
print("="*60)
print(f"Total: {total_passed}/{total_tests} tests passed")
print(f"Failed: {total_failed}")
if total_tests > 0:
    print(f"Success Rate: {(total_passed/total_tests)*100:.1f}%")
print("="*60)

if total_failed > 0:
    print("\nFailed servers:")
    for server in servers_tested:
        if server['failed'] > 0:
            print(f"  - {server['name']}: {server['failed']} failures")
