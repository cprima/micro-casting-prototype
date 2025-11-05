# Test Data Mapping for MCP Servers

This document maps each MCP server to its appropriate test data sources.

## Test Data Overview

### Available Databases

| Database | Size | Complexity | Tables | Records | Purpose |
|----------|------|------------|--------|---------|---------|
| books.db | 7 KB | Beginner | 2 | 18 | Simple book catalog for basic queries |
| library.db | 312 KB | Beginner | 5 | 1,816 | Library management with loans |
| ecommerce.db | 1.3 MB | Medium | 6 | 3,117+ | E-commerce with orders, reviews |
| logistics.db | 1.3 MB | Advanced | 11 | 3,015+ | Supply chain and logistics |
| finance.db | 700 KB | Advanced | 9 | 2,139+ | Accounting with double-entry |

### Other Test Files

| File | Size | Purpose |
|------|------|---------|
| users.json | 1 KB | JSON querying with JSONPath |
| sample.txt | 1 KB | Filesystem operations |

## Server to Testdata Mapping

### Foundation Tier

#### mcp-hello-world
- **Testdata**: None required
- **Purpose**: Demonstrates basic tool invocation

#### mcp-echo-tool
- **Testdata**: None required
- **Purpose**: Parameter handling and validation

#### mcp-simple-retrieval
- **Testdata**: Uses in-memory data
- **Purpose**: Basic resource patterns

### Retrieval Patterns

#### mcp-filesystem-retrieval
- **Primary**: `testdata/sample.txt`
- **Secondary**: All files in `testdata/` directory
- **Usage**:
  ```bash
  # List files
  list_files: {"path": "../../testdata"}

  # Read file
  read_file: {"path": "../../testdata/sample.txt"}
  ```

#### mcp-sqlite-retrieval
- **Primary**: `testdata/databases/library.db` (beginner-friendly)
- **Secondary**: `testdata/books.db` (minimal example)
- **Advanced**: `testdata/databases/ecommerce.db`, `logistics.db`, `finance.db`
- **Usage**:
  ```bash
  # Simple queries (books.db)
  query: {
    "database": "../../testdata/books.db",
    "query": "SELECT * FROM books WHERE genre='Fantasy'"
  }

  # Complex queries (library.db)
  query: {
    "database": "../../testdata/databases/library.db",
    "query": "SELECT b.title, a.name, l.checkout_date
              FROM loans l
              JOIN books b ON l.book_id = b.id
              JOIN authors a ON b.author_id = a.id
              WHERE l.return_date IS NULL"
  }
  ```

#### mcp-http-retrieval
- **Testdata**: External URLs (httpbin.org, jsonplaceholder.typicode.com)
- **Local Testing**: Could use file:// URLs for testdata files
- **Usage**:
  ```bash
  fetch: {"url": "https://httpbin.org/json"}
  ```

#### mcp-json-retrieval
- **Primary**: `testdata/users.json`
- **Purpose**: Demonstrates JSONPath queries
- **Usage**:
  ```bash
  query: {
    "file": "../../testdata/users.json",
    "jsonpath": "$.users[?(@.role=='developer')]"
  }
  ```

### Serialization Patterns

#### mcp-json-serialization
- **Testdata**: Uses inline examples
- **Could Use**: Any JSON file from testdata
- **Purpose**: Schema validation

#### mcp-pydantic-models
- **Testdata**: Uses model definitions
- **Could Use**: `testdata/users.json` for validation examples

#### mcp-protocol-buffers
- **Testdata**: Uses inline protobuf definitions
- **Purpose**: Binary serialization demo

#### mcp-custom-formats
- **Testdata**: Could generate CSV/YAML/TOML from databases
- **Example**: Export library.db to CSV

### Tool-Invocation Patterns

#### mcp-sync-tools
- **Testdata**: None required
- **Purpose**: Demonstrates synchronous calculations

#### mcp-async-tools
- **Testdata**: External URLs for parallel fetch demo

#### mcp-stateful-tools
- **Testdata**: Uses session state
- **Purpose**: State management patterns

#### mcp-chained-tools
- **Testdata**: Text input for number extraction

#### mcp-error-handling
- **Testdata**: Uses error-inducing inputs
- **Purpose**: Error handling patterns

### Advanced Integration

#### mcp-rag-pipeline
- **Primary**: `testdata/databases/library.db` or `ecommerce.db`
- **Purpose**: Build knowledge base from database content
- **Usage**:
  ```bash
  # Add knowledge from library
  add_knowledge: {
    "text": "The Great Gatsby by F. Scott Fitzgerald is a novel about...",
    "topic": "literature"
  }

  # Retrieve context
  retrieve_context: {
    "query": "novels about American dream",
    "top_k": 3
  }
  ```

#### mcp-vector-search
- **Primary**: Any text content from databases
- **Secondary**: `testdata/sample.txt`
- **Purpose**: Demonstrate vector embeddings
- **Usage**:
  ```bash
  # Add book descriptions to vector store
  add_vector: {
    "text": "Science fiction novel set in dystopian future",
    "metadata": {"genre": "sci-fi", "book_id": 3}
  }
  ```

