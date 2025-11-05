# Test Data

This directory contains sample data files for testing and demonstrating MCP servers.

## Files

### books.db
SQLite database with sample book and author data.

**Tables:**
- `books` - 10 sample books with title, author, year, genre, rating
- `authors` - 8 authors with name, country, birth_year

**Usage:**
```bash
cd apps/mcp-sqlite-retrieval
uv run python server.py
# Query: SELECT * FROM books WHERE genre='Fantasy'
```

**Regenerate:**
```bash
python testdata/create_sample_db.py
```

### users.json
JSON file with sample user data including nested arrays and objects.

**Structure:**
- `users` array with 4 user objects
- Each user has: id, name, email, role, skills, active status
- `metadata` object with version and statistics

**Usage with JSONPath:**
```bash
cd apps/mcp-json-retrieval
# Query: $.users[?(@.role=='developer')].name
# Query: $.users[*].skills[*]
```

### sample.txt
Simple text file for filesystem operations.

**Usage:**
```bash
cd apps/mcp-filesystem-retrieval
# Use to test file reading and directory navigation
```

## Creating Additional Test Data

### More Databases

```python
import sqlite3
conn = sqlite3.connect('testdata/mydata.db')
# ... create tables and insert data
```

### JSON Files

```python
import json
data = {"key": "value"}
with open('testdata/mydata.json', 'w') as f:
    json.dump(data, f, indent=2)
```

### Text Files

```bash
echo "Sample content" > testdata/myfile.txt
```

## Test Data Principles

1. **Realistic**: Data resembles real-world scenarios
2. **Diverse**: Multiple types and structures
3. **Complete**: Includes all necessary fields
4. **Safe**: No sensitive or personal information
5. **Documented**: Clear description of structure and usage

## Servers Using This Data

- **mcp-sqlite-retrieval**: Uses `books.db`
- **mcp-json-retrieval**: Uses `users.json`
- **mcp-filesystem-retrieval**: Uses all files in this directory
- **mcp-http-retrieval**: Can use local file:// URLs if needed

## Extending Test Data

To add more test data:

1. Create the data file (DB, JSON, TXT, etc.)
2. Document it in this README
3. Update relevant server READMEs with examples
4. Consider adding a generator script for complex data
