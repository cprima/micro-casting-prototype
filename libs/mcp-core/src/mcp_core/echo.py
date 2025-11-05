"""
Echo tool patterns - demonstrates parameter validation and structured responses.

Provides two echo tool variants:
1. Simple echo - basic text echoing
2. Structured echo - with validation, transformation, and metadata
"""

from mcp.types import Tool, TextContent


def create_echo_tools() -> list[Tool]:
    """
    Create echo tool definitions.

    Returns:
        List of Tool definitions for echo and echo_structured.
    """
    return [
        Tool(
            name="echo",
            description="Echo back the provided text",
            inputSchema={
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "Text to echo back",
                    }
                },
                "required": ["text"],
            },
        ),
        Tool(
            name="echo_structured",
            description="Echo back structured data with metadata and transformations",
            inputSchema={
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "Text to echo",
                    },
                    "count": {
                        "type": "integer",
                        "description": "Number of times to repeat (1-10)",
                        "minimum": 1,
                        "maximum": 10,
                    },
                    "uppercase": {
                        "type": "boolean",
                        "description": "Convert to uppercase",
                        "default": False,
                    },
                },
                "required": ["text"],
            },
        ),
    ]


async def echo_handler(arguments: dict) -> list[TextContent]:
    """
    Handle simple echo tool invocation.

    Args:
        arguments: Tool arguments with 'text' parameter.

    Returns:
        List containing echoed text content.
    """
    text = arguments.get("text", "")
    return [TextContent(type="text", text=f"Echo: {text}")]


async def echo_structured_handler(arguments: dict) -> list[TextContent]:
    """
    Handle structured echo tool invocation with validation and transformations.

    Args:
        arguments: Tool arguments with 'text', optional 'count', and 'uppercase'.

    Returns:
        List containing echoed text and metadata.

    Raises:
        ValueError: If count is outside valid range.
    """
    text = arguments.get("text", "")
    count = arguments.get("count", 1)
    uppercase = arguments.get("uppercase", False)

    # Validate count range
    if not 1 <= count <= 10:
        raise ValueError("count must be between 1 and 10")

    # Process text
    if uppercase:
        text = text.upper()

    # Repeat text
    result = "\n".join([text] * count)

    # Return with metadata
    metadata = f"Repeated {count} time(s), Uppercase: {uppercase}"

    return [
        TextContent(type="text", text=result),
        TextContent(type="text", text=f"[Metadata: {metadata}]"),
    ]
