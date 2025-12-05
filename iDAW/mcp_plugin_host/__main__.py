#!/usr/bin/env python3
"""
MCP Plugin Host - Main Entry Point

Run with:
    python -m mcp_plugin_host        # Start MCP server
    python -m mcp_plugin_host --cli  # Run CLI
"""

import sys


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--cli":
        # Remove --cli from args and run CLI
        sys.argv = [sys.argv[0]] + sys.argv[2:]
        from .cli import main as cli_main
        cli_main()
    else:
        # Run MCP server
        from .server import main as server_main
        server_main()


if __name__ == "__main__":
    main()
