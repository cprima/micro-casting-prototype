"""Simple resource retrieval."""
import asyncio
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Resource, TextContent

app = Server("mcp-simple-retrieval")

SAMPLE_DATA = {
    "docs/readme": "Welcome to MCP Server!",
    "docs/guide": "This is a simple retrieval example.",
    "data/config": "{\"key\": \"value\"}",
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
