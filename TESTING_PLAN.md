# MCP Server Monorepo - Testing Plan

This document describes how to validate the complete MCP server monorepo test suite.

## Quick Start

```bash
# Clone and test everything
git clone https://github.com/cprima/micro-casting-prototype.git
cd micro-casting-prototype
git checkout claude/mcp-server-monorepo-setup-011CUoKsKuAUdWuutmyr5CVG
python scripts/run_all_tests.py
```

Expected result: **195/195 tests passed (100% success rate)**

---

## Prerequisites

### Required
- **Python 3.11+** - Check with `python3 --version`
- **uv package manager** - Fast Python package installer

### Install uv

**Linux/macOS:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Alternative (pip):**
```bash
pip install uv
```

**Verify installation:**
```bash
uv --version
```

---

## Complete Validation Process

### Step 1: Clone Repository

```bash
git clone https://github.com/cprima/micro-casting-prototype.git
cd micro-casting-prototype
```

### Step 2: Checkout Test Branch

```bash
git checkout claude/mcp-server-monorepo-setup-011CUoKsKuAUdWuutmyr5CVG
```

### Step 3: Verify Branch

```bash
git log --oneline -5
```

You should see these recent commits:
- `85cd8f9` - docs: update test results - 100% success rate achieved
- `f2c228c` - fix: add pytest fixture to load catalog data in mcp-srv-mtdlgy_mcp
- `4005b47` - docs: add final test results summary
- `efd2fad` - test: add comprehensive test suites for 16 MCP servers and fix issues

### Step 4: Run Complete Test Suite

**Run all servers:**
```bash
python scripts/run_all_tests.py
```

**Expected output:**
```
=== Testing mcp-hello-world ===
........                                                                 [100%]
8 passed in 0.96s

=== Testing mcp-echo-tool ===
............                                                             [100%]
12 passed in 0.97s

[... continues for all 21 servers ...]

============================================================
FINAL RESULTS
============================================================
Total: 195/195 tests passed
Failed: 0
Success Rate: 100.0%
============================================================
```

---

## Individual Server Testing

### Test a Specific Server

```bash
cd apps/mcp-hello-world
uv run pytest test_server.py -v
```

### Test with Coverage Report

```bash
cd apps/mcp-hello-world
uv run pytest test_server.py -v --cov=server --cov-report=term-missing
```

### Test with Detailed Output

```bash
cd apps/mcp-hello-world
uv run pytest test_server.py -v --tb=short
```

---

## Server Inventory

### Foundation Tier (3 servers, 24 tests)
```bash
cd apps/mcp-hello-world && uv run pytest test_server.py -q        # 8 tests
cd apps/mcp-echo-tool && uv run pytest test_server.py -q          # 12 tests
cd apps/mcp-simple-retrieval && uv run pytest test_server.py -q   # 4 tests
```

### Retrieval Tier (4 servers, 71 tests)
```bash
cd apps/mcp-filesystem-retrieval && uv run pytest test_server.py -q  # 33 tests
cd apps/mcp-json-retrieval && uv run pytest test_server.py -q        # 32 tests
cd apps/mcp-sqlite-retrieval && uv run pytest test_server.py -q      # 6 tests
cd apps/mcp-http-retrieval && uv run pytest test_server.py -q        # 6 tests
```

### Serialization Tier (4 servers, 27 tests)
```bash
cd apps/mcp-custom-formats && uv run pytest test_server.py -q        # 15 tests
cd apps/mcp-json-serialization && uv run pytest test_server.py -q    # 6 tests
cd apps/mcp-pydantic-models && uv run pytest test_server.py -q       # 6 tests
cd apps/mcp-protocol-buffers && uv run pytest test_server.py -q      # 6 tests
```

### Tool-Invocation Tier (5 servers, 32 tests)
```bash
cd apps/mcp-sync-tools && uv run pytest test_server.py -q        # 7 tests
cd apps/mcp-async-tools && uv run pytest test_server.py -q       # 6 tests
cd apps/mcp-stateful-tools && uv run pytest test_server.py -q    # 6 tests
cd apps/mcp-chained-tools && uv run pytest test_server.py -q     # 6 tests
cd apps/mcp-error-handling && uv run pytest test_server.py -q    # 7 tests
```

