#!/usr/bin/env python3
"""Audit all MCP servers to identify testdata requirements."""

TESTDATA_REQUIREMENTS = {
    # Foundation Tier
    "mcp-hello-world": {"types": [], "description": "No testdata needed"},
    "mcp-echo-tool": {"types": [], "description": "No testdata needed"},
    "mcp-simple-retrieval": {"types": [], "description": "Uses in-memory data"},

    # Retrieval Patterns
    "mcp-filesystem-retrieval": {
        "types": ["txt", "md", "py", "json", "csv", "log", "conf"],
        "description": "Needs diverse file types in directory structure"
    },
    "mcp-sqlite-retrieval": {
        "types": ["db"],
        "description": "Needs SQLite databases (already have 5)"
    },
    "mcp-http-retrieval": {
        "types": ["external"],
        "description": "Uses external URLs"
    },
    "mcp-json-retrieval": {
        "types": ["json", "jsonl"],
        "description": "Needs JSON and JSONL files with nested structures"
    },

    # Serialization Patterns
    "mcp-json-serialization": {
        "types": ["json"],
        "description": "Needs JSON with various schemas"
    },
    "mcp-pydantic-models": {
        "types": ["json"],
        "description": "Needs JSON matching Pydantic models"
    },
    "mcp-protocol-buffers": {
        "types": ["proto", "bin"],
        "description": "Needs .proto definitions and binary data"
    },
    "mcp-custom-formats": {
        "types": ["csv", "yaml", "toml"],
        "description": "Needs CSV, YAML, TOML files"
    },

    # Tool-Invocation Patterns
    "mcp-sync-tools": {"types": [], "description": "No testdata needed"},
    "mcp-async-tools": {"types": ["external"], "description": "Uses external URLs"},
    "mcp-stateful-tools": {"types": [], "description": "Uses session state"},
    "mcp-chained-tools": {"types": [], "description": "Uses text inputs"},
    "mcp-error-handling": {"types": [], "description": "Uses error-inducing inputs"},

    # Advanced Integration
    "mcp-rag-pipeline": {
        "types": ["json", "txt", "db"],
        "description": "Can use any text source for knowledge base"
    },
    "mcp-vector-search": {
        "types": ["json", "txt"],
        "description": "Needs text documents for embedding"
    },
    "mcp-streaming-responses": {"types": [], "description": "No testdata needed"},
    "mcp-multi-resource-server": {
        "types": ["json", "txt", "db"],
        "description": "Can integrate multiple sources"
    },
}

# Current testdata
CURRENT_TESTDATA = {
    "db": ["books.db", "library.db", "ecommerce.db", "logistics.db", "finance.db"],
    "json": ["users.json"],
    "txt": ["sample.txt"],
}

print("=" * 70)
print("MCP SERVER TESTDATA AUDIT")
print("=" * 70)
print()

# Collect all needed types
all_types = set()
for server, req in TESTDATA_REQUIREMENTS.items():
    all_types.update(req["types"])

print("REQUIRED FILE TYPES:")
print("-" * 70)
for ftype in sorted(all_types):
    servers_needing = [s for s, r in TESTDATA_REQUIREMENTS.items() if ftype in r["types"]]
    current = CURRENT_TESTDATA.get(ftype, [])
    status = "✓" if current else "✗"
    print(f"{status} {ftype:12} - {len(current):2} files - needed by {len(servers_needing)} servers")
print()

print("MISSING FILE TYPES:")
print("-" * 70)
missing = []
for ftype in sorted(all_types):
    if ftype not in CURRENT_TESTDATA or not CURRENT_TESTDATA[ftype]:
        servers = [s for s, r in TESTDATA_REQUIREMENTS.items() if ftype in r["types"]]
        missing.append((ftype, servers))
        print(f"  • {ftype:12} - needed by: {', '.join(servers[:3])}")
        if len(servers) > 3:
            print(f"                  and {len(servers) - 3} more")

print()
print("RECOMMENDATIONS:")
print("-" * 70)
print("1. Create diverse files for mcp-filesystem-retrieval:")
print("   - Multiple .txt, .md, .py, .json, .csv files")
print("   - Nested directory structure")
print("   - Various file sizes")
print()
print("2. Create JSONL files for mcp-json-retrieval:")
print("   - Line-delimited JSON records")
print("   - Large datasets")
print()
print("3. Create serialization format files:")
print("   - CSV exports from databases")
print("   - YAML configuration files")
print("   - TOML configuration files")
print()
print("4. Create Protocol Buffer files:")
print("   - .proto definitions")
print("   - Binary encoded messages")
print()
print("5. Create document corpus for RAG/Vector Search:")
print("   - Multiple text documents")
print("   - Various domains and topics")
print("=" * 70)
