"""Multi-resource MCP server with multiple capabilities."""
import asyncio
import aiofiles
import httpx
from pathlib import Path
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Resource, Tool, TextContent

app = Server("mcp-multi-resource-server")

# In-memory data store
data_store = {
    "notes": [],
    "counters": {"global": 0}
}

@app.list_resources()
async def list_resources():
    return [
        Resource(
            uri="memory://notes",
            name="Notes Store",
            description=f"In-memory notes ({len(data_store['notes'])} entries)",
            mimeType="application/json"
        ),
        Resource(
            uri="memory://counters",
            name="Counters",
            description="Global counters",
            mimeType="application/json"
        )
    ]

@app.list_tools()
async def list_tools():
    return [
        Tool(
            name="add_note",
            description="Add a note to memory",
            inputSchema={
                "type": "object",
                "properties": {
                    "text": {"type": "string"}
                },
                "required": ["text"],
            },
        ),
        Tool(
            name="list_notes",
            description="List all notes",
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="increment",
            description="Increment global counter",
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="fetch_url",
            description="Fetch content from URL",
            inputSchema={
                "type": "object",
                "properties": {
                    "url": {"type": "string"}
                },
                "required": ["url"],
            },
        ),
        Tool(
            name="calculate",
            description="Simple calculator",
            inputSchema={
                "type": "object",
                "properties": {
                    "expression": {"type": "string", "description": "e.g., '2 + 2'"}
                },
                "required": ["expression"],
            },
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: dict):
    if name == "add_note":
        text = arguments["text"]
        note_id = len(data_store["notes"])
        data_store["notes"].append({"id": note_id, "text": text})
        return [TextContent(type="text", text=f"Added note {note_id}")]
    elif name == "list_notes":
        if not data_store["notes"]:
            return [TextContent(type="text", text="No notes")]
        notes = "\\n".join([f"{n['id']}: {n['text']}" for n in data_store["notes"]])
        return [TextContent(type="text", text=notes)]
    elif name == "increment":
        data_store["counters"]["global"] += 1
        return [TextContent(type="text", text=f"Counter: {data_store['counters']['global']}")]
    elif name == "fetch_url":
        url = arguments["url"]
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(url)
                return [TextContent(type="text", text=f"Status: {response.status_code}, Length: {len(response.text)}")]
        except Exception as e:
            return [TextContent(type="text", text=f"Error: {str(e)}")]
    elif name == "calculate":
        expression = arguments["expression"]
        try:
            # Safe eval with limited scope
            result = eval(expression, {"__builtins__": {}}, {})
            return [TextContent(type="text", text=f"{expression} = {result}")]
        except Exception as e:
            return [TextContent(type="text", text=f"Error: {str(e)}")]
    raise ValueError(f"Unknown tool: {name}")

async def main():
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())

if __name__ == "__main__":
    asyncio.run(main())
