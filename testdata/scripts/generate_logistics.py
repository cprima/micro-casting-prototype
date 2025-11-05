#!/usr/bin/env python3
"""
Generate logistics.db - Comprehensive logistics, warehouse, and supply chain database.

Schema covers:
- Shipment tracking and freight management
- Warehouse and inventory operations
- Supply chain from supplier to retailer
- Multi-location stock management

Use cases: Complex queries, route optimization, inventory tracking, supply chain analytics
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
    """Create the logistics database schema."""
    cursor = conn.cursor()

    # Addresses table (shared by many entities)
    cursor.execute("""
        CREATE TABLE addresses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            street TEXT NOT NULL,
            city TEXT NOT NULL,
            state TEXT,
            postal_code TEXT,
            country TEXT NOT NULL,
            latitude DECIMAL(10, 8),
            longitude DECIMAL(11, 8),
            address_type TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Carriers table
    cursor.execute("""
        CREATE TABLE carriers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            carrier_code TEXT UNIQUE NOT NULL,
            carrier_type TEXT,
            contact_email TEXT,
            phone TEXT,
            active_status BOOLEAN DEFAULT 1,
            rating DECIMAL(3, 2),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Hubs / Distribution Centers
    cursor.execute("""
        CREATE TABLE hubs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            hub_code TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            address_id INTEGER NOT NULL,
            capacity INTEGER,
            operating_hours TEXT,
            hub_type TEXT,
            manager_name TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (address_id) REFERENCES addresses(id),
            CHECK (hub_type IN ('warehouse', 'distribution_center', 'sorting_facility', 'cross_dock'))
        )
    """)

    # Routes table
    cursor.execute("""
        CREATE TABLE routes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            route_code TEXT UNIQUE NOT NULL,
            origin_hub_id INTEGER NOT NULL,
            dest_hub_id INTEGER NOT NULL,
            distance_km DECIMAL(10, 2),
            avg_transit_days INTEGER,
            transportation_mode TEXT,
            active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (origin_hub_id) REFERENCES hubs(id),
            FOREIGN KEY (dest_hub_id) REFERENCES hubs(id),
            CHECK (transportation_mode IN ('truck', 'rail', 'air', 'sea', 'multimodal'))
        )
    """)

    # Shipments table
    cursor.execute("""
        CREATE TABLE shipments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tracking_number TEXT UNIQUE NOT NULL,
            origin_address_id INTEGER NOT NULL,
            dest_address_id INTEGER NOT NULL,
            carrier_id INTEGER,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            shipped_at TIMESTAMP,
            delivered_at TIMESTAMP,
            weight_kg DECIMAL(10, 3),
            volume_m3 DECIMAL(10, 3),
            declared_value DECIMAL(12, 2),
            priority TEXT DEFAULT 'standard',
            FOREIGN KEY (origin_address_id) REFERENCES addresses(id),
            FOREIGN KEY (dest_address_id) REFERENCES addresses(id),
            FOREIGN KEY (carrier_id) REFERENCES carriers(id),
            CHECK (status IN ('pending', 'in_transit', 'out_for_delivery', 'delivered', 'exception', 'returned')),
            CHECK (priority IN ('standard', 'express', 'overnight'))
        )
    """)

    # Shipment events (tracking history)
    cursor.execute("""
        CREATE TABLE shipment_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            shipment_id INTEGER NOT NULL,
            event_type TEXT NOT NULL,
            location_id INTEGER,
            timestamp TIMESTAMP NOT NULL,
            description TEXT,
            scanned_by TEXT,
            FOREIGN KEY (shipment_id) REFERENCES shipments(id),
            FOREIGN KEY (location_id) REFERENCES addresses(id)
        )
    """)

    # Freight items (what's in the shipment)
    cursor.execute("""
        CREATE TABLE freight_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            shipment_id INTEGER NOT NULL,
            description TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            weight_kg DECIMAL(10, 3),
            dimensions TEXT,
            hs_code TEXT,
            insured_value DECIMAL(12, 2),
            FOREIGN KEY (shipment_id) REFERENCES shipments(id)
        )
    """)

    # Warehouses table
    cursor.execute("""
        CREATE TABLE warehouses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            warehouse_code TEXT UNIQUE NOT NULL,
            address_id INTEGER NOT NULL,
            manager_id INTEGER,
            capacity_sqm INTEGER,
            total_zones INTEGER,
            temperature_controlled BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (address_id) REFERENCES addresses(id)
        )
    """)

    # Zones within warehouses
    cursor.execute("""
        CREATE TABLE zones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            warehouse_id INTEGER NOT NULL,
            zone_code TEXT NOT NULL,
            zone_type TEXT,
            capacity_units INTEGER,
            temperature_min DECIMAL(5, 2),
            temperature_max DECIMAL(5, 2),
            FOREIGN KEY (warehouse_id) REFERENCES warehouses(id),
            UNIQUE(warehouse_id, zone_code)
        )
    """)

    # Products table
    cursor.execute("""
        CREATE TABLE products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sku TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            description TEXT,
            unit_of_measure TEXT DEFAULT 'each',
            weight_kg DECIMAL(10, 3),
            requires_refrigeration BOOLEAN DEFAULT 0,
            hazmat_class TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Inventory table
    cursor.execute("""
        CREATE TABLE inventory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            warehouse_id INTEGER NOT NULL,
            zone_id INTEGER,
            quantity_on_hand INTEGER DEFAULT 0,
            quantity_reserved INTEGER DEFAULT 0,
            quantity_available INTEGER DEFAULT 0,
            reorder_point INTEGER DEFAULT 0,
            last_count_date DATE,
            bin_location TEXT,
            FOREIGN KEY (product_id) REFERENCES products(id),
            FOREIGN KEY (warehouse_id) REFERENCES warehouses(id),
            FOREIGN KEY (zone_id) REFERENCES zones(id),
            UNIQUE(product_id, warehouse_id, zone_id)
        )
    """)

    # Stock movements
    cursor.execute("""
        CREATE TABLE stock_movements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            from_warehouse_id INTEGER,
            to_warehouse_id INTEGER,
            from_zone_id INTEGER,
            to_zone_id INTEGER,
            quantity INTEGER NOT NULL,
            movement_type TEXT NOT NULL,
            reason TEXT,
            reference_id INTEGER,
            moved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            moved_by TEXT,
            FOREIGN KEY (product_id) REFERENCES products(id),
            FOREIGN KEY (from_warehouse_id) REFERENCES warehouses(id),
            FOREIGN KEY (to_warehouse_id) REFERENCES warehouses(id),
            CHECK (movement_type IN ('transfer', 'adjustment', 'receipt', 'shipment', 'return'))
        )
    """)

    # Suppliers table
    cursor.execute("""
        CREATE TABLE suppliers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            supplier_code TEXT UNIQUE NOT NULL,
            contact_name TEXT,
            email TEXT,
            phone TEXT,
            address_id INTEGER,
            payment_terms TEXT,
            lead_time_days INTEGER,
            rating DECIMAL(3, 2),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (address_id) REFERENCES addresses(id)
        )
    """)

    # Purchase orders
    cursor.execute("""
        CREATE TABLE purchase_orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            po_number TEXT UNIQUE NOT NULL,
            supplier_id INTEGER NOT NULL,
            order_date DATE NOT NULL,
            expected_delivery DATE,
            status TEXT DEFAULT 'draft',
            total_amount DECIMAL(12, 2),
            created_by TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (supplier_id) REFERENCES suppliers(id),
            CHECK (status IN ('draft', 'sent', 'acknowledged', 'in_transit', 'received', 'cancelled'))
        )
    """)

    # PO items
    cursor.execute("""
        CREATE TABLE po_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            po_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            quantity_ordered INTEGER NOT NULL,
            unit_cost DECIMAL(10, 2),
            quantity_received INTEGER DEFAULT 0,
            delivery_date DATE,
            FOREIGN KEY (po_id) REFERENCES purchase_orders(id),
            FOREIGN KEY (product_id) REFERENCES products(id)
        )
    """)

    # Retailers table
    cursor.execute("""
        CREATE TABLE retailers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            retailer_code TEXT UNIQUE NOT NULL,
            store_type TEXT,
            address_id INTEGER,
            contact_email TEXT,
            contact_phone TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (address_id) REFERENCES addresses(id)
        )
    """)

    # Create indexes
    cursor.execute("CREATE INDEX idx_shipments_tracking ON shipments(tracking_number)")
    cursor.execute("CREATE INDEX idx_shipments_status ON shipments(status)")
    cursor.execute("CREATE INDEX idx_shipment_events_shipment ON shipment_events(shipment_id)")
    cursor.execute("CREATE INDEX idx_inventory_product ON inventory(product_id)")
    cursor.execute("CREATE INDEX idx_inventory_warehouse ON inventory(warehouse_id)")
    cursor.execute("CREATE INDEX idx_stock_movements_product ON stock_movements(product_id)")
    cursor.execute("CREATE INDEX idx_po_supplier ON purchase_orders(supplier_id)")

    conn.commit()


