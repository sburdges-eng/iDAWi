"""
MCP Phase 1 - Transport Tools

MCP tools for transport control development and testing.
"""

from typing import Any, Dict, List

from .models import TransportState, LoopRegion
from .storage import get_storage


def get_transport_tools() -> List[Dict[str, Any]]:
    """Get MCP tool definitions for transport control."""
    return [
        {
            "name": "transport_play",
            "description": "Start playback.",
            "inputSchema": {
                "type": "object",
                "properties": {},
            },
        },
        {
            "name": "transport_pause",
            "description": "Pause playback.",
            "inputSchema": {
                "type": "object",
                "properties": {},
            },
        },
        {
            "name": "transport_stop",
            "description": "Stop playback and return to start position.",
            "inputSchema": {
                "type": "object",
                "properties": {},
            },
        },
        {
            "name": "transport_record",
            "description": "Start recording (also starts playback if not playing).",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "punch_in": {
                        "type": "boolean",
                        "description": "Enable punch-in recording",
                    },
                    "punch_out": {
                        "type": "boolean",
                        "description": "Enable punch-out recording",
                    },
                },
            },
        },
        {
            "name": "transport_status",
            "description": "Get current transport status.",
            "inputSchema": {
                "type": "object",
                "properties": {},
            },
        },
        {
            "name": "transport_position_set",
            "description": "Set playback position.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "samples": {
                        "type": "integer",
                        "description": "Position in samples",
                    },
                    "beats": {
                        "type": "number",
                        "description": "Position in beats (alternative to samples)",
                    },
                    "bars": {
                        "type": "integer",
                        "description": "Position in bars (uses time signature)",
                    },
                    "timecode": {
                        "type": "string",
                        "description": "Position as timecode (HH:MM:SS:FF)",
                    },
                },
            },
        },
        {
            "name": "transport_position_get",
            "description": "Get current playback position in various formats.",
            "inputSchema": {
                "type": "object",
                "properties": {},
            },
        },
        {
            "name": "transport_tempo_set",
            "description": "Set tempo in BPM.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "bpm": {
                        "type": "number",
                        "minimum": 20,
                        "maximum": 300,
                        "description": "Tempo in BPM",
                    },
                },
                "required": ["bpm"],
            },
        },
        {
            "name": "transport_time_signature_set",
            "description": "Set time signature.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "numerator": {
                        "type": "integer",
                        "minimum": 1,
                        "maximum": 16,
                        "description": "Beats per bar",
                    },
                    "denominator": {
                        "type": "integer",
                        "enum": [2, 4, 8, 16],
                        "description": "Beat unit (note value)",
                    },
                },
                "required": ["numerator", "denominator"],
            },
        },
        {
            "name": "transport_loop_set",
            "description": "Set loop region.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "start_samples": {
                        "type": "integer",
                        "description": "Loop start in samples",
                    },
                    "end_samples": {
                        "type": "integer",
                        "description": "Loop end in samples",
                    },
                    "start_beats": {
                        "type": "number",
                        "description": "Loop start in beats (alternative)",
                    },
                    "end_beats": {
                        "type": "number",
                        "description": "Loop end in beats (alternative)",
                    },
                    "enabled": {
                        "type": "boolean",
                        "description": "Enable/disable loop",
                    },
                },
            },
        },
        {
            "name": "transport_loop_toggle",
            "description": "Toggle loop on/off.",
            "inputSchema": {
                "type": "object",
                "properties": {},
            },
        },
        {
            "name": "transport_locate",
            "description": "Locate to a specific marker or position.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "marker": {
                        "type": "string",
                        "enum": ["start", "end", "loop_start", "loop_end", "previous_marker", "next_marker"],
                        "description": "Marker to locate to",
                    },
                },
                "required": ["marker"],
            },
        },
        {
            "name": "transport_nudge",
            "description": "Nudge position forward or backward.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "direction": {
                        "type": "string",
                        "enum": ["forward", "backward"],
                        "description": "Direction to nudge",
                    },
                    "amount": {
                        "type": "string",
                        "enum": ["sample", "beat", "bar", "second"],
                        "description": "Amount to nudge by",
                    },
                    "count": {
                        "type": "integer",
                        "description": "Number of units to nudge (default: 1)",
                    },
                },
                "required": ["direction", "amount"],
            },
        },
    ]


