"""
MCP Phase 1 - MIDI Tools

MCP tools for MIDI engine development and testing.
"""

from typing import Any, Dict, List

from .models import MIDIDeviceInfo, MIDIEvent, MIDIEventType
from .storage import get_storage


def get_midi_tools() -> List[Dict[str, Any]]:
    """Get MCP tool definitions for MIDI engine."""
    return [
        {
            "name": "midi_list_devices",
            "description": "List available MIDI input and output devices.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "device_type": {
                        "type": "string",
                        "enum": ["input", "output", "all"],
                        "description": "Filter by device type (default: all)",
                    },
                },
            },
        },
        {
            "name": "midi_open_device",
            "description": "Open a MIDI device for input or output.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "device_id": {
                        "type": "integer",
                        "description": "Device ID to open",
                    },
                    "direction": {
                        "type": "string",
                        "enum": ["input", "output"],
                        "description": "Open for input or output",
                    },
                },
                "required": ["device_id", "direction"],
            },
        },
        {
            "name": "midi_close_device",
            "description": "Close a MIDI device.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "device_id": {
                        "type": "integer",
                        "description": "Device ID to close",
                    },
                },
                "required": ["device_id"],
            },
        },
        {
            "name": "midi_send_event",
            "description": "Send a MIDI event to an output device.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "device_id": {
                        "type": "integer",
                        "description": "Output device ID",
                    },
                    "event_type": {
                        "type": "string",
                        "enum": ["note_on", "note_off", "control_change", "program_change", "pitch_bend"],
                        "description": "MIDI event type",
                    },
                    "channel": {
                        "type": "integer",
                        "minimum": 1,
                        "maximum": 16,
                        "description": "MIDI channel (1-16)",
                    },
                    "data1": {
                        "type": "integer",
                        "minimum": 0,
                        "maximum": 127,
                        "description": "First data byte (note number, CC number, etc.)",
                    },
                    "data2": {
                        "type": "integer",
                        "minimum": 0,
                        "maximum": 127,
                        "description": "Second data byte (velocity, CC value, etc.)",
                    },
                },
                "required": ["device_id", "event_type", "channel", "data1"],
            },
        },
        {
            "name": "midi_clock_config",
            "description": "Configure MIDI clock synchronization.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "enabled": {
                        "type": "boolean",
                        "description": "Enable/disable MIDI clock sync",
                    },
                    "internal": {
                        "type": "boolean",
                        "description": "True for internal clock, False for external sync",
                    },
                    "tempo_bpm": {
                        "type": "number",
                        "minimum": 20,
                        "maximum": 300,
                        "description": "Tempo in BPM (for internal clock)",
                    },
                },
            },
        },
        {
            "name": "midi_clock_start",
            "description": "Start MIDI clock (sends MIDI Start message).",
            "inputSchema": {
                "type": "object",
                "properties": {},
            },
        },
        {
            "name": "midi_clock_stop",
            "description": "Stop MIDI clock (sends MIDI Stop message).",
            "inputSchema": {
                "type": "object",
                "properties": {},
            },
        },
        {
            "name": "midi_status",
            "description": "Get MIDI engine status.",
            "inputSchema": {
                "type": "object",
                "properties": {},
            },
        },
        {
            "name": "midi_cc_set",
            "description": "Set a CC value (Control Change).",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "channel": {
                        "type": "integer",
                        "minimum": 1,
                        "maximum": 16,
                        "description": "MIDI channel (1-16)",
                    },
                    "cc_number": {
                        "type": "integer",
                        "minimum": 0,
                        "maximum": 127,
                        "description": "CC number",
                    },
                    "value": {
                        "type": "integer",
                        "minimum": 0,
                        "maximum": 127,
                        "description": "CC value",
                    },
                },
                "required": ["channel", "cc_number", "value"],
            },
        },
        {
            "name": "midi_cc_get",
            "description": "Get current CC values.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "channel": {
                        "type": "integer",
                        "minimum": 1,
                        "maximum": 16,
                        "description": "MIDI channel (1-16)",
                    },
                    "cc_number": {
                        "type": "integer",
                        "minimum": 0,
                        "maximum": 127,
                        "description": "Specific CC number (optional, returns all if not specified)",
                    },
                },
            },
        },
        {
            "name": "midi_learn",
            "description": "Enable MIDI learn mode to capture incoming CC messages.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "timeout_seconds": {
                        "type": "number",
                        "description": "Timeout for MIDI learn (default: 10 seconds)",
                    },
                },
            },
        },
        {
            "name": "midi_reset",
            "description": "Reset MIDI engine state (all notes off, reset CCs).",
            "inputSchema": {
                "type": "object",
                "properties": {},
            },
        },
    ]


