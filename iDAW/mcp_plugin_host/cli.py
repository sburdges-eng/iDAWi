#!/usr/bin/env python3
"""
MCP Plugin Host - CLI Interface

Command-line interface for plugin management.

Usage:
    mcp-plugin-host-cli scan [--format vst3] [--path /custom/path]
    mcp-plugin-host-cli list [--format vst3] [--type effect] [--favorites]
    mcp-plugin-host-cli search <query>
    mcp-plugin-host-cli info <plugin_id>
    mcp-plugin-host-cli builtin
    mcp-plugin-host-cli summary
"""

import argparse
import json
import sys
from typing import Optional

from .storage import PluginStorage
from .scanner import PluginScanner, PluginProfiler
from .models import (
    PluginFormat, PluginType, PluginCategory,
    get_builtin_plugin_specs,
)


def cmd_scan(args, storage: PluginStorage):
    """Scan for plugins."""
    scanner = PluginScanner(storage)

    formats = None
    if args.format:
        formats = [PluginFormat(args.format)]

    paths = None
    if args.path:
        paths = [args.path]

    print("Scanning for plugins...")

    def progress_callback(progress: float, count: int):
        print(f"\rProgress: {progress*100:.1f}% ({count} plugins found)", end="", flush=True)

    plugins = scanner.scan_sync(paths, formats, progress_callback)

    print(f"\n\nScan complete! Found {len(plugins)} plugins:")
    print("-" * 60)

    for plugin in plugins[:20]:  # Show first 20
        print(f"  [{plugin.format.value.upper():5}] {plugin.name}")

    if len(plugins) > 20:
        print(f"  ... and {len(plugins) - 20} more")


def cmd_list(args, storage: PluginStorage):
    """List plugins."""
    fmt = PluginFormat(args.format) if args.format else None
    ptype = PluginType(args.type) if args.type else None
    cat = PluginCategory(args.category) if args.category else None

    plugins = storage.list_plugins(
        format=fmt,
        plugin_type=ptype,
        category=cat,
        favorites_only=args.favorites,
        recently_used=args.recent,
    )

    if not plugins:
        print("No plugins found matching criteria.")
        return

    print(f"Found {len(plugins)} plugins:")
    print("-" * 70)

    for plugin in plugins:
        fav = "*" if plugin.is_favorite else " "
        print(f"  {fav} [{plugin.format.value.upper():7}] {plugin.name:30} ({plugin.vendor})")


def cmd_search(args, storage: PluginStorage):
    """Search for plugins."""
    plugins = storage.search_plugins(args.query, limit=args.limit)

    if not plugins:
        print(f"No plugins found matching '{args.query}'")
        return

    print(f"Found {len(plugins)} plugins matching '{args.query}':")
    print("-" * 70)

    for plugin in plugins:
        print(f"  [{plugin.format.value.upper():7}] {plugin.name:30} - {plugin.vendor}")
        if plugin.description:
            print(f"           {plugin.description[:60]}...")


def cmd_info(args, storage: PluginStorage):
    """Get plugin info."""
    plugin = storage.get_plugin(args.plugin_id)

    if not plugin:
        print(f"Plugin not found: {args.plugin_id}")
        return

    print(f"\nPlugin: {plugin.name}")
    print("=" * 50)
    print(f"  ID:          {plugin.id}")
    print(f"  Vendor:      {plugin.vendor}")
    print(f"  Version:     {plugin.version}")
    print(f"  Format:      {plugin.format.value.upper()}")
    print(f"  Type:        {plugin.plugin_type.value}")
    print(f"  Category:    {plugin.category.value}")
    print(f"  Path:        {plugin.path}")
    print(f"  Status:      {plugin.status.value}")
    print(f"  Favorite:    {'Yes' if plugin.is_favorite else 'No'}")
    print(f"  Use count:   {plugin.use_count}")
    print(f"  Last used:   {plugin.last_used or 'Never'}")

    if plugin.tags:
        print(f"  Tags:        {', '.join(plugin.tags)}")

    if plugin.description:
        print(f"\nDescription:\n  {plugin.description}")


def cmd_builtin(args, storage: PluginStorage):
    """List built-in art-themed plugins."""
    specs = get_builtin_plugin_specs()

    print("\niDAWi Built-in Art-Themed Plugins")
    print("=" * 60)

    # Group by priority
    high = [s for s in specs if s.priority == "high"]
    medium = [s for s in specs if s.priority == "medium"]
    low = [s for s in specs if s.priority == "low"]

    for priority, group, label in [
        ("HIGH", high, "Core Effects"),
        ("MEDIUM", medium, "Creative Tools"),
        ("LOW", low, "Extended Suite"),
    ]:
        if group:
            print(f"\n{label} ({priority} priority):")
            print("-" * 40)
            for spec in group:
                print(f"  {spec.name:10} - {spec.theme:15} | {spec.description[:40]}...")


