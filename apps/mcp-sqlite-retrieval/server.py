"""SQLite retrieval MCP server."""
import asyncio
import aiosqlite
from pathlib import Path
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Resource, TextContent, Tool

app = Server("mcp-sqlite-retrieval")

# Use test database if available
DB_PATH = Path(__file__).parent.parent.parent / "libs" / "mcp-testdata" / "src" / "mcp_testdata" / "data" / "library.db"
if not DB_PATH.exists():
    DB_PATH = ":memory:"

@app.list_resources()
async def list_resources():
    return [
        Resource(
            uri="sqlite://library/books",
            name="Books Table",
            description="Library books data",
            mimeType="application/json"
        )
    ]

@app.list_tools()
async def list_tools():
    return [
        Tool(
            name="query_database",
            description="Execute SQL query",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "SQL query"}
                },
                "required": ["query"],
            },
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: dict):
    if name == "query_database":
        query = arguments["query"]
        async with aiosqlite.connect(DB_PATH) as db:
            async with db.execute(query) as cursor:
                rows = await cursor.fetchall()
                result = "\\n".join([str(row) for row in rows[:10]])
        return [TextContent(type="text", text=result)]
    raise ValueError(f"Unknown tool: {name}")

async def main():
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())

if __name__ == "__main__":
    asyncio.run(main())
