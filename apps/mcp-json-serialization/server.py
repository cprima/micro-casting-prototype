"""JSON serialization MCP server."""
import asyncio
import json
from jsonschema import validate, ValidationError
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

app = Server("mcp-json-serialization")

SCHEMA = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "age": {"type": "integer", "minimum": 0}
    },
    "required": ["name"]
}

@app.list_resources()
async def list_resources():
    return []

@app.list_tools()
async def list_tools():
    return [
        Tool(
            name="validate_json",
            description="Validate JSON against schema",
            inputSchema={
                "type": "object",
                "properties": {
                    "data": {"type": "string", "description": "JSON string to validate"}
                },
                "required": ["data"],
            },
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: dict):
    if name == "validate_json":
        try:
            data = json.loads(arguments["data"])
            validate(instance=data, schema=SCHEMA)
            return [TextContent(type="text", text="Valid JSON")]
        except (json.JSONDecodeError, ValidationError) as e:
            return [TextContent(type="text", text=f"Invalid: {str(e)}")]
    raise ValueError(f"Unknown tool: {name}")

async def main():
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())

if __name__ == "__main__":
    asyncio.run(main())