def cmd_summary(args, storage: PluginStorage):
    """Get database summary."""
    summary = storage.get_summary()

    print("\nPlugin Database Summary")
    print("=" * 50)
    print(f"  Total plugins:     {summary['total_plugins']}")
    print(f"  Favorites:         {summary['favorites']}")
    print(f"  Blacklisted:       {summary['blacklisted']}")
    print(f"  Last scan:         {summary['last_scan'] or 'Never'}")

    print("\nBy Format:")
    for fmt, count in summary.get("by_format", {}).items():
        print(f"    {fmt.upper():10} {count}")

    print("\nBy Type:")
    for ptype, count in summary.get("by_type", {}).items():
        print(f"    {ptype:15} {count}")


def cmd_blacklist(args, storage: PluginStorage):
    """Manage blacklist."""
    if args.add:
        storage.blacklist_plugin(args.add, args.reason or "")
        print(f"Added to blacklist: {args.add}")
    elif args.remove:
        storage.unblacklist_plugin(args.remove)
        print(f"Removed from blacklist: {args.remove}")
    else:
        blacklist = storage.get_blacklist()
        if not blacklist:
            print("Blacklist is empty.")
        else:
            print("\nBlacklisted Plugins:")
            print("-" * 50)
            for item in blacklist:
                reason = f" - {item['reason']}" if item['reason'] else ""
                print(f"  {item['plugin_id']}{reason}")


def cmd_paths(args, storage: PluginStorage):
    """Manage scan paths."""
    scanner = PluginScanner(storage)

    if args.add:
        storage.add_scan_path(args.add)
        print(f"Added scan path: {args.add}")
    elif args.remove:
        storage.remove_scan_path(args.remove)
        print(f"Removed scan path: {args.remove}")
    else:
        custom = storage.get_scan_paths()
        system = scanner.get_system_plugin_paths()

        print("\nPlugin Scan Paths")
        print("=" * 50)

        print("\nSystem paths:")
        for fmt, paths in system.items():
            print(f"  {fmt.upper()}:")
            for path in paths:
                print(f"    {path}")

        if custom:
            print("\nCustom paths:")
            for path in custom:
                print(f"    {path}")


def main():
    """CLI main entry point."""
    parser = argparse.ArgumentParser(
        description="iDAWi MCP Plugin Host CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    %(prog)s scan                    # Scan for all plugins
    %(prog)s scan --format vst3      # Scan only VST3 plugins
    %(prog)s list --type instrument  # List instrument plugins
    %(prog)s search "compressor"     # Search for compressor plugins
    %(prog)s builtin                 # List built-in art-themed plugins
        """
    )

    parser.add_argument(
        "--storage-dir",
        help="Storage directory (default: ~/.mcp_plugin_host/)",
        default=None
    )

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # scan command
    scan_parser = subparsers.add_parser("scan", help="Scan for plugins")
    scan_parser.add_argument("--format", choices=["vst3", "au", "lv2", "clap"])
    scan_parser.add_argument("--path", help="Custom scan path")

    # list command
    list_parser = subparsers.add_parser("list", help="List plugins")
    list_parser.add_argument("--format", choices=["vst3", "au", "lv2", "clap", "builtin"])
    list_parser.add_argument("--type", choices=["effect", "instrument", "midi_effect", "analyzer"])
    list_parser.add_argument("--category")
    list_parser.add_argument("--favorites", action="store_true")
    list_parser.add_argument("--recent", action="store_true")

    # search command
    search_parser = subparsers.add_parser("search", help="Search plugins")
    search_parser.add_argument("query", help="Search query")
    search_parser.add_argument("--limit", type=int, default=20)

    # info command
    info_parser = subparsers.add_parser("info", help="Get plugin info")
    info_parser.add_argument("plugin_id", help="Plugin ID")

    # builtin command
    subparsers.add_parser("builtin", help="List built-in plugins")

    # summary command
    subparsers.add_parser("summary", help="Database summary")

    # blacklist command
    bl_parser = subparsers.add_parser("blacklist", help="Manage blacklist")
    bl_parser.add_argument("--add", help="Plugin ID to blacklist")
    bl_parser.add_argument("--remove", help="Plugin ID to unblacklist")
    bl_parser.add_argument("--reason", help="Reason for blacklisting")

    # paths command
    paths_parser = subparsers.add_parser("paths", help="Manage scan paths")
    paths_parser.add_argument("--add", help="Path to add")
    paths_parser.add_argument("--remove", help="Path to remove")

    args = parser.parse_args()

    # Initialize storage
    storage = PluginStorage(args.storage_dir)

    # Route to command handler
    if args.command == "scan":
        cmd_scan(args, storage)
    elif args.command == "list":
        cmd_list(args, storage)
    elif args.command == "search":
        cmd_search(args, storage)
    elif args.command == "info":
        cmd_info(args, storage)
    elif args.command == "builtin":
        cmd_builtin(args, storage)
    elif args.command == "summary":
        cmd_summary(args, storage)
    elif args.command == "blacklist":
        cmd_blacklist(args, storage)
    elif args.command == "paths":
        cmd_paths(args, storage)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
