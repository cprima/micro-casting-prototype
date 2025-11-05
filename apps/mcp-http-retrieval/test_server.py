"""Comprehensive test suite for mcp-http-retrieval server."""

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
    async def test_fetch_url(self):
        # Test with a reliable public website
        # Note: May fail in restricted network environments
        import httpx
        try:
            result = await server.call_tool("fetch_url", {"url": "https://example.com"})
            assert len(result) > 0
            # If successful, verify content
            assert isinstance(result[0].text, str)
        except httpx.HTTPStatusError as e:
            # In restricted environments, verify error is handled
            pytest.skip(f"Network access restricted: {e}")


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
