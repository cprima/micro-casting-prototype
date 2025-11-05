"""Comprehensive test suite for mcp-sqlite-retrieval server."""

import pytest
from mcp.types import TextContent, Tool, Resource
import server
import tempfile, sqlite3

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

    @pytest.fixture
    def temp_db(self):
        import os
        fd, path = tempfile.mkstemp(suffix=".db")
        os.close(fd)
        conn = sqlite3.connect(path)
        conn.execute("CREATE TABLE test (id INTEGER, name TEXT)")
        conn.execute("INSERT INTO test VALUES (1, 'Alice')")
        conn.commit()
        conn.close()
        yield path
        os.unlink(path)


    @pytest.mark.asyncio
    async def test_query_database(self, temp_db):
        result = await server.call_tool("query_database", {"database": temp_db, "query": "SELECT * FROM test"})
        assert "Alice" in result[0].text


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
