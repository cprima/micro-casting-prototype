#!/usr/bin/env python
"""
Enhance methodology data.json with Porter-stemmed search text.

Adds a _search_stemmed field to each decision node containing stemmed versions
of searchable text (title, summary, why, tags). This enables fuzzy search where
"auth" matches "authentication", "implement" matches "implementation", etc.

Usage:
    uv run python tools/stem-methodology-search.py
"""

import json
import re
from pathlib import Path
from nltk.stem import PorterStemmer


def extract_searchable_text(node):
    """Extract all searchable text from a node."""
    parts = []

    # Title and summary
    if node.get('title'):
        parts.append(node['title'])
    if node.get('summary'):
        parts.append(node['summary'])
    if node.get('why'):
        parts.append(node['why'])

    # Tags
    if node.get('tags'):
        parts.extend(node['tags'])

    # Combine all parts
    return ' '.join(parts)


def stem_text(text, stemmer):
    """Apply Porter stemmer to all words in text."""
    # Convert to lowercase
    text = text.lower()

    # Extract words (alphanumeric only)
    words = re.findall(r'\w+', text)

    # Stem each word
    stemmed_words = [stemmer.stem(word) for word in words]

    # Join with spaces and return
    return ' '.join(stemmed_words)


def enhance_data_with_stems(data_path):
    """Add _search_stemmed field to all nodes in data.json."""
    # Read data
    with open(data_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Initialize stemmer
    stemmer = PorterStemmer()

    # Process each phase
    total_nodes = 0
    for phase in data.get('phases', []):
        for node in phase.get('nodes', []):
            # Extract searchable text
            searchable = extract_searchable_text(node)

            # Apply stemming
            stemmed = stem_text(searchable, stemmer)

            # Add to node
            node['_search_stemmed'] = stemmed

            total_nodes += 1
            print(f"[OK] {node.get('id', 'unknown')}: {len(stemmed.split())} stemmed words")

    # Write back to file
    with open(data_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"\n[SUCCESS] Enhanced {total_nodes} nodes with stemmed search text")
    print(f"[FILE] Updated: {data_path}")


def main():
    """Main entry point."""
    # Path to data.json
    project_root = Path(__file__).parent.parent
    data_path = project_root / 'docs' / 'methodology' / 'data.json'

    if not data_path.exists():
        print(f"[ERROR] File not found: {data_path}")
        return 1

    print(f"[INFO] Reading: {data_path}")
    enhance_data_with_stems(data_path)

    return 0


if __name__ == '__main__':
    exit(main())
