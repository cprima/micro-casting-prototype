"""Comprehensive test suite for mcp-filesystem-retrieval server."""

import pytest
import asyncio
import tempfile
from pathlib import Path
from mcp.types import TextContent, Resource, Tool
import server

# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def temp_testdata():
    """Create temporary test data directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        # Create test files
        (tmpdir / "file1.txt").write_text("Content of file 1")
        (tmpdir / "file2.txt").write_text("Content of file 2")
        (tmpdir / "large_file.txt").write_text("x" * 2000)  # 2000 chars

        # Create subdirectories
        (tmpdir / "subdir").mkdir()
        (tmpdir / "subdir" / "file3.txt").write_text("Content in subdir")
        (tmpdir / "subdir" / "nested").mkdir()
        (tmpdir / "subdir" / "nested" / "file4.txt").write_text("Deeply nested")

        # Create non-txt files
        (tmpdir / "data.json").write_text('{"key": "value"}')
        (tmpdir / "README.md").write_text("# README")

        # Empty file
        (tmpdir / "empty.txt").write_text("")

        yield tmpdir


@pytest.fixture
def mock_base_dir(temp_testdata, monkeypatch):
    """Mock BASE_DIR to use temp directory."""
    monkeypatch.setattr(server, "BASE_DIR", temp_testdata)
    return temp_testdata


# =============================================================================
# Test list_resources()
# =============================================================================

class TestListResources:
    """Test resource listing functionality."""

    @pytest.mark.asyncio
    async def test_list_resources_basic(self, mock_base_dir):
        """Test basic resource listing."""
        resources = await server.list_resources()

        assert isinstance(resources, list)
        assert len(resources) > 0
        assert all(isinstance(r, Resource) for r in resources)

    @pytest.mark.asyncio
    async def test_resource_structure(self, mock_base_dir):
        """Test resource structure is correct."""
        resources = await server.list_resources()

        for resource in resources:
            assert str(resource.uri).startswith("file://")
            assert resource.name
            assert resource.mimeType == "text/plain"

    @pytest.mark.asyncio
    async def test_only_txt_files_listed(self, mock_base_dir):
        """Test that only .txt files are listed."""
        resources = await server.list_resources()

        for resource in resources:
            # Extract path from URI
            path = Path(str(resource.uri).replace("file://", ""))
            assert path.suffix == ".txt"

    @pytest.mark.asyncio
    async def test_limit_to_10_resources(self, mock_base_dir):
        """Test that resources are limited to 10."""
        # Create more than 10 txt files
        for i in range(15):
            (mock_base_dir / f"extra_{i}.txt").write_text(f"Extra {i}")

        resources = await server.list_resources()
        assert len(resources) <= 10

    @pytest.mark.asyncio
    async def test_recursive_search(self, mock_base_dir):
        """Test that files in subdirectories are found."""
        resources = await server.list_resources()

        # Should find files in subdirectories
        uris = [str(r.uri) for r in resources]
        assert any("subdir" in uri for uri in uris)

    @pytest.mark.asyncio
    async def test_empty_directory(self, monkeypatch):
        """Test behavior with no txt files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            monkeypatch.setattr(server, "BASE_DIR", Path(tmpdir))
            resources = await server.list_resources()
            assert resources == []


# =============================================================================
# Test read_resource()
# =============================================================================

class TestReadResource:
    """Test resource reading functionality."""

    @pytest.mark.asyncio
    async def test_read_existing_file(self, mock_base_dir):
        """Test reading an existing file."""
        test_file = mock_base_dir / "file1.txt"
        uri = f"file://{test_file}"

        result = await server.read_resource(uri)

        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], TextContent)
        assert result[0].text == "Content of file 1"

    @pytest.mark.asyncio
    async def test_read_nonexistent_file(self, mock_base_dir):
        """Test reading a file that doesn't exist."""
        uri = f"file://{mock_base_dir}/nonexistent.txt"

        with pytest.raises(ValueError, match="File not found"):
            await server.read_resource(uri)

    @pytest.mark.asyncio
    async def test_read_large_file_truncated(self, mock_base_dir):
        """Test that large files are truncated to 1000 chars."""
        test_file = mock_base_dir / "large_file.txt"
        uri = f"file://{test_file}"

        result = await server.read_resource(uri)

        assert len(result[0].text) == 1000
        assert result[0].text == "x" * 1000

    @pytest.mark.asyncio
    async def test_read_empty_file(self, mock_base_dir):
        """Test reading an empty file."""
        test_file = mock_base_dir / "empty.txt"
        uri = f"file://{test_file}"

        result = await server.read_resource(uri)

        assert len(result) == 1
        assert result[0].text == ""

    @pytest.mark.asyncio
    async def test_read_file_with_uri_format(self, mock_base_dir):
        """Test URI parsing works correctly."""
        test_file = mock_base_dir / "file1.txt"
        uri = f"file://{test_file}"

        result = await server.read_resource(uri)
        assert result[0].text == "Content of file 1"

    @pytest.mark.asyncio
    async def test_read_nested_file(self, mock_base_dir):
        """Test reading a file in nested directory."""
        test_file = mock_base_dir / "subdir" / "nested" / "file4.txt"
        uri = f"file://{test_file}"

        result = await server.read_resource(uri)
        assert result[0].text == "Deeply nested"


