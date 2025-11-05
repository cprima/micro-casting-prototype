# MCP Environment Setup

This document explains how to set up your development environment for the MCP server monorepo.

## Quick Start

1. **Copy the example environment file:**
   ```bash
   cp .env.example .env
   ```

2. **Configure your credentials:**
   Edit `.env` and add your GitHub Personal Access Token:
   ```bash
   GITHUB_PAT=your_token_here
   ```

3. **Load environment variables:**
   ```bash
   source scripts/load_env.sh
   ```

## Environment Variables

The `.env` file contains:

| Variable | Description | Example |
|----------|-------------|---------|
| `GITHUB_PAT` | GitHub Personal Access Token for repository operations | `github_pat_...` |
| `GITHUB_REPO` | Repository name | `cprima/micro-casting-prototype` |
| `GITHUB_BRANCH` | Current working branch | `claude/mcp-server-...` |
| `PYTHON_VERSION` | Python version to use | `3.11` |
| `UV_PYTHON_PREFERENCE` | uv Python preference | `only-managed` |

## Getting a GitHub PAT

1. Go to GitHub Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Click "Generate new token (classic)"
3. Give it a descriptive name (e.g., "MCP Monorepo Development")
4. Select scopes:
   - `repo` (Full control of private repositories)
5. Click "Generate token"
6. Copy the token and add it to your `.env` file

**Important**: Never commit the `.env` file to git! It's already in `.gitignore`.

## Using the Environment

### In Scripts

Load environment variables at the beginning of your script:

```bash
#!/bin/bash
source scripts/load_env.sh

# Now you can use the variables
git push https://${GITHUB_PAT}@github.com/${GITHUB_REPO}.git ${GITHUB_BRANCH}
```

### In Python

Use python-dotenv or load manually:

```python
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Access variables
github_pat = os.getenv('GITHUB_PAT')
repo = os.getenv('GITHUB_REPO')
```

### Manual Loading

```bash
# Load environment
cd /path/to/micro-casting-prototype
export $(grep -v '^#' .env | xargs)

# Verify
echo $GITHUB_REPO
```

## Security Best Practices

1. **Never commit `.env`** - It's in `.gitignore`, but always double-check
2. **Use environment-specific files** - `.env.development`, `.env.production`
3. **Rotate tokens regularly** - Update your PAT periodically
4. **Minimal permissions** - Only grant necessary scopes to tokens
5. **Backup safely** - Store credentials in a password manager

## Troubleshooting

### Environment not loading

```bash
# Check if .env exists
ls -la .env

# Check if .gitignore includes .env
grep "\.env" .gitignore

# Manually source
source .env
```

### Git push fails with authentication error

```bash
# Check if PAT is loaded
echo ${GITHUB_PAT:0:20}...

# Reload environment
source scripts/load_env.sh

# Try push again
git push https://${GITHUB_PAT}@github.com/${GITHUB_REPO}.git
```

### Permission denied on load_env.sh

```bash
# Make it executable
chmod +x scripts/load_env.sh
```

## Files

- `.env` - Your local environment configuration (NOT committed)
- `.env.example` - Template for environment configuration (committed)
- `scripts/load_env.sh` - Helper script to load environment variables

## See Also

- [GitHub PAT Documentation](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token)
- [uv Documentation](https://github.com/astral-sh/uv)
- [python-dotenv Documentation](https://github.com/theskumar/python-dotenv)