def generate_addresses(conn, count=500):
    """Generate address records."""
    cursor = conn.cursor()
    addresses = []

    address_types = ["residential", "commercial", "warehouse", "distribution_center"]

    for _ in range(count):
        street = fake.street_address()
        city = fake.city()
        state = fake.state_abbr()
        postal_code = fake.postcode()
        country = fake.country_code()
        latitude = float(fake.latitude())
        longitude = float(fake.longitude())
        address_type = random.choice(address_types)

        addresses.append((
            street, city, state, postal_code, country,
            latitude, longitude, address_type
        ))

    cursor.executemany(
        """INSERT INTO addresses
           (street, city, state, postal_code, country, latitude, longitude, address_type)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        addresses
    )
    conn.commit()
    return count


def generate_carriers(conn, count=20):
    """Generate carrier records."""
    cursor = conn.cursor()
    carriers = []

    carrier_types = ["ground", "air", "sea", "rail", "courier"]
    carrier_names = ["FastShip", "QuickDeliver", "GlobalFreight", "ExpressAir", "RailCargo"]

    for i in range(count):
        name = f"{random.choice(carrier_names)} {fake.company_suffix()}"
        carrier_code = f"CAR-{i+1:03d}"
        carrier_type = random.choice(carrier_types)
        contact_email = fake.company_email()
        phone = fake.phone_number()
        active_status = random.choice([True, True, True, False])
        rating = round(random.uniform(3.0, 5.0), 2)

        carriers.append((
            name, carrier_code, carrier_type, contact_email,
            phone, active_status, rating
        ))

    cursor.executemany(
        """INSERT INTO carriers
           (name, carrier_code, carrier_type, contact_email, phone, active_status, rating)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        carriers
    )
    conn.commit()
    return count


