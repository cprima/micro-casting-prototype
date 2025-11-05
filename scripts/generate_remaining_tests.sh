#!/bin/bash
# Generate all remaining test suites efficiently

cd /home/user/micro-casting-prototype/apps

# Function to create test file and add dev deps
create_test_suite() {
    local server_name=$1
    local test_content=$2
    
    if [ ! -d "$server_name" ]; then
        echo "⚠️  $server_name not found"
        return
    fi
    
    echo "$test_content" > "$server_name/test_server.py"
    
    # Add dev-dependencies if not present
    if ! grep -q "dev-dependencies" "$server_name/pyproject.toml"; then
        cat >> "$server_name/pyproject.toml" << 'PYEOF'

[tool.uv]
dev-dependencies = [
    "pytest>=7.0.0",
    "pytest-asyncio>=0.21.0",
    "pytest-cov>=4.0.0",
]
PYEOF
    fi
    
    echo "✓ Created $server_name/test_server.py"
}

echo "=============================================="
echo "CREATING REMAINING 13 TEST SUITES"
echo "=============================================="
echo

# I'll create comprehensive test templates that work for all remaining servers
# Since this is getting long, let me run the script generation in Python instead

