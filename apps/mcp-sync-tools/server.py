"""Synchronous tools MCP server."""
import asyncio
import time
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

app = Server("mcp-sync-tools")

@app.list_resources()
async def list_resources():
    return []

@app.list_tools()
async def list_tools():
    return [
        Tool(
            name="calculate_factorial",
            description="Calculate factorial (synchronous computation)",
            inputSchema={
                "type": "object",
                "properties": {
                    "n": {"type": "integer", "description": "Number (0-20)", "minimum": 0, "maximum": 20}
                },
                "required": ["n"],
            },
        ),
        Tool(
            name="fibonacci",
            description="Calculate Fibonacci number",
            inputSchema={
                "type": "object",
                "properties": {
                    "n": {"type": "integer", "description": "Position (0-30)", "minimum": 0, "maximum": 30}
                },
                "required": ["n"],
            },
        )
    ]

def factorial(n: int) -> int:
    """Synchronous factorial calculation."""
    if n <= 1:
        return 1
    return n * factorial(n - 1)

def fibonacci(n: int) -> int:
    """Synchronous fibonacci calculation."""
    if n <= 1:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)

@app.call_tool()
async def call_tool(name: str, arguments: dict):
    if name == "calculate_factorial":
        n = arguments["n"]
        result = factorial(n)
        return [TextContent(type="text", text=f"factorial({n}) = {result}")]
    elif name == "fibonacci":
        n = arguments["n"]
        result = fibonacci(n)
        return [TextContent(type="text", text=f"fibonacci({n}) = {result}")]
    raise ValueError(f"Unknown tool: {name}")

async def main():
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())

if __name__ == "__main__":
    asyncio.run(main())