def generate_hubs(conn, address_count=500, count=30):
    """Generate hub/distribution center records."""
    cursor = conn.cursor()
    hubs = []

    hub_types = ["warehouse", "distribution_center", "sorting_facility", "cross_dock"]

    for i in range(count):
        hub_code = f"HUB-{i+1:03d}"
        name = f"{fake.city()} {random.choice(hub_types).replace('_', ' ').title()}"
        address_id = random.randint(1, min(address_count, 100))  # Use first 100 addresses
        capacity = random.randint(5000, 50000)
        operating_hours = "24/7" if random.random() > 0.3 else "06:00-22:00"
        hub_type = random.choice(hub_types)
        manager_name = fake.name()

        hubs.append((
            hub_code, name, address_id, capacity, operating_hours, hub_type, manager_name
        ))

    cursor.executemany(
        """INSERT INTO hubs
           (hub_code, name, address_id, capacity, operating_hours, hub_type, manager_name)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        hubs
    )
    conn.commit()
    return count


def generate_routes(conn, hub_count=30, count=100):
    """Generate route records."""
    cursor = conn.cursor()
    routes = []

    transport_modes = ["truck", "rail", "air", "sea", "multimodal"]

    for i in range(count):
        route_code = f"RT-{i+1:04d}"
        origin_hub_id = random.randint(1, hub_count)
        dest_hub_id = random.randint(1, hub_count)

        # Avoid same origin and destination
        while dest_hub_id == origin_hub_id:
            dest_hub_id = random.randint(1, hub_count)

        distance_km = round(random.uniform(50, 5000), 2)
        avg_transit_days = max(1, int(distance_km / random.uniform(200, 500)))
        transportation_mode = random.choice(transport_modes)
        active = random.choice([True, True, True, False])

        routes.append((
            route_code, origin_hub_id, dest_hub_id, distance_km,
            avg_transit_days, transportation_mode, active
        ))

    cursor.executemany(
        """INSERT INTO routes
           (route_code, origin_hub_id, dest_hub_id, distance_km,
            avg_transit_days, transportation_mode, active)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        routes
    )
    conn.commit()
    return count