def handle_midi_tool(name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Handle a MIDI tool call."""
    storage = get_storage()

    try:
        if name == "midi_list_devices":
            device_type = arguments.get("device_type", "all")
            devices = _get_simulated_midi_devices()

            if device_type == "input":
                devices = [d for d in devices if d["is_input"]]
            elif device_type == "output":
                devices = [d for d in devices if d["is_output"]]

            return {
                "success": True,
                "devices": devices,
                "count": len(devices),
            }

        elif name == "midi_open_device":
            device_id = arguments["device_id"]
            direction = arguments["direction"]

            return {
                "success": True,
                "message": f"Opened MIDI {direction} device {device_id}",
                "device_id": device_id,
                "direction": direction,
            }

        elif name == "midi_close_device":
            device_id = arguments["device_id"]

            return {
                "success": True,
                "message": f"Closed MIDI device {device_id}",
            }

        elif name == "midi_send_event":
            device_id = arguments["device_id"]
            event_type = arguments["event_type"]
            channel = arguments["channel"]
            data1 = arguments["data1"]
            data2 = arguments.get("data2", 0)

            event = MIDIEvent(
                event_type=MIDIEventType(event_type),
                channel=channel,
                data1=data1,
                data2=data2,
            )

            return {
                "success": True,
                "message": f"Sent {event_type} on channel {channel}",
                "event": event.to_dict(),
            }

        elif name == "midi_clock_config":
            updates = {}
            if "enabled" in arguments:
                updates["clock_sync_enabled"] = arguments["enabled"]
            if "internal" in arguments:
                updates["internal_clock"] = arguments["internal"]
            if "tempo_bpm" in arguments:
                updates["tempo_bpm"] = arguments["tempo_bpm"]

            if updates:
                storage.update_midi_state(**updates)

            return {
                "success": True,
                "message": "MIDI clock configured",
                "state": storage.midi_state.to_dict(),
            }

        elif name == "midi_clock_start":
            storage.update_midi_state(playing=True)

            return {
                "success": True,
                "message": "MIDI clock started",
                "tempo_bpm": storage.midi_state.tempo_bpm,
            }

        elif name == "midi_clock_stop":
            storage.update_midi_state(playing=False, position_beats=0.0)

            return {
                "success": True,
                "message": "MIDI clock stopped",
            }

        elif name == "midi_status":
            return {
                "success": True,
                "state": storage.midi_state.to_dict(),
            }

        elif name == "midi_cc_set":
            channel = arguments["channel"]
            cc_number = arguments["cc_number"]
            value = arguments["value"]

            # Update CC value in state
            cc_values = storage.midi_state.cc_values.copy()
            if channel not in cc_values:
                cc_values[channel] = {}
            cc_values[channel][cc_number] = value
            storage.update_midi_state(cc_values=cc_values)

            return {
                "success": True,
                "message": f"Set CC{cc_number} = {value} on channel {channel}",
                "channel": channel,
                "cc_number": cc_number,
                "value": value,
            }

        elif name == "midi_cc_get":
            channel = arguments.get("channel")
            cc_number = arguments.get("cc_number")

            cc_values = storage.midi_state.cc_values

            if channel and cc_number is not None:
                # Get specific CC value
                value = cc_values.get(channel, {}).get(cc_number, 0)
                return {
                    "success": True,
                    "channel": channel,
                    "cc_number": cc_number,
                    "value": value,
                }
            elif channel:
                # Get all CCs for channel
                return {
                    "success": True,
                    "channel": channel,
                    "cc_values": cc_values.get(channel, {}),
                }
            else:
                # Get all CCs
                return {
                    "success": True,
                    "cc_values": cc_values,
                }

        elif name == "midi_learn":
            timeout = arguments.get("timeout_seconds", 10)

            # Simulate MIDI learn (in real implementation, would wait for input)
            return {
                "success": True,
                "message": f"MIDI learn mode enabled for {timeout} seconds",
                "timeout_seconds": timeout,
                "captured": {
                    "channel": 1,
                    "cc_number": 1,
                    "description": "Modulation Wheel",
                },
            }

        elif name == "midi_reset":
            storage.update_midi_state(
                playing=False,
                position_beats=0.0,
                cc_values={},
            )

            return {
                "success": True,
                "message": "MIDI engine reset (All Notes Off, CCs cleared)",
            }

        else:
            return {"success": False, "error": f"Unknown MIDI tool: {name}"}

    except Exception as e:
        return {"success": False, "error": str(e)}


def _get_simulated_midi_devices() -> List[Dict[str, Any]]:
    """Get simulated MIDI devices for testing."""
    return [
        {
            "id": 0,
            "name": "IAC Driver Bus 1",
            "is_input": True,
            "is_output": True,
            "is_virtual": True,
            "is_open": False,
        },
        {
            "id": 1,
            "name": "USB MIDI Controller",
            "is_input": True,
            "is_output": False,
            "is_virtual": False,
            "is_open": False,
        },
        {
            "id": 2,
            "name": "Virtual MIDI Keyboard",
            "is_input": True,
            "is_output": False,
            "is_virtual": True,
            "is_open": False,
        },
        {
            "id": 3,
            "name": "External Synth",
            "is_input": False,
            "is_output": True,
            "is_virtual": False,
            "is_open": False,
        },
    ]
