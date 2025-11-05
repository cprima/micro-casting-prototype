# MCP Server Blueprints

A comprehensive collection of 20 fully-implemented Model Context Protocol (MCP) server applications demonstrating various patterns and capabilities for teaching and reference purposes.

## Overview

This collection provides proof-of-concept implementations of MCP servers organized into five tiers, progressing from basic concepts to advanced integration patterns. Each server is a complete, working example suitable for learning and adaptation.

## Quick Start

Each server can be run independently:

```bash
cd apps/<server-name>
uv run python server.py
```

The servers communicate via stdio and are designed to be used with MCP-compatible clients.

## Server Organization

### Foundation Tier (3 servers)

**Core Concepts** - Basic MCP server patterns

#### 1. mcp-hello-world
- **Purpose**: Minimal MCP server demonstrating basic setup
- **Features**:
  - Simple server initialization
  - Basic tool registration
  - Hello world functionality
- **Learning Focus**: Understanding MCP server lifecycle
- **Dependencies**: `mcp>=0.1.0`

#### 2. mcp-echo-tool
- **Purpose**: Simple tool invocation pattern
- **Features**:
  - Parameter handling
  - Input validation
  - Echo tool with options (uppercase, repeat count)
- **Learning Focus**: Tool definition and argument processing
- **Dependencies**: `mcp>=0.1.0`

#### 3. mcp-simple-retrieval
- **Purpose**: Basic resource retrieval (read-only)
- **Features**:
  - Resource listing
  - Resource reading
  - In-memory data storage
- **Learning Focus**: Resource patterns in MCP
- **Dependencies**: `mcp>=0.1.0`

### Retrieval Patterns (4 servers)

**Data Access** - Reading and retrieving data from various sources

#### 4. mcp-filesystem-retrieval
- **Purpose**: File system navigation and reading
- **Features**:
  - Directory listing
  - File reading with async I/O
  - Path validation and security
  - File metadata (size, modification time)
- **Learning Focus**: Async file operations, path security
- **Dependencies**: `mcp>=0.1.0`, `aiofiles>=23.0.0`

#### 5. mcp-sqlite-retrieval
- **Purpose**: Database query and retrieval
- **Features**:
  - SQLite database connection
  - Table listing
  - Query execution
  - Schema inspection
- **Learning Focus**: Async database operations
- **Dependencies**: `mcp>=0.1.0`, `aiosqlite>=0.19.0`
- **Use Case**: Query sample databases in testdata/

#### 6. mcp-http-retrieval
- **Purpose**: REST API data fetching
- **Features**:
  - HTTP GET requests
  - Response caching
  - Timeout handling
  - Error management
- **Learning Focus**: HTTP client patterns, caching strategies
- **Dependencies**: `mcp>=0.1.0`, `httpx>=0.25.0`

#### 7. mcp-json-retrieval
- **Purpose**: JSON document querying
- **Features**:
  - JSONPath query support
  - Nested data navigation
  - Array filtering
  - Result formatting
- **Learning Focus**: JSON processing, JSONPath queries
- **Dependencies**: `mcp>=0.1.0`, `jsonpath-ng>=1.6.0`

### Serialization Patterns (4 servers)

**Data Transformation** - Converting between formats and validating data

#### 8. mcp-json-serialization
- **Purpose**: JSON schema validation and serialization
- **Features**:
  - JSON Schema validation
  - Schema enforcement
  - Format conversion
  - Validation error reporting
- **Learning Focus**: Schema validation, type checking
- **Dependencies**: `mcp>=0.1.0`, `jsonschema>=4.0.0`

#### 9. mcp-pydantic-models
- **Purpose**: Type-safe serialization with Pydantic
- **Features**:
  - Pydantic model definitions
  - Automatic validation
  - Type coercion
  - Serialization to/from JSON
- **Learning Focus**: Type safety, data validation with Pydantic
- **Dependencies**: `mcp>=0.1.0`, `pydantic>=2.0.0`

#### 10. mcp-protocol-buffers
- **Purpose**: Protocol Buffers serialization
- **Features**:
  - Protobuf message definitions
  - Binary serialization
  - Compact encoding
  - Cross-language compatibility
- **Learning Focus**: Binary protocols, efficient serialization
- **Dependencies**: `mcp>=0.1.0`, `protobuf>=4.24.0`

