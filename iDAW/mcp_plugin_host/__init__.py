"""
MCP Plugin Host

Model Context Protocol server for plugin hosting and management.
Supports VST3, AU, LV2, CLAP formats and built-in art-themed plugins.

This is Phase 2 of the iDAWi project:
- Plugin Format Support (VST3, AU, LV2, CLAP)
- Plugin Discovery & Management
- Built-in Art-Themed Plugins (11 plugins)
- Instrument Hosting

Usage:
    # As MCP server (stdio transport)
    python -m mcp_plugin_host.server

    # CLI commands
    python -m mcp_plugin_host.cli scan
    python -m mcp_plugin_host.cli list
    python -m mcp_plugin_host.cli search "reverb"
"""

from .models import (
    # Enums
    PluginFormat,
    PluginCategory,
    PluginType,
    PluginStatus,
    InstanceStatus,
    VoiceAllocationMode,
    InstrumentLayerMode,
    # Data classes
    Plugin,
    PluginParameter,
    PluginPreset,
    PluginInstance,
    PluginChain,
    InstrumentRack,
    InstrumentLayer,
    MIDIMapping,
    BuiltinPluginSpec,
    # Functions
    get_builtin_plugins,
    get_builtin_plugin_specs,
    ART_THEMED_PLUGINS,
)

from .storage import PluginStorage
from .scanner import PluginScanner, PluginProfiler
from .server import MCPPluginHostServer

__version__ = "1.0.0"
__all__ = [
    # Enums
    "PluginFormat",
    "PluginCategory",
    "PluginType",
    "PluginStatus",
    "InstanceStatus",
    "VoiceAllocationMode",
    "InstrumentLayerMode",
    # Data classes
    "Plugin",
    "PluginParameter",
    "PluginPreset",
    "PluginInstance",
    "PluginChain",
    "InstrumentRack",
    "InstrumentLayer",
    "MIDIMapping",
    "BuiltinPluginSpec",
    # Functions
    "get_builtin_plugins",
    "get_builtin_plugin_specs",
    "ART_THEMED_PLUGINS",
    # Core classes
    "PluginStorage",
    "PluginScanner",
    "PluginProfiler",
    "MCPPluginHostServer",
]
