"""Stateful tools MCP server."""
import asyncio
from typing import Dict, Any
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

app = Server("mcp-stateful-tools")

# Session state storage
session_state: Dict[str, Any] = {
    "counter": 0,
    "history": [],
    "variables": {}
}

@app.list_resources()
async def list_resources():
    return []

@app.list_tools()
async def list_tools():
    return [
        Tool(
            name="increment_counter",
            description="Increment session counter",
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="get_counter",
            description="Get current counter value",
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="set_variable",
            description="Set a session variable",
            inputSchema={
                "type": "object",
                "properties": {
                    "key": {"type": "string"},
                    "value": {"type": "string"}
                },
                "required": ["key", "value"],
            },
        ),
        Tool(
            name="get_variable",
            description="Get a session variable",
            inputSchema={
                "type": "object",
                "properties": {
                    "key": {"type": "string"}
                },
                "required": ["key"],
            },
        ),
        Tool(
            name="get_history",
            description="Get command history",
            inputSchema={"type": "object", "properties": {}},
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: dict):
    session_state["history"].append(name)

    if name == "increment_counter":
        session_state["counter"] += 1
        return [TextContent(type="text", text=f"Counter: {session_state['counter']}")]
    elif name == "get_counter":
        return [TextContent(type="text", text=f"Counter: {session_state['counter']}")]
    elif name == "set_variable":
        key = arguments["key"]
        value = arguments["value"]
        session_state["variables"][key] = value
        return [TextContent(type="text", text=f"Set {key} = {value}")]
    elif name == "get_variable":
        key = arguments["key"]
        value = session_state["variables"].get(key, "NOT_FOUND")
        return [TextContent(type="text", text=f"{key} = {value}")]
    elif name == "get_history":
        history = ", ".join(session_state["history"][-10:])  # Last 10
        return [TextContent(type="text", text=f"History: {history}")]
    raise ValueError(f"Unknown tool: {name}")

async def main():
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())

if __name__ == "__main__":
    asyncio.run(main())