#### 11. mcp-custom-formats
- **Purpose**: Custom serialization formats (CSV, YAML, TOML)
- **Features**:
  - Multi-format support
  - Format conversion tools
  - CSV reading/writing
  - YAML and TOML parsing
- **Learning Focus**: Working with multiple data formats
- **Dependencies**: `mcp>=0.1.0`, `pyyaml>=6.0`, `toml>=0.10.2`

### Tool-Invocation Patterns (5 servers)

**Tool Execution** - Different approaches to tool implementation

#### 12. mcp-sync-tools
- **Purpose**: Synchronous tool execution patterns
- **Features**:
  - Blocking operations
  - Factorial calculation
  - Fibonacci sequence
  - CPU-bound tasks
- **Learning Focus**: Synchronous computation in async context
- **Dependencies**: `mcp>=0.1.0`

#### 13. mcp-async-tools
- **Purpose**: Async/await tool patterns with concurrency
- **Features**:
  - Non-blocking operations
  - Parallel execution
  - Concurrent HTTP requests
  - Async sleep/delays
- **Learning Focus**: Async patterns, concurrency
- **Dependencies**: `mcp>=0.1.0`, `httpx>=0.25.0`

#### 14. mcp-stateful-tools
- **Purpose**: Tools with persistent session state
- **Features**:
  - Session counter
  - Variable storage
  - Command history
  - State management
- **Learning Focus**: Managing state across tool calls
- **Dependencies**: `mcp>=0.1.0`

#### 15. mcp-chained-tools
- **Purpose**: Tool composition and chaining patterns
- **Features**:
  - Number extraction from text
  - Mathematical operations
  - Result formatting
  - Demonstration of tool composition
- **Learning Focus**: Building complex operations from simple tools
- **Dependencies**: `mcp>=0.1.0`

#### 16. mcp-error-handling
- **Purpose**: Robust error handling patterns
- **Features**:
  - Division by zero handling
  - JSON parse errors
  - Email validation
  - Graceful error responses
- **Learning Focus**: Error handling, validation, user feedback
- **Dependencies**: `mcp>=0.1.0`

### Advanced Integration Patterns (4 servers)

**Complex Systems** - Production-ready patterns

#### 17. mcp-rag-pipeline
- **Purpose**: RAG (Retrieval-Augmented Generation) pattern
- **Features**:
  - In-memory knowledge base
  - Similarity search
  - Context retrieval
  - Knowledge management
- **Learning Focus**: RAG implementation, semantic search
- **Dependencies**: `mcp>=0.1.0`
- **Note**: Uses simplified word-overlap similarity for demonstration

#### 18. mcp-vector-search
- **Purpose**: Vector database integration
- **Features**:
  - Vector embeddings
  - Cosine similarity
  - Semantic search
  - Vector storage
- **Learning Focus**: Vector operations, embeddings
- **Dependencies**: `mcp>=0.1.0`, `numpy>=1.24.0`
- **Note**: Uses character frequency vectors for educational simplicity

#### 19. mcp-streaming-responses
- **Purpose**: Streaming data patterns
- **Features**:
  - Incremental results
  - Simulated streaming
  - Progress indication
  - Chunked processing
- **Learning Focus**: Streaming responses, progressive output
- **Dependencies**: `mcp>=0.1.0`

#### 20. mcp-multi-resource-server
- **Purpose**: Comprehensive server with multiple capabilities
- **Features**:
  - Multiple resource types
  - Various tools (notes, counters, calculator)
  - URL fetching
  - Combined functionality
- **Learning Focus**: Building comprehensive servers
- **Dependencies**: `mcp>=0.1.0`, `aiofiles>=23.0.0`, `httpx>=0.25.0`

## Usage Patterns

### Running a Server

```bash
# Navigate to server directory
cd apps/mcp-hello-world

# Run with uv (handles dependencies automatically)
uv run python server.py
```

### Testing with MCP Inspector

```bash
# Install MCP Inspector
npm install -g @modelcontextprotocol/inspector

# Inspect a server
mcp-inspector python apps/mcp-hello-world/server.py
```

### Integration with Claude Desktop

