"""Comprehensive test suite for mcp-rag-pipeline server."""

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
            assert tool.name
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
    async def test_retrieve(self):
        result = await server.call_tool("retrieve_context", {"query": "Python", "top_k": 2})
        assert len(result) > 0


    @pytest.mark.asyncio
    async def test_workflow(self):
        """Test basic workflow."""
        tools = await server.list_tools()
        assert len(tools) > 0


class TestErrorHandling:
    """Test error conditions."""

    @pytest.mark.asyncio
    async def test_unknown_tool(self):
        """Test that unknown tool raises ValueError."""
        with pytest.raises(ValueError, match="Unknown tool"):
            await server.call_tool("unknown_tool", {})


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--cov=server", "--cov-report=term-missing"])
