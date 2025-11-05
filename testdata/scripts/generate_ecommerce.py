#!/usr/bin/env python3
"""
Generate ecommerce.db - An e-commerce database with medium complexity.

Schema:
- categories: Hierarchical product categories
- products: Product catalog
- customers: Customer accounts
- orders: Customer orders
- order_items: Line items in orders
- reviews: Product reviews
- inventory_log: Stock movement history

Use cases: Complex JOINs, aggregations, time-series analysis, hierarchical data
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
    """Create the ecommerce database schema."""
    cursor = conn.cursor()

    # Categories table (hierarchical)
    cursor.execute("""
        CREATE TABLE categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            slug TEXT NOT NULL UNIQUE,
            parent_id INTEGER,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (parent_id) REFERENCES categories(id)
        )
    """)

    # Products table
    cursor.execute("""
        CREATE TABLE products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            sku TEXT UNIQUE NOT NULL,
            description TEXT,
            price DECIMAL(10, 2) NOT NULL,
            cost DECIMAL(10, 2),
            stock_quantity INTEGER DEFAULT 0,
            category_id INTEGER,
            weight_kg DECIMAL(8, 3),
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (category_id) REFERENCES categories(id)
        )
    """)

    # Customers table
    cursor.execute("""
        CREATE TABLE customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            phone TEXT,
            address TEXT,
            city TEXT,
            state TEXT,
            postal_code TEXT,
            country TEXT DEFAULT 'USA',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP
        )
    """)

    # Orders table
    cursor.execute("""
        CREATE TABLE orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER NOT NULL,
            order_number TEXT UNIQUE NOT NULL,
            order_date TIMESTAMP NOT NULL,
            status TEXT DEFAULT 'pending',
            subtotal DECIMAL(10, 2) NOT NULL,
            tax_amount DECIMAL(10, 2) DEFAULT 0,
            shipping_amount DECIMAL(10, 2) DEFAULT 0,
            total_amount DECIMAL(10, 2) NOT NULL,
            shipping_address TEXT,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (customer_id) REFERENCES customers(id),
            CHECK (status IN ('pending', 'processing', 'shipped', 'delivered', 'cancelled'))
        )
    """)

    # Order items table
    cursor.execute("""
        CREATE TABLE order_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            unit_price DECIMAL(10, 2) NOT NULL,
            line_total DECIMAL(10, 2) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (order_id) REFERENCES orders(id),
            FOREIGN KEY (product_id) REFERENCES products(id)
        )
    """)

    # Reviews table
    cursor.execute("""
        CREATE TABLE reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            customer_id INTEGER NOT NULL,
            rating INTEGER NOT NULL,
            title TEXT,
            comment TEXT,
            helpful_count INTEGER DEFAULT 0,
            verified_purchase BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (product_id) REFERENCES products(id),
            FOREIGN KEY (customer_id) REFERENCES customers(id),
            CHECK (rating >= 1 AND rating <= 5)
        )
    """)

    # Inventory log table
    cursor.execute("""
        CREATE TABLE inventory_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            change_qty INTEGER NOT NULL,
            reason TEXT,
            reference_type TEXT,
            reference_id INTEGER,
            notes TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (product_id) REFERENCES products(id)
        )
    """)

    # Create indexes
    cursor.execute("CREATE INDEX idx_products_category ON products(category_id)")
    cursor.execute("CREATE INDEX idx_products_sku ON products(sku)")
    cursor.execute("CREATE INDEX idx_orders_customer ON orders(customer_id)")
    cursor.execute("CREATE INDEX idx_orders_status ON orders(status)")
    cursor.execute("CREATE INDEX idx_orders_date ON orders(order_date)")
    cursor.execute("CREATE INDEX idx_order_items_order ON order_items(order_id)")
    cursor.execute("CREATE INDEX idx_order_items_product ON order_items(product_id)")
    cursor.execute("CREATE INDEX idx_reviews_product ON reviews(product_id)")
    cursor.execute("CREATE INDEX idx_inventory_log_product ON inventory_log(product_id)")

    conn.commit()


def generate_categories(conn):
    """Generate hierarchical category structure."""
    cursor = conn.cursor()

    # Root categories
    root_categories = [
        ("Electronics", "electronics", "Electronic devices and accessories"),
        ("Clothing", "clothing", "Apparel and fashion"),
        ("Home & Garden", "home-garden", "Home improvement and garden supplies"),
        ("Books", "books", "Books and media"),
        ("Sports", "sports", "Sports and outdoor equipment"),
    ]

    category_ids = {}
    for name, slug, desc in root_categories:
        cursor.execute(
            "INSERT INTO categories (name, slug, description) VALUES (?, ?, ?)",
            (name, slug, desc)
        )
        category_ids[name] = cursor.lastrowid

    # Subcategories
    subcategories = [
        ("Laptops", "laptops", "Laptop computers", "Electronics"),
        ("Smartphones", "smartphones", "Mobile phones", "Electronics"),
        ("Headphones", "headphones", "Audio devices", "Electronics"),
        ("Men's Clothing", "mens-clothing", "Men's apparel", "Clothing"),
        ("Women's Clothing", "womens-clothing", "Women's apparel", "Clothing"),
        ("Shoes", "shoes", "Footwear", "Clothing"),
        ("Furniture", "furniture", "Home furniture", "Home & Garden"),
        ("Kitchen", "kitchen", "Kitchen supplies", "Home & Garden"),
        ("Fiction", "fiction", "Fiction books", "Books"),
        ("Non-Fiction", "non-fiction", "Non-fiction books", "Books"),
        ("Fitness", "fitness", "Fitness equipment", "Sports"),
        ("Camping", "camping", "Camping gear", "Sports"),
    ]

    for name, slug, desc, parent_name in subcategories:
        parent_id = category_ids[parent_name]
        cursor.execute(
            "INSERT INTO categories (name, slug, description, parent_id) VALUES (?, ?, ?, ?)",
            (name, slug, desc, parent_id)
        )

    conn.commit()
    return len(root_categories) + len(subcategories)


def generate_products(conn, count=300):
    """Generate product catalog."""
    cursor = conn.cursor()
    products = []

    product_templates = [
        ("Laptop", "Electronics", 800, 1500),
        ("Smartphone", "Electronics", 300, 1200),
        ("Headphones", "Electronics", 20, 300),
        ("T-Shirt", "Clothing", 10, 50),
        ("Jeans", "Clothing", 30, 100),
        ("Sneakers", "Clothing", 40, 150),
        ("Chair", "Home & Garden", 50, 300),
        ("Desk", "Home & Garden", 100, 500),
        ("Blender", "Home & Garden", 30, 150),
        ("Novel", "Books", 10, 30),
        ("Textbook", "Books", 40, 150),
        ("Dumbbells", "Sports", 20, 100),
        ("Tent", "Sports", 100, 400),
    ]

    for i in range(count):
        template_name, category, min_price, max_price = random.choice(product_templates)

        name = f"{fake.word().title()} {template_name} {fake.color_name()}"
        sku = f"SKU-{i+1:05d}"
        description = fake.text(max_nb_chars=200)
        price = round(random.uniform(min_price, max_price), 2)
        cost = round(price * random.uniform(0.4, 0.7), 2)
        stock_quantity = random.randint(0, 200)

        # Get category_id (simplified - use category name range)
        category_id = random.randint(1, 17)  # Total categories

        weight_kg = round(random.uniform(0.1, 20), 3)
        is_active = random.choice([True, True, True, False])  # 75% active

        products.append((
            name, sku, description, price, cost, stock_quantity,
            category_id, weight_kg, is_active
        ))

    cursor.executemany(
        """INSERT INTO products
           (name, sku, description, price, cost, stock_quantity, category_id, weight_kg, is_active)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        products
    )
    conn.commit()
    return count


