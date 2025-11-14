"""
MCP Core - Foundation patterns for building MCP servers.

This library provides reusable components and patterns for building
Model Context Protocol (MCP) servers, including:
- Basic server setup utilities
- Common tool patterns (hello, echo)
- Parameter validation helpers
- Response formatting utilities
"""

from mcp_core.hello import create_hello_tool, hello_handler
from mcp_core.echo import create_echo_tools, echo_handler, echo_structured_handler

__version__ = "0.1.0"

__all__ = [
    "create_hello_tool",
    "hello_handler",
    "create_echo_tools",
    "echo_handler",
    "echo_structured_handler",
]
