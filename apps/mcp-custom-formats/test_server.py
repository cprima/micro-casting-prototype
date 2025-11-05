"""Comprehensive test suite for mcp-custom-formats server."""

import pytest
from mcp.types import TextContent, Tool
import server

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
    async def test_tools_exist(self):
        """Test that expected tools are defined."""
        tools = await server.list_tools()
        tool_names = [t.name for t in tools]
        assert "parse_yaml" in tool_names
        assert "csv_to_json" in tool_names

    @pytest.mark.asyncio
    async def test_tool_schemas(self):
        """Test tool schemas are correct."""
        tools = await server.list_tools()
        for tool in tools:
            assert isinstance(tool, Tool)
            assert tool.name
            assert tool.description
            assert tool.inputSchema


# =============================================================================
# Test parse_yaml tool
# =============================================================================

class TestParseYAML:
    """Test YAML parsing functionality."""

    @pytest.mark.asyncio
    async def test_parse_simple_yaml(self):
        """Test parsing simple YAML."""
        yaml_str = "name: John\nage: 30"
        result = await server.call_tool("parse_yaml", {"yaml_string": yaml_str})

        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], TextContent)
        assert "John" in result[0].text
        assert "30" in result[0].text

    @pytest.mark.asyncio
    async def test_parse_nested_yaml(self):
        """Test parsing nested YAML."""
        yaml_str = """
person:
  name: Alice
  address:
    city: NYC
    zip: 10001
"""
        result = await server.call_tool("parse_yaml", {"yaml_string": yaml_str})

        assert "Alice" in result[0].text
        assert "NYC" in result[0].text

    @pytest.mark.asyncio
    async def test_parse_yaml_list(self):
        """Test parsing YAML list."""
        yaml_str = """
items:
  - apple
  - banana
  - cherry
"""
        result = await server.call_tool("parse_yaml", {"yaml_string": yaml_str})

        assert "apple" in result[0].text
        assert "banana" in result[0].text

    @pytest.mark.asyncio
    async def test_parse_empty_yaml(self):
        """Test parsing empty YAML."""
        yaml_str = ""
        result = await server.call_tool("parse_yaml", {"yaml_string": yaml_str})

        assert result[0].text == "None"

    @pytest.mark.asyncio
    async def test_parse_invalid_yaml(self):
        """Test parsing invalid YAML raises error."""
        yaml_str = "invalid: [unclosed bracket"
        with pytest.raises(Exception):
            await server.call_tool("parse_yaml", {"yaml_string": yaml_str})


# =============================================================================
# Test csv_to_json tool
# =============================================================================

class TestCSVToJSON:
    """Test CSV to JSON conversion functionality."""

    @pytest.mark.asyncio
    async def test_simple_csv(self):
        """Test converting simple CSV."""
        csv_str = "name,age\nAlice,30\nBob,25"
        result = await server.call_tool("csv_to_json", {"csv_string": csv_str})

        assert isinstance(result, list)
        assert "Alice" in result[0].text
        assert "Bob" in result[0].text
        assert "30" in result[0].text
        assert "25" in result[0].text

    @pytest.mark.asyncio
    async def test_csv_with_quotes(self):
        """Test CSV with quoted fields."""
        csv_str = 'name,city\n"Smith, John","New York, NY"\n"Doe, Jane","Los Angeles, CA"'
        result = await server.call_tool("csv_to_json", {"csv_string": csv_str})

        assert "Smith" in result[0].text
        assert "New York" in result[0].text

    @pytest.mark.asyncio
    async def test_empty_csv(self):
        """Test converting empty CSV."""
        csv_str = "name,age"
        result = await server.call_tool("csv_to_json", {"csv_string": csv_str})

        assert result[0].text == "[]"

    @pytest.mark.asyncio
    async def test_csv_single_row(self):
        """Test CSV with single data row."""
        csv_str = "name,age\nAlice,30"
        result = await server.call_tool("csv_to_json", {"csv_string": csv_str})

        assert "Alice" in result[0].text

    @pytest.mark.asyncio
    async def test_csv_many_columns(self):
        """Test CSV with many columns."""
        csv_str = "a,b,c,d,e\n1,2,3,4,5\n6,7,8,9,10"
        result = await server.call_tool("csv_to_json", {"csv_string": csv_str})

        for num in ["1", "2", "3", "4", "5"]:
            assert num in result[0].text


# =============================================================================
# Integration Tests
# =============================================================================

class TestIntegration:
    """Integration tests for complete workflows."""

    @pytest.mark.asyncio
    async def test_process_both_formats(self):
        """Test processing both YAML and CSV."""
        # YAML
        yaml_result = await server.call_tool("parse_yaml", {"yaml_string": "key: value"})
        assert "value" in yaml_result[0].text

        # CSV
        csv_result = await server.call_tool("csv_to_json", {"csv_string": "a,b\n1,2"})
        assert "1" in csv_result[0].text


# =============================================================================
# Error Handling Tests
# =============================================================================

class TestErrorHandling:
    """Test error conditions."""

    @pytest.mark.asyncio
    async def test_unknown_tool(self):
        """Test unknown tool raises error."""
        with pytest.raises(ValueError, match="Unknown tool"):
            await server.call_tool("unknown", {})


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--cov=server", "--cov-report=term-missing"])