def generate_customers(conn, count=500):
    """Generate customer records."""
    cursor = conn.cursor()
    customers = []

    end_date = datetime.now()
    start_date = end_date - timedelta(days=3*365)  # 3 years

    for _ in range(count):
        first_name = fake.first_name()
        last_name = fake.last_name()
        email = f"{first_name.lower()}.{last_name.lower()}@{fake.free_email_domain()}"
        phone = fake.phone_number()
        address = fake.street_address()
        city = fake.city()
        state = fake.state_abbr()
        postal_code = fake.postcode()
        country = "USA"
        created_at = fake.date_time_between(start_date=start_date, end_date=end_date)
        last_login = fake.date_time_between(start_date=created_at, end_date=end_date)

        customers.append((
            first_name, last_name, email, phone, address, city,
            state, postal_code, country, created_at, last_login
        ))

    cursor.executemany(
        """INSERT INTO customers
           (first_name, last_name, email, phone, address, city, state,
            postal_code, country, created_at, last_login)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        customers
    )
    conn.commit()
    return count


def generate_orders(conn, customer_count=500, product_count=300, order_count=1500):
    """Generate orders and order items."""
    cursor = conn.cursor()

    end_date = datetime.now()
    start_date = end_date - timedelta(days=2*365)  # 2 years of orders

    statuses = ["pending", "processing", "shipped", "delivered", "cancelled"]
    status_weights = [5, 10, 15, 60, 10]  # Mostly delivered

    # Get product prices
    cursor.execute("SELECT id, price FROM products")
    product_prices = dict(cursor.fetchall())

    for order_num in range(1, order_count + 1):
        customer_id = random.randint(1, customer_count)
        order_number = f"ORD-{order_num:07d}"
        order_date = fake.date_time_between(start_date=start_date, end_date=end_date)
        status = random.choices(statuses, weights=status_weights)[0]

        # Generate 1-5 order items
        num_items = random.randint(1, 5)
        order_items = []
        subtotal = 0

        for _ in range(num_items):
            product_id = random.randint(1, product_count)
            if product_id not in product_prices:
                continue

            quantity = random.randint(1, 3)
            unit_price = product_prices[product_id]
            line_total = quantity * unit_price
            subtotal += line_total

            order_items.append((product_id, quantity, unit_price, line_total))

        if not order_items:
            continue

        # Calculate totals
        tax_rate = 0.08  # 8% tax
        tax_amount = round(subtotal * tax_rate, 2)
        shipping_amount = round(random.uniform(0, 15), 2) if subtotal < 50 else 0
        total_amount = subtotal + tax_amount + shipping_amount

        shipping_address = fake.address().replace('\n', ', ')

        # Insert order
        cursor.execute(
            """INSERT INTO orders
               (customer_id, order_number, order_date, status, subtotal,
                tax_amount, shipping_amount, total_amount, shipping_address)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (customer_id, order_number, order_date, status, subtotal,
             tax_amount, shipping_amount, total_amount, shipping_address)
        )
        order_id = cursor.lastrowid

        # Insert order items
        for product_id, quantity, unit_price, line_total in order_items:
            cursor.execute(
                """INSERT INTO order_items
                   (order_id, product_id, quantity, unit_price, line_total)
                   VALUES (?, ?, ?, ?, ?)""",
                (order_id, product_id, quantity, unit_price, line_total)
            )

    conn.commit()
    return order_count


