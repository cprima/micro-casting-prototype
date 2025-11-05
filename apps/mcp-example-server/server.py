"""
Example MCP server using mcp-core library.

Demonstrates how to build an MCP server using reusable components
from the mcp-core library.
"""

import asyncio
from mcp.server import Server
from mcp.server.stdio import stdio_server

# Import from mcp-core library
from mcp_core import (
    create_hello_tool,
    hello_handler,
    create_echo_tools,
    echo_handler,
    echo_structured_handler,
)


# Initialize MCP server
app = Server("mcp-example-server")


@app.list_resources()
async def list_resources():
    """List available resources (none in this example)."""
    return []


@app.list_tools()
async def list_tools():
    """
    List available tools.

    Uses tool definitions from mcp-core library.
    """
    return [create_hello_tool()] + create_echo_tools()


@app.call_tool()
async def call_tool(name: str, arguments: dict):
    """
    Handle tool invocations.

    Routes to appropriate handlers from mcp-core library.

    Args:
        name: Tool name
        arguments: Tool arguments

    Returns:
        Tool execution results

    Raises:
        ValueError: If tool name is unknown
    """
    # Route to mcp-core handlers
    if name == "hello":
        return await hello_handler(arguments)
    elif name == "echo":
        return await echo_handler(arguments)
    elif name == "echo_structured":
        return await echo_structured_handler(arguments)

    raise ValueError(f"Unknown tool: {name}")


async def main():
    """Main entry point for the MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
