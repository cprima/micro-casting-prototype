# MCP Example Server

Example MCP server demonstrating how to use the `mcp-core` library to build MCP servers with reusable components.

## Overview

This application shows how to:
- Import and use tool definitions from `mcp-core`
- Route tool invocations to library handlers
- Build a working MCP server with minimal code

## Features

Uses the following tools from `mcp-core`:
- **hello** - Simple greeting tool
- **echo** - Basic text echoing
- **echo_structured** - Advanced echo with transformations

## Installation

```bash
# From repository root
uv sync

# Or directly
cd apps/mcp-example-server
uv pip install -e .
```

## Usage

### Run the Server

```bash
cd apps/mcp-example-server
uv run python server.py
```

### Test with MCP Inspector

```bash
mcp-inspector uv run python server.py
```

### Example Tool Calls

**Hello tool**:
```json
{
  "name": "hello",
  "arguments": {"name": "Alice"}
}
```

**Echo tool**:
```json
{
  "name": "echo",
  "arguments": {"text": "Hello MCP!"}
}
```

**Structured echo**:
```json
{
  "name": "echo_structured",
  "arguments": {
    "text": "test",
    "count": 3,
    "uppercase": true
  }
}
```

## Code Structure

```
server.py          # Main server implementation
README.md          # This file
pyproject.toml     # Dependencies and configuration
```

## Key Patterns

### Using Library Components

```python
from mcp_core import create_hello_tool, hello_handler

# In list_tools()
return [create_hello_tool()]

# In call_tool()
if name == "hello":
    return await hello_handler(arguments)
```

### Minimal Server Code

By using `mcp-core`, the server code is reduced to just routing logic:
1. Import tool definitions and handlers
2. Register tools in `list_tools()`
3. Route calls in `call_tool()`

## Related

- [mcp-core library](../../libs/mcp-core/) - Tool definitions and handlers
- [mcp-testdata library](../../libs/mcp-testdata/) - Test databases
- [Micro-casting methodology](../../docs/methodology/) - Decision framework

## License

See [LICENSE](../../LICENSE) in repository root.