def generate_reviews(conn, product_count=300, customer_count=500, count=800):
    """Generate product reviews."""
    cursor = conn.cursor()
    reviews = []

    end_date = datetime.now()
    start_date = end_date - timedelta(days=2*365)

    # Rating distribution: skewed toward positive
    rating_choices = [1, 2, 3, 4, 5]
    rating_weights = [5, 5, 10, 30, 50]  # Mostly 4-5 stars

    for _ in range(count):
        product_id = random.randint(1, product_count)
        customer_id = random.randint(1, customer_count)
        rating = random.choices(rating_choices, weights=rating_weights)[0]
        title = fake.sentence(nb_words=5).rstrip('.')
        comment = fake.text(max_nb_chars=300) if random.random() > 0.3 else None
        helpful_count = random.randint(0, 50)
        verified_purchase = random.choice([True, False])
        created_at = fake.date_time_between(start_date=start_date, end_date=end_date)

        reviews.append((
            product_id, customer_id, rating, title, comment,
            helpful_count, verified_purchase, created_at
        ))

    cursor.executemany(
        """INSERT INTO reviews
           (product_id, customer_id, rating, title, comment,
            helpful_count, verified_purchase, created_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        reviews
    )
    conn.commit()
    return count


def generate_inventory_log(conn, product_count=300, count=1000):
    """Generate inventory movement history."""
    cursor = conn.cursor()
    logs = []

    end_date = datetime.now()
    start_date = end_date - timedelta(days=2*365)

    reasons = ["purchase", "sale", "return", "adjustment", "damage", "restock"]
    reference_types = ["order", "purchase_order", "manual", "return"]

    for _ in range(count):
        product_id = random.randint(1, product_count)
        reason = random.choice(reasons)

        # Negative for sales/damage, positive for purchase/return
        if reason in ["sale", "damage"]:
            change_qty = -random.randint(1, 10)
        else:
            change_qty = random.randint(1, 50)

        reference_type = random.choice(reference_types)
        reference_id = random.randint(1, 1000)
        notes = fake.sentence() if random.random() > 0.7 else None
        timestamp = fake.date_time_between(start_date=start_date, end_date=end_date)

        logs.append((
            product_id, change_qty, reason, reference_type,
            reference_id, notes, timestamp
        ))

    cursor.executemany(
        """INSERT INTO inventory_log
           (product_id, change_qty, reason, reference_type, reference_id, notes, timestamp)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        logs
    )
    conn.commit()
    return count


def main():
    """Generate the complete ecommerce database."""
    output_dir = Path(__file__).parent.parent / "databases"
    output_dir.mkdir(parents=True, exist_ok=True)
    db_path = output_dir / "ecommerce.db"

    if db_path.exists():
        db_path.unlink()

    print(f"Generating ecommerce.db at {db_path}")

    conn = sqlite3.connect(db_path)

    try:
        print("Creating schema...")
        create_schema(conn)

        print("Generating categories...")
        category_count = generate_categories(conn)
        print(f"  ✓ Created {category_count} categories")

        print("Generating products...")
        product_count = generate_products(conn, count=300)
        print(f"  ✓ Created {product_count} products")

        print("Generating customers...")
        customer_count = generate_customers(conn, count=500)
        print(f"  ✓ Created {customer_count} customers")

        print("Generating orders and order items...")
        order_count = generate_orders(conn, customer_count, product_count, order_count=1500)
        print(f"  ✓ Created {order_count} orders")

        print("Generating reviews...")
        review_count = generate_reviews(conn, product_count, customer_count, count=800)
        print(f"  ✓ Created {review_count} reviews")

        print("Generating inventory log...")
        log_count = generate_inventory_log(conn, product_count, count=1000)
        print(f"  ✓ Created {log_count} inventory log entries")

        print(f"\n✓ Successfully generated ecommerce.db")
        print(f"  Location: {db_path}")
        print(f"  Size: {db_path.stat().st_size / 1024:.1f} KB")

    finally:
        conn.close()


if __name__ == "__main__":
    main()
