# MCP Server Blueprints

Reusable libraries and example applications for building Model Context Protocol (MCP) servers.

## Overview

This repository includes a collection of MCP server blueprints organized as:

1. **Reusable Libraries** (`libs/`) - Core components and patterns
2. **Example Applications** (`apps/`) - Working servers demonstrating library usage
3. **Test Data** (`libs/mcp-testdata/`) - Realistic databases for testing

## Structure

```
micro-casting-prototype/
├── libs/
│   ├── mcp-core/              # Foundation MCP patterns
│   │   ├── src/mcp_core/
│   │   │   ├── hello.py       # Hello tool pattern
│   │   │   └── echo.py        # Echo tool patterns
│   │   ├── tests/
│   │   └── README.md
│   ├── mcp-testdata/          # Test databases
│   │   ├── src/mcp_testdata/
│   │   │   ├── generators/    # Database generators
│   │   │   └── data/          # Generated databases
│   │   └── README.md
│   └── crawling/              # Existing: web scraping
│
└── apps/
    ├── mcp-example-server/    # Example using mcp-core
    │   ├── server.py
    │   └── README.md
    ├── mcp-srv-mtdlgy_mcp/    # Existing: methodology server
    └── sitemap-crawler/        # Existing
```

## Libraries

### mcp-core

Foundation patterns for building MCP servers.

**Features**:
- Hello tool (simple greeting)
- Echo tools (simple and structured)
- Parameter validation
- Response formatting

**Usage**:
```python
from mcp_core import create_hello_tool, hello_handler

@app.list_tools()
async def list_tools():
    return [create_hello_tool()]

@app.call_tool()
async def call_tool(name: str, arguments: dict):
    if name == "hello":
        return await hello_handler(arguments)
```

**Documentation**: [libs/mcp-core/README.md](../libs/mcp-core/README.md)

### mcp-testdata

Test data corpus with realistic SQLite databases.

**Features**:
- Database generators (library, ecommerce, logistics, finance)
- Pre-generated test databases
- Faker-based realistic data
- CLI for generation

**Usage**:
```python
from mcp_testdata import get_database_path

db_path = get_database_path("library")
# Use with sqlite3 or aiosqlite
```

**Documentation**: [libs/mcp-testdata/README.md](../libs/mcp-testdata/README.md)

## Applications

### mcp-example-server

Example MCP server demonstrating `mcp-core` library usage.

**Features**:
- Uses hello and echo tools from mcp-core
- Minimal server code
- Complete working example

**Run**:
```bash
cd apps/mcp-example-server
uv run python server.py
```

**Documentation**: [apps/mcp-example-server/README.md](../apps/mcp-example-server/README.md)

## Getting Started

### Prerequisites

- Python 3.10+
- uv package manager

### Installation

```bash
# Clone repository
git clone https://github.com/cprima/micro-casting-prototype.git
cd micro-casting-prototype

# Sync workspace
uv sync
```

### Quick Start

1. **Explore the mcp-core library**:
```bash
cd libs/mcp-core
cat README.md
uv run pytest  # Run tests
```

2. **Run the example server**:
```bash
cd apps/mcp-example-server
uv run python server.py
```

3. **Generate test data**:
```bash
cd libs/mcp-testdata
uv run generate-testdata --database library
```

## Development

### Adding a New Library

1. Create directory: `libs/your-lib-name/`
2. Add `pyproject.toml` with workspace configuration
3. Create `src/your_lib_name/` directory
4. Add code and tests
5. Run `uv sync` from root

### Adding a New Application

1. Create directory: `apps/your-app-name/`
2. Add `pyproject.toml` with dependencies
3. Add `[tool.uv.sources]` for workspace libraries
4. Create `server.py` and other files
5. Run `uv sync` from root

### Workspace Configuration

The root `pyproject.toml` defines workspace members:
```toml
[tool.uv.workspace]
members = ["libs/*", "apps/*", "apps/uipac/*"]
```

Libraries and apps are automatically discovered.

### Using Workspace Libraries

In your app's `pyproject.toml`:
```toml
[project]
dependencies = [
    "mcp-core",      # Workspace library
    "other-pkg",     # External package
]

[tool.uv.sources]
mcp-core = { workspace = true }
```

## Methodology Alignment

These blueprints align with the micro-casting decision-driven framework:

### Phase 1: Getting Started

**Libraries**:
- `mcp-core` - Foundation patterns

**Decision Nodes**:
- Tool naming conventions
- Parameter handling
- Response formats

### Phase 2: Core Features

**Libraries** (Coming Soon):
- `mcp-retrieval` - Data access patterns
- `mcp-serialization` - Data format handling

**Decision Nodes**:
- Input validation
- Schema design
- Error handling

### Phase 3: Production Ready

**Patterns**:
- Error handling and retries
- State management
- Testing strategies

### Phase 4: Advanced

**Patterns** (Coming Soon):
- RAG integration
- Vector search
- Streaming responses

See [docs/methodology/data.json](./methodology/data.json) for complete framework.

## Testing

### Run All Tests

```bash
# From repository root
uv run pytest

# Specific library
cd libs/mcp-core
uv run pytest

# With coverage
uv run pytest --cov=mcp_core --cov-report=html
```

### Test Structure

Each library includes:
- `tests/` directory
- pytest configuration
- Async test support

## Contributing

### Code Style

- Type hints throughout
- Comprehensive docstrings
- Follow existing patterns
- Add tests for new features

### Pull Request Process

1. Create feature branch
2. Implement changes with tests
3. Update documentation
4. Run tests: `uv run pytest`
5. Submit PR

## Roadmap

### Immediate

- [x] mcp-core library with foundation patterns
- [x] mcp-testdata library with generators
- [x] Example server application
- [ ] Complete mcp-testdata generators (ecommerce, logistics, finance)

### Short Term

- [ ] mcp-retrieval library (filesystem, sqlite, http, json)
- [ ] mcp-serialization library (json, pydantic, protobuf)
- [ ] Additional example applications

### Long Term

- [ ] mcp-tools library (sync, async, stateful, chained, error-handling)
- [ ] mcp-advanced library (RAG, vector search, streaming)
- [ ] Comprehensive documentation site
- [ ] Video tutorials

## Resources

### Documentation

- [MCP Protocol Specification](https://modelcontextprotocol.io/)
- [Micro-casting Methodology](./methodology/data.json)
- [Library Documentation](../libs/)
- [Example Applications](../apps/)

### Tools

- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [uv Package Manager](https://github.com/astral-sh/uv)

## License

See [LICENSE](../LICENSE) in repository root.

---

**Last Updated**: 2025-01-04
**Maintained By**: Christian Prior-Mamulyan