def generate_shipments(conn, address_count=500, carrier_count=20, count=2000):
    """Generate shipment records with tracking events."""
    cursor = conn.cursor()

    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)  # 1 year of shipments

    statuses = ["pending", "in_transit", "out_for_delivery", "delivered", "exception", "returned"]
    priorities = ["standard", "express", "overnight"]

    for i in range(count):
        tracking_number = f"TRK-{i+1:010d}"
        origin_address_id = random.randint(1, address_count)
        dest_address_id = random.randint(1, address_count)
        while dest_address_id == origin_address_id:
            dest_address_id = random.randint(1, address_count)

        carrier_id = random.randint(1, carrier_count)
        status = random.choice(statuses)
        priority = random.choice(priorities)

        created_at = fake.date_time_between(start_date=start_date, end_date=end_date)

        if status in ["delivered", "returned"]:
            shipped_at = created_at + timedelta(hours=random.randint(2, 48))
            delivered_at = shipped_at + timedelta(days=random.randint(1, 14))
        elif status in ["in_transit", "out_for_delivery", "exception"]:
            shipped_at = created_at + timedelta(hours=random.randint(2, 48))
            delivered_at = None
        else:
            shipped_at = None
            delivered_at = None

        weight_kg = round(random.uniform(0.5, 500), 3)
        volume_m3 = round(random.uniform(0.01, 10), 3)
        declared_value = round(random.uniform(10, 10000), 2)

        cursor.execute(
            """INSERT INTO shipments
               (tracking_number, origin_address_id, dest_address_id, carrier_id,
                status, created_at, shipped_at, delivered_at, weight_kg, volume_m3,
                declared_value, priority)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (tracking_number, origin_address_id, dest_address_id, carrier_id,
             status, created_at, shipped_at, delivered_at, weight_kg, volume_m3,
             declared_value, priority)
        )

        shipment_id = cursor.lastrowid

        # Generate tracking events
        event_types = ["picked_up", "arrived_at_hub", "departed_hub", "out_for_delivery", "delivered"]
        current_time = created_at

        num_events = random.randint(2, 6) if status == "delivered" else random.randint(1, 3)

        for _ in range(num_events):
            event_type = random.choice(event_types)
            current_time = current_time + timedelta(hours=random.randint(6, 48))
            location_id = random.randint(1, min(address_count, 100))
            description = fake.sentence()
            scanned_by = fake.name()

            cursor.execute(
                """INSERT INTO shipment_events
                   (shipment_id, event_type, location_id, timestamp, description, scanned_by)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (shipment_id, event_type, location_id, current_time, description, scanned_by)
            )

    conn.commit()
    return count


def generate_warehouses_and_zones(conn, address_count=500, warehouse_count=15):
    """Generate warehouse and zone records."""
    cursor = conn.cursor()

    for i in range(warehouse_count):
        name = f"{fake.city()} Distribution Center"
        warehouse_code = f"WH-{i+1:03d}"
        address_id = random.randint(1, min(address_count, 100))
        manager_id = random.randint(1000, 9999)
        capacity_sqm = random.randint(5000, 100000)
        total_zones = random.randint(4, 12)
        temperature_controlled = random.choice([True, False])

        cursor.execute(
            """INSERT INTO warehouses
               (name, warehouse_code, address_id, manager_id, capacity_sqm,
                total_zones, temperature_controlled)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (name, warehouse_code, address_id, manager_id, capacity_sqm,
             total_zones, temperature_controlled)
        )

        warehouse_id = cursor.lastrowid

        # Generate zones for this warehouse
        zone_types = ["receiving", "storage", "picking", "packing", "shipping"]

        for j in range(total_zones):
            zone_code = f"Z{j+1:02d}"
            zone_type = random.choice(zone_types)
            capacity_units = random.randint(500, 5000)
            temp_min = round(random.uniform(-20, 15), 2) if temperature_controlled else None
            temp_max = round(random.uniform(16, 25), 2) if temperature_controlled else None

            cursor.execute(
                """INSERT INTO zones
                   (warehouse_id, zone_code, zone_type, capacity_units,
                    temperature_min, temperature_max)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (warehouse_id, zone_code, zone_type, capacity_units, temp_min, temp_max)
            )

    conn.commit()
    return warehouse_count


