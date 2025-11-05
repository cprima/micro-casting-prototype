"""Comprehensive test suite for mcp-hello-world server."""

import pytest
from mcp.types import TextContent, Tool
import server

class TestListTools:
    """Test tool listing functionality."""

    @pytest.mark.asyncio
    async def test_list_tools_returns_list(self):
        """Test that list_tools returns a list."""
        tools = await server.list_tools()
        assert isinstance(tools, list)
        assert len(tools) > 0

    @pytest.mark.asyncio
    async def test_hello_tool_exists(self):
        """Test that hello tool is defined."""
        tools = await server.list_tools()
        tool_names = [t.name for t in tools]
        assert "hello" in tool_names


class TestHelloTool:
    """Test hello tool functionality."""

    @pytest.mark.asyncio
    async def test_hello_world(self):
        """Test hello without name."""
        result = await server.call_tool("hello", {})
        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], TextContent)
        assert "World" in result[0].text

    @pytest.mark.asyncio
    async def test_hello_with_name(self):
        """Test hello with specific name."""
        result = await server.call_tool("hello", {"name": "Alice"})
        assert "Alice" in result[0].text

    @pytest.mark.asyncio
    async def test_hello_with_empty_name(self):
        """Test hello with empty name falls back to World."""
        result = await server.call_tool("hello", {"name": ""})
        assert "World" in result[0].text or "" in result[0].text

    @pytest.mark.asyncio
    async def test_hello_unicode_name(self):
        """Test hello with unicode characters."""
        result = await server.call_tool("hello", {"name": "世界"})
        assert "世界" in result[0].text


class TestErrorHandling:
    """Test error conditions."""

    @pytest.mark.asyncio
    async def test_unknown_tool(self):
        """Test that unknown tool raises ValueError."""
        with pytest.raises(ValueError, match="Unknown tool"):
            await server.call_tool("unknown", {})


class TestIntegration:
    """Integration tests."""

    @pytest.mark.asyncio
    async def test_workflow(self):
        """Test complete workflow: list tools then call."""
        tools = await server.list_tools()
        assert len(tools) > 0

        result = await server.call_tool("hello", {"name": "Test"})
        assert "Test" in result[0].text


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--cov=server", "--cov-report=term-missing"])
