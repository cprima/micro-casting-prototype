"""
Hello tool pattern - the simplest possible MCP tool.

Demonstrates basic tool definition, parameter handling, and response formatting.
"""

from mcp.types import Tool, TextContent


def create_hello_tool() -> Tool:
    """
    Create a hello tool definition.

    Returns:
        Tool definition for the hello tool.
    """
    return Tool(
        name="hello",
        description="Say hello to the world or a specific person",
        inputSchema={
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "Name of person to greet (optional)",
                }
            },
        },
    )


async def hello_handler(arguments: dict) -> list[TextContent]:
    """
    Handle hello tool invocation.

    Args:
        arguments: Tool arguments with optional 'name' parameter.

    Returns:
        List containing greeting text content.
    """
    person_name = arguments.get("name", "World")
    greeting = f"Hello, {person_name}! 👋"

    return [TextContent(type="text", text=greeting)]
