#!/usr/bin/env python3
"""Create sample SQLite database for testing mcp-sqlite-retrieval server."""

import sqlite3
from pathlib import Path

# Create testdata directory
testdata_dir = Path(__file__).parent
testdata_dir.mkdir(exist_ok=True)

# Database path
db_path = testdata_dir / "books.db"

# Remove existing database
if db_path.exists():
    db_path.unlink()

# Create database and tables
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Create books table
cursor.execute("""
CREATE TABLE books (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    author TEXT NOT NULL,
    year INTEGER,
    genre TEXT,
    rating REAL
)
""")

# Create authors table
cursor.execute("""
CREATE TABLE authors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    country TEXT,
    birth_year INTEGER
)
""")

# Insert sample books
books_data = [
    ("The Great Gatsby", "F. Scott Fitzgerald", 1925, "Fiction", 4.5),
    ("To Kill a Mockingbird", "Harper Lee", 1960, "Fiction", 4.8),
    ("1984", "George Orwell", 1949, "Science Fiction", 4.7),
    ("Pride and Prejudice", "Jane Austen", 1813, "Romance", 4.6),
    ("The Catcher in the Rye", "J.D. Salinger", 1951, "Fiction", 4.2),
    ("Animal Farm", "George Orwell", 1945, "Political Fiction", 4.5),
    ("The Hobbit", "J.R.R. Tolkien", 1937, "Fantasy", 4.7),
    ("Brave New World", "Aldous Huxley", 1932, "Science Fiction", 4.3),
    ("The Lord of the Rings", "J.R.R. Tolkien", 1954, "Fantasy", 4.9),
    ("Harry Potter and the Sorcerer's Stone", "J.K. Rowling", 1997, "Fantasy", 4.7),
]

cursor.executemany(
    "INSERT INTO books (title, author, year, genre, rating) VALUES (?, ?, ?, ?, ?)",
    books_data
)

# Insert sample authors
authors_data = [
    ("F. Scott Fitzgerald", "USA", 1896),
    ("Harper Lee", "USA", 1926),
    ("George Orwell", "UK", 1903),
    ("Jane Austen", "UK", 1775),
    ("J.D. Salinger", "USA", 1919),
    ("J.R.R. Tolkien", "UK", 1892),
    ("Aldous Huxley", "UK", 1894),
    ("J.K. Rowling", "UK", 1965),
]

cursor.executemany(
    "INSERT INTO authors (name, country, birth_year) VALUES (?, ?, ?)",
    authors_data
)

# Commit and close
conn.commit()
conn.close()

print(f"✓ Created sample database: {db_path}")
print(f"  - {len(books_data)} books")
print(f"  - {len(authors_data)} authors")
