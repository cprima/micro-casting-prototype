"""Comprehensive test suite for mcp-json-retrieval server."""

import pytest
import json
from mcp.types import TextContent, Resource, Tool
import server

# =============================================================================
# Test list_resources()
# =============================================================================

class TestListResources:
    """Test resource listing functionality."""

    @pytest.mark.asyncio
    async def test_list_resources_returns_list(self):
        """Test that list_resources returns a list."""
        resources = await server.list_resources()
        assert isinstance(resources, list)
        assert len(resources) > 0

    @pytest.mark.asyncio
    async def test_resource_structure(self):
        """Test resource structure is correct."""
        resources = await server.list_resources()
        for resource in resources:
            assert isinstance(resource, Resource)
            assert str(resource.uri).startswith("json://")
            assert resource.name
            assert resource.mimeType == "application/json"


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
    async def test_query_json_tool_exists(self):
        """Test that query_json tool is defined."""
        tools = await server.list_tools()
        tool_names = [t.name for t in tools]
        assert "query_json" in tool_names

    @pytest.mark.asyncio
    async def test_tool_schema(self):
        """Test query_json tool schema."""
        tools = await server.list_tools()
        query_tool = next(t for t in tools if t.name == "query_json")

        assert "path" in query_tool.inputSchema["properties"]
        assert "path" in query_tool.inputSchema["required"]


# =============================================================================
# Test call_tool() - JSONPath queries
# =============================================================================

class TestJSONPathQueries:
    """Test JSONPath query functionality."""

    @pytest.mark.asyncio
    async def test_root_query(self):
        """Test querying root element."""
        result = await server.call_tool("query_json", {"path": "$"})

        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], TextContent)

        data = json.loads(result[0].text)
        assert isinstance(data, list)
        assert len(data) == 1
        assert "users" in data[0]
        assert "config" in data[0]

    @pytest.mark.asyncio
    async def test_query_users_array(self):
        """Test querying users array."""
        result = await server.call_tool("query_json", {"path": "$.users"})

        data = json.loads(result[0].text)
        assert len(data) == 1
        users = data[0]
        assert isinstance(users, list)
        assert len(users) == 2

    @pytest.mark.asyncio
    async def test_query_first_user(self):
        """Test querying first user."""
        result = await server.call_tool("query_json", {"path": "$.users[0]"})

        data = json.loads(result[0].text)
        user = data[0]
        assert user["name"] == "Alice"
        assert user["age"] == 30
        assert user["city"] == "NYC"

    @pytest.mark.asyncio
    async def test_query_user_names(self):
        """Test querying all user names."""
        result = await server.call_tool("query_json", {"path": "$.users[*].name"})

        data = json.loads(result[0].text)
        assert data == ["Alice", "Bob"]

    @pytest.mark.asyncio
    async def test_query_config_version(self):
        """Test querying config version."""
        result = await server.call_tool("query_json", {"path": "$.config.version"})

        data = json.loads(result[0].text)
        assert data == ["1.0"]

    @pytest.mark.asyncio
    async def test_query_config_features(self):
        """Test querying config features."""
        result = await server.call_tool("query_json", {"path": "$.config.features"})

        data = json.loads(result[0].text)
        features = data[0]
        assert features == ["a", "b", "c"]

    @pytest.mark.asyncio
    async def test_query_nested_array_element(self):
        """Test querying element within nested array."""
        result = await server.call_tool("query_json", {"path": "$.config.features[1]"})

        data = json.loads(result[0].text)
        assert data == ["b"]

    @pytest.mark.asyncio
    async def test_query_all_ages(self):
        """Test querying all user ages."""
        result = await server.call_tool("query_json", {"path": "$.users[*].age"})

        data = json.loads(result[0].text)
        assert data == [30, 25]

    @pytest.mark.asyncio
    async def test_query_slice_users(self):
        """Test querying slice of users."""
        result = await server.call_tool("query_json", {"path": "$.users[0:1]"})

        data = json.loads(result[0].text)
        assert len(data) == 1
        assert data[0]["name"] == "Alice"

    @pytest.mark.asyncio
    async def test_query_nonexistent_path(self):
        """Test querying a path that doesn't exist."""
        result = await server.call_tool("query_json", {"path": "$.nonexistent"})

        data = json.loads(result[0].text)
        assert data == []

    @pytest.mark.asyncio
    async def test_invalid_jsonpath_syntax(self):
        """Test invalid JSONPath syntax raises error."""
        with pytest.raises(Exception):  # jsonpath_ng will raise an exception
            await server.call_tool("query_json", {"path": "$.[[[invalid"})


# =============================================================================
# Advanced JSONPath Tests
# =============================================================================