# =============================================================================
# Test list_tools()
# =============================================================================

class TestListTools:
    """Test tool listing functionality."""

    @pytest.mark.asyncio
    async def test_list_tools_returns_list(self):
        """Test that list_tools returns a list."""
        tools = await server.list_tools()

        assert isinstance(tools, list)
        assert len(tools) > 0

    @pytest.mark.asyncio
    async def test_list_directory_tool_exists(self):
        """Test that list_directory tool is defined."""
        tools = await server.list_tools()

        tool_names = [t.name for t in tools]
        assert "list_directory" in tool_names

    @pytest.mark.asyncio
    async def test_tool_structure(self):
        """Test tool structure is correct."""
        tools = await server.list_tools()

        for tool in tools:
            assert isinstance(tool, Tool)
            assert tool.name
            assert tool.description
            assert tool.inputSchema
            assert "type" in tool.inputSchema
            assert "properties" in tool.inputSchema

    @pytest.mark.asyncio
    async def test_list_directory_schema(self):
        """Test list_directory tool schema."""
        tools = await server.list_tools()
        list_dir_tool = next(t for t in tools if t.name == "list_directory")

        assert "path" in list_dir_tool.inputSchema["properties"]
        assert "path" in list_dir_tool.inputSchema["required"]


# =============================================================================
# Test call_tool()
# =============================================================================

class TestCallTool:
    """Test tool invocation functionality."""

    @pytest.mark.asyncio
    async def test_list_directory_basic(self, mock_base_dir):
        """Test basic directory listing."""
        result = await server.call_tool(
            "list_directory",
            {"path": str(mock_base_dir)}
        )

        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], TextContent)

        files = result[0].text.split("\n")
        assert len(files) > 0

    @pytest.mark.asyncio
    async def test_list_directory_finds_files(self, mock_base_dir):
        """Test that directory listing finds known files."""
        result = await server.call_tool(
            "list_directory",
            {"path": str(mock_base_dir)}
        )

        files_text = result[0].text
        assert "file1.txt" in files_text
        assert "file2.txt" in files_text
        assert "subdir" in files_text

    @pytest.mark.asyncio
    async def test_list_directory_limit_20(self, mock_base_dir):
        """Test that listing is limited to 20 files."""
        # Create 25 files
        for i in range(25):
            (mock_base_dir / f"test_{i}.txt").write_text("test")

        result = await server.call_tool(
            "list_directory",
            {"path": str(mock_base_dir)}
        )

        files = result[0].text.split("\n")
        assert len(files) <= 20

    @pytest.mark.asyncio
    async def test_list_directory_nonexistent(self, mock_base_dir):
        """Test listing a directory that doesn't exist."""
        with pytest.raises(ValueError, match="Invalid directory"):
            await server.call_tool(
                "list_directory",
                {"path": str(mock_base_dir / "nonexistent")}
            )

    @pytest.mark.asyncio
    async def test_list_directory_file_not_dir(self, mock_base_dir):
        """Test listing a file instead of directory."""
        with pytest.raises(ValueError, match="Invalid directory"):
            await server.call_tool(
                "list_directory",
                {"path": str(mock_base_dir / "file1.txt")}
            )

    @pytest.mark.asyncio
    async def test_list_directory_subdirectory(self, mock_base_dir):
        """Test listing a subdirectory."""
        result = await server.call_tool(
            "list_directory",
            {"path": str(mock_base_dir / "subdir")}
        )

        files_text = result[0].text
        assert "file3.txt" in files_text
        assert "nested" in files_text

    @pytest.mark.asyncio
    async def test_list_directory_empty(self, mock_base_dir):
        """Test listing an empty directory."""
        empty_dir = mock_base_dir / "empty_dir"
        empty_dir.mkdir()

        result = await server.call_tool(
            "list_directory",
            {"path": str(empty_dir)}
        )

        # Should return empty string or list
        assert result[0].text == ""

    @pytest.mark.asyncio
    async def test_unknown_tool_raises_error(self, mock_base_dir):
        """Test that unknown tool raises ValueError."""
        with pytest.raises(ValueError, match="Unknown tool"):
            await server.call_tool("unknown_tool", {})


# =============================================================================
# Integration Tests
# =============================================================================