def generate_products_and_inventory(conn, warehouse_count=15, product_count=200):
    """Generate products and inventory records."""
    cursor = conn.cursor()

    # Generate products
    products = []
    units = ["each", "case", "pallet", "box", "kg"]
    hazmat_classes = [None, None, None, "1", "3", "8", "9"]  # Mostly non-hazmat

    for i in range(product_count):
        sku = f"PROD-{i+1:05d}"
        name = f"{fake.word().title()} {fake.word().title()}"
        description = fake.text(max_nb_chars=150)
        unit_of_measure = random.choice(units)
        weight_kg = round(random.uniform(0.1, 100), 3)
        requires_refrigeration = random.choice([True, False])
        hazmat_class = random.choice(hazmat_classes)

        products.append((
            sku, name, description, unit_of_measure, weight_kg,
            requires_refrigeration, hazmat_class
        ))

    cursor.executemany(
        """INSERT INTO products
           (sku, name, description, unit_of_measure, weight_kg,
            requires_refrigeration, hazmat_class)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        products
    )

    # Generate inventory records (not all products in all warehouses)
    cursor.execute("SELECT id FROM zones")
    zone_ids = [row[0] for row in cursor.fetchall()]

    inventory_records = []

    for product_id in range(1, product_count + 1):
        # Each product in 1-5 warehouses
        num_warehouses = random.randint(1, min(5, warehouse_count))
        selected_warehouses = random.sample(range(1, warehouse_count + 1), num_warehouses)

        for warehouse_id in selected_warehouses:
            # Get zones for this warehouse
            cursor.execute("SELECT id FROM zones WHERE warehouse_id = ?", (warehouse_id,))
            wh_zones = [row[0] for row in cursor.fetchall()]

            if not wh_zones:
                continue

            zone_id = random.choice(wh_zones)
            quantity_on_hand = random.randint(0, 1000)
            quantity_reserved = random.randint(0, min(quantity_on_hand, 100))
            quantity_available = quantity_on_hand - quantity_reserved
            reorder_point = random.randint(10, 100)
            last_count_date = fake.date_between(start_date='-60d', end_date='today')
            bin_location = f"{random.choice(['A', 'B', 'C'])}{random.randint(1, 20):02d}-{random.randint(1, 50):02d}"

            inventory_records.append((
                product_id, warehouse_id, zone_id, quantity_on_hand,
                quantity_reserved, quantity_available, reorder_point,
                last_count_date, bin_location
            ))

    cursor.executemany(
        """INSERT INTO inventory
           (product_id, warehouse_id, zone_id, quantity_on_hand, quantity_reserved,
            quantity_available, reorder_point, last_count_date, bin_location)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        inventory_records
    )

    conn.commit()
    return product_count


