"""
Stage 1: Ingest

Load data.json, pick active/previous versions, strip bloat, write to var/
"""
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from utils import load_json, save_json, pick_versions, strip_runtime_bloat


def main():
    try:
        # Load source data
        data_path = Path(__file__).parent.parent.parent.parent / "docs" / "methodology" / "data.json"
        print(f"Loading: {data_path}")
        data = load_json(data_path)

        # Pick active and previous
        print("Picking active and previous catalogs...")
        current, previous = pick_versions(data)

        print(f"  Active: {current['program']['version']} ({current['program']['status']})")
        print(f"  Previous: {previous['program']['version']} ({previous['program']['status']})")

        # Strip runtime bloat
        print("Stripping _search_stemmed fields...")
        strip_runtime_bloat(current)
        strip_runtime_bloat(previous)

        # Write output
        var_dir = Path(__file__).parent.parent / "var"
        var_dir.mkdir(exist_ok=True)

        current_path = var_dir / "catalog.current.json"
        previous_path = var_dir / "catalog.previous.json"

        print(f"Writing: {current_path}")
        save_json(current_path, current)

        print(f"Writing: {previous_path}")
        save_json(previous_path, previous)

        print("[OK] Ingest complete")
        return 0

    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