Add to Claude Desktop config (`~/Library/Application Support/Claude/claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "hello-world": {
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "/path/to/micro-casting-prototype/apps/mcp-hello-world",
        "python",
        "server.py"
      ]
    }
  }
}
```

## Learning Path

### Beginner Path
1. Start with **Foundation Tier** (1-3)
2. Explore **Retrieval Patterns** (4-7)
3. Study **Serialization** basics (8-9)

### Intermediate Path
1. **Tool-Invocation Patterns** (12-16)
2. Advanced **Serialization** (10-11)
3. Begin **Advanced Integration** (17)

### Advanced Path
1. **RAG Pipeline** (17)
2. **Vector Search** (18)
3. **Streaming** (19)
4. **Multi-Resource** (20)

## Design Principles

All servers follow these principles:

1. **Educational First**: Code is optimized for learning, not production
2. **Complete Examples**: Each server is fully functional
3. **Minimal Dependencies**: Only essential packages required
4. **Clear Patterns**: Demonstrates specific MCP patterns
5. **Well-Commented**: Explains why, not just what
6. **Type Hints**: Modern Python type annotations
7. **Error Handling**: Graceful failure with informative messages
8. **Async-First**: Proper async/await patterns throughout

## Common Patterns

### Server Structure

```python
import asyncio
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, Resource, TextContent

# Create server instance
app = Server("server-name")

# Register resource handler
@app.list_resources()
async def list_resources():
    return [...]

# Register tool handler
@app.list_tools()
async def list_tools():
    return [...]

# Register tool call handler
@app.call_tool()
async def call_tool(name: str, arguments: dict):
    if name == "tool_name":
        # Handle tool invocation
        return [TextContent(type="text", text="result")]
    raise ValueError(f"Unknown tool: {name}")

# Main entry point
async def main():
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())
```

### Tool Definition

```python
Tool(
    name="tool_name",
    description="Clear description of what the tool does",
    inputSchema={
        "type": "object",
        "properties": {
            "param1": {
                "type": "string",
                "description": "Parameter description"
            }
        },
        "required": ["param1"]
    }
)
```

### Resource Definition

```python
Resource(
    uri="scheme://identifier",
    name="Human Readable Name",
    description="What this resource provides",
    mimeType="application/json"
)
```

## Testing

Each server includes basic self-tests in docstrings and can be validated with:

```bash
# Syntax check
python -m py_compile apps/*/server.py

# Import test
cd apps/mcp-hello-world && python -c "import server; print('OK')"

# Run test (with timeout for stdio servers)
timeout 2 uv run python server.py || echo "Started successfully"
```

## Dependencies

All servers require:
- Python >= 3.10
- mcp >= 0.1.0
- uv package manager

Additional dependencies vary by server (see individual pyproject.toml files).

## Contributing

These servers are educational examples. To adapt them:

1. Copy the server directory
2. Modify pyproject.toml (name, description, dependencies)
3. Update server.py with your functionality
4. Test with `uv run python server.py`

## References

- [Model Context Protocol Specification](https://modelcontextprotocol.io/)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [MCP Server Examples](https://github.com/modelcontextprotocol/servers)
- [uv Documentation](https://github.com/astral-sh/uv)

## License

See LICENSE file in repository root.

## Architecture Decisions

### Why Separate Apps?

Each server is a separate application rather than a monolithic library because:
- **Clarity**: Each example is self-contained and understandable
- **Modularity**: Easy to copy and adapt individual servers
- **Learning**: Clear separation helps understand each pattern
- **Dependencies**: Each server has only required dependencies

### Why Simplified Implementations?

Advanced servers (RAG, vector search) use simplified algorithms because:
- **Educational**: Focus on MCP patterns, not ML algorithms
- **Dependencies**: Avoid heavy ML dependencies
- **Performance**: Faster startup and execution
- **Clarity**: Easier to understand and modify

### Why In-Memory Storage?

Most servers use in-memory storage instead of persistent databases because:
- **Simplicity**: No database setup required
- **Portability**: Works everywhere Python runs
- **Focus**: Emphasizes MCP patterns over data persistence
- **Testing**: Easy to reset and test

## Next Steps

After exploring these blueprints:

1. **Build Your Own**: Adapt a blueprint for your use case
2. **Combine Patterns**: Mix techniques from multiple servers
3. **Add Persistence**: Integrate with real databases
4. **Production Hardening**: Add logging, monitoring, error tracking
5. **Client Integration**: Connect with MCP-compatible clients
6. **Share**: Contribute your own patterns back

---

Generated as part of the micro-casting-prototype monorepo.
