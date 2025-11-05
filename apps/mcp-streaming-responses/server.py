"""Streaming responses MCP server."""
import asyncio
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

app = Server("mcp-streaming-responses")

@app.list_resources()
async def list_resources():
    return []

@app.list_tools()
async def list_tools():
    return [
        Tool(
            name="stream_count",
            description="Simulate streaming count from 1 to N",
            inputSchema={
                "type": "object",
                "properties": {
                    "count": {"type": "integer", "description": "Count to (1-10)", "minimum": 1, "maximum": 10}
                },
                "required": ["count"],
            },
        ),
        Tool(
            name="stream_text",
            description="Simulate streaming text word by word",
            inputSchema={
                "type": "object",
                "properties": {
                    "text": {"type": "string"}
                },
                "required": ["text"],
            },
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: dict):
    if name == "stream_count":
        count = arguments["count"]
        # Simulate streaming by building result incrementally
        results = []
        for i in range(1, count + 1):
            await asyncio.sleep(0.1)  # Simulate delay
            results.append(str(i))
        return [TextContent(type="text", text=" -> ".join(results))]
    elif name == "stream_text":
        text = arguments["text"]
        words = text.split()
        # Simulate streaming words
        results = []
        for word in words:
            await asyncio.sleep(0.05)
            results.append(word)
        return [TextContent(type="text", text=" | ".join(results))]
    raise ValueError(f"Unknown tool: {name}")

async def main():
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())

if __name__ == "__main__":
    asyncio.run(main())
