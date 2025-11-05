"""JSON retrieval MCP server."""
import asyncio
import json
from jsonpath_ng import parse
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Resource, TextContent, Tool

app = Server("mcp-json-retrieval")

SAMPLE_JSON = {
    "users": [
        {"name": "Alice", "age": 30, "city": "NYC"},
        {"name": "Bob", "age": 25, "city": "LA"},
    ],
    "config": {"version": "1.0", "features": ["a", "b", "c"]}
}

@app.list_resources()
async def list_resources():
    return [
        Resource(
            uri="json://sample",
            name="Sample JSON",
            mimeType="application/json"
        )
    ]

@app.list_tools()
async def list_tools():
    return [
        Tool(
            name="query_json",
            description="Query JSON with JSONPath",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "JSONPath expression"}
                },
                "required": ["path"],
            },
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: dict):
    if name == "query_json":
        jsonpath_expr = parse(arguments["path"])
        matches = jsonpath_expr.find(SAMPLE_JSON)
        result = json.dumps([match.value for match in matches], indent=2)
        return [TextContent(type="text", text=result)]
    raise ValueError(f"Unknown tool: {name}")

async def main():
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())

if __name__ == "__main__":
    asyncio.run(main())
