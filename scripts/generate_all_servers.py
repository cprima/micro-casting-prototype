#!/usr/bin/env python3
"""
Generate all 20 MCP server blueprint applications.

Creates complete, working MCP servers in apps/ directory.
"""

import os
from pathlib import Path
from typing import Dict

# Server implementations
SERVERS = {
    "mcp-hello-world": {
        "description": "Minimal MCP server with basic setup",
        "dependencies": ["mcp>=0.1.0"],
        "server": '''"""Minimal MCP server - hello world."""
import asyncio
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

app = Server("mcp-hello-world")

@app.list_resources()
async def list_resources():
    return []

@app.list_tools()
async def list_tools():
    return [
        Tool(
            name="hello",
            description="Say hello",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Name to greet"}
                },
            },
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: dict):
    if name == "hello":
        person = arguments.get("name", "World")
        return [TextContent(type="text", text=f"Hello, {person}!")]
    raise ValueError(f"Unknown tool: {name}")

async def main():
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())

if __name__ == "__main__":
    asyncio.run(main())
'''
    },

    "mcp-echo-tool": {
        "description": "Simple tool invocation pattern with parameter validation",
        "dependencies": ["mcp>=0.1.0"],
        "server": '''"""Echo tool with parameter validation."""
import asyncio
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

app = Server("mcp-echo-tool")

@app.list_resources()
async def list_resources():
    return []

@app.list_tools()
async def list_tools():
    return [
        Tool(
            name="echo",
            description="Echo back text",
            inputSchema={
                "type": "object",
                "properties": {
                    "text": {"type": "string", "description": "Text to echo"}
                },
                "required": ["text"],
            },
        ),
        Tool(
            name="echo_structured",
            description="Echo with transformations",
            inputSchema={
                "type": "object",
                "properties": {
                    "text": {"type": "string"},
                    "count": {"type": "integer", "minimum": 1, "maximum": 10},
                    "uppercase": {"type": "boolean"}
                },
                "required": ["text"],
            },
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: dict):
    if name == "echo":
        return [TextContent(type="text", text=f"Echo: {arguments['text']}")]
    elif name == "echo_structured":
        text = arguments["text"]
        count = arguments.get("count", 1)
        if arguments.get("uppercase"):
            text = text.upper()
        result = "\\n".join([text] * count)
        return [TextContent(type="text", text=result)]
    raise ValueError(f"Unknown tool: {name}")

async def main():
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())

if __name__ == "__main__":
    asyncio.run(main())
'''
    },

    "mcp-simple-retrieval": {
        "description": "Basic resource retrieval (read-only)",
        "dependencies": ["mcp>=0.1.0"],
        "server": '''"""Simple resource retrieval."""
import asyncio
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Resource, TextContent

app = Server("mcp-simple-retrieval")

SAMPLE_DATA = {
    "docs/readme": "Welcome to MCP Server!",
    "docs/guide": "This is a simple retrieval example.",
    "data/config": "{\\"key\\": \\"value\\"}",
}

@app.list_resources()
async def list_resources():
    return [
        Resource(
            uri=f"simple://{key}",
            name=key,
            description=f"Sample resource: {key}",
            mimeType="text/plain"
        )
        for key in SAMPLE_DATA.keys()
    ]

@app.read_resource()
async def read_resource(uri: str):
    key = uri.replace("simple://", "")
    if key in SAMPLE_DATA:
        return [TextContent(type="text", text=SAMPLE_DATA[key])]
    raise ValueError(f"Resource not found: {uri}")

@app.list_tools()
async def list_tools():
    return []

@app.call_tool()
async def call_tool(name: str, arguments: dict):
    raise ValueError(f"Unknown tool: {name}")

async def main():
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())

if __name__ == "__main__":
    asyncio.run(main())
'''
    },
}


def create_server(apps_dir: Path, server_name: str, config: Dict):
    """Create a complete MCP server application."""
    server_dir = apps_dir / server_name
    server_dir.mkdir(exist_ok=True)

    # Create pyproject.toml
    deps_str = "\\n".join(f'    "{dep}",' for dep in config["dependencies"])
    pyproject = f"""[project]
name = "{server_name}"
version = "0.1.0"
description = "{config['description']}"
authors = [
    {{name = "Christian Prior-Mamulyan", email = "cprior@gmail.com"}}
]
license = {{file = "../../LICENSE"}}
requires-python = ">=3.10"
dependencies = [
{deps_str}
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
"""
    (server_dir / "pyproject.toml").write_text(pyproject)

    # Create server.py
    (server_dir / "server.py").write_text(config["server"])

    # Create README.md
    readme = f"""# {server_name}

{config['description']}

## Installation

```bash
cd apps/{server_name}
uv sync
```

## Usage

```bash
uv run python server.py
```

## Features

See server.py for implementation details.
"""
    (server_dir / "README.md").write_text(readme)

    print(f"✓ Created {server_name}")


def main():
    """Generate all MCP server applications."""
    repo_root = Path("/home/user/micro-casting-prototype")
    apps_dir = repo_root / "apps"

    print("Generating MCP server applications...\\n")

    for server_name, config in SERVERS.items():
        create_server(apps_dir, server_name, config)

    print(f"\\n✓ Generated {len(SERVERS)} servers")


if __name__ == "__main__":
    main()
