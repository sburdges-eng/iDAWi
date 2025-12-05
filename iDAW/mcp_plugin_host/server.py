#!/usr/bin/env python3
"""
MCP Plugin Host Server

Model Context Protocol server for plugin hosting and management.
Supports VST3, AU, LV2, CLAP formats and built-in art-themed plugins.

Run with:
    python -m mcp_plugin_host.server
    # or
    mcp-plugin-host
"""

import json
import sys
import asyncio
from typing import Any, Dict, List, Optional

from .storage import PluginStorage
from .scanner import PluginScanner, PluginProfiler
from .models import (
    Plugin, PluginFormat, PluginType, PluginCategory, PluginStatus,
    PluginPreset, PluginInstance, PluginChain, InstanceStatus,
    InstrumentRack, InstrumentLayer, MIDIMapping,
    VoiceAllocationMode, InstrumentLayerMode,
    get_builtin_plugin_specs,
)


class MCPPluginHostServer:
    """
    MCP-compliant Plugin Host server.

    Implements the Model Context Protocol for plugin management,
    discovery, and hosting operations.
    """

    def __init__(self, storage_dir: Optional[str] = None):
        self.storage = PluginStorage(storage_dir)
        self.scanner = PluginScanner(self.storage)
        self.profiler = PluginProfiler(self.storage)
        self.server_info = {
            "name": "mcp-plugin-host",
            "version": "1.0.0",
            "description": "Plugin hosting and management for iDAWi",
        }

    def get_tools(self) -> List[Dict[str, Any]]:
        """Return the list of available MCP tools."""
        return [
            # =================================================================
            # Plugin Discovery & Management
            # =================================================================
            {
                "name": "plugin_scan",
                "description": "Scan system for audio plugins (VST3, AU, LV2, CLAP). Returns discovered plugins.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "paths": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Custom paths to scan (uses defaults if not specified)"
                        },
                        "formats": {
                            "type": "array",
                            "items": {
                                "type": "string",
                                "enum": ["vst3", "au", "lv2", "clap"]
                            },
                            "description": "Plugin formats to scan (all if not specified)"
                        }
                    }
                }
            },
            {
                "name": "plugin_list",
                "description": "List available plugins with optional filters.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "format": {
                            "type": "string",
                            "enum": ["vst3", "au", "lv2", "clap", "builtin"],
                            "description": "Filter by plugin format"
                        },
                        "type": {
                            "type": "string",
                            "enum": ["effect", "instrument", "midi_effect", "analyzer"],
                            "description": "Filter by plugin type"
                        },
                        "category": {
                            "type": "string",
                            "description": "Filter by category (dynamics, eq, reverb, synth, etc.)"
                        },
                        "favorites_only": {
                            "type": "boolean",
                            "description": "Only show favorite plugins"
                        },
                        "recently_used": {
                            "type": "boolean",
                            "description": "Only show recently used plugins"
                        }
                    }
                }
            },
            {
                "name": "plugin_search",
                "description": "Search for plugins by name, vendor, or description.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum results (default 20)"
                        }
                    },
                    "required": ["query"]
                }
            },
            {
                "name": "plugin_get_info",
                "description": "Get detailed information about a specific plugin.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "plugin_id": {
                            "type": "string",
                            "description": "Plugin ID"
                        }
                    },
                    "required": ["plugin_id"]
                }
            },
            {
                "name": "plugin_set_favorite",
                "description": "Mark or unmark a plugin as favorite.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "plugin_id": {
                            "type": "string",
                            "description": "Plugin ID"
                        },
                        "is_favorite": {
                            "type": "boolean",
                            "description": "True to mark as favorite"
                        }
                    },
                    "required": ["plugin_id", "is_favorite"]
                }
            },
            {
                "name": "plugin_add_tag",
                "description": "Add a tag to a plugin for organization.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "plugin_id": {
                            "type": "string",
                            "description": "Plugin ID"
                        },
                        "tag": {
                            "type": "string",
                            "description": "Tag to add"
                        }
                    },
                    "required": ["plugin_id", "tag"]
                }
            },
            {
                "name": "plugin_validate",
                "description": "Validate a plugin by checking if it can be loaded.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "plugin_id": {
                            "type": "string",
                            "description": "Plugin ID to validate"
                        }
                    },
                    "required": ["plugin_id"]
                }
            },
            {
                "name": "plugin_get_summary",
                "description": "Get a summary of all plugins in the database.",
                "inputSchema": {
                    "type": "object",
                    "properties": {}
                }
            },

            # =================================================================
            # Blacklist Management
            # =================================================================
            {
                "name": "plugin_blacklist",
                "description": "Add a plugin to the blacklist (won't load).",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "plugin_id": {
                            "type": "string",
                            "description": "Plugin ID to blacklist"
                        },
                        "reason": {
                            "type": "string",
                            "description": "Reason for blacklisting"
                        }
                    },
                    "required": ["plugin_id"]
                }
            },
            {
                "name": "plugin_unblacklist",
                "description": "Remove a plugin from the blacklist.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "plugin_id": {
                            "type": "string",
                            "description": "Plugin ID to unblacklist"
                        }
                    },
                    "required": ["plugin_id"]
                }
            },
            {
                "name": "plugin_get_blacklist",
                "description": "Get list of blacklisted plugins.",
                "inputSchema": {
                    "type": "object",
                    "properties": {}
                }
            },

            # =================================================================
            # Plugin Instance Management
            # =================================================================
            {
                "name": "plugin_create_instance",
                "description": "Create a new instance of a plugin.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "plugin_id": {
                            "type": "string",
                            "description": "Plugin ID to instantiate"
                        },
                        "sample_rate": {
                            "type": "number",
                            "description": "Sample rate (default 44100)"
                        },
                        "block_size": {
                            "type": "integer",
                            "description": "Block size (default 512)"
                        }
                    },
                    "required": ["plugin_id"]
                }
            },
            {
                "name": "plugin_release_instance",
                "description": "Release/destroy a plugin instance.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "instance_id": {
                            "type": "string",
                            "description": "Instance ID to release"
                        }
                    },
                    "required": ["instance_id"]
                }
            },
            {
                "name": "plugin_list_instances",
                "description": "List all active plugin instances.",
                "inputSchema": {
                    "type": "object",
                    "properties": {}
                }
            },
            {
                "name": "plugin_set_parameter",
                "description": "Set a parameter value on a plugin instance.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "instance_id": {
                            "type": "string",
                            "description": "Instance ID"
                        },
                        "parameter_id": {
                            "type": "string",
                            "description": "Parameter ID"
                        },
                        "value": {
                            "type": "number",
                            "description": "Parameter value (0.0 - 1.0)"
                        }
                    },
                    "required": ["instance_id", "parameter_id", "value"]
                }
            },
            {
                "name": "plugin_get_parameters",
                "description": "Get all parameters for a plugin instance.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "instance_id": {
                            "type": "string",
                            "description": "Instance ID"
                        }
                    },
                    "required": ["instance_id"]
                }
            },
            {
                "name": "plugin_set_bypass",
                "description": "Enable or disable bypass on a plugin instance.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "instance_id": {
                            "type": "string",
                            "description": "Instance ID"
                        },
                        "bypassed": {
                            "type": "boolean",
                            "description": "True to bypass"
                        }
                    },
                    "required": ["instance_id", "bypassed"]
                }
            },

            # =================================================================
            # Preset Management
            # =================================================================
            {
                "name": "preset_save",
                "description": "Save current plugin state as a preset.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "instance_id": {
                            "type": "string",
                            "description": "Instance ID to save preset from"
                        },
                        "name": {
                            "type": "string",
                            "description": "Preset name"
                        },
                        "tags": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Tags for the preset"
                        }
                    },
                    "required": ["instance_id", "name"]
                }
            },
            {
                "name": "preset_load",
                "description": "Load a preset into a plugin instance.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "instance_id": {
                            "type": "string",
                            "description": "Instance ID to load preset into"
                        },
                        "preset_id": {
                            "type": "string",
                            "description": "Preset ID to load"
                        }
                    },
                    "required": ["instance_id", "preset_id"]
                }
            },
            {
                "name": "preset_list",
                "description": "List presets for a plugin.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "plugin_id": {
                            "type": "string",
                            "description": "Plugin ID (optional, lists all if not specified)"
                        },
                        "favorites_only": {
                            "type": "boolean",
                            "description": "Only show favorites"
                        }
                    }
                }
            },
            {
                "name": "preset_delete",
                "description": "Delete a preset.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "preset_id": {
                            "type": "string",
                            "description": "Preset ID to delete"
                        }
                    },
                    "required": ["preset_id"]
                }
            },

            # =================================================================
            # Plugin Chain Management
            # =================================================================
            {
                "name": "chain_save",
                "description": "Save a plugin chain (multiple plugins) as a preset.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "Chain name"
                        },
                        "description": {
                            "type": "string",
                            "description": "Chain description"
                        },
                        "instance_ids": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Ordered list of instance IDs in the chain"
                        },
                        "tags": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Tags for the chain"
                        }
                    },
                    "required": ["name", "instance_ids"]
                }
            },
            {
                "name": "chain_list",
                "description": "List saved plugin chains.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "favorites_only": {
                            "type": "boolean",
                            "description": "Only show favorites"
                        }
                    }
                }
            },
            {
                "name": "chain_load",
                "description": "Load a plugin chain, creating instances for each plugin.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "chain_id": {
                            "type": "string",
                            "description": "Chain ID to load"
                        }
                    },
                    "required": ["chain_id"]
                }
            },

            # =================================================================
            # Built-in Plugins
            # =================================================================
            {
                "name": "builtin_list",
                "description": "List all built-in art-themed plugins.",
                "inputSchema": {
                    "type": "object",
                    "properties": {}
                }
            },
            {
                "name": "builtin_get_info",
                "description": "Get detailed info about a built-in plugin.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "Plugin name (Pencil, Eraser, Press, etc.)"
                        }
                    },
                    "required": ["name"]
                }
            },

            # =================================================================
            # Instrument Hosting
            # =================================================================
            {
                "name": "instrument_rack_create",
                "description": "Create a new instrument rack for layering/splitting.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "Rack name"
                        },
                        "max_voices": {
                            "type": "integer",
                            "description": "Maximum polyphony (default 64)"
                        },
                        "voice_mode": {
                            "type": "string",
                            "enum": ["polyphonic", "mono", "legato", "unison"],
                            "description": "Voice allocation mode"
                        }
                    },
                    "required": ["name"]
                }
            },
            {
                "name": "instrument_rack_add_layer",
                "description": "Add an instrument layer to a rack.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "rack_id": {
                            "type": "string",
                            "description": "Rack ID"
                        },
                        "plugin_id": {
                            "type": "string",
                            "description": "Instrument plugin ID"
                        },
                        "name": {
                            "type": "string",
                            "description": "Layer name"
                        },
                        "key_range_low": {
                            "type": "integer",
                            "description": "Lowest MIDI note (for split)"
                        },
                        "key_range_high": {
                            "type": "integer",
                            "description": "Highest MIDI note (for split)"
                        }
                    },
                    "required": ["rack_id", "plugin_id"]
                }
            },
            {
                "name": "instrument_rack_set_macro",
                "description": "Set a macro control value on an instrument rack.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "rack_id": {
                            "type": "string",
                            "description": "Rack ID"
                        },
                        "macro_number": {
                            "type": "integer",
                            "minimum": 1,
                            "maximum": 8,
                            "description": "Macro number (1-8)"
                        },
                        "value": {
                            "type": "number",
                            "description": "Macro value (0.0 - 1.0)"
                        }
                    },
                    "required": ["rack_id", "macro_number", "value"]
                }
            },
            {
                "name": "instrument_rack_list",
                "description": "List all instrument racks.",
                "inputSchema": {
                    "type": "object",
                    "properties": {}
                }
            },
            {
                "name": "instrument_rack_freeze",
                "description": "Freeze an instrument rack to audio for CPU optimization.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "rack_id": {
                            "type": "string",
                            "description": "Rack ID to freeze"
                        }
                    },
                    "required": ["rack_id"]
                }
            },

            # =================================================================
            # Performance & Diagnostics
            # =================================================================
            {
                "name": "plugin_profile",
                "description": "Profile a plugin's CPU and memory usage.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "plugin_id": {
                            "type": "string",
                            "description": "Plugin ID to profile"
                        },
                        "duration_seconds": {
                            "type": "number",
                            "description": "Profile duration (default 5)"
                        }
                    },
                    "required": ["plugin_id"]
                }
            },
            {
                "name": "plugin_get_performance",
                "description": "Get performance summary for all plugins.",
                "inputSchema": {
                    "type": "object",
                    "properties": {}
                }
            },
            {
                "name": "plugin_get_scan_paths",
                "description": "Get configured and default plugin scan paths.",
                "inputSchema": {
                    "type": "object",
                    "properties": {}
                }
            },
            {
                "name": "plugin_add_scan_path",
                "description": "Add a custom plugin scan path.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "Path to add"
                        }
                    },
                    "required": ["path"]
                }
            },
        ]

    def handle_tool_call(
        self,
        tool_name: str,
        arguments: Dict[str, Any],
        ai_source: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Handle a tool call and return the result.

        Args:
            tool_name: Name of the tool to call
            arguments: Tool arguments
            ai_source: Which AI is making the call

        Returns:
            Tool result as a dictionary
        """
        try:
            # =================================================================
            # Plugin Discovery & Management
            # =================================================================
            if tool_name == "plugin_scan":
                paths = arguments.get("paths")
                formats = None
                if "formats" in arguments:
                    formats = [PluginFormat(f) for f in arguments["formats"]]

                plugins = self.scanner.scan_sync(paths, formats)
                return {
                    "success": True,
                    "plugins_found": len(plugins),
                    "plugins": [
                        {"id": p.id, "name": p.name, "format": p.format.value}
                        for p in plugins
                    ]
                }

            elif tool_name == "plugin_list":
                fmt = PluginFormat(arguments["format"]) if "format" in arguments else None
                ptype = PluginType(arguments["type"]) if "type" in arguments else None
                cat = PluginCategory(arguments["category"]) if "category" in arguments else None

                plugins = self.storage.list_plugins(
                    format=fmt,
                    plugin_type=ptype,
                    category=cat,
                    favorites_only=arguments.get("favorites_only", False),
                    recently_used=arguments.get("recently_used", False),
                )
                return {
                    "success": True,
                    "count": len(plugins),
                    "plugins": [
                        {
                            "id": p.id,
                            "name": p.name,
                            "vendor": p.vendor,
                            "format": p.format.value,
                            "type": p.plugin_type.value,
                            "category": p.category.value,
                            "is_favorite": p.is_favorite,
                        }
                        for p in plugins
                    ]
                }

            elif tool_name == "plugin_search":
                plugins = self.storage.search_plugins(
                    arguments["query"],
                    limit=arguments.get("limit", 20)
                )
                return {
                    "success": True,
                    "count": len(plugins),
                    "plugins": [
                        {"id": p.id, "name": p.name, "vendor": p.vendor, "format": p.format.value}
                        for p in plugins
                    ]
                }

            elif tool_name == "plugin_get_info":
                plugin = self.storage.get_plugin(arguments["plugin_id"])
                if plugin:
                    return {"success": True, "plugin": plugin.to_dict()}
                return {"success": False, "error": "Plugin not found"}

            elif tool_name == "plugin_set_favorite":
                success = self.storage.set_favorite(
                    arguments["plugin_id"],
                    arguments["is_favorite"]
                )
                return {"success": success}

            elif tool_name == "plugin_add_tag":
                success = self.storage.add_tag(
                    arguments["plugin_id"],
                    arguments["tag"]
                )
                return {"success": success}

            elif tool_name == "plugin_validate":
                result = self.scanner.validate_plugin(arguments["plugin_id"])
                return result

            elif tool_name == "plugin_get_summary":
                summary = self.storage.get_summary()
                return {"success": True, "summary": summary}

            # =================================================================
            # Blacklist Management
            # =================================================================
            elif tool_name == "plugin_blacklist":
                success = self.storage.blacklist_plugin(
                    arguments["plugin_id"],
                    arguments.get("reason", "")
                )
                return {"success": success}

            elif tool_name == "plugin_unblacklist":
                success = self.storage.unblacklist_plugin(arguments["plugin_id"])
                return {"success": success}

            elif tool_name == "plugin_get_blacklist":
                blacklist = self.storage.get_blacklist()
                return {"success": True, "blacklist": blacklist}

            # =================================================================
            # Plugin Instance Management
            # =================================================================
            elif tool_name == "plugin_create_instance":
                plugin = self.storage.get_plugin(arguments["plugin_id"])
                if not plugin:
                    return {"success": False, "error": "Plugin not found"}

                instance = PluginInstance(
                    plugin_id=plugin.id,
                    plugin_name=plugin.name,
                    status=InstanceStatus.READY,
                    sample_rate=arguments.get("sample_rate", 44100.0),
                    block_size=arguments.get("block_size", 512),
                )
                instance = self.storage.register_instance(instance)
                return {
                    "success": True,
                    "instance": instance.to_dict()
                }

            elif tool_name == "plugin_release_instance":
                success = self.storage.release_instance(arguments["instance_id"])
                return {"success": success}

            elif tool_name == "plugin_list_instances":
                instances = self.storage.list_instances()
                return {
                    "success": True,
                    "count": len(instances),
                    "instances": [inst.to_dict() for inst in instances]
                }

            elif tool_name == "plugin_set_parameter":
                instance = self.storage.get_instance(arguments["instance_id"])
                if not instance:
                    return {"success": False, "error": "Instance not found"}

                instance.parameters[arguments["parameter_id"]] = arguments["value"]
                self.storage.update_instance(instance)
                return {"success": True}

            elif tool_name == "plugin_get_parameters":
                instance = self.storage.get_instance(arguments["instance_id"])
                if not instance:
                    return {"success": False, "error": "Instance not found"}

                # Get builtin plugin parameters if applicable
                plugin = self.storage.get_plugin(instance.plugin_id)
                if plugin and plugin.format == PluginFormat.BUILTIN:
                    for spec in get_builtin_plugin_specs():
                        if spec.name.lower() == plugin.name.lower():
                            return {
                                "success": True,
                                "parameters": spec.parameters,
                                "current_values": instance.parameters,
                            }

                return {
                    "success": True,
                    "parameters": instance.parameters
                }

            elif tool_name == "plugin_set_bypass":
                instance = self.storage.get_instance(arguments["instance_id"])
                if not instance:
                    return {"success": False, "error": "Instance not found"}

                instance.is_bypassed = arguments["bypassed"]
                instance.status = InstanceStatus.BYPASSED if arguments["bypassed"] else InstanceStatus.READY
                self.storage.update_instance(instance)
                return {"success": True}

            # =================================================================
            # Preset Management
            # =================================================================
            elif tool_name == "preset_save":
                instance = self.storage.get_instance(arguments["instance_id"])
                if not instance:
                    return {"success": False, "error": "Instance not found"}

                preset = PluginPreset(
                    name=arguments["name"],
                    plugin_id=instance.plugin_id,
                    parameters=instance.parameters.copy(),
                    tags=arguments.get("tags", []),
                )
                preset = self.storage.save_preset(preset)
                return {"success": True, "preset": preset.to_dict()}

            elif tool_name == "preset_load":
                instance = self.storage.get_instance(arguments["instance_id"])
                if not instance:
                    return {"success": False, "error": "Instance not found"}

                preset = self.storage.get_preset(arguments["preset_id"])
                if not preset:
                    return {"success": False, "error": "Preset not found"}

                # Apply preset parameters
                instance.parameters = preset.parameters.copy()
                instance.current_preset_id = preset.id
                instance.current_preset_name = preset.name
                self.storage.update_instance(instance)
                return {"success": True}

            elif tool_name == "preset_list":
                presets = self.storage.list_presets(
                    plugin_id=arguments.get("plugin_id"),
                    favorites_only=arguments.get("favorites_only", False),
                )
                return {
                    "success": True,
                    "count": len(presets),
                    "presets": [p.to_dict() for p in presets]
                }

            elif tool_name == "preset_delete":
                success = self.storage.delete_preset(arguments["preset_id"])
                return {"success": success}

            # =================================================================
            # Plugin Chain Management
            # =================================================================
            elif tool_name == "chain_save":
                instances = []
                for inst_id in arguments["instance_ids"]:
                    inst = self.storage.get_instance(inst_id)
                    if inst:
                        instances.append({
                            "plugin_id": inst.plugin_id,
                            "plugin_name": inst.plugin_name,
                            "parameters": inst.parameters,
                        })

                chain = PluginChain(
                    name=arguments["name"],
                    description=arguments.get("description", ""),
                    plugins=instances,
                    tags=arguments.get("tags", []),
                )
                chain = self.storage.save_chain(chain)
                return {"success": True, "chain": chain.to_dict()}

            elif tool_name == "chain_list":
                chains = self.storage.list_chains(
                    favorites_only=arguments.get("favorites_only", False)
                )
                return {
                    "success": True,
                    "count": len(chains),
                    "chains": [c.to_dict() for c in chains]
                }

            elif tool_name == "chain_load":
                chain = self.storage.get_chain(arguments["chain_id"])
                if not chain:
                    return {"success": False, "error": "Chain not found"}

                instances = []
                for plugin_config in chain.plugins:
                    plugin = self.storage.get_plugin(plugin_config["plugin_id"])
                    if plugin:
                        instance = PluginInstance(
                            plugin_id=plugin.id,
                            plugin_name=plugin.name,
                            status=InstanceStatus.READY,
                            parameters=plugin_config.get("parameters", {}),
                        )
                        instance = self.storage.register_instance(instance)
                        instances.append(instance.to_dict())

                return {
                    "success": True,
                    "chain_name": chain.name,
                    "instances": instances
                }

            # =================================================================
            # Built-in Plugins
            # =================================================================
            elif tool_name == "builtin_list":
                specs = get_builtin_plugin_specs()
                return {
                    "success": True,
                    "count": len(specs),
                    "plugins": [
                        {
                            "name": s.name,
                            "theme": s.theme,
                            "category": s.category.value,
                            "type": s.plugin_type.value,
                            "description": s.description,
                            "priority": s.priority,
                        }
                        for s in specs
                    ]
                }

            elif tool_name == "builtin_get_info":
                name = arguments["name"].lower()
                for spec in get_builtin_plugin_specs():
                    if spec.name.lower() == name:
                        return {
                            "success": True,
                            "plugin": {
                                "name": spec.name,
                                "theme": spec.theme,
                                "category": spec.category.value,
                                "type": spec.plugin_type.value,
                                "description": spec.description,
                                "priority": spec.priority,
                                "parameters": spec.parameters,
                            }
                        }
                return {"success": False, "error": "Built-in plugin not found"}

            # =================================================================
            # Instrument Hosting
            # =================================================================
            elif tool_name == "instrument_rack_create":
                voice_mode = VoiceAllocationMode.POLYPHONIC
                if "voice_mode" in arguments:
                    voice_mode = VoiceAllocationMode(arguments["voice_mode"])

                rack = InstrumentRack(
                    name=arguments["name"],
                    max_voices=arguments.get("max_voices", 64),
                    voice_mode=voice_mode,
                )
                rack = self.storage.save_rack(rack)
                return {"success": True, "rack": rack.to_dict()}

            elif tool_name == "instrument_rack_add_layer":
                rack = self.storage.get_rack(arguments["rack_id"])
                if not rack:
                    return {"success": False, "error": "Rack not found"}

                plugin = self.storage.get_plugin(arguments["plugin_id"])
                if not plugin:
                    return {"success": False, "error": "Plugin not found"}

                # Create instance for the layer
                instance = PluginInstance(
                    plugin_id=plugin.id,
                    plugin_name=plugin.name,
                    status=InstanceStatus.READY,
                )
                instance = self.storage.register_instance(instance)

                layer = InstrumentLayer(
                    name=arguments.get("name", plugin.name),
                    plugin_instance_id=instance.id,
                    key_range_low=arguments.get("key_range_low", 0),
                    key_range_high=arguments.get("key_range_high", 127),
                )
                rack.layers.append(layer)
                self.storage.save_rack(rack)

                return {
                    "success": True,
                    "layer": layer.to_dict(),
                    "instance_id": instance.id
                }

            elif tool_name == "instrument_rack_set_macro":
                rack = self.storage.get_rack(arguments["rack_id"])
                if not rack:
                    return {"success": False, "error": "Rack not found"}

                macro_key = f"macro_{arguments['macro_number']}"
                rack.macros[macro_key] = arguments["value"]
                self.storage.save_rack(rack)
                return {"success": True}

            elif tool_name == "instrument_rack_list":
                racks = self.storage.list_racks()
                return {
                    "success": True,
                    "count": len(racks),
                    "racks": [r.to_dict() for r in racks]
                }

            elif tool_name == "instrument_rack_freeze":
                rack = self.storage.get_rack(arguments["rack_id"])
                if not rack:
                    return {"success": False, "error": "Rack not found"}

                # Placeholder - actual freezing requires audio rendering
                rack.is_frozen = True
                rack.frozen_audio_path = f"frozen_{rack.id}.wav"
                self.storage.save_rack(rack)

                return {
                    "success": True,
                    "message": "Rack frozen (audio rendering requires C++ integration)",
                    "frozen_path": rack.frozen_audio_path
                }

            # =================================================================
            # Performance & Diagnostics
            # =================================================================
            elif tool_name == "plugin_profile":
                result = self.profiler.profile_plugin(
                    arguments["plugin_id"],
                    arguments.get("duration_seconds", 5.0)
                )
                return result

            elif tool_name == "plugin_get_performance":
                summary = self.profiler.get_performance_summary()
                return {"success": True, "summary": summary}

            elif tool_name == "plugin_get_scan_paths":
                custom_paths = self.storage.get_scan_paths()
                system_paths = self.scanner.get_system_plugin_paths()
                return {
                    "success": True,
                    "custom_paths": custom_paths,
                    "system_paths": system_paths,
                }

            elif tool_name == "plugin_add_scan_path":
                success = self.storage.add_scan_path(arguments["path"])
                return {"success": success}

            else:
                return {"success": False, "error": f"Unknown tool: {tool_name}"}

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def handle_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Handle an MCP protocol message."""
        method = message.get("method", "")
        msg_id = message.get("id")
        params = message.get("params", {})

        if method == "initialize":
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "serverInfo": self.server_info,
                    "capabilities": {
                        "tools": {"listChanged": False},
                    }
                }
            }

        elif method == "tools/list":
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "tools": self.get_tools()
                }
            }

        elif method == "tools/call":
            tool_name = params.get("name", "")
            arguments = params.get("arguments", {})
            ai_source = params.get("_meta", {}).get("ai_source")

            result = self.handle_tool_call(tool_name, arguments, ai_source)

            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps(result, indent=2)
                        }
                    ]
                }
            }

        elif method == "notifications/initialized":
            return None

        else:
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "error": {
                    "code": -32601,
                    "message": f"Method not found: {method}"
                }
            }

    async def run_stdio(self):
        """Run the server using stdio transport."""
        print(f"MCP Plugin Host v{self.server_info['version']} starting...", file=sys.stderr)

        while True:
            try:
                line = await asyncio.get_event_loop().run_in_executor(
                    None, sys.stdin.readline
                )
                if not line:
                    break

                line = line.strip()
                if not line:
                    continue

                message = json.loads(line)
                response = await self.handle_message(message)

                if response:
                    print(json.dumps(response), flush=True)

            except json.JSONDecodeError as e:
                error_response = {
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {
                        "code": -32700,
                        "message": f"Parse error: {str(e)}"
                    }
                }
                print(json.dumps(error_response), flush=True)
            except Exception as e:
                print(f"Error: {e}", file=sys.stderr)


def main():
    """Entry point for the MCP server."""
    import argparse

    parser = argparse.ArgumentParser(description="MCP Plugin Host Server")
    parser.add_argument(
        "--storage-dir",
        help="Directory for plugin storage",
        default=None
    )
    args = parser.parse_args()

    server = MCPPluginHostServer(storage_dir=args.storage_dir)
    asyncio.run(server.run_stdio())


if __name__ == "__main__":
    main()
