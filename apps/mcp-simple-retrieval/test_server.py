"""Comprehensive test suite for mcp-simple-retrieval server."""

import pytest
from mcp.types import TextContent, Resource
import server

class TestListResources:
    """Test resource listing functionality."""

    @pytest.mark.asyncio
    async def test_list_resources_returns_list(self):
        """Test that list_resources returns a list."""
        resources = await server.list_resources()
        assert isinstance(resources, list)

    @pytest.mark.asyncio
    async def test_resources_structure(self):
        """Test resource structure."""
        resources = await server.list_resources()
        if len(resources) > 0:
            for resource in resources:
                assert isinstance(resource, Resource)
                assert resource.uri
                assert resource.name


class TestReadResource:
    """Test resource reading functionality."""

    @pytest.mark.asyncio
    async def test_read_sample_resource(self):
        """Test reading a sample resource."""
        resources = await server.list_resources()
        if len(resources) > 0:
            first_uri = str(resources[0].uri)
            content = await server.read_resource(first_uri)
            assert isinstance(content, list)
            assert len(content) > 0
            assert isinstance(content[0], TextContent)


class TestIntegration:
    """Integration tests."""

    @pytest.mark.asyncio
    async def test_workflow_list_then_read(self):
        """Test workflow: list resources then read one."""
        resources = await server.list_resources()
        if len(resources) > 0:
            content = await server.read_resource(str(resources[0].uri))
            assert isinstance(content[0], TextContent)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--cov=server", "--cov-report=term-missing"])