def handle_transport_tool(name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Handle a transport tool call."""
    storage = get_storage()

    try:
        if name == "transport_play":
            storage.update_transport(state="playing", recording=False)

            return {
                "success": True,
                "message": "Playback started",
                "state": storage.transport_info.to_dict(),
            }

        elif name == "transport_pause":
            if storage.transport_info.state == TransportState.PLAYING:
                storage.update_transport(state="paused")

                return {
                    "success": True,
                    "message": "Playback paused",
                    "state": storage.transport_info.to_dict(),
                }
            else:
                return {
                    "success": False,
                    "error": "Not currently playing",
                }

        elif name == "transport_stop":
            storage.update_transport(
                state="stopped",
                position_samples=0,
                position_beats=0.0,
                recording=False,
            )

            return {
                "success": True,
                "message": "Playback stopped",
                "state": storage.transport_info.to_dict(),
            }

        elif name == "transport_record":
            punch_in = arguments.get("punch_in", False)
            punch_out = arguments.get("punch_out", False)

            storage.update_transport(
                state="recording",
                recording=True,
                punch_in_enabled=punch_in,
                punch_out_enabled=punch_out,
            )

            return {
                "success": True,
                "message": "Recording started",
                "punch_in": punch_in,
                "punch_out": punch_out,
                "state": storage.transport_info.to_dict(),
            }

        elif name == "transport_status":
            return {
                "success": True,
                "state": storage.transport_info.to_dict(),
            }

        elif name == "transport_position_set":
            sample_rate = 48000  # Default sample rate

            if "samples" in arguments:
                position = arguments["samples"]
            elif "beats" in arguments:
                beats = arguments["beats"]
                # Convert beats to samples
                samples_per_beat = (60.0 / storage.transport_info.tempo_bpm) * sample_rate
                position = int(beats * samples_per_beat)
            elif "bars" in arguments:
                bars = arguments["bars"]
                beats_per_bar = storage.transport_info.time_signature_num
                total_beats = bars * beats_per_bar
                samples_per_beat = (60.0 / storage.transport_info.tempo_bpm) * sample_rate
                position = int(total_beats * samples_per_beat)
            elif "timecode" in arguments:
                # Parse timecode HH:MM:SS:FF
                tc = arguments["timecode"]
                parts = tc.split(":")
                if len(parts) == 4:
                    h, m, s, f = map(int, parts)
                    total_seconds = h * 3600 + m * 60 + s + f / 30.0
                    position = int(total_seconds * sample_rate)
                else:
                    return {"success": False, "error": "Invalid timecode format"}
            else:
                return {"success": False, "error": "No position specified"}

            # Calculate beats from samples
            samples_per_beat = (60.0 / storage.transport_info.tempo_bpm) * sample_rate
            position_beats = position / samples_per_beat

            storage.update_transport(
                position_samples=position,
                position_beats=position_beats,
            )

            return {
                "success": True,
                "message": f"Position set to {position} samples",
                "state": storage.transport_info.to_dict(),
            }

        elif name == "transport_position_get":
            sample_rate = 48000
            position = storage.transport_info.position_samples
            tempo = storage.transport_info.tempo_bpm
            time_sig_num = storage.transport_info.time_signature_num

            samples_per_beat = (60.0 / tempo) * sample_rate
            beats = position / samples_per_beat
            bars = beats / time_sig_num
            total_seconds = position / sample_rate

            # Format timecode
            hours = int(total_seconds // 3600)
            minutes = int((total_seconds % 3600) // 60)
            seconds = int(total_seconds % 60)
            frames = int((total_seconds % 1) * 30)
            timecode = f"{hours:02d}:{minutes:02d}:{seconds:02d}:{frames:02d}"

            return {
                "success": True,
                "position": {
                    "samples": position,
                    "beats": round(beats, 4),
                    "bars": round(bars, 4),
                    "seconds": round(total_seconds, 4),
                    "timecode": timecode,
                },
                "tempo_bpm": tempo,
                "time_signature": f"{time_sig_num}/{storage.transport_info.time_signature_denom}",
            }

        elif name == "transport_tempo_set":
            bpm = arguments["bpm"]
            storage.update_transport(tempo_bpm=bpm)

            return {
                "success": True,
                "message": f"Tempo set to {bpm} BPM",
                "tempo_bpm": bpm,
            }

        elif name == "transport_time_signature_set":
            numerator = arguments["numerator"]
            denominator = arguments["denominator"]

            storage.update_transport(
                time_signature_num=numerator,
                time_signature_denom=denominator,
            )

            return {
                "success": True,
                "message": f"Time signature set to {numerator}/{denominator}",
                "time_signature": f"{numerator}/{denominator}",
            }

        elif name == "transport_loop_set":
            sample_rate = 48000
            tempo = storage.transport_info.tempo_bpm

            # Get start position
            if "start_samples" in arguments:
                start = arguments["start_samples"]
            elif "start_beats" in arguments:
                samples_per_beat = (60.0 / tempo) * sample_rate
                start = int(arguments["start_beats"] * samples_per_beat)
            else:
                start = storage.transport_info.loop.start_samples if storage.transport_info.loop else 0

            # Get end position
            if "end_samples" in arguments:
                end = arguments["end_samples"]
            elif "end_beats" in arguments:
                samples_per_beat = (60.0 / tempo) * sample_rate
                end = int(arguments["end_beats"] * samples_per_beat)
            else:
                end = storage.transport_info.loop.end_samples if storage.transport_info.loop else sample_rate * 4

            enabled = arguments.get("enabled", True)

            loop = LoopRegion(start_samples=start, end_samples=end, enabled=enabled)
            storage.transport_info.loop = loop
            storage.save_transport_info()

            return {
                "success": True,
                "message": f"Loop set: {start} - {end} samples",
                "loop": loop.to_dict(),
            }

        elif name == "transport_loop_toggle":
            if storage.transport_info.loop:
                storage.transport_info.loop.enabled = not storage.transport_info.loop.enabled
                storage.save_transport_info()
                enabled = storage.transport_info.loop.enabled
            else:
                enabled = False

            return {
                "success": True,
                "message": f"Loop {'enabled' if enabled else 'disabled'}",
                "loop_enabled": enabled,
            }

        elif name == "transport_locate":
            marker = arguments["marker"]
            sample_rate = 48000

            if marker == "start":
                position = 0
            elif marker == "end":
                # Assume 5 minute project length
                position = sample_rate * 60 * 5
            elif marker == "loop_start":
                if storage.transport_info.loop:
                    position = storage.transport_info.loop.start_samples
                else:
                    position = 0
            elif marker == "loop_end":
                if storage.transport_info.loop:
                    position = storage.transport_info.loop.end_samples
                else:
                    position = sample_rate * 60
            else:
                return {"success": False, "error": f"Unknown marker: {marker}"}

            samples_per_beat = (60.0 / storage.transport_info.tempo_bpm) * sample_rate
            position_beats = position / samples_per_beat

            storage.update_transport(
                position_samples=position,
                position_beats=position_beats,
            )

            return {
                "success": True,
                "message": f"Located to {marker}",
                "position_samples": position,
            }

        elif name == "transport_nudge":
            direction = arguments["direction"]
            amount = arguments["amount"]
            count = arguments.get("count", 1)
            sample_rate = 48000

            # Calculate nudge amount in samples
            if amount == "sample":
                nudge = count
            elif amount == "beat":
                samples_per_beat = (60.0 / storage.transport_info.tempo_bpm) * sample_rate
                nudge = int(samples_per_beat * count)
            elif amount == "bar":
                samples_per_beat = (60.0 / storage.transport_info.tempo_bpm) * sample_rate
                nudge = int(samples_per_beat * storage.transport_info.time_signature_num * count)
            elif amount == "second":
                nudge = sample_rate * count
            else:
                return {"success": False, "error": f"Unknown nudge amount: {amount}"}

            if direction == "backward":
                nudge = -nudge

            new_position = max(0, storage.transport_info.position_samples + nudge)
            samples_per_beat = (60.0 / storage.transport_info.tempo_bpm) * sample_rate
            new_beats = new_position / samples_per_beat

            storage.update_transport(
                position_samples=new_position,
                position_beats=new_beats,
            )

            return {
                "success": True,
                "message": f"Nudged {direction} by {count} {amount}(s)",
                "position_samples": new_position,
            }

        else:
            return {"success": False, "error": f"Unknown transport tool: {name}"}

    except Exception as e:
        return {"success": False, "error": str(e)}
