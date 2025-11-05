#!/usr/bin/env python3
"""
Generate finance.db - Comprehensive finance and accounting database.

Schema covers:
- Double-entry bookkeeping and chart of accounts
- Accounts receivable/payable and invoicing
- Bank accounts and transaction reconciliation
- Budget planning and variance analysis

Use cases: Ledger queries, trial balance, AR/AP aging, cash flow, budget analysis
"""

import sqlite3
import random
from datetime import datetime, timedelta
from pathlib import Path
from faker import Faker
from decimal import Decimal

fake = Faker()
Faker.seed(42)
random.seed(42)


def create_schema(conn):
    """Create the finance database schema."""
    cursor = conn.cursor()

    # Chart of Accounts
    cursor.execute("""
        CREATE TABLE accounts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            account_number TEXT UNIQUE NOT NULL,
            account_name TEXT NOT NULL,
            account_type TEXT NOT NULL,
            parent_account_id INTEGER,
            is_active BOOLEAN DEFAULT 1,
            normal_balance TEXT NOT NULL,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (parent_account_id) REFERENCES accounts(id),
            CHECK (account_type IN ('Asset', 'Liability', 'Equity', 'Revenue', 'Expense')),
            CHECK (normal_balance IN ('Debit', 'Credit'))
        )
    """)

    # Fiscal Periods
    cursor.execute("""
        CREATE TABLE fiscal_periods (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            period_name TEXT NOT NULL,
            start_date DATE NOT NULL,
            end_date DATE NOT NULL,
            fiscal_year INTEGER NOT NULL,
            period_status TEXT DEFAULT 'open',
            UNIQUE(fiscal_year, period_name),
            CHECK (period_status IN ('open', 'closed', 'locked'))
        )
    """)

    # Cost Centers / Departments
    cursor.execute("""
        CREATE TABLE cost_centers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            manager_name TEXT,
            budget_amount DECIMAL(15, 2),
            parent_cost_center_id INTEGER,
            is_active BOOLEAN DEFAULT 1,
            FOREIGN KEY (parent_cost_center_id) REFERENCES cost_centers(id)
        )
    """)

    # Journal Entries
    cursor.execute("""
        CREATE TABLE journal_entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            entry_number TEXT UNIQUE NOT NULL,
            entry_date DATE NOT NULL,
            fiscal_period_id INTEGER NOT NULL,
            description TEXT,
            reference_type TEXT,
            reference_id INTEGER,
            posted_by TEXT,
            posted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            reversed BOOLEAN DEFAULT 0,
            reversed_by_entry_id INTEGER,
            FOREIGN KEY (fiscal_period_id) REFERENCES fiscal_periods(id),
            FOREIGN KEY (reversed_by_entry_id) REFERENCES journal_entries(id)
        )
    """)

    # Journal Entry Lines (double-entry)
    cursor.execute("""
        CREATE TABLE journal_entry_lines (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            journal_entry_id INTEGER NOT NULL,
            line_number INTEGER NOT NULL,
            account_id INTEGER NOT NULL,
            cost_center_id INTEGER,
            debit_amount DECIMAL(15, 2) DEFAULT 0,
            credit_amount DECIMAL(15, 2) DEFAULT 0,
            description TEXT,
            FOREIGN KEY (journal_entry_id) REFERENCES journal_entries(id),
            FOREIGN KEY (account_id) REFERENCES accounts(id),
            FOREIGN KEY (cost_center_id) REFERENCES cost_centers(id),
            UNIQUE(journal_entry_id, line_number)
        )
    """)

    # Customers
    cursor.execute("""
        CREATE TABLE customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_code TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            billing_address TEXT,
            email TEXT,
            phone TEXT,
            payment_terms TEXT,
            credit_limit DECIMAL(12, 2),
            tax_id TEXT,
            currency_code TEXT DEFAULT 'USD',
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Vendors / Suppliers
    cursor.execute("""
        CREATE TABLE vendors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vendor_code TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            address TEXT,
            email TEXT,
            phone TEXT,
            payment_terms TEXT,
            tax_id TEXT,
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Invoices (AR)
    cursor.execute("""
        CREATE TABLE invoices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            invoice_number TEXT UNIQUE NOT NULL,
            invoice_type TEXT DEFAULT 'standard',
            customer_id INTEGER NOT NULL,
            invoice_date DATE NOT NULL,
            due_date DATE NOT NULL,
            subtotal DECIMAL(12, 2) NOT NULL,
            tax_amount DECIMAL(12, 2) DEFAULT 0,
            total_amount DECIMAL(12, 2) NOT NULL,
            amount_paid DECIMAL(12, 2) DEFAULT 0,
            amount_due DECIMAL(12, 2) NOT NULL,
            status TEXT DEFAULT 'draft',
            currency_code TEXT DEFAULT 'USD',
            exchange_rate DECIMAL(10, 6) DEFAULT 1,
            journal_entry_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (customer_id) REFERENCES customers(id),
            FOREIGN KEY (journal_entry_id) REFERENCES journal_entries(id),
            CHECK (invoice_type IN ('standard', 'credit_memo', 'debit_memo')),
            CHECK (status IN ('draft', 'sent', 'partial', 'paid', 'overdue', 'void'))
        )
    """)

    # Invoice Lines
    cursor.execute("""
        CREATE TABLE invoice_lines (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            invoice_id INTEGER NOT NULL,
            line_number INTEGER NOT NULL,
            description TEXT NOT NULL,
            quantity DECIMAL(10, 3) DEFAULT 1,
            unit_price DECIMAL(12, 2) NOT NULL,
            discount_percent DECIMAL(5, 2) DEFAULT 0,
            line_total DECIMAL(12, 2) NOT NULL,
            account_id INTEGER,
            FOREIGN KEY (invoice_id) REFERENCES invoices(id),
            FOREIGN KEY (account_id) REFERENCES accounts(id),
            UNIQUE(invoice_id, line_number)
        )
    """)

    # Bills (AP)
    cursor.execute("""
        CREATE TABLE bills (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            bill_number TEXT UNIQUE NOT NULL,
            vendor_id INTEGER NOT NULL,
            bill_date DATE NOT NULL,
            due_date DATE NOT NULL,
            subtotal DECIMAL(12, 2) NOT NULL,
            tax_amount DECIMAL(12, 2) DEFAULT 0,
            total_amount DECIMAL(12, 2) NOT NULL,
            amount_paid DECIMAL(12, 2) DEFAULT 0,
            amount_due DECIMAL(12, 2) NOT NULL,
            status TEXT DEFAULT 'draft',
            po_reference TEXT,
            journal_entry_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (vendor_id) REFERENCES vendors(id),
            FOREIGN KEY (journal_entry_id) REFERENCES journal_entries(id),
            CHECK (status IN ('draft', 'approved', 'partial', 'paid', 'overdue', 'void'))
        )
    """)

    # Bill Lines
    cursor.execute("""
        CREATE TABLE bill_lines (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            bill_id INTEGER NOT NULL,
            line_number INTEGER NOT NULL,
            description TEXT NOT NULL,
            quantity DECIMAL(10, 3) DEFAULT 1,
            unit_price DECIMAL(12, 2) NOT NULL,
            line_total DECIMAL(12, 2) NOT NULL,
            expense_account_id INTEGER,
            FOREIGN KEY (bill_id) REFERENCES bills(id),
            FOREIGN KEY (expense_account_id) REFERENCES accounts(id),
            UNIQUE(bill_id, line_number)
        )
    """)

    # Bank Accounts
    cursor.execute("""
        CREATE TABLE bank_accounts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            account_number TEXT UNIQUE NOT NULL,
            bank_name TEXT NOT NULL,
            account_type TEXT,
            currency_code TEXT DEFAULT 'USD',
            current_balance DECIMAL(15, 2) DEFAULT 0,
            gl_account_id INTEGER,
            is_active BOOLEAN DEFAULT 1,
            last_reconciled_date DATE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (gl_account_id) REFERENCES accounts(id),
            CHECK (account_type IN ('checking', 'savings', 'money_market', 'credit_line'))
        )
    """)

    # Bank Transactions
    cursor.execute("""
        CREATE TABLE bank_transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            bank_account_id INTEGER NOT NULL,
            transaction_date DATE NOT NULL,
            value_date DATE,
            description TEXT NOT NULL,
            reference_number TEXT,
            debit_amount DECIMAL(12, 2) DEFAULT 0,
            credit_amount DECIMAL(12, 2) DEFAULT 0,
            balance DECIMAL(15, 2),
            transaction_type TEXT,
            reconciled BOOLEAN DEFAULT 0,
            journal_entry_id INTEGER,
            imported_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (bank_account_id) REFERENCES bank_accounts(id),
            FOREIGN KEY (journal_entry_id) REFERENCES journal_entries(id)
        )
    """)

    # Payments
    cursor.execute("""
        CREATE TABLE payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            payment_number TEXT UNIQUE NOT NULL,
            payment_date DATE NOT NULL,
            payment_type TEXT NOT NULL,
            customer_id INTEGER,
            vendor_id INTEGER,
            amount DECIMAL(12, 2) NOT NULL,
            currency_code TEXT DEFAULT 'USD',
            reference_number TEXT,
            bank_account_id INTEGER,
            status TEXT DEFAULT 'pending',
            journal_entry_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (customer_id) REFERENCES customers(id),
            FOREIGN KEY (vendor_id) REFERENCES vendors(id),
            FOREIGN KEY (bank_account_id) REFERENCES bank_accounts(id),
            FOREIGN KEY (journal_entry_id) REFERENCES journal_entries(id),
            CHECK (payment_type IN ('customer_payment', 'vendor_payment', 'transfer')),
            CHECK (status IN ('pending', 'cleared', 'cancelled', 'returned'))
        )
    """)

    # Payment Applications (linking payments to invoices/bills)
    cursor.execute("""
        CREATE TABLE payment_applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            payment_id INTEGER NOT NULL,
            invoice_id INTEGER,
            bill_id INTEGER,
            amount_applied DECIMAL(12, 2) NOT NULL,
            application_date DATE NOT NULL,
            FOREIGN KEY (payment_id) REFERENCES payments(id),
            FOREIGN KEY (invoice_id) REFERENCES invoices(id),
            FOREIGN KEY (bill_id) REFERENCES bills(id)
        )
    """)

    # Budget Versions
    cursor.execute("""
        CREATE TABLE budget_versions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            version_name TEXT NOT NULL,
            fiscal_year INTEGER NOT NULL,
            status TEXT DEFAULT 'draft',
            created_by TEXT,
            approved_by TEXT,
            approved_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(fiscal_year, version_name),
            CHECK (status IN ('draft', 'submitted', 'approved', 'active', 'closed'))
        )
    """)

    # Budget Lines
    cursor.execute("""
        CREATE TABLE budget_lines (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            budget_version_id INTEGER NOT NULL,
            account_id INTEGER NOT NULL,
            cost_center_id INTEGER,
            period_id INTEGER NOT NULL,
            budgeted_amount DECIMAL(15, 2) NOT NULL,
            notes TEXT,
            FOREIGN KEY (budget_version_id) REFERENCES budget_versions(id),
            FOREIGN KEY (account_id) REFERENCES accounts(id),
            FOREIGN KEY (cost_center_id) REFERENCES cost_centers(id),
            FOREIGN KEY (period_id) REFERENCES fiscal_periods(id)
        )
    """)

    # Create indexes
    cursor.execute("CREATE INDEX idx_accounts_type ON accounts(account_type)")
    cursor.execute("CREATE INDEX idx_journal_entries_date ON journal_entries(entry_date)")
    cursor.execute("CREATE INDEX idx_journal_entry_lines_account ON journal_entry_lines(account_id)")
    cursor.execute("CREATE INDEX idx_journal_entry_lines_je ON journal_entry_lines(journal_entry_id)")
    cursor.execute("CREATE INDEX idx_invoices_customer ON invoices(customer_id)")
    cursor.execute("CREATE INDEX idx_invoices_status ON invoices(status)")
    cursor.execute("CREATE INDEX idx_bills_vendor ON bills(vendor_id)")
    cursor.execute("CREATE INDEX idx_bank_trans_account ON bank_transactions(bank_account_id)")
    cursor.execute("CREATE INDEX idx_payments_customer ON payments(customer_id)")
    cursor.execute("CREATE INDEX idx_payments_vendor ON payments(vendor_id)")

    conn.commit()


def generate_chart_of_accounts(conn):
    """Generate a realistic chart of accounts."""
    cursor = conn.cursor()

    accounts = [
        # Assets
        ("1000", "Assets", "Asset", None, "Debit", "All company assets"),
        ("1100", "Current Assets", "Asset", 1, "Debit", "Assets convertible to cash within 1 year"),
        ("1110", "Cash and Cash Equivalents", "Asset", 2, "Debit", "Cash accounts"),
        ("1120", "Accounts Receivable", "Asset", 2, "Debit", "Money owed by customers"),
        ("1130", "Inventory", "Asset", 2, "Debit", "Goods for sale"),
        ("1140", "Prepaid Expenses", "Asset", 2, "Debit", "Prepaid costs"),
        ("1200", "Fixed Assets", "Asset", 1, "Debit", "Long-term assets"),
        ("1210", "Property, Plant & Equipment", "Asset", 7, "Debit", "Physical assets"),
        ("1220", "Accumulated Depreciation", "Asset", 7, "Credit", "Contra-asset account"),

        # Liabilities
        ("2000", "Liabilities", "Liability", None, "Credit", "All company liabilities"),
        ("2100", "Current Liabilities", "Liability", 10, "Credit", "Due within 1 year"),
        ("2110", "Accounts Payable", "Liability", 11, "Credit", "Money owed to vendors"),
        ("2120", "Accrued Expenses", "Liability", 11, "Credit", "Expenses incurred but not paid"),
        ("2130", "Sales Tax Payable", "Liability", 11, "Credit", "Sales tax collected"),
        ("2200", "Long-term Liabilities", "Liability", 10, "Credit", "Due after 1 year"),
        ("2210", "Long-term Debt", "Liability", 15, "Credit", "Loans and bonds"),

        # Equity
        ("3000", "Equity", "Equity", None, "Credit", "Owner's equity"),
        ("3100", "Common Stock", "Equity", 17, "Credit", "Shareholder equity"),
        ("3200", "Retained Earnings", "Equity", 17, "Credit", "Accumulated profits"),
        ("3300", "Current Year Earnings", "Equity", 17, "Credit", "Current period net income"),

        # Revenue
        ("4000", "Revenue", "Revenue", None, "Credit", "All income"),
        ("4100", "Sales Revenue", "Revenue", 21, "Credit", "Product sales"),
        ("4200", "Service Revenue", "Revenue", 21, "Credit", "Services provided"),
        ("4300", "Interest Income", "Revenue", 21, "Credit", "Interest earned"),

        # Expenses
        ("5000", "Cost of Goods Sold", "Expense", None, "Debit", "Direct costs"),
        ("5100", "Materials", "Expense", 25, "Debit", "Raw materials cost"),
        ("5200", "Labor", "Expense", 25, "Debit", "Direct labor costs"),

        ("6000", "Operating Expenses", "Expense", None, "Debit", "Operating costs"),
        ("6100", "Salaries and Wages", "Expense", 28, "Debit", "Employee compensation"),
        ("6200", "Rent Expense", "Expense", 28, "Debit", "Facility rent"),
        ("6300", "Utilities", "Expense", 28, "Debit", "Electricity, water, etc."),
        ("6400", "Marketing and Advertising", "Expense", 28, "Debit", "Marketing costs"),
        ("6500", "Professional Fees", "Expense", 28, "Debit", "Legal, accounting fees"),
        ("6600", "Insurance", "Expense", 28, "Debit", "Insurance premiums"),
        ("6700", "Depreciation Expense", "Expense", 28, "Debit", "Asset depreciation"),
    ]

    account_map = {}

    for acc_num, acc_name, acc_type, parent_idx, normal_bal, desc in accounts:
        parent_id = account_map.get(parent_idx) if parent_idx else None

        cursor.execute(
            """INSERT INTO accounts
               (account_number, account_name, account_type, parent_account_id, normal_balance, description)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (acc_num, acc_name, acc_type, parent_id, normal_bal, desc)
        )

        account_map[len(account_map) + 1] = cursor.lastrowid

    conn.commit()
    return len(accounts)


def generate_fiscal_periods(conn, years=3):
    """Generate fiscal periods for multiple years."""
    cursor = conn.cursor()

    current_year = datetime.now().year
    periods_created = 0

    for year_offset in range(-years + 1, 2):  # Past 2 years + current year + next year
        fiscal_year = current_year + year_offset

        for month in range(1, 13):
            month_name = datetime(fiscal_year, month, 1).strftime("%B")
            period_name = f"{month_name} {fiscal_year}"

            # Calculate start and end dates
            start_date = datetime(fiscal_year, month, 1).date()

            if month == 12:
                end_date = datetime(fiscal_year, 12, 31).date()
            else:
                end_date = (datetime(fiscal_year, month + 1, 1) - timedelta(days=1)).date()

            # Past periods are closed
            if fiscal_year < current_year or (fiscal_year == current_year and month < datetime.now().month):
                status = "closed"
            else:
                status = "open"

            cursor.execute(
                """INSERT INTO fiscal_periods
                   (period_name, start_date, end_date, fiscal_year, period_status)
                   VALUES (?, ?, ?, ?, ?)""",
                (period_name, start_date, end_date, fiscal_year, status)
            )
            periods_created += 1

    conn.commit()
    return periods_created


def generate_cost_centers(conn):
    """Generate cost centers/departments."""
    cursor = conn.cursor()

    cost_centers = [
        ("CC-100", "Corporate", "CEO", 500000),
        ("CC-200", "Sales", "Sales VP", 800000),
        ("CC-210", "Sales North", "Regional Manager", 400000),
        ("CC-220", "Sales South", "Regional Manager", 400000),
        ("CC-300", "Marketing", "CMO", 600000),
        ("CC-400", "Engineering", "CTO", 1200000),
        ("CC-410", "Product Development", "Director", 700000),
        ("CC-420", "Infrastructure", "Director", 500000),
        ("CC-500", "Operations", "COO", 400000),
        ("CC-600", "Finance", "CFO", 300000),
        ("CC-700", "Human Resources", "HR Director", 250000),
    ]

    parent_map = {
        "CC-210": "CC-200",
        "CC-220": "CC-200",
        "CC-410": "CC-400",
        "CC-420": "CC-400",
    }

    code_to_id = {}

    for code, name, manager, budget in cost_centers:
        parent_code = parent_map.get(code)
        parent_id = code_to_id.get(parent_code) if parent_code else None

        cursor.execute(
            """INSERT INTO cost_centers
               (code, name, manager_name, budget_amount, parent_cost_center_id)
               VALUES (?, ?, ?, ?, ?)""",
            (code, name, manager, budget, parent_id)
        )

        code_to_id[code] = cursor.lastrowid

    conn.commit()
    return len(cost_centers)


def generate_customers_and_vendors(conn, customer_count=100, vendor_count=50):
    """Generate customers and vendors."""
    cursor = conn.cursor()

    # Generate customers
    payment_terms = ["Net 30", "Net 60", "Net 15", "Due on Receipt", "2/10 Net 30"]

    customers = []
    for i in range(customer_count):
        customer_code = f"CUST-{i+1:05d}"
        name = fake.company()
        billing_address = fake.address().replace('\n', ', ')
        email = fake.company_email()
        phone = fake.phone_number()
        terms = random.choice(payment_terms)
        credit_limit = round(random.uniform(5000, 100000), 2)
        tax_id = fake.ssn()

        customers.append((
            customer_code, name, billing_address, email, phone, terms, credit_limit, tax_id
        ))

    cursor.executemany(
        """INSERT INTO customers
           (customer_code, name, billing_address, email, phone, payment_terms, credit_limit, tax_id)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        customers
    )

    # Generate vendors
    vendors = []
    for i in range(vendor_count):
        vendor_code = f"VEND-{i+1:05d}"
        name = fake.company()
        address = fake.address().replace('\n', ', ')
        email = fake.company_email()
        phone = fake.phone_number()
        terms = random.choice(payment_terms)
        tax_id = fake.ssn()

        vendors.append((
            vendor_code, name, address, email, phone, terms, tax_id
        ))

    cursor.executemany(
        """INSERT INTO vendors
           (vendor_code, name, address, email, phone, payment_terms, tax_id)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        vendors
    )

    conn.commit()
    return customer_count, vendor_count


def generate_invoices_and_payments(conn, customer_count=100, invoice_count=500):
    """Generate invoices with linked journal entries and payments."""
    cursor = conn.cursor()

    # Get AR and Revenue account IDs
    cursor.execute("SELECT id FROM accounts WHERE account_number = '1120'")  # AR
    ar_account_id = cursor.fetchone()[0]

    cursor.execute("SELECT id FROM accounts WHERE account_number = '4100'")  # Revenue
    revenue_account_id = cursor.fetchone()[0]

    # Get periods
    cursor.execute("SELECT id, start_date, end_date FROM fiscal_periods WHERE period_status = 'closed' ORDER BY start_date")
    periods = cursor.fetchall()

    end_date = datetime.now()
    start_date = end_date - timedelta(days=2*365)

    statuses = ["sent", "partial", "paid", "overdue"]
    status_weights = [15, 10, 60, 15]

    for i in range(invoice_count):
        invoice_number = f"INV-{i+1:07d}"
        customer_id = random.randint(1, customer_count)
        invoice_date = fake.date_between(start_date=start_date, end_date=end_date)
        due_date = invoice_date + timedelta(days=30)

        # Generate line items
        num_lines = random.randint(1, 5)
        subtotal = 0

        for line_num in range(1, num_lines + 1):
            description = fake.bs().title()
            quantity = random.randint(1, 20)
            unit_price = round(random.uniform(50, 500), 2)
            line_total = quantity * unit_price
            subtotal += line_total

        tax_rate = 0.08
        tax_amount = round(subtotal * tax_rate, 2)
        total_amount = subtotal + tax_amount

        status = random.choices(statuses, weights=status_weights)[0]

        if status == "paid":
            amount_paid = total_amount
            amount_due = 0
        elif status == "partial":
            amount_paid = round(total_amount * random.uniform(0.3, 0.7), 2)
            amount_due = total_amount - amount_paid
        else:
            amount_paid = 0
            amount_due = total_amount

        # Create journal entry for invoice
        cursor.execute(
            "SELECT id FROM fiscal_periods WHERE ? BETWEEN start_date AND end_date",
            (invoice_date,)
        )
        period_result = cursor.fetchone()
        period_id = period_result[0] if period_result else periods[0][0]

        entry_number = f"JE-INV-{i+1:07d}"

        cursor.execute(
            """INSERT INTO journal_entries
               (entry_number, entry_date, fiscal_period_id, description, reference_type, reference_id, posted_by)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (entry_number, invoice_date, period_id, f"Invoice {invoice_number}", "invoice", i+1, "System")
        )
        je_id = cursor.lastrowid

        # Debit AR, Credit Revenue
        cursor.execute(
            """INSERT INTO journal_entry_lines
               (journal_entry_id, line_number, account_id, debit_amount, credit_amount, description)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (je_id, 1, ar_account_id, total_amount, 0, f"AR - {invoice_number}")
        )

        cursor.execute(
            """INSERT INTO journal_entry_lines
               (journal_entry_id, line_number, account_id, debit_amount, credit_amount, description)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (je_id, 2, revenue_account_id, 0, total_amount, f"Revenue - {invoice_number}")
        )

        # Insert invoice
        cursor.execute(
            """INSERT INTO invoices
               (invoice_number, customer_id, invoice_date, due_date, subtotal,
                tax_amount, total_amount, amount_paid, amount_due, status, journal_entry_id)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (invoice_number, customer_id, invoice_date, due_date, subtotal,
             tax_amount, total_amount, amount_paid, amount_due, status, je_id)
        )

        invoice_id = cursor.lastrowid

        # Insert invoice lines
        subtotal_check = 0
        for line_num in range(1, num_lines + 1):
            description = fake.bs().title()
            quantity = random.randint(1, 20)
            unit_price = round(random.uniform(50, 500), 2)
            line_total = quantity * unit_price
            subtotal_check += line_total

            cursor.execute(
                """INSERT INTO invoice_lines
                   (invoice_id, line_number, description, quantity, unit_price, line_total, account_id)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (invoice_id, line_num, description, quantity, unit_price, line_total, revenue_account_id)
            )

    conn.commit()
    return invoice_count


def generate_bank_accounts_and_transactions(conn, count=5, transaction_count=1000):
    """Generate bank accounts and transactions."""
    cursor = conn.cursor()

    # Get cash account
    cursor.execute("SELECT id FROM accounts WHERE account_number = '1110'")
    cash_account_id = cursor.fetchone()[0]

    bank_names = ["Chase", "Bank of America", "Wells Fargo", "Citibank", "US Bank"]
    account_types = ["checking", "savings"]

    for i in range(count):
        account_number = fake.bban()
        bank_name = random.choice(bank_names)
        account_type = random.choice(account_types)
        current_balance = round(random.uniform(10000, 500000), 2)

        cursor.execute(
            """INSERT INTO bank_accounts
               (account_number, bank_name, account_type, current_balance, gl_account_id)
               VALUES (?, ?, ?, ?, ?)""",
            (account_number, bank_name, account_type, current_balance, cash_account_id)
        )

    # Generate transactions
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)

    transaction_types = ["deposit", "withdrawal", "transfer", "fee", "interest"]

    for _ in range(transaction_count):
        bank_account_id = random.randint(1, count)
        transaction_date = fake.date_between(start_date=start_date, end_date=end_date)
        description = fake.sentence(nb_words=5)
        reference_number = fake.bothify(text="CHK-#####")
        transaction_type = random.choice(transaction_types)

        if transaction_type in ["deposit", "interest"]:
            debit_amount = 0
            credit_amount = round(random.uniform(100, 5000), 2)
        else:
            debit_amount = round(random.uniform(50, 2000), 2)
            credit_amount = 0

        reconciled = random.choice([True, True, False])  # 66% reconciled

        cursor.execute(
            """INSERT INTO bank_transactions
               (bank_account_id, transaction_date, description, reference_number,
                debit_amount, credit_amount, transaction_type, reconciled)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (bank_account_id, transaction_date, description, reference_number,
             debit_amount, credit_amount, transaction_type, reconciled)
        )

    conn.commit()
    return count, transaction_count


def main():
    """Generate the complete finance database."""
    output_dir = Path(__file__).parent.parent / "databases"
    output_dir.mkdir(parents=True, exist_ok=True)
    db_path = output_dir / "finance.db"

    if db_path.exists():
        db_path.unlink()

    print(f"Generating finance.db at {db_path}")

    conn = sqlite3.connect(db_path)

    try:
        print("Creating schema...")
        create_schema(conn)

        print("Generating chart of accounts...")
        account_count = generate_chart_of_accounts(conn)
        print(f"  ✓ Created {account_count} accounts")

        print("Generating fiscal periods...")
        period_count = generate_fiscal_periods(conn, years=3)
        print(f"  ✓ Created {period_count} fiscal periods")

        print("Generating cost centers...")
        cc_count = generate_cost_centers(conn)
        print(f"  ✓ Created {cc_count} cost centers")

        print("Generating customers and vendors...")
        customer_count, vendor_count = generate_customers_and_vendors(conn, customer_count=100, vendor_count=50)
        print(f"  ✓ Created {customer_count} customers and {vendor_count} vendors")

        print("Generating invoices with journal entries...")
        invoice_count = generate_invoices_and_payments(conn, customer_count, invoice_count=500)
        print(f"  ✓ Created {invoice_count} invoices")

        print("Generating bank accounts and transactions...")
        bank_count, transaction_count = generate_bank_accounts_and_transactions(conn, count=5, transaction_count=1000)
        print(f"  ✓ Created {bank_count} bank accounts and {transaction_count} transactions")

        print(f"\n✓ Successfully generated finance.db")
        print(f"  Location: {db_path}")
        print(f"  Size: {db_path.stat().st_size / 1024:.1f} KB")

    finally:
        conn.close()


if __name__ == "__main__":
    main()
