"""Tests for hello tool pattern."""

import pytest
from mcp_core.hello import create_hello_tool, hello_handler


def test_create_hello_tool():
    """Test hello tool creation."""
    tool = create_hello_tool()
    assert tool.name == "hello"
    assert "greet" in tool.description.lower()
    assert "properties" in tool.inputSchema


@pytest.mark.asyncio
async def test_hello_handler_default():
    """Test hello handler with default name."""
    result = await hello_handler({})
    assert len(result) == 1
    assert "Hello, World!" in result[0].text


@pytest.mark.asyncio
async def test_hello_handler_with_name():
    """Test hello handler with custom name."""
    result = await hello_handler({"name": "Alice"})
    assert len(result) == 1
    assert "Hello, Alice!" in result[0].text
