#!/usr/bin/env python3
"""Enhance README files with detailed usage examples."""

from pathlib import Path

README_TEMPLATES = {
    "mcp-hello-world": """# MCP Hello World Server

Minimal MCP server demonstrating basic setup and tool invocation.

## Purpose

Learn the fundamental structure of an MCP server:
- Server initialization
- Tool registration
- Basic request/response handling
- Stdio transport

## Features

- **hello** tool: Say hello to the world or a specific person

## Usage

### Running the Server

```bash
cd apps/mcp-hello-world
uv run python server.py
```

### Testing with MCP Inspector

```bash
npm install -g @modelcontextprotocol/inspector
mcp-inspector python server.py
```

### Example Tool Call

Tool: `hello`

Input:
```json
{
  "name": "World"
}
```

Output:
```
Hello, World!
```

Input:
```json
{
  "name": "Alice"
}
```

Output:
```
Hello, Alice!
```

## Code Structure

```python
# 1. Import MCP components
from mcp.server import Server
from mcp.server.stdio import stdio_server

# 2. Create server instance
app = Server("mcp-hello-world")

# 3. Register tools
@app.list_tools()
async def list_tools():
    return [Tool(...)]

# 4. Handle tool calls
@app.call_tool()
async def call_tool(name, arguments):
    ...

# 5. Main entry point
async def main():
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, ...)
```

## Learning Objectives

- Understand MCP server lifecycle
- Learn tool definition syntax
- Practice async/await patterns
- Master stdio transport basics

## Next Steps

After understanding this server, explore:
- **mcp-echo-tool**: More complex tool with parameters
- **mcp-simple-retrieval**: Resource patterns
- **mcp-sync-tools**: Synchronous computations
""",

    "mcp-sqlite-retrieval": """# MCP SQLite Retrieval Server

Database query and retrieval using SQLite with async operations.

## Purpose

Demonstrate how to:
- Connect to SQLite databases asynchronously
- List tables and schemas
- Execute queries safely
- Return structured data

## Features

- **list_tables** tool: Get all tables in database
- **query** tool: Execute SELECT queries
- **schema** tool: Get table schema information

## Usage

### Running the Server

```bash
cd apps/mcp-sqlite-retrieval
uv run python server.py
```

### Sample Database

Use the provided test database:

```bash
# Database location: ../../testdata/books.db
# Tables: books, authors
```

### Example Tool Calls

#### List Tables

Tool: `list_tables`

Input:
```json
{
  "database": "../../testdata/books.db"
}
```

Output:
```
Tables: books, authors
```

#### Query Books

Tool: `query`

Input:
```json
{
  "database": "../../testdata/books.db",
  "query": "SELECT title, author, year FROM books WHERE genre='Fantasy' ORDER BY year"
}
```

Output:
```
title                                  | author           | year
The Hobbit                            | J.R.R. Tolkien   | 1937
The Lord of the Rings                 | J.R.R. Tolkien   | 1954
Harry Potter and the Sorcerer's Stone | J.K. Rowling     | 1997
```

#### Get Schema

Tool: `schema`

Input:
```json
{
  "database": "../../testdata/books.db",
  "table": "books"
}
```

Output:
```
Table: books
Columns:
  - id: INTEGER (PRIMARY KEY)
  - title: TEXT
  - author: TEXT
  - year: INTEGER
  - genre: TEXT
  - rating: REAL
```

## Security Features

- Only SELECT queries allowed (read-only)
- SQL injection prevention
- Query timeout limits
- Path validation

## Learning Objectives

- Async database operations with aiosqlite
- Safe query execution
- Result formatting
- Error handling for database operations

## Next Steps

- **mcp-http-retrieval**: Fetch data from REST APIs
- **mcp-json-retrieval**: Query JSON with JSONPath
- **mcp-rag-pipeline**: Build knowledge bases
""",

    "mcp-rag-pipeline": """# MCP RAG Pipeline Server

Retrieval-Augmented Generation (RAG) pattern demonstration.

## Purpose

Show simplified RAG implementation:
- Knowledge base storage
- Context retrieval
- Similarity search
- Knowledge management

## Features

- **retrieve_context** tool: Find relevant context for queries
- **add_knowledge** tool: Add entries to knowledge base
- In-memory knowledge base with metadata
- Simple word-overlap similarity scoring

## Usage

### Running the Server

```bash
cd apps/mcp-rag-pipeline
uv run python server.py
```

### Example Workflow

#### 1. Retrieve Context

Tool: `retrieve_context`

Input:
```json
{
  "query": "What is Python",
  "top_k": 3
}
```

Output:
```
[Score: 1.00] Python is a high-level programming language.
[Score: 0.00] MCP stands for Model Context Protocol.
[Score: 0.00] RAG combines retrieval and generation.
```

#### 2. Add Knowledge

Tool: `add_knowledge`

Input:
```json
{
  "text": "Python was created by Guido van Rossum in 1991.",
  "topic": "python"
}
```

Output:
```
Added entry 5
```

#### 3. Query Again

Tool: `retrieve_context`

Input:
```json
{
  "query": "Who created Python",
  "top_k": 2
}
```

Output:
```
[Score: 0.67] Python was created by Guido van Rossum in 1991.
[Score: 0.33] Python is a high-level programming language.
```

## How It Works

### Similarity Calculation

Uses word overlap for demonstration:

```python
def simple_similarity(query: str, text: str) -> float:
    query_words = set(query.lower().split())
    text_words = set(text.lower().split())
    return len(query_words & text_words) / len(query_words)
```

### Knowledge Base Structure

```python
{
  "id": 1,
  "text": "The knowledge entry text",
  "metadata": {"topic": "category"}
}
```

## Production Considerations

For real applications, replace with:
- **Vector embeddings** (OpenAI, Sentence Transformers)
- **Vector databases** (Pinecone, Weaviate, Qdrant)
- **Semantic similarity** (cosine similarity on embeddings)
- **Persistent storage** (database, disk)

## Learning Objectives

- Understand RAG architecture
- Implement context retrieval
- Score relevance
- Manage knowledge bases

## Next Steps

- **mcp-vector-search**: More sophisticated vector similarity
- **mcp-multi-resource-server**: Combine multiple capabilities
- Integrate real embedding models (OpenAI, HuggingFace)
""",

    "mcp-async-tools": """# MCP Async Tools Server

Asynchronous tool patterns with concurrency.

## Purpose

Demonstrate async/await patterns:
- Non-blocking operations
- Concurrent execution
- Parallel HTTP requests
- Proper async handling

## Features

- **async_wait** tool: Non-blocking delays
- **parallel_fetch** tool: Concurrent URL fetching

## Usage

### Running the Server

```bash
cd apps/mcp-async-tools
uv run python server.py
```

### Example Tool Calls

#### Async Wait

Tool: `async_wait`

Input:
```json
{
  "seconds": 1.5
}
```

Output:
```
Waited 1.50 seconds
```

The server remains responsive during the wait.

#### Parallel Fetch

Tool: `parallel_fetch`

Input:
```json
{
  "urls": [
    "https://httpbin.org/status/200",
    "https://httpbin.org/status/404",
    "https://httpbin.org/delay/1"
  ]
}
```

Output:
```
https://httpbin.org/status/200: Status 200
https://httpbin.org/status/404: Status 404
https://httpbin.org/delay/1: Status 200
```

All URLs are fetched concurrently.

## Async Patterns

### Concurrent Execution

```python
# Sequential (slow)
result1 = await fetch_url(url1)
result2 = await fetch_url(url2)

# Concurrent (fast)
tasks = [fetch_url(url1), fetch_url(url2)]
results = await asyncio.gather(*tasks)
```

### Error Handling

```python
responses = await asyncio.gather(*tasks, return_exceptions=True)
for response in responses:
    if isinstance(response, Exception):
        handle_error(response)
```

## Learning Objectives

- Master async/await syntax
- Understand concurrency vs parallelism
- Use asyncio.gather for parallel execution
- Handle exceptions in async code

## Comparison with mcp-sync-tools

| Aspect | Sync Tools | Async Tools |
|--------|------------|-------------|
| Blocking | Yes | No |
| Concurrency | No | Yes |
| I/O Operations | Slow | Fast |
| CPU-bound | Good | Slower |

## Next Steps

- **mcp-stateful-tools**: Maintain state across calls
- **mcp-streaming-responses**: Progressive output
- **mcp-error-handling**: Robust error patterns
"""
}

def write_enhanced_readme(server_name, content):
    """Write enhanced README to server directory."""
    readme_path = Path(f"/home/user/micro-casting-prototype/apps/{server_name}/README.md")
    readme_path.write_text(content)
    print(f"✓ Enhanced {server_name}/README.md")

# Write enhanced READMEs
for server_name, content in README_TEMPLATES.items():
    write_enhanced_readme(server_name, content)

print(f"\n✓ Enhanced {len(README_TEMPLATES)} README files")
print("\nTo enhance remaining READMEs, follow similar patterns:")
print("- Clear purpose statement")
print("- Detailed usage examples")
print("- Code snippets")
print("- Learning objectives")
print("- Next steps")
