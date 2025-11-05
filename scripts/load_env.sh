#!/bin/bash
# Load MCP environment variables from .env file

ENV_FILE="$(dirname "$0")/../.env"

if [ -f "$ENV_FILE" ]; then
    export $(grep -v '^#' "$ENV_FILE" | xargs)
    echo "✓ MCP environment loaded from .env"
    echo "  GITHUB_REPO: $GITHUB_REPO"
    echo "  GITHUB_BRANCH: $GITHUB_BRANCH"
    echo "  GITHUB_PAT: ${GITHUB_PAT:0:20}..."
else
    echo "✗ .env file not found. Copy .env.example to .env and configure it."
    exit 1
fi
