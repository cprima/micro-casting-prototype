"""Echo tool with parameter validation."""
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
        result = "\n".join([text] * count)
        return [TextContent(type="text", text=result)]
    raise ValueError(f"Unknown tool: {name}")

async def main():
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())

if __name__ == "__main__":
    asyncio.run(main())
