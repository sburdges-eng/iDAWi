"""
Tests for MCP Phase 1 Server
"""

import pytest
import json
from pathlib import Path
import tempfile
import shutil

from mcp_phase1.server import MCPPhase1Server
from mcp_phase1.storage import Phase1Storage
from mcp_phase1.models import (
    AudioEngineState,
    MIDIState,
    TransportInfo,
    TransportState,
    MixerState,
    Phase1Status,
)


@pytest.fixture
def temp_storage_dir():
    """Create a temporary directory for storage."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def storage(temp_storage_dir):
    """Create a storage instance with temp directory."""
    return Phase1Storage(temp_storage_dir)


@pytest.fixture
def server(temp_storage_dir):
    """Create a server instance with temp storage."""
    return MCPPhase1Server(storage_dir=temp_storage_dir)


class TestAudioTools:
    """Test audio engine tools."""

    def test_audio_list_devices(self, server):
        result = server.handle_tool_call("audio_list_devices", {})
        assert result["success"]
        assert "devices" in result
        assert result["count"] > 0

    def test_audio_configure(self, server):
        result = server.handle_tool_call("audio_configure", {
            "sample_rate": 48000,
            "buffer_size": 256,
        })
        assert result["success"]
        assert result["state"]["sample_rate"] == 48000
        assert result["state"]["buffer_size"] == 256

    def test_audio_start_stop(self, server):
        # Start
        result = server.handle_tool_call("audio_start", {})
        assert result["success"]
        assert result["state"]["running"]

        # Stop
        result = server.handle_tool_call("audio_stop", {})
        assert result["success"]
        assert not result["state"]["running"]

    def test_audio_status(self, server):
        result = server.handle_tool_call("audio_status", {})
        assert result["success"]
        assert "state" in result


class TestMIDITools:
    """Test MIDI tools."""

    def test_midi_list_devices(self, server):
        result = server.handle_tool_call("midi_list_devices", {})
        assert result["success"]
        assert "devices" in result

    def test_midi_clock_config(self, server):
        result = server.handle_tool_call("midi_clock_config", {
            "enabled": True,
            "internal": True,
            "tempo_bpm": 120,
        })
        assert result["success"]
        assert result["state"]["clock_sync_enabled"]

    def test_midi_cc_set_get(self, server):
        # Set CC
        result = server.handle_tool_call("midi_cc_set", {
            "channel": 1,
            "cc_number": 1,
            "value": 64,
        })
        assert result["success"]

        # Get CC
        result = server.handle_tool_call("midi_cc_get", {
            "channel": 1,
            "cc_number": 1,
        })
        assert result["success"]
        assert result["value"] == 64


class TestTransportTools:
    """Test transport tools."""

    def test_transport_play_pause_stop(self, server):
        # Play
        result = server.handle_tool_call("transport_play", {})
        assert result["success"]
        assert result["state"]["state"] == "playing"

        # Pause
        result = server.handle_tool_call("transport_pause", {})
        assert result["success"]
        assert result["state"]["state"] == "paused"

        # Stop
        result = server.handle_tool_call("transport_stop", {})
        assert result["success"]
        assert result["state"]["state"] == "stopped"

    def test_transport_tempo_set(self, server):
        result = server.handle_tool_call("transport_tempo_set", {"bpm": 140})
        assert result["success"]
        assert result["tempo_bpm"] == 140

    def test_transport_position(self, server):
        # Set position
        result = server.handle_tool_call("transport_position_set", {
            "samples": 48000,
        })
        assert result["success"]

        # Get position
        result = server.handle_tool_call("transport_position_get", {})
        assert result["success"]
        assert result["position"]["samples"] == 48000


class TestMixerTools:
    """Test mixer tools."""

    def test_mixer_channel_add_remove(self, server):
        # Add channel
        result = server.handle_tool_call("mixer_channel_add", {"name": "Test Channel"})
        assert result["success"]
        channel_id = result["channel"]["id"]

        # Get channel
        result = server.handle_tool_call("mixer_channel_get", {"channel_id": channel_id})
        assert result["success"]
        assert result["channel"]["name"] == "Test Channel"

        # Remove channel
        result = server.handle_tool_call("mixer_channel_remove", {"channel_id": channel_id})
        assert result["success"]

    def test_mixer_gain_pan(self, server):
        # Add channel
        result = server.handle_tool_call("mixer_channel_add", {"name": "Gain Test"})
        channel_id = result["channel"]["id"]

        # Set gain
        result = server.handle_tool_call("mixer_gain_set", {
            "channel_id": channel_id,
            "gain_db": -6.0,
        })
        assert result["success"]
        assert result["channel"]["gain_db"] == -6.0

        # Set pan
        result = server.handle_tool_call("mixer_pan_set", {
            "channel_id": channel_id,
            "pan": -0.5,
        })
        assert result["success"]
        assert result["channel"]["pan"] == -0.5


class TestPhase1StatusTools:
    """Test Phase 1 status tools."""

    def test_phase1_status(self, server):
        result = server.handle_tool_call("phase1_status", {})
        assert result["success"]
        assert "phase1" in result

    def test_phase1_component_update(self, server):
        result = server.handle_tool_call("phase1_component_update", {
            "component": "audio_io",
            "status": "in_progress",
            "progress": 0.5,
            "note": "Test note",
        })
        assert result["success"]

    def test_phase1_checklist(self, server):
        result = server.handle_tool_call("phase1_checklist", {})
        assert result["success"]
        assert "checklist" in result
        assert result["total"] > 0


class TestStorage:
    """Test storage functionality."""

    def test_audio_state_persistence(self, storage):
        storage.update_audio_state(sample_rate=96000, buffer_size=128)

        # Reload storage
        new_storage = Phase1Storage(str(storage.storage_dir))
        assert new_storage.audio_state.sample_rate == 96000
        assert new_storage.audio_state.buffer_size == 128

    def test_mixer_channel_persistence(self, storage):
        channel = storage.add_channel("Persistent Channel")

        # Reload storage
        new_storage = Phase1Storage(str(storage.storage_dir))
        assert len(new_storage.mixer_state.channels) == 1
        assert new_storage.mixer_state.channels[0].name == "Persistent Channel"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
