#!/usr/bin/env python3
"""
Generate library.db - A simple library management database for teaching MCP basics.

Schema:
- authors: Writers of books
- books: Book catalog
- categories: Genre/topic categories
- members: Library members
- loans: Book checkout history

Use cases: Basic queries, simple JOINs, date filtering
"""

import sqlite3
import random
from datetime import datetime, timedelta
from pathlib import Path
from faker import Faker

fake = Faker()
Faker.seed(42)
random.seed(42)


def create_schema(conn):
    """Create the library database schema."""
    cursor = conn.cursor()

    # Authors table
    cursor.execute("""
        CREATE TABLE authors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            birth_year INTEGER,
            nationality TEXT,
            biography TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Categories table
    cursor.execute("""
        CREATE TABLE categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            description TEXT,
            parent_category_id INTEGER,
            FOREIGN KEY (parent_category_id) REFERENCES categories(id)
        )
    """)

    # Books table
    cursor.execute("""
        CREATE TABLE books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author_id INTEGER NOT NULL,
            isbn TEXT UNIQUE,
            published_year INTEGER,
            category_id INTEGER,
            pages INTEGER,
            language TEXT DEFAULT 'English',
            available_copies INTEGER DEFAULT 1,
            total_copies INTEGER DEFAULT 1,
            added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (author_id) REFERENCES authors(id),
            FOREIGN KEY (category_id) REFERENCES categories(id)
        )
    """)

    # Members table
    cursor.execute("""
        CREATE TABLE members (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            phone TEXT,
            address TEXT,
            joined_date DATE NOT NULL,
            membership_type TEXT DEFAULT 'standard',
            active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Loans table
    cursor.execute("""
        CREATE TABLE loans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            book_id INTEGER NOT NULL,
            member_id INTEGER NOT NULL,
            loan_date DATE NOT NULL,
            due_date DATE NOT NULL,
            return_date DATE,
            renewed_count INTEGER DEFAULT 0,
            status TEXT DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (book_id) REFERENCES books(id),
            FOREIGN KEY (member_id) REFERENCES members(id),
            CHECK (status IN ('active', 'returned', 'overdue', 'lost'))
        )
    """)

    # Create indexes for common queries
    cursor.execute("CREATE INDEX idx_books_author ON books(author_id)")
    cursor.execute("CREATE INDEX idx_books_category ON books(category_id)")
    cursor.execute("CREATE INDEX idx_loans_book ON loans(book_id)")
    cursor.execute("CREATE INDEX idx_loans_member ON loans(member_id)")
    cursor.execute("CREATE INDEX idx_loans_status ON loans(status)")

    conn.commit()


def generate_authors(conn, count=100):
    """Generate author records."""
    cursor = conn.cursor()
    authors = []

    for _ in range(count):
        name = fake.name()
        birth_year = random.randint(1920, 2000)
        nationality = fake.country()
        biography = fake.text(max_nb_chars=200)

        authors.append((name, birth_year, nationality, biography))

    cursor.executemany(
        "INSERT INTO authors (name, birth_year, nationality, biography) VALUES (?, ?, ?, ?)",
        authors
    )
    conn.commit()
    return count


def generate_categories(conn):
    """Generate category records."""
    cursor = conn.cursor()

    # Main categories
    main_categories = [
        ("Fiction", "Imaginative literature"),
        ("Non-Fiction", "Factual literature"),
        ("Science", "Scientific topics"),
        ("History", "Historical accounts"),
        ("Biography", "Life stories"),
        ("Children", "Books for children"),
        ("Technology", "Technical subjects"),
        ("Art", "Art and design"),
        ("Philosophy", "Philosophical works"),
        ("Poetry", "Poetic works"),
    ]

    for name, description in main_categories:
        cursor.execute(
            "INSERT INTO categories (name, description) VALUES (?, ?)",
            (name, description)
        )

    # Add some subcategories
    subcategories = [
        ("Mystery", "Mystery and detective fiction", 1),  # Fiction
        ("Romance", "Romantic fiction", 1),
        ("Science Fiction", "Futuristic fiction", 1),
        ("Physics", "Physics topics", 3),  # Science
        ("Biology", "Biological sciences", 3),
        ("World War II", "WWII history", 4),  # History
    ]

    for name, description, parent_id in subcategories:
        cursor.execute(
            "INSERT INTO categories (name, description, parent_category_id) VALUES (?, ?, ?)",
            (name, description, parent_id)
        )

    conn.commit()
    return len(main_categories) + len(subcategories)


def generate_books(conn, author_count=100, count=500):
    """Generate book records."""
    cursor = conn.cursor()
    books = []

    languages = ["English", "Spanish", "French", "German", "Italian"]

    for _ in range(count):
        title = fake.sentence(nb_words=random.randint(2, 6)).rstrip('.')
        author_id = random.randint(1, author_count)
        isbn = fake.isbn13()
        published_year = random.randint(1950, 2024)
        category_id = random.randint(1, 16)  # Total categories
        pages = random.randint(100, 800)
        language = random.choice(languages)
        total_copies = random.randint(1, 5)
        available_copies = random.randint(0, total_copies)

        books.append((
            title, author_id, isbn, published_year, category_id,
            pages, language, available_copies, total_copies
        ))

    cursor.executemany(
        """INSERT INTO books
           (title, author_id, isbn, published_year, category_id, pages,
            language, available_copies, total_copies)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        books
    )
    conn.commit()
    return count


def generate_members(conn, count=200):
    """Generate library member records."""
    cursor = conn.cursor()
    members = []

    membership_types = ["standard", "premium", "student", "senior"]

    # Generate members who joined over the last 5 years
    end_date = datetime.now()
    start_date = end_date - timedelta(days=5*365)

    for _ in range(count):
        first_name = fake.first_name()
        last_name = fake.last_name()
        email = f"{first_name.lower()}.{last_name.lower()}@{fake.free_email_domain()}"
        phone = fake.phone_number()
        address = fake.address().replace('\n', ', ')
        joined_date = fake.date_between(start_date=start_date, end_date=end_date)
        membership_type = random.choice(membership_types)
        active = random.choice([True, True, True, False])  # 75% active

        members.append((
            first_name, last_name, email, phone, address,
            joined_date, membership_type, active
        ))

    cursor.executemany(
        """INSERT INTO members
           (first_name, last_name, email, phone, address, joined_date, membership_type, active)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        members
    )
    conn.commit()
    return count


def generate_loans(conn, book_count=500, member_count=200, count=1000):
    """Generate loan records with realistic patterns."""
    cursor = conn.cursor()
    loans = []

    end_date = datetime.now()
    start_date = end_date - timedelta(days=2*365)  # 2 years of loan history

    for _ in range(count):
        book_id = random.randint(1, book_count)
        member_id = random.randint(1, member_count)
        loan_date = fake.date_between(start_date=start_date, end_date=end_date)
        due_date = loan_date + timedelta(days=21)  # 3 week loan period

        # 70% returned, 20% active, 10% overdue
        status_roll = random.random()
        if status_roll < 0.70:
            status = "returned"
            return_date = loan_date + timedelta(days=random.randint(1, 25))
        elif status_roll < 0.90:
            status = "active"
            return_date = None
        else:
            status = "overdue"
            return_date = None

        renewed_count = random.randint(0, 2) if status in ["active", "overdue"] else 0

        loans.append((
            book_id, member_id, loan_date, due_date, return_date,
            renewed_count, status
        ))

    cursor.executemany(
        """INSERT INTO loans
           (book_id, member_id, loan_date, due_date, return_date, renewed_count, status)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        loans
    )
    conn.commit()
    return count


def main():
    """Generate the complete library database."""
    output_dir = Path(__file__).parent.parent / "databases"
    output_dir.mkdir(parents=True, exist_ok=True)
    db_path = output_dir / "library.db"

    # Remove existing database
    if db_path.exists():
        db_path.unlink()

    print(f"Generating library.db at {db_path}")

    conn = sqlite3.connect(db_path)

    try:
        print("Creating schema...")
        create_schema(conn)

        print("Generating authors...")
        author_count = generate_authors(conn, count=100)
        print(f"  ✓ Created {author_count} authors")

        print("Generating categories...")
        category_count = generate_categories(conn)
        print(f"  ✓ Created {category_count} categories")

        print("Generating books...")
        book_count = generate_books(conn, author_count=author_count, count=500)
        print(f"  ✓ Created {book_count} books")

        print("Generating members...")
        member_count = generate_members(conn, count=200)
        print(f"  ✓ Created {member_count} members")

        print("Generating loans...")
        loan_count = generate_loans(conn, book_count=book_count, member_count=member_count, count=1000)
        print(f"  ✓ Created {loan_count} loans")

        print(f"\n✓ Successfully generated library.db")
        print(f"  Location: {db_path}")
        print(f"  Size: {db_path.stat().st_size / 1024:.1f} KB")

    finally:
        conn.close()


if __name__ == "__main__":
    main()
