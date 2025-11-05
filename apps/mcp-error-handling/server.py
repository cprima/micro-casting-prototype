"""Error handling MCP server."""
import asyncio
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

app = Server("mcp-error-handling")

@app.list_resources()
async def list_resources():
    return []

@app.list_tools()
async def list_tools():
    return [
        Tool(
            name="divide",
            description="Divide two numbers with error handling",
            inputSchema={
                "type": "object",
                "properties": {
                    "a": {"type": "number"},
                    "b": {"type": "number"}
                },
                "required": ["a", "b"],
            },
        ),
        Tool(
            name="parse_json",
            description="Parse JSON with error handling",
            inputSchema={
                "type": "object",
                "properties": {
                    "json_string": {"type": "string"}
                },
                "required": ["json_string"],
            },
        ),
        Tool(
            name="validate_email",
            description="Validate email format",
            inputSchema={
                "type": "object",
                "properties": {
                    "email": {"type": "string"}
                },
                "required": ["email"],
            },
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: dict):
    try:
        if name == "divide":
            a = arguments["a"]
            b = arguments["b"]
            if b == 0:
                return [TextContent(type="text", text="Error: Division by zero")]
            result = a / b
            return [TextContent(type="text", text=f"Result: {result}")]
        elif name == "parse_json":
            import json
            json_string = arguments["json_string"]
            try:
                data = json.loads(json_string)
                return [TextContent(type="text", text=f"Valid JSON: {json.dumps(data, indent=2)}")]
            except json.JSONDecodeError as e:
                return [TextContent(type="text", text=f"JSON Error: {str(e)}")]
        elif name == "validate_email":
            import re
            email = arguments["email"]
            pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$'
            if re.match(pattern, email):
                return [TextContent(type="text", text=f"Valid email: {email}")]
            else:
                return [TextContent(type="text", text=f"Invalid email format: {email}")]
        raise ValueError(f"Unknown tool: {name}")
    except Exception as e:
        return [TextContent(type="text", text=f"Unexpected error: {type(e).__name__}: {str(e)}")]

async def main():
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())

if __name__ == "__main__":
    asyncio.run(main())
