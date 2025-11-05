"""Comprehensive test suite for mcp-error-handling server."""

import pytest
from mcp.types import TextContent, Tool, Resource
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
    async def test_tool_structure(self):
        """Test tool structure."""
        tools = await server.list_tools()
        for tool in tools:
            assert isinstance(tool, Tool)
            assert tool.name  # No specific fix, check actual error
            assert tool.description
            assert tool.inputSchema


class TestListResources:
    """Test resource listing functionality."""

    @pytest.mark.asyncio
    async def test_list_resources_returns_list(self):
        """Test that list_resources returns a list."""
        resources = await server.list_resources()
        assert isinstance(resources, list)


class TestIntegration:
    """Integration tests."""


    @pytest.mark.asyncio
    async def test_divide(self):
        result = await server.call_tool("divide", {"a": 10, "b": 2})
        assert "5" in result[0].text
    
    @pytest.mark.asyncio
    async def test_divide_by_zero(self):
        result = await server.call_tool("divide", {"a": 10, "b": 0})
        assert "Error" in result[0].text or "zero" in result[0].text.lower()


    @pytest.mark.asyncio
    async def test_workflow(self):
        """Test basic workflow."""
        tools = await server.list_tools()
        assert len(tools) > 0


class TestErrorHandling:
    """Test error conditions."""

    @pytest.mark.asyncio
    async def test_unknown_tool(self):
        """Test that unknown tool returns error message."""
        result = await server.call_tool("unknown_tool", {})
        assert isinstance(result, list)
        assert len(result) == 1
        assert "Unknown tool" in result[0].text or "Unexpected error" in result[0].text


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--cov=server", "--cov-report=term-missing"])
