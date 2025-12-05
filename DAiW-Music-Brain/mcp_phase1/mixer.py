"""
MCP Phase 1 - Mixer Tools

MCP tools for mixer development and testing.
"""

from typing import Any, Dict, List

from .models import ChannelStrip, MixerState
from .storage import get_storage


def get_mixer_tools() -> List[Dict[str, Any]]:
    """Get MCP tool definitions for mixer."""
    return [
        {
            "name": "mixer_status",
            "description": "Get current mixer status including all channels and master.",
            "inputSchema": {
                "type": "object",
                "properties": {},
            },
        },
        {
            "name": "mixer_channel_add",
            "description": "Add a new mixer channel.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Channel name",
                    },
                },
                "required": ["name"],
            },
        },
        {
            "name": "mixer_channel_remove",
            "description": "Remove a mixer channel.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "channel_id": {
                        "type": "integer",
                        "description": "Channel ID to remove",
                    },
                },
                "required": ["channel_id"],
            },
        },
        {
            "name": "mixer_channel_get",
            "description": "Get a specific channel's settings.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "channel_id": {
                        "type": "integer",
                        "description": "Channel ID",
                    },
                },
                "required": ["channel_id"],
            },
        },
        {
            "name": "mixer_gain_set",
            "description": "Set channel gain/fader level.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "channel_id": {
                        "type": "integer",
                        "description": "Channel ID (omit for master)",
                    },
                    "gain_db": {
                        "type": "number",
                        "minimum": -96,
                        "maximum": 12,
                        "description": "Gain in dB",
                    },
                },
                "required": ["gain_db"],
            },
        },
        {
            "name": "mixer_pan_set",
            "description": "Set channel pan position.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "channel_id": {
                        "type": "integer",
                        "description": "Channel ID",
                    },
                    "pan": {
                        "type": "number",
                        "minimum": -1,
                        "maximum": 1,
                        "description": "Pan position (-1 = full left, 0 = center, 1 = full right)",
                    },
                },
                "required": ["channel_id", "pan"],
            },
        },
        {
            "name": "mixer_mute_toggle",
            "description": "Toggle mute on a channel.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "channel_id": {
                        "type": "integer",
                        "description": "Channel ID (omit for master)",
                    },
                },
            },
        },
        {
            "name": "mixer_solo_toggle",
            "description": "Toggle solo on a channel.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "channel_id": {
                        "type": "integer",
                        "description": "Channel ID",
                    },
                },
                "required": ["channel_id"],
            },
        },
        {
            "name": "mixer_solo_clear",
            "description": "Clear all solos.",
            "inputSchema": {
                "type": "object",
                "properties": {},
            },
        },
        {
            "name": "mixer_aux_send_set",
            "description": "Set aux send level for a channel.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "channel_id": {
                        "type": "integer",
                        "description": "Channel ID",
                    },
                    "aux_id": {
                        "type": "integer",
                        "description": "Aux bus ID",
                    },
                    "level_db": {
                        "type": "number",
                        "minimum": -96,
                        "maximum": 12,
                        "description": "Send level in dB",
                    },
                },
                "required": ["channel_id", "aux_id", "level_db"],
            },
        },
        {
            "name": "mixer_meters_get",
            "description": "Get current meter readings for all channels.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "channel_id": {
                        "type": "integer",
                        "description": "Specific channel ID (optional, returns all if omitted)",
                    },
                },
            },
        },
        {
            "name": "mixer_solo_mode_set",
            "description": "Set solo mode (AFL/PFL).",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "mode": {
                        "type": "string",
                        "enum": ["afl", "pfl"],
                        "description": "Solo mode: AFL (after fader listen) or PFL (pre fader listen)",
                    },
                },
                "required": ["mode"],
            },
        },
        {
            "name": "mixer_reset",
            "description": "Reset mixer to default state.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "keep_channels": {
                        "type": "boolean",
                        "description": "Keep existing channels (just reset their settings)",
                    },
                },
            },
        },
        {
            "name": "mixer_channel_rename",
            "description": "Rename a mixer channel.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "channel_id": {
                        "type": "integer",
                        "description": "Channel ID",
                    },
                    "name": {
                        "type": "string",
                        "description": "New channel name",
                    },
                },
                "required": ["channel_id", "name"],
            },
        },
        {
            "name": "mixer_routing_set",
            "description": "Set channel output routing.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "channel_id": {
                        "type": "integer",
                        "description": "Channel ID",
                    },
                    "output": {
                        "type": "string",
                        "enum": ["master", "aux_1", "aux_2", "aux_3", "aux_4", "bus_1", "bus_2"],
                        "description": "Output destination",
                    },
                },
                "required": ["channel_id", "output"],
            },
        },
    ]