#### mcp-streaming-responses
- **Testdata**: None required
- **Purpose**: Demonstrates progressive output

#### mcp-multi-resource-server
- **Primary**: Can integrate multiple data sources
- **Could Use**:
  - `books.db` for database operations
  - `users.json` for JSON operations
  - External URLs for HTTP operations

## Recommended Teaching Progression

### Level 1: Beginner (Simple Data)
1. **books.db** - Minimal database (2 tables, 18 records)
   - Use with: mcp-sqlite-retrieval
   - Teaches: Basic SQL queries, simple joins

2. **sample.txt** - Plain text file
   - Use with: mcp-filesystem-retrieval
   - Teaches: File I/O, path handling

3. **users.json** - Small JSON file
   - Use with: mcp-json-retrieval, mcp-json-serialization
   - Teaches: JSON parsing, JSONPath

### Level 2: Intermediate (Realistic Data)
1. **library.db** - Real-world library system
   - Use with: mcp-sqlite-retrieval, mcp-rag-pipeline
   - Teaches: Complex queries, data relationships

2. **ecommerce.db** - E-commerce platform
   - Use with: mcp-sqlite-retrieval, mcp-vector-search
   - Teaches: Hierarchical data, aggregations

### Level 3: Advanced (Complex Systems)
1. **logistics.db** - Supply chain management
   - Use with: mcp-sqlite-retrieval, mcp-rag-pipeline
   - Teaches: Many-to-many relationships, tracking

2. **finance.db** - Accounting system
   - Use with: mcp-sqlite-retrieval
   - Teaches: Double-entry bookkeeping, fiscal periods

## Creating Custom Test Data

### For Specific Servers

#### Custom JSON for mcp-json-retrieval
```bash
echo '{
  "products": [
    {"id": 1, "name": "Widget", "price": 9.99},
    {"id": 2, "name": "Gadget", "price": 19.99}
  ]
}' > testdata/products.json
```

#### Custom SQLite for mcp-sqlite-retrieval
```python
import sqlite3
conn = sqlite3.connect('testdata/custom.db')
cursor = conn.cursor()
cursor.execute("CREATE TABLE items (id INTEGER, name TEXT)")
cursor.execute("INSERT INTO items VALUES (1, 'Item 1')")
conn.commit()
conn.close()
```

#### Export Database to CSV for mcp-custom-formats
```python
import sqlite3
import csv

conn = sqlite3.connect('testdata/databases/library.db')
cursor = conn.cursor()
cursor.execute("SELECT * FROM books")

with open('testdata/books.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow([desc[0] for desc in cursor.description])
    writer.writerows(cursor.fetchall())
```

## Test Data Regeneration

All databases can be regenerated:

```bash
cd testdata/scripts

# Regenerate all databases
uv run python seed_all.py

# Regenerate specific database
uv run python generate_library.py
uv run python generate_ecommerce.py
uv run python generate_logistics.py
uv run python generate_finance.py
```

## Data Characteristics

### Books.db
- **Records**: 10 books, 8 authors
- **Features**: Simple structure, easy to understand
- **Best For**: First-time SQL learners

### Library.db
- **Records**: 100 authors, 500 books, 200 members, 1000 loans
- **Features**: Realistic library management, date-based queries
- **Best For**: Learning joins, date filtering

### Ecommerce.db
- **Records**: 500 customers, 300 products, 1500 orders, 800 reviews
- **Features**: Hierarchical categories, order items, ratings
- **Best For**: Aggregations, grouping, hierarchical queries

### Logistics.db
- **Records**: 2000 shipments, 30 hubs, 100 routes, tracking events
- **Features**: Geographic data, status tracking, complex relationships
- **Best For**: Advanced joins, status workflows

### Finance.db
- **Records**: 500 invoices, 1000 transactions, 48 fiscal periods
- **Features**: Double-entry bookkeeping, GL accounts, cost centers
- **Best For**: Financial calculations, period-based queries

## Sample Queries by Database

See individual database documentation in `testdata/scripts/README.md` for comprehensive query examples.

## Integration Tips

1. **Path Resolution**: Use relative paths from server directory
   - `../../testdata/databases/library.db`
   - `../../testdata/users.json`

2. **Database Choice**: Match complexity to learning objective
   - Teaching basics? Use books.db or library.db
   - Teaching advanced concepts? Use logistics.db or finance.db

3. **Combining Data**: Multi-resource server can use multiple databases
   ```python
   # Access different databases for different queries
   library_conn = await aiosqlite.connect('../../testdata/databases/library.db')
   ecom_conn = await aiosqlite.connect('../../testdata/databases/ecommerce.db')
   ```

4. **Performance**: Large databases (logistics, ecommerce) good for teaching
   - Query optimization
   - Index usage
   - Result pagination

---

Last updated: 2024-11-05
Testdata version: 1.0
