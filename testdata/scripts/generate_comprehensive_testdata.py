#!/usr/bin/env python3
"""Generate comprehensive testdata for all MCP servers."""

import json
import csv
import yaml
import toml
from pathlib import Path
from datetime import datetime, timedelta
import random

# Base directory
BASE_DIR = Path(__file__).parent.parent
FILES_DIR = BASE_DIR / "files"
FILES_DIR.mkdir(exist_ok=True)

print("=" * 70)
print("GENERATING COMPREHENSIVE TESTDATA")
print("=" * 70)
print()

# =============================================================================
# 1. JSON FILES (various structures)
# =============================================================================
print("1. Generating JSON files...")

# Products JSON
products = {
    "products": [
        {
            "id": i,
            "name": f"Product {i}",
            "category": random.choice(["Electronics", "Books", "Clothing", "Home"]),
            "price": round(random.uniform(10, 500), 2),
            "in_stock": random.choice([True, False]),
            "tags": random.sample(["new", "sale", "featured", "bestseller"], k=random.randint(0, 3))
        }
        for i in range(1, 51)
    ],
    "metadata": {
        "generated_at": datetime.now().isoformat(),
        "total": 50
    }
}
(FILES_DIR / "products.json").write_text(json.dumps(products, indent=2))
print("  ✓ products.json (50 products)")

# Config JSON
config = {
    "server": {
        "host": "localhost",
        "port": 8080,
        "ssl": True
    },
    "database": {
        "host": "db.example.com",
        "port": 5432,
        "name": "mydb",
        "pool_size": 10
    },
    "features": {
        "caching": True,
        "logging": "info",
        "max_connections": 100
    }
}
(FILES_DIR / "config.json").write_text(json.dumps(config, indent=2))
print("  ✓ config.json (configuration)")

# Nested JSON
nested = {
    "company": {
        "name": "TechCorp",
        "departments": [
            {
                "name": "Engineering",
                "teams": [
                    {"name": "Frontend", "members": 12},
                    {"name": "Backend", "members": 15},
                    {"name": "DevOps", "members": 8}
                ]
            },
            {
                "name": "Sales",
                "teams": [
                    {"name": "Enterprise", "members": 20},
                    {"name": "SMB", "members": 15}
                ]
            }
        ]
    }
}
(FILES_DIR / "nested.json").write_text(json.dumps(nested, indent=2))
print("  ✓ nested.json (deeply nested structure)")

# =============================================================================
# 2. JSONL FILES (line-delimited JSON)
# =============================================================================
print("\n2. Generating JSONL files...")

# Events JSONL
events = []
for i in range(100):
    event = {
        "id": i,
        "timestamp": (datetime.now() - timedelta(hours=random.randint(0, 100))).isoformat(),
        "event_type": random.choice(["login", "logout", "purchase", "view"]),
        "user_id": random.randint(1000, 9999),
        "metadata": {"ip": f"192.168.1.{random.randint(1, 255)}"}
    }
    events.append(json.dumps(event))

(FILES_DIR / "events.jsonl").write_text("\n".join(events))
print("  ✓ events.jsonl (100 events)")

# Logs JSONL
logs = []
levels = ["DEBUG", "INFO", "WARNING", "ERROR"]
for i in range(50):
    log = {
        "timestamp": (datetime.now() - timedelta(minutes=random.randint(0, 1000))).isoformat(),
        "level": random.choice(levels),
        "message": f"Log message {i}",
        "component": random.choice(["api", "database", "cache", "worker"])
    }
    logs.append(json.dumps(log))

(FILES_DIR / "logs.jsonl").write_text("\n".join(logs))
print("  ✓ logs.jsonl (50 log entries)")

# =============================================================================
# 3. CSV FILES
# =============================================================================
print("\n3. Generating CSV files...")

