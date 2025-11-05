"""CLI for generating test databases."""

import sys
import argparse
from pathlib import Path


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Generate test databases for MCP servers"
    )
    parser.add_argument(
        "--database",
        choices=["library", "ecommerce", "logistics", "finance", "all"],
        default="all",
        help="Which database to generate"
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        help="Output directory for databases"
    )

    args = parser.parse_args()

    print(f"Generating {args.database} database(s)...")

    if args.database == "library" or args.database == "all":
        from mcp_testdata.generators import library
        library.main()
        print("✓ Generated library.db")

    # TODO: Add other databases
    if args.database == "ecommerce" or args.database == "all":
        print("⚠ ecommerce.db generator not yet implemented")

    if args.database == "logistics" or args.database == "all":
        print("⚠ logistics.db generator not yet implemented")

    if args.database == "finance" or args.database == "all":
        print("⚠ finance.db generator not yet implemented")

    print("\n✓ Database generation complete")
    return 0


if __name__ == "__main__":
    sys.exit(main())