class TestIntegration:
    """Integration tests for complete workflows."""

    @pytest.mark.asyncio
    async def test_workflow_list_then_read(self, mock_base_dir):
        """Test complete workflow: list resources then read one."""
        # Step 1: List resources
        resources = await server.list_resources()
        assert len(resources) > 0

        # Step 2: Read first resource
        first_resource = resources[0]
        content = await server.read_resource(str(str(first_resource.uri)))

        assert isinstance(content[0], TextContent)
        assert len(content[0].text) > 0

    @pytest.mark.asyncio
    async def test_workflow_list_dir_then_read_file(self, mock_base_dir):
        """Test workflow: list directory then read file from it."""
        # Step 1: List directory
        dir_result = await server.call_tool(
            "list_directory",
            {"path": str(mock_base_dir)}
        )
        files_text = dir_result[0].text

        # Step 2: Find a txt file in the output
        txt_files = [f for f in files_text.split("\n") if f.strip() and f.endswith(".txt")]
        assert len(txt_files) > 0

        txt_file = txt_files[0].strip()
        file_path = mock_base_dir / txt_file
        uri = f"file://{file_path}"

        content = await server.read_resource(uri)
        assert isinstance(content[0], TextContent)

    @pytest.mark.asyncio
    async def test_concurrent_operations(self, mock_base_dir):
        """Test multiple concurrent operations."""
        # Run multiple operations concurrently
        tasks = [
            server.list_resources(),
            server.list_tools(),
            server.call_tool("list_directory", {"path": str(mock_base_dir)}),
        ]

        results = await asyncio.gather(*tasks)

        assert len(results) == 3
        assert isinstance(results[0], list)  # resources
        assert isinstance(results[1], list)  # tools
        assert isinstance(results[2], list)  # tool result


# =============================================================================
# Edge Cases and Error Handling
# =============================================================================

class TestEdgeCases:
    """Test edge cases and error conditions."""

    @pytest.mark.asyncio
    async def test_unicode_content(self, mock_base_dir):
        """Test reading files with unicode content."""
        unicode_file = mock_base_dir / "unicode.txt"
        unicode_file.write_text("Hello 世界 🌍 Привет")
        uri = f"file://{unicode_file}"

        result = await server.read_resource(uri)
        assert "世界" in result[0].text
        assert "🌍" in result[0].text

    @pytest.mark.asyncio
    async def test_special_characters_in_filename(self, mock_base_dir):
        """Test files with special characters in name."""
        special_file = mock_base_dir / "file with spaces.txt"
        special_file.write_text("Content")
        uri = f"file://{special_file}"

        result = await server.read_resource(uri)
        assert result[0].text == "Content"

    @pytest.mark.asyncio
    async def test_symlink_handling(self, mock_base_dir):
        """Test handling of symbolic links (if supported)."""
        real_file = mock_base_dir / "real.txt"
        real_file.write_text("Real content")

        symlink = mock_base_dir / "link.txt"
        try:
            symlink.symlink_to(real_file)

            # Should be able to read through symlink
            uri = f"file://{symlink}"
            result = await server.read_resource(uri)
            assert result[0].text == "Real content"
        except OSError:
            pytest.skip("Symlinks not supported on this platform")

    @pytest.mark.asyncio
    async def test_hidden_files(self, mock_base_dir):
        """Test handling of hidden files."""
        hidden = mock_base_dir / ".hidden.txt"
        hidden.write_text("Hidden content")

        # Should still be able to list/read hidden files
        resources = await server.list_resources()
        uris = [str(r.uri) for r in resources]

        # Check if hidden file is included
        assert any(".hidden.txt" in uri for uri in uris)


# =============================================================================
# Performance Tests
# =============================================================================

class TestPerformance:
    """Test performance characteristics."""

    @pytest.mark.asyncio
    async def test_large_directory_listing(self, mock_base_dir):
        """Test listing directory with many files."""
        # Create 100 files
        for i in range(100):
            (mock_base_dir / f"file_{i:03d}.txt").write_text(f"Content {i}")

        # Should complete in reasonable time
        result = await server.call_tool(
            "list_directory",
            {"path": str(mock_base_dir)}
        )

        # Should be limited to 20
        files = result[0].text.split("\n")
        assert len(files) <= 20

    @pytest.mark.asyncio
    async def test_deep_nesting(self, mock_base_dir):
        """Test handling of deeply nested directories."""
        # Create deep nesting
        current = mock_base_dir
        for i in range(10):
            current = current / f"level_{i}"
            current.mkdir()
            (current / f"file_{i}.txt").write_text(f"Level {i}")

        # Should find files at various depths
        resources = await server.list_resources()
        assert len(resources) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--cov=server", "--cov-report=term-missing"])
