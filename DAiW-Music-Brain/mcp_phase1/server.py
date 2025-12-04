#!/usr/bin/env python3
"""
MCP Phase 1 Server

Unified Model Context Protocol server for Phase 1 audio engine development.
Provides tools for Audio I/O, MIDI, Transport, and Mixer testing.

Run with:
    python -m mcp_phase1.server
    # or
    mcp-phase1-server
"""

import json
import sys
import asyncio
from typing import Any, Dict, List, Optional

from .audio_engine import get_audio_tools, handle_audio_tool
from .midi_tools import get_midi_tools, handle_midi_tool
from .transport import get_transport_tools, handle_transport_tool
from .mixer import get_mixer_tools, handle_mixer_tool
from .storage import get_storage
from .models import Phase1Component, ComponentStatus


class MCPPhase1Server:
    """
    Unified MCP server for Phase 1 development.

    Combines Audio, MIDI, Transport, and Mixer tools into a single server
    for comprehensive Phase 1 testing and development.
    """

    def __init__(self, storage_dir: Optional[str] = None):
        self.storage = get_storage()
        self.server_info = {
            "name": "mcp-phase1",
            "version": "1.0.0",
            "description": "Phase 1 Real-Time Audio Engine Development Tools",
        }

    def get_tools(self) -> List[Dict[str, Any]]:
        """Return all available MCP tools for Phase 1."""
        tools = []

        # Add all tool groups
        tools.extend(get_audio_tools())
        tools.extend(get_midi_tools())
        tools.extend(get_transport_tools())
        tools.extend(get_mixer_tools())

        # Add Phase 1 status tools
        tools.extend(self._get_phase1_status_tools())

        return tools

    def _get_phase1_status_tools(self) -> List[Dict[str, Any]]:
        """Get Phase 1 development status tools."""
        return [
            {
                "name": "phase1_status",
                "description": "Get Phase 1 development status overview.",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                },
            },
            {
                "name": "phase1_component_update",
                "description": "Update a Phase 1 component's development status.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "component": {
                            "type": "string",
                            "enum": ["audio_io", "midi_engine", "transport", "mixer", "dsp_graph", "recording"],
                            "description": "Component to update",
                        },
                        "status": {
                            "type": "string",
                            "enum": ["not_started", "in_progress", "testing", "complete", "blocked"],
                            "description": "New status",
                        },
                        "progress": {
                            "type": "number",
                            "minimum": 0,
                            "maximum": 1,
                            "description": "Progress (0.0 to 1.0)",
                        },
                        "note": {
                            "type": "string",
                            "description": "Development note to add",
                        },
                        "blocker": {
                            "type": "string",
                            "description": "Blocker to record",
                        },
                    },
                    "required": ["component"],
                },
            },
            {
                "name": "phase1_checklist",
                "description": "Get Phase 1 completion checklist.",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                },
            },
            {
                "name": "phase1_activity_log",
                "description": "Get recent activity log for Phase 1 development.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "limit": {
                            "type": "integer",
                            "description": "Number of entries to return (default: 50)",
                        },
                        "category": {
                            "type": "string",
                            "enum": ["audio", "midi", "transport", "mixer", "phase1"],
                            "description": "Filter by category",
                        },
                    },
                },
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

        Routes to the appropriate handler based on tool prefix.
        """
        try:
            # Route based on tool prefix
            if tool_name.startswith("audio_"):
                return handle_audio_tool(tool_name, arguments)
            elif tool_name.startswith("midi_"):
                return handle_midi_tool(tool_name, arguments)
            elif tool_name.startswith("transport_"):
                return handle_transport_tool(tool_name, arguments)
            elif tool_name.startswith("mixer_"):
                return handle_mixer_tool(tool_name, arguments)
            elif tool_name.startswith("phase1_"):
                return self._handle_phase1_tool(tool_name, arguments)
            else:
                return {
                    "success": False,
                    "error": f"Unknown tool: {tool_name}"
                }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def _handle_phase1_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle Phase 1 status tools."""
        if name == "phase1_status":
            return {
                "success": True,
                "phase1": self.storage.phase1_status.to_dict(),
                "audio": self.storage.audio_state.to_dict(),
                "midi": self.storage.midi_state.to_dict(),
                "transport": self.storage.transport_info.to_dict(),
                "mixer": self.storage.mixer_state.to_dict(),
            }

        elif name == "phase1_component_update":
            component = arguments["component"]
            status = arguments.get("status")
            progress = arguments.get("progress")
            note = arguments.get("note")
            blocker = arguments.get("blocker")

            result = self.storage.update_phase1_component(
                component, status, progress, note, blocker
            )

            return {
                "success": True,
                "message": f"Updated component: {component}",
                "phase1": result,
            }

        elif name == "phase1_checklist":
            checklist = [
                {
                    "item": "Audio I/O works on macOS (CoreAudio)",
                    "component": "audio_io",
                    "status": self._get_component_status("audio_io"),
                },
                {
                    "item": "Audio I/O works on Windows (WASAPI)",
                    "component": "audio_io",
                    "status": self._get_component_status("audio_io"),
                },
                {
                    "item": "Audio I/O works on Linux (ALSA/PulseAudio)",
                    "component": "audio_io",
                    "status": self._get_component_status("audio_io"),
                },
                {
                    "item": "MIDI input/output functional",
                    "component": "midi_engine",
                    "status": self._get_component_status("midi_engine"),
                },
                {
                    "item": "MIDI clock synchronization working",
                    "component": "midi_engine",
                    "status": self._get_component_status("midi_engine"),
                },
                {
                    "item": "Transport control (play/pause/stop/record)",
                    "component": "transport",
                    "status": self._get_component_status("transport"),
                },
                {
                    "item": "Mixer with gain/pan/mute/solo",
                    "component": "mixer",
                    "status": self._get_component_status("mixer"),
                },
                {
                    "item": "DSP processing graph",
                    "component": "dsp_graph",
                    "status": self._get_component_status("dsp_graph"),
                },
                {
                    "item": "Latency < 2ms at 256 sample buffer",
                    "component": "audio_io",
                    "status": self._get_component_status("audio_io"),
                },
                {
                    "item": "Zero audio dropouts in stress tests",
                    "component": "audio_io",
                    "status": self._get_component_status("audio_io"),
                },
                {
                    "item": "Recording functionality",
                    "component": "recording",
                    "status": self._get_component_status("recording"),
                },
            ]

            completed = sum(1 for item in checklist if item["status"] == "complete")

            return {
                "success": True,
                "checklist": checklist,
                "completed": completed,
                "total": len(checklist),
                "progress_percent": f"{(completed / len(checklist) * 100):.1f}%",
            }

        elif name == "phase1_activity_log":
            limit = arguments.get("limit", 50)
            category = arguments.get("category")

            entries = self.storage.get_recent_activity(limit * 2)  # Get more to filter

            if category:
                entries = [e for e in entries if e.get("category") == category]

            entries = entries[-limit:]  # Apply limit after filtering

            return {
                "success": True,
                "entries": entries,
                "count": len(entries),
            }

        else:
            return {"success": False, "error": f"Unknown phase1 tool: {name}"}

    def _get_component_status(self, component: str) -> str:
        """Get status for a component."""
        components = self.storage.phase1_status.components
        if component in components:
            return components[component].get("status", "not_started")
        return "not_started"

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
            # Client acknowledgment, no response needed
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
        print(f"MCP Phase 1 Server v{self.server_info['version']} starting...", file=sys.stderr)
        print("Tools: Audio I/O, MIDI, Transport, Mixer, Phase 1 Status", file=sys.stderr)

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

    parser = argparse.ArgumentParser(description="MCP Phase 1 Server")
    parser.add_argument(
        "--storage-dir",
        help="Directory for state storage",
        default=None
    )
    args = parser.parse_args()

    server = MCPPhase1Server(storage_dir=args.storage_dir)
    asyncio.run(server.run_stdio())


if __name__ == "__main__":
    main()