# Employees CSV
with open(FILES_DIR / "employees.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["id", "name", "department", "salary", "hire_date"])
    for i in range(1, 31):
        writer.writerow([
            i,
            f"Employee {i}",
            random.choice(["Engineering", "Sales", "Marketing", "HR"]),
            random.randint(50000, 150000),
            (datetime.now() - timedelta(days=random.randint(0, 1000))).strftime("%Y-%m-%d")
        ])
print("  ✓ employees.csv (30 employees)")

# Sales CSV
with open(FILES_DIR / "sales.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["date", "product", "quantity", "revenue"])
    for i in range(100):
        writer.writerow([
            (datetime.now() - timedelta(days=random.randint(0, 365))).strftime("%Y-%m-%d"),
            f"Product-{random.randint(1, 20)}",
            random.randint(1, 100),
            round(random.uniform(100, 10000), 2)
        ])
print("  ✓ sales.csv (100 sales records)")

# =============================================================================
# 4. YAML FILES
# =============================================================================
print("\n4. Generating YAML files...")

# Application config YAML
app_config = {
    "application": {
        "name": "MyApp",
        "version": "1.0.0",
        "environment": "production"
    },
    "server": {
        "host": "0.0.0.0",
        "port": 3000,
        "workers": 4
    },
    "logging": {
        "level": "info",
        "format": "json",
        "outputs": ["stdout", "file"]
    }
}
(FILES_DIR / "config.yaml").write_text(yaml.dump(app_config, default_flow_style=False))
print("  ✓ config.yaml (application configuration)")

# Docker compose style YAML
docker_config = {
    "version": "3.8",
    "services": {
        "web": {
            "image": "nginx:latest",
            "ports": ["80:80"],
            "volumes": ["./html:/usr/share/nginx/html"]
        },
        "api": {
            "build": ".",
            "ports": ["3000:3000"],
            "environment": ["NODE_ENV=production"],
            "depends_on": ["db"]
        },
        "db": {
            "image": "postgres:14",
            "environment": ["POSTGRES_PASSWORD=secret"]
        }
    }
}
(FILES_DIR / "docker-compose.yaml").write_text(yaml.dump(docker_config, default_flow_style=False))
print("  ✓ docker-compose.yaml (services configuration)")

# =============================================================================
# 5. TOML FILES
# =============================================================================
print("\n5. Generating TOML files...")

# Project config TOML
project_config = {
    "project": {
        "name": "my-project",
        "version": "0.1.0",
        "description": "A sample project",
        "authors": ["John Doe <john@example.com>"]
    },
    "dependencies": {
        "requests": "^2.28.0",
        "pydantic": "^2.0.0",
        "fastapi": "^0.100.0"
    },
    "dev-dependencies": {
        "pytest": "^7.0.0",
        "black": "^23.0.0"
    }
}
(FILES_DIR / "pyproject.toml").write_text(toml.dumps(project_config))
print("  ✓ pyproject.toml (Python project config)")

# Application settings TOML
app_settings = {
    "database": {
        "host": "localhost",
        "port": 5432,
        "name": "mydb"
    },
    "cache": {
        "enabled": True,
        "ttl": 3600,
        "backend": "redis"
    },
    "logging": {
        "level": "INFO",
        "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    }
}
(FILES_DIR / "settings.toml").write_text(toml.dumps(app_settings))
print("  ✓ settings.toml (application settings)")

# =============================================================================
# 6. TEXT FILES (various types)
# =============================================================================
print("\n6. Generating text files...")

# Markdown
markdown_content = """# Project Documentation

## Overview

This is a sample project demonstrating various features.

## Features

- Feature 1: Data processing
- Feature 2: API integration
- Feature 3: Real-time updates

## Installation

```bash
pip install my-project
```

## Usage

```python
from my_project import MyClass

obj = MyClass()
obj.do_something()
```

## Contributing

Pull requests are welcome!
"""
(FILES_DIR / "README.md").write_text(markdown_content)
print("  ✓ README.md (markdown documentation)")

# Python file
python_content = '''#!/usr/bin/env python3
"""Sample Python module for testing."""

def calculate_factorial(n: int) -> int:
    """Calculate factorial of n."""
    if n <= 1:
        return 1
    return n * calculate_factorial(n - 1)

def fibonacci(n: int) -> int:
    """Calculate nth Fibonacci number."""
    if n <= 1:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)

class DataProcessor:
    """Process data with various methods."""

    def __init__(self, data):
        self.data = data

    def process(self):
        """Process the data."""
        return [x * 2 for x in self.data]

if __name__ == "__main__":
    print(calculate_factorial(5))
    print(fibonacci(10))
'''
(FILES_DIR / "sample.py").write_text(python_content)
print("  ✓ sample.py (Python source code)")

# Log file
log_content = """2024-11-05 10:00:00 INFO Starting application
2024-11-05 10:00:01 INFO Connected to database
2024-11-05 10:00:02 DEBUG Loading configuration
2024-11-05 10:00:03 INFO Server listening on port 8080
2024-11-05 10:01:15 INFO Received request from 192.168.1.100
2024-11-05 10:01:16 WARNING Slow query detected: 1.5s
2024-11-05 10:02:30 ERROR Connection timeout to external service
2024-11-05 10:02:31 INFO Retrying connection
2024-11-05 10:02:32 INFO Connection successful
2024-11-05 10:05:00 INFO Daily backup started
2024-11-05 10:05:45 INFO Daily backup completed
"""
(FILES_DIR / "application.log").write_text(log_content)
print("  ✓ application.log (log file)")

# Config file
conf_content = """# Application Configuration

[server]
host = 0.0.0.0
port = 8080
workers = 4

[database]
url = postgresql://localhost/mydb
pool_size = 10
timeout = 30

[cache]
enabled = true
backend = redis
host = localhost
port = 6379
"""
(FILES_DIR / "app.conf").write_text(conf_content)
print("  ✓ app.conf (configuration file)")

# Multiple text documents for RAG/Vector search
documents = [
    ("python_intro.txt", "Python is a high-level, interpreted programming language known for its simplicity and readability. Created by Guido van Rossum in 1991, Python emphasizes code readability with significant whitespace."),
    ("javascript_intro.txt", "JavaScript is a programming language that enables interactive web pages. Originally developed by Brendan Eich at Netscape, JavaScript is now an essential part of web development alongside HTML and CSS."),
    ("database_intro.txt", "Databases are organized collections of data that can be easily accessed, managed, and updated. SQL databases like PostgreSQL and MySQL use structured query language for data manipulation."),
    ("api_design.txt", "REST APIs (Representational State Transfer) are architectural styles for designing networked applications. RESTful APIs use HTTP methods and follow principles like statelessness and resource-based URLs."),
    ("machine_learning.txt", "Machine Learning is a subset of artificial intelligence that enables systems to learn from data without explicit programming. Common algorithms include neural networks, decision trees, and support vector machines."),
]

for filename, content in documents:
    (FILES_DIR / filename).write_text(content)
print(f"  ✓ {len(documents)} text documents for RAG/Vector search")

# =============================================================================
# 7. PROTOCOL BUFFER FILES
# =============================================================================
print("\n7. Generating Protocol Buffer files...")

proto_content = '''syntax = "proto3";

package example;

message Person {
  int32 id = 1;
  string name = 2;
  string email = 3;
  PhoneNumber phone = 4;
}

message PhoneNumber {
  string number = 1;
  PhoneType type = 2;
}

enum PhoneType {
  MOBILE = 0;
  HOME = 1;
  WORK = 2;
}

message AddressBook {
  repeated Person people = 1;
}
'''
(FILES_DIR / "person.proto").write_text(proto_content)
print("  ✓ person.proto (Protocol Buffer definition)")

# =============================================================================
# 8. DIRECTORY STRUCTURE
# =============================================================================
print("\n8. Creating directory structure...")

# Create nested directories
(FILES_DIR / "project" / "src").mkdir(parents=True, exist_ok=True)
(FILES_DIR / "project" / "tests").mkdir(parents=True, exist_ok=True)
(FILES_DIR / "project" / "docs").mkdir(parents=True, exist_ok=True)
(FILES_DIR / "data" / "raw").mkdir(parents=True, exist_ok=True)
(FILES_DIR / "data" / "processed").mkdir(parents=True, exist_ok=True)

# Add files to directories
(FILES_DIR / "project" / "src" / "main.py").write_text("# Main application\nprint('Hello, World!')")
(FILES_DIR / "project" / "tests" / "test_main.py").write_text("# Tests\ndef test_main():\n    assert True")
(FILES_DIR / "project" / "docs" / "API.md").write_text("# API Documentation\n\nEndpoints...")
(FILES_DIR / "data" / "raw" / "data.txt").write_text("Raw data here")
(FILES_DIR / "data" / "processed" / "results.txt").write_text("Processed results")

print("  ✓ Created nested directory structure")

# =============================================================================
# SUMMARY
# =============================================================================
print()
print("=" * 70)
print("TESTDATA GENERATION COMPLETE")
print("=" * 70)
print()
print(f"Location: {FILES_DIR}")
print()

# Count files by type
file_counts = {}
for file in FILES_DIR.rglob("*"):
    if file.is_file():
        ext = file.suffix or "no-ext"
        file_counts[ext] = file_counts.get(ext, 0) + 1

print("Files created by type:")
for ext in sorted(file_counts.keys()):
    print(f"  • {ext:15} - {file_counts[ext]:2} files")

total_files = sum(file_counts.values())
print(f"\nTotal: {total_files} files")
print("=" * 70)
