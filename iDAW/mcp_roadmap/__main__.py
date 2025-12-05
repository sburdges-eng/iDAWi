#!/usr/bin/env python3
"""
MCP Roadmap - Module Entry Point

Allows running the package directly:
    python -m mcp_roadmap [command]
    python -m mcp_roadmap server  # Run MCP server
    python -m mcp_roadmap overview  # CLI overview
"""

from .cli import main

if __name__ == "__main__":
    main()