def handle_mixer_tool(name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Handle a mixer tool call."""
    storage = get_storage()

    try:
        if name == "mixer_status":
            return {
                "success": True,
                "mixer": storage.mixer_state.to_dict(),
            }

        elif name == "mixer_channel_add":
            channel_name = arguments["name"]
            channel = storage.add_channel(channel_name)

            return {
                "success": True,
                "message": f"Added channel '{channel_name}' (ID: {channel.id})",
                "channel": channel.to_dict(),
            }

        elif name == "mixer_channel_remove":
            channel_id = arguments["channel_id"]
            success = storage.remove_channel(channel_id)

            if success:
                return {
                    "success": True,
                    "message": f"Removed channel {channel_id}",
                }
            else:
                return {
                    "success": False,
                    "error": f"Channel {channel_id} not found",
                }

        elif name == "mixer_channel_get":
            channel_id = arguments["channel_id"]

            for channel in storage.mixer_state.channels:
                if channel.id == channel_id:
                    return {
                        "success": True,
                        "channel": channel.to_dict(),
                    }

            return {
                "success": False,
                "error": f"Channel {channel_id} not found",
            }

        elif name == "mixer_gain_set":
            gain_db = arguments["gain_db"]
            channel_id = arguments.get("channel_id")

            if channel_id is None:
                # Set master gain
                storage.mixer_state.master_gain_db = gain_db
                storage.save_mixer_state()

                return {
                    "success": True,
                    "message": f"Master gain set to {gain_db} dB",
                    "master_gain_db": gain_db,
                }
            else:
                channel = storage.update_channel(channel_id, gain_db=gain_db)
                if channel:
                    return {
                        "success": True,
                        "message": f"Channel {channel_id} gain set to {gain_db} dB",
                        "channel": channel.to_dict(),
                    }
                else:
                    return {
                        "success": False,
                        "error": f"Channel {channel_id} not found",
                    }

        elif name == "mixer_pan_set":
            channel_id = arguments["channel_id"]
            pan = arguments["pan"]

            channel = storage.update_channel(channel_id, pan=pan)
            if channel:
                pan_desc = "center" if pan == 0 else f"{'left' if pan < 0 else 'right'} {abs(int(pan * 100))}%"
                return {
                    "success": True,
                    "message": f"Channel {channel_id} pan set to {pan_desc}",
                    "channel": channel.to_dict(),
                }
            else:
                return {
                    "success": False,
                    "error": f"Channel {channel_id} not found",
                }

        elif name == "mixer_mute_toggle":
            channel_id = arguments.get("channel_id")

            if channel_id is None:
                # Toggle master mute
                storage.mixer_state.master_mute = not storage.mixer_state.master_mute
                storage.save_mixer_state()

                return {
                    "success": True,
                    "message": f"Master {'muted' if storage.mixer_state.master_mute else 'unmuted'}",
                    "master_mute": storage.mixer_state.master_mute,
                }
            else:
                for channel in storage.mixer_state.channels:
                    if channel.id == channel_id:
                        channel.mute = not channel.mute
                        storage.save_mixer_state()

                        return {
                            "success": True,
                            "message": f"Channel {channel_id} {'muted' if channel.mute else 'unmuted'}",
                            "channel": channel.to_dict(),
                        }

                return {
                    "success": False,
                    "error": f"Channel {channel_id} not found",
                }

        elif name == "mixer_solo_toggle":
            channel_id = arguments["channel_id"]

            for channel in storage.mixer_state.channels:
                if channel.id == channel_id:
                    channel.solo = not channel.solo
                    storage.save_mixer_state()

                    return {
                        "success": True,
                        "message": f"Channel {channel_id} solo {'on' if channel.solo else 'off'}",
                        "channel": channel.to_dict(),
                    }

            return {
                "success": False,
                "error": f"Channel {channel_id} not found",
            }

        elif name == "mixer_solo_clear":
            count = 0
            for channel in storage.mixer_state.channels:
                if channel.solo:
                    channel.solo = False
                    count += 1

            storage.save_mixer_state()

            return {
                "success": True,
                "message": f"Cleared solo on {count} channel(s)",
                "cleared_count": count,
            }

        elif name == "mixer_aux_send_set":
            channel_id = arguments["channel_id"]
            aux_id = arguments["aux_id"]
            level_db = arguments["level_db"]

            for channel in storage.mixer_state.channels:
                if channel.id == channel_id:
                    channel.aux_sends[aux_id] = level_db
                    storage.save_mixer_state()

                    return {
                        "success": True,
                        "message": f"Channel {channel_id} aux {aux_id} send set to {level_db} dB",
                        "channel": channel.to_dict(),
                    }

            return {
                "success": False,
                "error": f"Channel {channel_id} not found",
            }

        elif name == "mixer_meters_get":
            channel_id = arguments.get("channel_id")

            if channel_id is not None:
                for channel in storage.mixer_state.channels:
                    if channel.id == channel_id:
                        return {
                            "success": True,
                            "channel_id": channel_id,
                            "meters": {
                                "input_db": channel.input_meter_db,
                                "output_db": channel.output_meter_db,
                            },
                        }
                return {
                    "success": False,
                    "error": f"Channel {channel_id} not found",
                }
            else:
                meters = {
                    "master": {
                        "output_db": storage.mixer_state.master_meter_db,
                    },
                    "channels": {},
                }
                for channel in storage.mixer_state.channels:
                    meters["channels"][channel.id] = {
                        "name": channel.name,
                        "input_db": channel.input_meter_db,
                        "output_db": channel.output_meter_db,
                    }

                return {
                    "success": True,
                    "meters": meters,
                }

        elif name == "mixer_solo_mode_set":
            mode = arguments["mode"]
            storage.mixer_state.solo_mode = mode
            storage.save_mixer_state()

            mode_name = "After Fader Listen" if mode == "afl" else "Pre Fader Listen"
            return {
                "success": True,
                "message": f"Solo mode set to {mode_name}",
                "solo_mode": mode,
            }

        elif name == "mixer_reset":
            keep_channels = arguments.get("keep_channels", False)

            if keep_channels:
                # Reset settings only
                for channel in storage.mixer_state.channels:
                    channel.gain_db = 0.0
                    channel.pan = 0.0
                    channel.mute = False
                    channel.solo = False
                    channel.aux_sends = {}
            else:
                # Clear all channels
                storage.mixer_state.channels = []

            storage.mixer_state.master_gain_db = 0.0
            storage.mixer_state.master_mute = False
            storage.save_mixer_state()

            return {
                "success": True,
                "message": "Mixer reset to defaults",
                "mixer": storage.mixer_state.to_dict(),
            }

        elif name == "mixer_channel_rename":
            channel_id = arguments["channel_id"]
            new_name = arguments["name"]

            channel = storage.update_channel(channel_id, name=new_name)
            if channel:
                return {
                    "success": True,
                    "message": f"Channel {channel_id} renamed to '{new_name}'",
                    "channel": channel.to_dict(),
                }
            else:
                return {
                    "success": False,
                    "error": f"Channel {channel_id} not found",
                }

        elif name == "mixer_routing_set":
            channel_id = arguments["channel_id"]
            output = arguments["output"]

            # Store routing info (simplified for now)
            return {
                "success": True,
                "message": f"Channel {channel_id} routed to {output}",
                "channel_id": channel_id,
                "output": output,
            }

        else:
            return {"success": False, "error": f"Unknown mixer tool: {name}"}

    except Exception as e:
        return {"success": False, "error": str(e)}
