"""HTTP retrieval MCP server."""
import asyncio
import httpx
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Resource, TextContent, Tool

app = Server("mcp-http-retrieval")

@app.list_resources()
async def list_resources():
    return [
        Resource(
            uri="http://api.github.com/users/github",
            name="GitHub API Example",
            mimeType="application/json"
        )
    ]

@app.list_tools()
async def list_tools():
    return [
        Tool(
            name="fetch_url",
            description="Fetch content from URL",
            inputSchema={
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "URL to fetch"}
                },
                "required": ["url"],
            },
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: dict):
    if name == "fetch_url":
        url = arguments["url"]
        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=10.0)
            response.raise_for_status()
            content = response.text[:1000]  # First 1000 chars
        return [TextContent(type="text", text=content)]
    raise ValueError(f"Unknown tool: {name}")

async def main():
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())

if __name__ == "__main__":
    asyncio.run(main())
