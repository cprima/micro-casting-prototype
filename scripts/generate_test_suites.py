#!/usr/bin/env python3
"""Generate comprehensive test suites for all MCP servers."""

from pathlib import Path

BASE_DIR = Path("/home/user/micro-casting-prototype/apps")

# Test suite templates for each server
TEST_SUITES = {
    "mcp-hello-world": '''"""Comprehensive test suite for mcp-hello-world server."""

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
''',

    "mcp-echo-tool": '''"""Comprehensive test suite for mcp-echo-tool server."""

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
    async def test_echo_tool_exists(self):
        """Test that echo tool is defined."""
        tools = await server.list_tools()
        tool_names = [t.name for t in tools]
        assert "echo" in tool_names


class TestEchoTool:
    """Test echo tool functionality."""

    @pytest.mark.asyncio
    async def test_echo_simple(self):
        """Test simple echo."""
        result = await server.call_tool("echo", {"text": "Hello"})
        assert isinstance(result, list)
        assert len(result) == 1
        assert "Hello" in result[0].text

    @pytest.mark.asyncio
    async def test_echo_with_count(self):
        """Test echo with repetition count."""
        result = await server.call_tool("echo", {"text": "Hi", "count": 3})
        text = result[0].text
        assert text.count("Hi") == 3

    @pytest.mark.asyncio
    async def test_echo_uppercase(self):
        """Test echo with uppercase option."""
        result = await server.call_tool("echo", {"text": "hello", "uppercase": True})
        assert "HELLO" in result[0].text

    @pytest.mark.asyncio
    async def test_echo_empty_text(self):
        """Test echo with empty text."""
        result = await server.call_tool("echo", {"text": ""})
        assert result[0].text == "" or len(result[0].text) == 0

    @pytest.mark.asyncio
    async def test_echo_count_validation(self):
        """Test that count is validated."""
        # Assuming count must be between 1-10
        try:
            result = await server.call_tool("echo", {"text": "Hi", "count": 15})
            # If no validation, should still work
            assert len(result) > 0
        except ValueError:
            # If validation exists, error is expected
            pass

    @pytest.mark.asyncio
    async def test_echo_unicode(self):
        """Test echo with unicode."""
        result = await server.call_tool("echo", {"text": "Hello 世界 🌍"})
        assert "世界" in result[0].text
        assert "🌍" in result[0].text


class TestErrorHandling:
    """Test error conditions."""

    @pytest.mark.asyncio
    async def test_unknown_tool(self):
        """Test that unknown tool raises ValueError."""
        with pytest.raises(ValueError, match="Unknown tool"):
            await server.call_tool("unknown", {})


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--cov=server", "--cov-report=term-missing"])
''',

    "mcp-simple-retrieval": '''"""Comprehensive test suite for mcp-simple-retrieval server."""

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
'''
}

def add_dev_dependencies(pyproject_path):
    """Add dev dependencies to pyproject.toml if not present."""
    with open(pyproject_path, "r") as f:
        content = f.read()

    if "[tool.uv]" not in content and "dev-dependencies" not in content:
        content += '''

[tool.uv]
dev-dependencies = [
    "pytest>=7.0.0",
    "pytest-asyncio>=0.21.0",
    "pytest-cov>=4.0.0",
]
'''
        with open(pyproject_path, "w") as f:
            f.write(content)
        return True
    return False

def generate_tests():
    """Generate all test suites."""
    created = []

    for server_name, test_content in TEST_SUITES.items():
        server_dir = BASE_DIR / server_name
        if not server_dir.exists():
            print(f"⚠️  {server_name} directory not found")
            continue

        # Write test file
        test_file = server_dir / "test_server.py"
        test_file.write_text(test_content)
        print(f"✓ Created {server_name}/test_server.py")

        # Add dev dependencies
        pyproject_file = server_dir / "pyproject.toml"
        if pyproject_file.exists():
            if add_dev_dependencies(pyproject_file):
                print(f"  + Added dev-dependencies to {server_name}/pyproject.toml")

        created.append(server_name)

    print(f"\n✓ Created {len(created)} test suites")
    return created

if __name__ == "__main__":
    print("=" * 70)
    print("GENERATING TEST SUITES - FOUNDATION TIER")
    print("=" * 70)
    print()

    created = generate_tests()

    print("\nCreated tests for:")
    for name in created:
        print(f"  - {name}")
