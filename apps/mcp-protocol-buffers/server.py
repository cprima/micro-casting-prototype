"""Protocol Buffers MCP server (minimal example)."""
import asyncio
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

app = Server("mcp-protocol-buffers")

@app.list_resources()
async def list_resources():
    return []

@app.list_tools()
async def list_tools():
    return [
        Tool(
            name="demo_protobuf",
            description="Demonstrate protobuf serialization",
            inputSchema={
                "type": "object",
                "properties": {
                    "message": {"type": "string"}
                },
                "required": ["message"],
            },
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: dict):
    if name == "demo_protobuf":
        # Simplified protobuf demo
        msg = arguments["message"]
        return [TextContent(type="text", text=f"Protobuf demo: {msg}")]
    raise ValueError(f"Unknown tool: {name}")

async def main():
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())

if __name__ == "__main__":
    asyncio.run(main())
