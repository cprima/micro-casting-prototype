"""Async tools MCP server."""
import asyncio
import httpx
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

app = Server("mcp-async-tools")

@app.list_resources()
async def list_resources():
    return []

@app.list_tools()
async def list_tools():
    return [
        Tool(
            name="async_wait",
            description="Asynchronously wait for specified duration",
            inputSchema={
                "type": "object",
                "properties": {
                    "seconds": {"type": "number", "description": "Wait time in seconds (0-5)", "minimum": 0, "maximum": 5}
                },
                "required": ["seconds"],
            },
        ),
        Tool(
            name="parallel_fetch",
            description="Fetch multiple URLs in parallel",
            inputSchema={
                "type": "object",
                "properties": {
                    "urls": {"type": "array", "items": {"type": "string"}, "description": "URLs to fetch (max 3)"}
                },
                "required": ["urls"],
            },
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: dict):
    if name == "async_wait":
        seconds = arguments["seconds"]
        start = asyncio.get_event_loop().time()
        await asyncio.sleep(seconds)
        elapsed = asyncio.get_event_loop().time() - start
        return [TextContent(type="text", text=f"Waited {elapsed:.2f} seconds")]
    elif name == "parallel_fetch":
        urls = arguments["urls"][:3]  # Limit to 3
        async with httpx.AsyncClient(timeout=5.0) as client:
            tasks = [client.get(url) for url in urls]
            responses = await asyncio.gather(*tasks, return_exceptions=True)
            results = []
            for url, response in zip(urls, responses):
                if isinstance(response, Exception):
                    results.append(f"{url}: Error - {str(response)}")
                else:
                    results.append(f"{url}: Status {response.status_code}")
            return [TextContent(type="text", text="\\n".join(results))]
    raise ValueError(f"Unknown tool: {name}")

async def main():
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())

if __name__ == "__main__":
    asyncio.run(main())
