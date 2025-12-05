"""
MCP Phase 1 - Audio Engine Tools

MCP tools for audio I/O development and testing.
"""

from typing import Any, Dict, List

from .models import AudioDeviceInfo, AudioBackend, DeviceType
from .storage import get_storage


def get_audio_tools() -> List[Dict[str, Any]]:
    """Get MCP tool definitions for audio engine."""
    return [
        {
            "name": "audio_list_devices",
            "description": "List available audio devices. Returns device info including channels, sample rates, and latency.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "device_type": {
                        "type": "string",
                        "enum": ["input", "output", "duplex", "all"],
                        "description": "Filter by device type (default: all)",
                    },
                    "backend": {
                        "type": "string",
                        "enum": ["coreaudio", "wasapi", "alsa", "pulseaudio", "pipewire", "jack"],
                        "description": "Filter by audio backend",
                    },
                },
            },
        },
        {
            "name": "audio_select_device",
            "description": "Select an audio device for input or output.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "device_id": {
                        "type": "integer",
                        "description": "Device ID to select",
                    },
                    "role": {
                        "type": "string",
                        "enum": ["input", "output"],
                        "description": "Role for the device",
                    },
                },
                "required": ["device_id", "role"],
            },
        },
        {
            "name": "audio_configure",
            "description": "Configure audio engine settings (sample rate, buffer size).",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "sample_rate": {
                        "type": "integer",
                        "enum": [44100, 48000, 88200, 96000, 176400, 192000],
                        "description": "Sample rate in Hz",
                    },
                    "buffer_size": {
                        "type": "integer",
                        "enum": [32, 64, 128, 256, 512, 1024, 2048, 4096],
                        "description": "Buffer size in samples",
                    },
                },
            },
        },
        {
            "name": "audio_start",
            "description": "Start the audio engine.",
            "inputSchema": {
                "type": "object",
                "properties": {},
            },
        },
        {
            "name": "audio_stop",
            "description": "Stop the audio engine.",
            "inputSchema": {
                "type": "object",
                "properties": {},
            },
        },
        {
            "name": "audio_status",
            "description": "Get current audio engine status including CPU usage, latency, and xrun count.",
            "inputSchema": {
                "type": "object",
                "properties": {},
            },
        },
        {
            "name": "audio_latency_test",
            "description": "Run a latency measurement test.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "duration_seconds": {
                        "type": "number",
                        "description": "Test duration in seconds (default: 5)",
                    },
                },
            },
        },
        {
            "name": "audio_stress_test",
            "description": "Run a stress test to check for xruns and dropouts.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "duration_seconds": {
                        "type": "number",
                        "description": "Test duration in seconds (default: 30)",
                    },
                    "cpu_load_percent": {
                        "type": "number",
                        "description": "Target CPU load percentage (default: 80)",
                    },
                },
            },
        },
        {
            "name": "audio_reset",
            "description": "Reset audio engine to default state.",
            "inputSchema": {
                "type": "object",
                "properties": {},
            },
        },
    ]


