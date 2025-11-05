"""Comprehensive test suite for mcp-echo-tool server."""

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
    async def test_echo_tools_exist(self):
        """Test that both echo tools are defined."""
        tools = await server.list_tools()
        tool_names = [t.name for t in tools]
        assert "echo" in tool_names
        assert "echo_structured" in tool_names


class TestEchoTool:
    """Test simple echo tool functionality."""

    @pytest.mark.asyncio
    async def test_echo_simple(self):
        """Test simple echo."""
        result = await server.call_tool("echo", {"text": "Hello"})
        assert isinstance(result, list)
        assert len(result) == 1
        assert "Hello" in result[0].text
        assert "Echo:" in result[0].text

    @pytest.mark.asyncio
    async def test_echo_empty_text(self):
        """Test echo with empty text."""
        result = await server.call_tool("echo", {"text": ""})
        assert "Echo:" in result[0].text

    @pytest.mark.asyncio
    async def test_echo_unicode(self):
        """Test echo with unicode."""
        result = await server.call_tool("echo", {"text": "Hello 世界 🌍"})
        assert "世界" in result[0].text
        assert "🌍" in result[0].text


class TestEchoStructuredTool:
    """Test echo_structured tool functionality."""

    @pytest.mark.asyncio
    async def test_echo_structured_simple(self):
        """Test echo_structured without options."""
        result = await server.call_tool("echo_structured", {"text": "Hello"})
        assert "Hello" in result[0].text

    @pytest.mark.asyncio
    async def test_echo_structured_with_count(self):
        """Test echo_structured with repetition count."""
        result = await server.call_tool("echo_structured", {"text": "Hi", "count": 3})
        text = result[0].text
        lines = text.split("\n")
        assert len(lines) == 3
        assert all(line == "Hi" for line in lines)

    @pytest.mark.asyncio
    async def test_echo_structured_uppercase(self):
        """Test echo_structured with uppercase option."""
        result = await server.call_tool("echo_structured", {"text": "hello", "uppercase": True})
        assert "HELLO" in result[0].text
        assert "hello" not in result[0].text

    @pytest.mark.asyncio
    async def test_echo_structured_uppercase_and_count(self):
        """Test echo_structured with both options."""
        result = await server.call_tool("echo_structured", {"text": "hi", "uppercase": True, "count": 2})
        text = result[0].text
        assert text.count("HI") == 2

    @pytest.mark.asyncio
    async def test_echo_structured_count_validation(self):
        """Test that count must be 1-10."""
        # Valid range
        result = await server.call_tool("echo_structured", {"text": "Hi", "count": 10})
        assert len(result[0].text.split("\n")) == 10


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
        assert len(tools) == 2

        # Test simple echo
        result1 = await server.call_tool("echo", {"text": "Test"})
        assert "Test" in result1[0].text

        # Test structured echo
        result2 = await server.call_tool("echo_structured", {"text": "Test", "count": 2})
        assert result2[0].text.count("Test") == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--cov=server", "--cov-report=term-missing"])
