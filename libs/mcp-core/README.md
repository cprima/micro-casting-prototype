# MCP Core Library

Foundation patterns for building Model Context Protocol (MCP) servers.

## Overview

The `mcp-core` library provides reusable components and patterns for building MCP servers. It includes battle-tested implementations of common tool patterns that serve as both learning resources and production-ready components.

## Features

### Hello Tool Pattern
The simplest possible MCP tool - demonstrates:
- Basic tool definition
- Parameter handling (optional parameters)
- Response formatting

### Echo Tool Patterns
Two variants demonstrating progressive complexity:

**Simple Echo**:
- Required parameters
- Basic text handling

**Structured Echo**:
- Parameter validation (range checking)
- Text transformations (uppercase)
- Repetition logic
- Multiple return values with metadata

## Installation

```bash
# In the workspace root
uv sync

# Or install directly
cd libs/mcp-core
uv pip install -e .
```

## Usage

### As Library Components

```python
from mcp.server import Server
from mcp_core import create_hello_tool, hello_handler, create_echo_tools, echo_handler, echo_structured_handler

# Initialize server
app = Server("my-mcp-server")

# Register tools
@app.list_tools()
async def list_tools():
    return [create_hello_tool()] + create_echo_tools()

# Handle tool calls
@app.call_tool()
async def call_tool(name: str, arguments: dict):
    if name == "hello":
        return await hello_handler(arguments)
    elif name == "echo":
        return await echo_handler(arguments)
    elif name == "echo_structured":
        return await echo_structured_handler(arguments)

    raise ValueError(f"Unknown tool: {name}")
```

### Standalone Server

See `apps/mcp-examples/` for complete working examples.

## API Reference

### `create_hello_tool() -> Tool`
Creates the hello tool definition.

### `hello_handler(arguments: dict) -> list[TextContent]`
Handles hello tool invocations.

**Parameters**:
- `name` (str, optional): Person to greet. Defaults to "World".

**Returns**: Greeting text content.

### `create_echo_tools() -> list[Tool]`
Creates echo and echo_structured tool definitions.

### `echo_handler(arguments: dict) -> list[TextContent]`
Handles simple echo tool invocations.

**Parameters**:
- `text` (str, required): Text to echo.

**Returns**: Echoed text content.

### `echo_structured_handler(arguments: dict) -> list[TextContent]`
Handles structured echo tool invocations with validation and transformations.

**Parameters**:
- `text` (str, required): Text to echo.
- `count` (int, optional): Repetition count (1-10). Defaults to 1.
- `uppercase` (bool, optional): Convert to uppercase. Defaults to False.

**Returns**: List containing echoed text and metadata.

**Raises**: `ValueError` if count is outside valid range.

## Development

### Running Tests

```bash
cd libs/mcp-core
uv run pytest
```

### Test Coverage

```bash
uv run pytest --cov=mcp_core --cov-report=html
```

## Pattern Alignment

These patterns align with the micro-casting methodology:

- **Phase 1 (Getting Started)**: Tool naming, parameter conventions
- **Decision Nodes**: Tool definition, input validation, response formats
- **Evidence**: test_report (comprehensive test suite)

## Related

- [MCP Retrieval Library](../mcp-retrieval/) - Data access patterns
- [MCP Serialization Library](../mcp-serialization/) - Data format handling
- [MCP Examples App](../../apps/mcp-examples/) - Complete working servers

## License

See [LICENSE](../../LICENSE) in repository root.
