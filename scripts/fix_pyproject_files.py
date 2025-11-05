#!/usr/bin/env python3
"""Fix pyproject.toml files to remove build-system requirements."""

import os
from pathlib import Path

# Template for simplified pyproject.toml
TEMPLATE = '''[project]
name = "{name}"
version = "0.1.0"
description = "{description}"
requires-python = ">=3.10"
dependencies = {dependencies}
'''

# Server configurations
servers = {
    "mcp-hello-world": ("Minimal MCP server with basic setup", ["mcp>=0.1.0"]),
    "mcp-echo-tool": ("Simple tool invocation pattern", ["mcp>=0.1.0"]),
    "mcp-simple-retrieval": ("Basic resource retrieval", ["mcp>=0.1.0"]),
    "mcp-filesystem-retrieval": ("File system navigation and reading", ["mcp>=0.1.0", "aiofiles>=23.0.0"]),
    "mcp-sqlite-retrieval": ("Database query and retrieval", ["mcp>=0.1.0", "aiosqlite>=0.19.0"]),
    "mcp-http-retrieval": ("REST API data fetching", ["mcp>=0.1.0", "httpx>=0.25.0"]),
    "mcp-json-retrieval": ("JSON document querying", ["mcp>=0.1.0", "jsonpath-ng>=1.6.0"]),
    "mcp-json-serialization": ("JSON schema validation", ["mcp>=0.1.0", "jsonschema>=4.0.0"]),
    "mcp-pydantic-models": ("Type-safe serialization with Pydantic", ["mcp>=0.1.0", "pydantic>=2.0.0"]),
    "mcp-protocol-buffers": ("Protocol Buffers serialization", ["mcp>=0.1.0", "protobuf>=4.24.0"]),
    "mcp-custom-formats": ("Custom serialization formats", ["mcp>=0.1.0", "pyyaml>=6.0", "toml>=0.10.2"]),
    "mcp-sync-tools": ("Synchronous tool execution", ["mcp>=0.1.0"]),
    "mcp-async-tools": ("Async/await tool patterns", ["mcp>=0.1.0", "httpx>=0.25.0"]),
    "mcp-stateful-tools": ("Tools with persistent session state", ["mcp>=0.1.0"]),
    "mcp-chained-tools": ("Tool composition and chaining", ["mcp>=0.1.0"]),
    "mcp-error-handling": ("Robust error handling patterns", ["mcp>=0.1.0"]),
    "mcp-rag-pipeline": ("RAG pattern", ["mcp>=0.1.0"]),
    "mcp-vector-search": ("Vector database integration", ["mcp>=0.1.0", "numpy>=1.24.0"]),
    "mcp-streaming-responses": ("Streaming data patterns", ["mcp>=0.1.0"]),
    "mcp-multi-resource-server": ("Multi-capability server", ["mcp>=0.1.0", "aiofiles>=23.0.0", "httpx>=0.25.0"]),
}

apps_dir = Path("/home/user/micro-casting-prototype/apps")

for name, (description, dependencies) in servers.items():
    pyproject_path = apps_dir / name / "pyproject.toml"
    if pyproject_path.parent.exists():
        content = TEMPLATE.format(
            name=name,
            description=description,
            dependencies=str(dependencies)
        )
        pyproject_path.write_text(content)
        print(f"✓ Updated {name}/pyproject.toml")

print(f"\n✓ Updated {len(servers)} pyproject.toml files")