### Advanced Tier (4 servers, 24 tests)
```bash
cd apps/mcp-rag-pipeline && uv run pytest test_server.py -q          # 6 tests
cd apps/mcp-vector-search && uv run pytest test_server.py -q         # 6 tests
cd apps/mcp-streaming-responses && uv run pytest test_server.py -q   # 6 tests
cd apps/mcp-multi-resource-server && uv run pytest test_server.py -q # 6 tests
```

### Additional Server (1 server, 6 tests)
```bash
cd apps/mcp-srv-mtdlgy_mcp && uv run pytest test_server.py -q   # 6 tests
```

---

## Manual Test Loop

Run all servers manually:

```bash
cd apps
for dir in mcp-*/; do
    if [ -f "$dir/test_server.py" ]; then
        echo "=== Testing $dir ==="
        cd "$dir"
        uv run pytest test_server.py -q
        cd ..
    fi
done
```

---

## Troubleshooting

### Issue: `uv: command not found`

**Solution:** Install uv package manager
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
# Or: pip install uv
```

### Issue: `Python version mismatch`

**Solution:** Ensure Python 3.11+ is installed
```bash
python3 --version  # Should be 3.11 or higher
```

### Issue: Network errors during HTTP tests

**Symptom:** `mcp-http-retrieval` tests skip with network errors

**Explanation:** The test is designed to skip gracefully in restricted network environments. This is expected behavior and not a failure.

### Issue: Slow first run

**Explanation:** `uv` downloads and caches dependencies on first run. Subsequent runs are much faster.

**Solution:** Be patient on first run, or pre-warm the cache:
```bash
cd apps/mcp-hello-world
uv sync
```

### Issue: Permission errors

**Solution:** Ensure you have write permissions in the directory
```bash
chmod -R u+w micro-casting-prototype
```

---

## Continuous Integration

### GitHub Actions Example

```yaml
name: Test MCP Servers

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install uv
        run: curl -LsSf https://astral.sh/uv/install.sh | sh

      - name: Run all tests
        run: python scripts/run_all_tests.py
```

---

## Test Categories

Each test suite includes:

### 1. TestListTools
- Validates tool listing returns a list
- Checks tool structure (name, description, inputSchema)
- Ensures all required fields are present

### 2. TestListResources
- Validates resource listing returns a list
- Checks resource structure when applicable

### 3. TestIntegration
- Tests actual tool functionality
- Validates input/output behavior
- Tests workflows and tool composition

### 4. TestErrorHandling
- Tests unknown tool errors
- Tests invalid input handling
- Tests edge cases

---

## Performance Benchmarks

Expected test execution times (approximate):

| Server | Tests | Time |
|--------|-------|------|
| mcp-hello-world | 8 | ~1s |
| mcp-echo-tool | 12 | ~1s |
| mcp-filesystem-retrieval | 33 | ~1.2s |
| mcp-json-retrieval | 32 | ~1.1s |
| **Total (all servers)** | **195** | **~25-30s** |

*Times vary based on system performance and network conditions*

---

## Validation Checklist

- [ ] Repository cloned successfully
- [ ] Branch `claude/mcp-server-monorepo-setup-011CUoKsKuAUdWuutmyr5CVG` checked out
- [ ] uv package manager installed
- [ ] All 195 tests pass (100% success rate)
- [ ] No errors or failures reported
- [ ] All 21 servers tested

---

## Success Criteria

✅ **Test suite is valid if:**
- All 195 tests pass
- 0 failures reported
- Success rate is 100.0%
- No exceptions or errors during test execution

❌ **Test suite has issues if:**
- Any test failures occur
- Success rate below 100%
- Python/dependency errors
- Missing test files

---

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review `TEST_RESULTS_FINAL.md` for detailed results
3. Check individual server `test_server.py` files
4. Review commit history for recent changes

---

## Related Documentation

- `TEST_RESULTS_FINAL.md` - Detailed test results and bug fixes
- `TEST_REPORT.md` - Initial test report
- `docs/mcp-server-blueprints.md` - Server architecture overview
- Individual server `README.md` files in `apps/*/`

---

## Version Information

- **Branch:** `claude/mcp-server-monorepo-setup-011CUoKsKuAUdWuutmyr5CVG`
- **Test Suite Version:** 1.0
- **Total Tests:** 195
- **Total Servers:** 21
- **Success Rate:** 100%
- **Last Updated:** 2025-11-05
