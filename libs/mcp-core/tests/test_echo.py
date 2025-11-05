"""Tests for echo tool patterns."""

import pytest
from mcp_core.echo import (
    create_echo_tools,
    echo_handler,
    echo_structured_handler,
)


def test_create_echo_tools():
    """Test echo tools creation."""
    tools = create_echo_tools()
    assert len(tools) == 2
    assert tools[0].name == "echo"
    assert tools[1].name == "echo_structured"


@pytest.mark.asyncio
async def test_echo_handler():
    """Test simple echo handler."""
    result = await echo_handler({"text": "Hello"})
    assert len(result) == 1
    assert "Echo: Hello" in result[0].text


@pytest.mark.asyncio
async def test_echo_structured_simple():
    """Test structured echo with defaults."""
    result = await echo_structured_handler({"text": "Test"})
    assert len(result) >= 1
    assert "Test" in result[0].text


@pytest.mark.asyncio
async def test_echo_structured_uppercase():
    """Test structured echo with uppercase."""
    result = await echo_structured_handler({"text": "hello", "uppercase": True})
    assert "HELLO" in result[0].text


@pytest.mark.asyncio
async def test_echo_structured_repeat():
    """Test structured echo with repetition."""
    result = await echo_structured_handler({"text": "Test", "count": 3})
    text = result[0].text
    assert text.count("Test") == 3


@pytest.mark.asyncio
async def test_echo_structured_invalid_count():
    """Test structured echo with invalid count."""
    with pytest.raises(ValueError, match="count must be between"):
        await echo_structured_handler({"text": "Test", "count": 20})