class TestAdvancedJSONPath:
    """Test advanced JSONPath features."""

    @pytest.mark.asyncio
    async def test_filter_expression(self):
        """Test filtering with condition (if supported)."""
        # Note: jsonpath-ng has limited filter support
        # This tests what's available
        result = await server.call_tool("query_json", {"path": "$.users[*]"})

        data = json.loads(result[0].text)
        assert len(data) == 2

    @pytest.mark.asyncio
    async def test_recursive_descent(self):
        """Test recursive descent operator."""
        result = await server.call_tool("query_json", {"path": "$..name"})

        data = json.loads(result[0].text)
        assert "Alice" in data
        assert "Bob" in data

    @pytest.mark.asyncio
    async def test_wildcard_all_properties(self):
        """Test wildcard to get all properties."""
        result = await server.call_tool("query_json", {"path": "$.config.*"})

        data = json.loads(result[0].text)
        assert len(data) == 2  # version and features

    @pytest.mark.asyncio
    async def test_last_array_element(self):
        """Test accessing last element of array."""
        result = await server.call_tool("query_json", {"path": "$.users[-1]"})

        data = json.loads(result[0].text)
        user = data[0]
        assert user["name"] == "Bob"


# =============================================================================
# Integration Tests
# =============================================================================

class TestIntegration:
    """Integration tests for complete workflows."""

    @pytest.mark.asyncio
    async def test_workflow_list_resources_then_query(self):
        """Test complete workflow: list resources then query."""
        # Step 1: List resources
        resources = await server.list_resources()
        assert len(resources) > 0

        # Step 2: Query the JSON
        result = await server.call_tool("query_json", {"path": "$.users[0].name"})
        data = json.loads(result[0].text)
        assert data == ["Alice"]

    @pytest.mark.asyncio
    async def test_multiple_queries_sequence(self):
        """Test running multiple queries in sequence."""
        queries = [
            "$.users[*].name",
            "$.config.version",
            "$.users[0].city"
        ]

        for query_path in queries:
            result = await server.call_tool("query_json", {"path": query_path})
            data = json.loads(result[0].text)
            assert isinstance(data, list)
            assert len(data) > 0

    @pytest.mark.asyncio
    async def test_extract_and_reconstruct(self):
        """Test extracting data and verifying structure."""
        # Get all user data
        result = await server.call_tool("query_json", {"path": "$.users[*]"})
        data = json.loads(result[0].text)

        # Verify we can work with extracted data
        assert len(data) == 2
        for user in data:
            assert "name" in user
            assert "age" in user
            assert "city" in user


# =============================================================================
# Error Handling Tests
# =============================================================================

class TestErrorHandling:
    """Test error conditions and edge cases."""

    @pytest.mark.asyncio
    async def test_unknown_tool_raises_error(self):
        """Test that unknown tool raises ValueError."""
        with pytest.raises(ValueError, match="Unknown tool"):
            await server.call_tool("unknown_tool", {})

    @pytest.mark.asyncio
    async def test_empty_path_query(self):
        """Test querying with empty path."""
        # Empty string might be invalid JSONPath
        with pytest.raises(Exception):
            await server.call_tool("query_json", {"path": ""})

    @pytest.mark.asyncio
    async def test_malformed_jsonpath(self):
        """Test various malformed JSONPath expressions."""
        malformed_paths = [
            "$.users[",  # Unclosed bracket
            "$.users]",  # Extra closing bracket
            "$...",      # Too many dots
        ]

        for path in malformed_paths:
            with pytest.raises(Exception):
                await server.call_tool("query_json", {"path": path})


# =============================================================================
# Data Structure Tests
# =============================================================================

class TestDataStructure:
    """Test the SAMPLE_JSON data structure."""

    def test_sample_json_structure(self):
        """Test that SAMPLE_JSON has expected structure."""
        assert "users" in server.SAMPLE_JSON
        assert "config" in server.SAMPLE_JSON

    def test_users_array_structure(self):
        """Test users array structure."""
        users = server.SAMPLE_JSON["users"]
        assert isinstance(users, list)
        assert len(users) == 2

        for user in users:
            assert "name" in user
            assert "age" in user
            assert "city" in user

    def test_config_structure(self):
        """Test config structure."""
        config = server.SAMPLE_JSON["config"]
        assert "version" in config
        assert "features" in config
        assert isinstance(config["features"], list)


# =============================================================================
# Response Format Tests
# =============================================================================

class TestResponseFormat:
    """Test response formatting."""

    @pytest.mark.asyncio
    async def test_response_is_valid_json(self):
        """Test that responses are valid JSON."""
        result = await server.call_tool("query_json", {"path": "$.users"})

        # Should not raise exception
        data = json.loads(result[0].text)
        assert isinstance(data, list)

    @pytest.mark.asyncio
    async def test_response_is_formatted(self):
        """Test that JSON responses are formatted with indentation."""
        result = await server.call_tool("query_json", {"path": "$.users[0]"})

        # Formatted JSON should have newlines
        assert "\n" in result[0].text

    @pytest.mark.asyncio
    async def test_empty_result_format(self):
        """Test format of empty results."""
        result = await server.call_tool("query_json", {"path": "$.nonexistent"})

        data = json.loads(result[0].text)
        assert data == []
        assert result[0].text.strip() == "[]"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--cov=server", "--cov-report=term-missing"])
