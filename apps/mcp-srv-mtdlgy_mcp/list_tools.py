"""
List all tools available in the MCP server.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from server import mcp, load_data

# Load server data
load_data()

# Get tool registry from FastMCP
print("=" * 60)
print("MCP Server Tools")
print("=" * 60)
print()

# FastMCP stores tools in the _tools attribute
if hasattr(mcp, '_tools'):
    tools = mcp._tools
    print(f"Total tools: {len(tools)}\n")

    for i, (name, tool_info) in enumerate(tools.items(), 1):
        print(f"{i}. {name}")

        # Get function object
        if hasattr(tool_info, 'fn'):
            fn = tool_info.fn
            # Get docstring
            if fn.__doc__:
                lines = fn.__doc__.strip().split('\n')
                description = lines[0] if lines else "No description"
                print(f"   Description: {description}")

            # Get annotations
            if hasattr(tool_info, 'annotations'):
                annotations = tool_info.annotations
                print(f"   Annotations: readOnly={annotations.get('readOnlyHint')}, "
                      f"destructive={annotations.get('destructiveHint')}, "
                      f"idempotent={annotations.get('idempotentHint')}, "
                      f"openWorld={annotations.get('openWorldHint')}")

        print()
else:
    print("Unable to access tool registry")

print("=" * 60)