def handle_audio_tool(name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Handle an audio engine tool call."""
    storage = get_storage()

    try:
        if name == "audio_list_devices":
            # Simulate device enumeration (in real implementation, would query system)
            devices = _get_simulated_devices()

            # Apply filters
            device_type = arguments.get("device_type", "all")
            backend = arguments.get("backend")

            if device_type != "all":
                devices = [d for d in devices if d["device_type"] == device_type]
            if backend:
                devices = [d for d in devices if d["backend"] == backend]

            return {
                "success": True,
                "devices": devices,
                "count": len(devices),
            }

        elif name == "audio_select_device":
            device_id = arguments["device_id"]
            role = arguments["role"]

            if role == "input":
                storage.update_audio_state(input_device_id=device_id)
            else:
                storage.update_audio_state(output_device_id=device_id)

            return {
                "success": True,
                "message": f"Selected device {device_id} for {role}",
                "state": storage.audio_state.to_dict(),
            }

        elif name == "audio_configure":
            sample_rate = arguments.get("sample_rate")
            buffer_size = arguments.get("buffer_size")

            updates = {}
            if sample_rate:
                updates["sample_rate"] = sample_rate
            if buffer_size:
                updates["buffer_size"] = buffer_size

            if updates:
                # Calculate new latency
                sr = updates.get("sample_rate", storage.audio_state.sample_rate)
                bs = updates.get("buffer_size", storage.audio_state.buffer_size)
                updates["latency_samples"] = bs * 2  # Input + output buffer

                storage.update_audio_state(**updates)

            return {
                "success": True,
                "message": "Audio configuration updated",
                "state": storage.audio_state.to_dict(),
            }

        elif name == "audio_start":
            if storage.audio_state.running:
                return {
                    "success": False,
                    "error": "Audio engine is already running",
                }

            storage.update_audio_state(running=True, xrun_count=0)

            return {
                "success": True,
                "message": "Audio engine started",
                "state": storage.audio_state.to_dict(),
            }

        elif name == "audio_stop":
            if not storage.audio_state.running:
                return {
                    "success": False,
                    "error": "Audio engine is not running",
                }

            storage.update_audio_state(running=False, cpu_usage=0.0)

            return {
                "success": True,
                "message": "Audio engine stopped",
                "state": storage.audio_state.to_dict(),
            }

        elif name == "audio_status":
            return {
                "success": True,
                "state": storage.audio_state.to_dict(),
                "devices": {
                    "input": storage.audio_state.input_device_id,
                    "output": storage.audio_state.output_device_id,
                },
            }

        elif name == "audio_latency_test":
            duration = arguments.get("duration_seconds", 5)

            if not storage.audio_state.running:
                return {
                    "success": False,
                    "error": "Audio engine must be running for latency test",
                }

            # Simulated latency test results
            sample_rate = storage.audio_state.sample_rate
            buffer_size = storage.audio_state.buffer_size
            latency_samples = buffer_size * 2
            latency_ms = latency_samples / sample_rate * 1000

            return {
                "success": True,
                "test_duration_seconds": duration,
                "results": {
                    "input_latency_ms": latency_ms / 2,
                    "output_latency_ms": latency_ms / 2,
                    "roundtrip_latency_ms": latency_ms,
                    "latency_samples": latency_samples,
                    "sample_rate": sample_rate,
                    "buffer_size": buffer_size,
                    "meets_target": latency_ms < 10,  # <10ms target
                },
            }

        elif name == "audio_stress_test":
            duration = arguments.get("duration_seconds", 30)
            target_load = arguments.get("cpu_load_percent", 80)

            if not storage.audio_state.running:
                return {
                    "success": False,
                    "error": "Audio engine must be running for stress test",
                }

            # Simulated stress test results
            return {
                "success": True,
                "test_duration_seconds": duration,
                "target_cpu_load_percent": target_load,
                "results": {
                    "average_cpu_percent": target_load * 0.9,
                    "peak_cpu_percent": target_load * 1.1,
                    "xrun_count": 0,
                    "dropout_count": 0,
                    "passed": True,
                    "notes": "No xruns detected during stress test",
                },
            }

        elif name == "audio_reset":
            storage.audio_state = storage._load_audio_state()
            storage.update_audio_state(
                running=False,
                sample_rate=48000,
                buffer_size=256,
                input_device_id=None,
                output_device_id=None,
                cpu_usage=0.0,
                xrun_count=0,
                latency_samples=512,
            )

            return {
                "success": True,
                "message": "Audio engine reset to defaults",
                "state": storage.audio_state.to_dict(),
            }

        else:
            return {"success": False, "error": f"Unknown audio tool: {name}"}

    except Exception as e:
        return {"success": False, "error": str(e)}


def _get_simulated_devices() -> List[Dict[str, Any]]:
    """Get simulated audio devices for testing."""
    import platform

    system = platform.system()

    if system == "Darwin":
        backend = "coreaudio"
        devices = [
            {
                "id": 0,
                "name": "Built-in Output",
                "backend": backend,
                "device_type": "output",
                "input_channels": 0,
                "output_channels": 2,
                "sample_rates": [44100, 48000, 96000],
                "current_sample_rate": 48000,
                "buffer_sizes": [64, 128, 256, 512, 1024],
                "current_buffer_size": 256,
                "latency_ms": 5.3,
                "is_default": True,
            },
            {
                "id": 1,
                "name": "Built-in Microphone",
                "backend": backend,
                "device_type": "input",
                "input_channels": 2,
                "output_channels": 0,
                "sample_rates": [44100, 48000],
                "current_sample_rate": 48000,
                "buffer_sizes": [64, 128, 256, 512, 1024],
                "current_buffer_size": 256,
                "latency_ms": 5.3,
                "is_default": True,
            },
        ]
    elif system == "Windows":
        backend = "wasapi"
        devices = [
            {
                "id": 0,
                "name": "Speakers (High Definition Audio)",
                "backend": backend,
                "device_type": "output",
                "input_channels": 0,
                "output_channels": 2,
                "sample_rates": [44100, 48000, 96000, 192000],
                "current_sample_rate": 48000,
                "buffer_sizes": [128, 256, 512, 1024, 2048],
                "current_buffer_size": 256,
                "latency_ms": 10.0,
                "is_default": True,
            },
            {
                "id": 1,
                "name": "Microphone (High Definition Audio)",
                "backend": backend,
                "device_type": "input",
                "input_channels": 2,
                "output_channels": 0,
                "sample_rates": [44100, 48000],
                "current_sample_rate": 48000,
                "buffer_sizes": [128, 256, 512, 1024, 2048],
                "current_buffer_size": 256,
                "latency_ms": 10.0,
                "is_default": True,
            },
        ]
    else:  # Linux
        backend = "alsa"
        devices = [
            {
                "id": 0,
                "name": "default",
                "backend": backend,
                "device_type": "duplex",
                "input_channels": 2,
                "output_channels": 2,
                "sample_rates": [44100, 48000, 96000],
                "current_sample_rate": 48000,
                "buffer_sizes": [64, 128, 256, 512, 1024, 2048],
                "current_buffer_size": 256,
                "latency_ms": 5.3,
                "is_default": True,
            },
            {
                "id": 1,
                "name": "hw:0,0 (HDA Intel PCH)",
                "backend": backend,
                "device_type": "duplex",
                "input_channels": 2,
                "output_channels": 2,
                "sample_rates": [44100, 48000, 96000, 192000],
                "current_sample_rate": 48000,
                "buffer_sizes": [32, 64, 128, 256, 512, 1024],
                "current_buffer_size": 256,
                "latency_ms": 2.7,
                "is_default": False,
            },
        ]

    return devices
