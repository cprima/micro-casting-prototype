#!/usr/bin/env python3
"""
Generate all test databases for MCP server blueprints.

This script orchestrates the generation of all test databases:
- library.db: Simple library management system
- ecommerce.db: E-commerce platform with orders and reviews
- logistics.db: Comprehensive logistics, warehouse, and supply chain
- finance.db: Complete finance and accounting system

Usage:
    python seed_all.py              # Generate all databases
    python seed_all.py --only library   # Generate only library.db
    python seed_all.py --skip finance   # Skip finance.db
"""

import sys
import time
import argparse
from pathlib import Path

# Import individual generators
import generate_library
import generate_ecommerce
import generate_logistics
import generate_finance


GENERATORS = {
    "library": {
        "module": generate_library,
        "description": "Simple library management database",
        "complexity": "Beginner",
    },
    "ecommerce": {
        "module": generate_ecommerce,
        "description": "E-commerce database with hierarchical categories",
        "complexity": "Medium",
    },
    "logistics": {
        "module": generate_logistics,
        "description": "Comprehensive logistics and supply chain database",
        "complexity": "Advanced",
    },
    "finance": {
        "module": generate_finance,
        "description": "Complete finance and accounting database",
        "complexity": "Advanced",
    },
}


def print_banner():
    """Print a welcome banner."""
    banner = """
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║         MCP Test Database Generator                           ║
║         Creating realistic test data for MCP servers          ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
"""
    print(banner)


def print_summary():
    """Print a summary of available databases."""
    print("\nAvailable databases:\n")
    for name, info in GENERATORS.items():
        print(f"  • {name:12s} - {info['description']}")
        print(f"    {'':12s}   Complexity: {info['complexity']}")
    print()


def generate_database(name: str) -> tuple[bool, float]:
    """
    Generate a single database.

    Args:
        name: Database name (e.g., 'library', 'ecommerce')

    Returns:
        Tuple of (success: bool, duration: float)
    """
    if name not in GENERATORS:
        print(f"❌ Error: Unknown database '{name}'")
        return False, 0

    info = GENERATORS[name]
    module = info["module"]

    print(f"\n{'='*70}")
    print(f"Generating {name}.db...")
    print(f"Description: {info['description']}")
    print(f"Complexity: {info['complexity']}")
    print(f"{'='*70}")

    start_time = time.time()

    try:
        module.main()
        duration = time.time() - start_time
        print(f"\n✓ {name}.db generated successfully in {duration:.2f}s")
        return True, duration

    except Exception as e:
        duration = time.time() - start_time
        print(f"\n❌ Error generating {name}.db: {e}")
        import traceback
        traceback.print_exc()
        return False, duration


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Generate test databases for MCP server blueprints"
    )
    parser.add_argument(
        "--only",
        metavar="DB",
        choices=list(GENERATORS.keys()),
        help="Generate only the specified database"
    )
    parser.add_argument(
        "--skip",
        metavar="DB",
        action="append",
        help="Skip the specified database (can be used multiple times)"
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List available databases and exit"
    )

    args = parser.parse_args()

    print_banner()

    if args.list:
        print_summary()
        return 0

    # Determine which databases to generate
    if args.only:
        databases_to_generate = [args.only]
    else:
        databases_to_generate = list(GENERATORS.keys())
        if args.skip:
            databases_to_generate = [db for db in databases_to_generate if db not in args.skip]

    if not databases_to_generate:
        print("No databases to generate.")
        return 0

    print(f"Generating {len(databases_to_generate)} database(s): {', '.join(databases_to_generate)}")

    # Generate databases
    results = {}
    total_start = time.time()

    for db_name in databases_to_generate:
        success, duration = generate_database(db_name)
        results[db_name] = {"success": success, "duration": duration}

    total_duration = time.time() - total_start

    # Print summary
    print(f"\n{'='*70}")
    print("GENERATION SUMMARY")
    print(f"{'='*70}")

    success_count = sum(1 for r in results.values() if r["success"])
    fail_count = len(results) - success_count

    for db_name, result in results.items():
        status = "✓" if result["success"] else "❌"
        print(f"  {status} {db_name:12s} - {result['duration']:.2f}s")

    print(f"\n{'='*70}")
    print(f"Total: {success_count} succeeded, {fail_count} failed")
    print(f"Total time: {total_duration:.2f}s")
    print(f"{'='*70}")

    # Check output directory
    output_dir = Path(__file__).parent.parent / "databases"
    if output_dir.exists():
        db_files = list(output_dir.glob("*.db"))
        if db_files:
            print(f"\nGenerated databases in: {output_dir}")
            total_size = sum(f.stat().st_size for f in db_files)
            print(f"Total size: {total_size / 1024:.1f} KB")
            print(f"\nFiles:")
            for db_file in sorted(db_files):
                size_kb = db_file.stat().st_size / 1024
                print(f"  • {db_file.name:20s} {size_kb:>8.1f} KB")

    return 0 if fail_count == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
