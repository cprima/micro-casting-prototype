"""Custom formats MCP server."""
import asyncio
import csv
import io
import yaml
import tomli
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

app = Server("mcp-custom-formats")

@app.list_resources()
async def list_resources():
    return []

@app.list_tools()
async def list_tools():
    return [
        Tool(
            name="parse_yaml",
            description="Parse YAML string",
            inputSchema={
                "type": "object",
                "properties": {
                    "yaml_string": {"type": "string"}
                },
                "required": ["yaml_string"],
            },
        ),
        Tool(
            name="csv_to_json",
            description="Convert CSV to JSON",
            inputSchema={
                "type": "object",
                "properties": {
                    "csv_string": {"type": "string"}
                },
                "required": ["csv_string"],
            },
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: dict):
    if name == "parse_yaml":
        data = yaml.safe_load(arguments["yaml_string"])
        return [TextContent(type="text", text=str(data))]
    elif name == "csv_to_json":
        reader = csv.DictReader(io.StringIO(arguments["csv_string"]))
        rows = list(reader)
        return [TextContent(type="text", text=str(rows))]
    raise ValueError(f"Unknown tool: {name}")

async def main():
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())

if __name__ == "__main__":
    asyncio.run(main())
