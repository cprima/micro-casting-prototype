"""Chained tools MCP server."""
import asyncio
import json
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

app = Server("mcp-chained-tools")

@app.list_resources()
async def list_resources():
    return []

@app.list_tools()
async def list_tools():
    return [
        Tool(
            name="extract_numbers",
            description="Extract numbers from text",
            inputSchema={
                "type": "object",
                "properties": {
                    "text": {"type": "string"}
                },
                "required": ["text"],
            },
        ),
        Tool(
            name="sum_numbers",
            description="Sum a list of numbers",
            inputSchema={
                "type": "object",
                "properties": {
                    "numbers": {"type": "array", "items": {"type": "number"}}
                },
                "required": ["numbers"],
            },
        ),
        Tool(
            name="format_result",
            description="Format a result with units",
            inputSchema={
                "type": "object",
                "properties": {
                    "value": {"type": "number"},
                    "unit": {"type": "string"}
                },
                "required": ["value", "unit"],
            },
        ),
        Tool(
            name="chain_example",
            description="Example: extract numbers from text, sum them, format result",
            inputSchema={
                "type": "object",
                "properties": {
                    "text": {"type": "string"}
                },
                "required": ["text"],
            },
        )
    ]

def extract_numbers_impl(text: str) -> list:
    """Extract numbers from text."""
    import re
    return [float(x) for x in re.findall(r'-?\\d+\\.?\\d*', text)]

def sum_numbers_impl(numbers: list) -> float:
    """Sum numbers."""
    return sum(numbers)

def format_result_impl(value: float, unit: str) -> str:
    """Format result."""
    return f"{value:.2f} {unit}"

@app.call_tool()
async def call_tool(name: str, arguments: dict):
    if name == "extract_numbers":
        text = arguments["text"]
        numbers = extract_numbers_impl(text)
        return [TextContent(type="text", text=json.dumps(numbers))]
    elif name == "sum_numbers":
        numbers = arguments["numbers"]
        result = sum_numbers_impl(numbers)
        return [TextContent(type="text", text=str(result))]
    elif name == "format_result":
        value = arguments["value"]
        unit = arguments["unit"]
        result = format_result_impl(value, unit)
        return [TextContent(type="text", text=result)]
    elif name == "chain_example":
        # Demonstrate chaining: extract -> sum -> format
        text = arguments["text"]
        numbers = extract_numbers_impl(text)
        total = sum_numbers_impl(numbers)
        formatted = format_result_impl(total, "units")
        steps = f"1. Extracted: {numbers}\\n2. Sum: {total}\\n3. Formatted: {formatted}"
        return [TextContent(type="text", text=steps)]
    raise ValueError(f"Unknown tool: {name}")

async def main():
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())

if __name__ == "__main__":
    asyncio.run(main())