def generate_suppliers_and_pos(conn, address_count=500, product_count=200, supplier_count=30, po_count=150):
    """Generate suppliers and purchase orders."""
    cursor = conn.cursor()

    # Generate suppliers
    suppliers = []
    for i in range(supplier_count):
        name = fake.company()
        supplier_code = f"SUP-{i+1:04d}"
        contact_name = fake.name()
        email = fake.company_email()
        phone = fake.phone_number()
        address_id = random.randint(1, min(address_count, 100))
        payment_terms = random.choice(["Net 30", "Net 60", "COD", "2/10 Net 30"])
        lead_time_days = random.randint(7, 90)
        rating = round(random.uniform(3.0, 5.0), 2)

        suppliers.append((
            name, supplier_code, contact_name, email, phone,
            address_id, payment_terms, lead_time_days, rating
        ))

    cursor.executemany(
        """INSERT INTO suppliers
           (name, supplier_code, contact_name, email, phone, address_id,
            payment_terms, lead_time_days, rating)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        suppliers
    )

    # Generate purchase orders
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)
    statuses = ["draft", "sent", "acknowledged", "in_transit", "received", "cancelled"]

    for i in range(po_count):
        po_number = f"PO-{i+1:06d}"
        supplier_id = random.randint(1, supplier_count)
        order_date = fake.date_between(start_date=start_date, end_date=end_date)
        expected_delivery = order_date + timedelta(days=random.randint(14, 60))
        status = random.choice(statuses)
        created_by = fake.name()

        cursor.execute(
            """INSERT INTO purchase_orders
               (po_number, supplier_id, order_date, expected_delivery, status, created_by)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (po_number, supplier_id, order_date, expected_delivery, status, created_by)
        )

        po_id = cursor.lastrowid

        # Generate PO items
        num_items = random.randint(1, 10)
        total_amount = 0

        for _ in range(num_items):
            product_id = random.randint(1, product_count)
            quantity_ordered = random.randint(10, 500)
            unit_cost = round(random.uniform(5, 500), 2)
            quantity_received = quantity_ordered if status == "received" else random.randint(0, quantity_ordered)
            delivery_date = expected_delivery if status == "received" else None

            total_amount += quantity_ordered * unit_cost

            cursor.execute(
                """INSERT INTO po_items
                   (po_id, product_id, quantity_ordered, unit_cost, quantity_received, delivery_date)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (po_id, product_id, quantity_ordered, unit_cost, quantity_received, delivery_date)
            )

        # Update PO total
        cursor.execute(
            "UPDATE purchase_orders SET total_amount = ? WHERE id = ?",
            (total_amount, po_id)
        )

    conn.commit()
    return supplier_count, po_count


def main():
    """Generate the complete logistics database."""
    output_dir = Path(__file__).parent.parent / "databases"
    output_dir.mkdir(parents=True, exist_ok=True)
    db_path = output_dir / "logistics.db"

    if db_path.exists():
        db_path.unlink()

    print(f"Generating logistics.db at {db_path}")

    conn = sqlite3.connect(db_path)

    try:
        print("Creating schema...")
        create_schema(conn)

        print("Generating addresses...")
        address_count = generate_addresses(conn, count=500)
        print(f"  ✓ Created {address_count} addresses")

        print("Generating carriers...")
        carrier_count = generate_carriers(conn, count=20)
        print(f"  ✓ Created {carrier_count} carriers")

        print("Generating hubs...")
        hub_count = generate_hubs(conn, address_count, count=30)
        print(f"  ✓ Created {hub_count} hubs")

        print("Generating routes...")
        route_count = generate_routes(conn, hub_count, count=100)
        print(f"  ✓ Created {route_count} routes")

        print("Generating shipments and tracking events...")
        shipment_count = generate_shipments(conn, address_count, carrier_count, count=2000)
        print(f"  ✓ Created {shipment_count} shipments")

        print("Generating warehouses and zones...")
        warehouse_count = generate_warehouses_and_zones(conn, address_count, warehouse_count=15)
        print(f"  ✓ Created {warehouse_count} warehouses")

        print("Generating products and inventory...")
        product_count = generate_products_and_inventory(conn, warehouse_count, product_count=200)
        print(f"  ✓ Created {product_count} products")

        print("Generating suppliers and purchase orders...")
        supplier_count, po_count = generate_suppliers_and_pos(conn, address_count, product_count, supplier_count=30, po_count=150)
        print(f"  ✓ Created {supplier_count} suppliers and {po_count} purchase orders")

        print(f"\n✓ Successfully generated logistics.db")
        print(f"  Location: {db_path}")
        print(f"  Size: {db_path.stat().st_size / 1024:.1f} KB")

    finally:
        conn.close()


if __name__ == "__main__":
    main()
