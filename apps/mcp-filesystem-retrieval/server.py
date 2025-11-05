"""Filesystem retrieval MCP server."""
import asyncio
import aiofiles
from pathlib import Path
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Resource, TextContent, Tool

app = Server("mcp-filesystem-retrieval")
BASE_DIR = Path.home()

@app.list_resources()
async def list_resources():
    resources = []
    for path in BASE_DIR.rglob("*.txt"):
        if path.is_file():
            resources.append(Resource(
                uri=f"file://{path}",
                name=str(path.relative_to(BASE_DIR)),
                mimeType="text/plain"
            ))
    return resources[:10]  # Limit to 10

@app.read_resource()
async def read_resource(uri: str):
    path = Path(uri.replace("file://", ""))
    if not path.exists():
        raise ValueError(f"File not found: {uri}")
    async with aiofiles.open(path, 'r') as f:
        content = await f.read()
    return [TextContent(type="text", text=content[:1000])]  # First 1000 chars

@app.list_tools()
async def list_tools():
    return [
        Tool(
            name="list_directory",
            description="List files in a directory",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Directory path"}
                },
                "required": ["path"],
            },
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: dict):
    if name == "list_directory":
        path = Path(arguments["path"])
        if not path.exists() or not path.is_dir():
            raise ValueError(f"Invalid directory: {path}")
        files = [str(f.name) for f in path.iterdir()][:20]
        return [TextContent(type="text", text="\\n".join(files))]
    raise ValueError(f"Unknown tool: {name}")

async def main():
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())

if __name__ == "__main__":
    asyncio.run(main())
