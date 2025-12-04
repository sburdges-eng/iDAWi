"""
MCP Phase 1 - Storage

Persistent storage for Phase 1 development state.
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional
from datetime import datetime

from .models import (
    AudioEngineState,
    MIDIState,
    TransportInfo,
    TransportState,
    MixerState,
    ChannelStrip,
    Phase1Status,
)


class Phase1Storage:
    """
    Persistent storage for Phase 1 MCP state.

    Stores state in ~/.mcp_phase1/ directory for cross-AI synchronization.
    """

    def __init__(self, storage_dir: Optional[str] = None):
        if storage_dir:
            self.storage_dir = Path(storage_dir)
        else:
            self.storage_dir = Path.home() / ".mcp_phase1"

        self.storage_dir.mkdir(parents=True, exist_ok=True)

        # State files
        self.audio_file = self.storage_dir / "audio_state.json"
        self.midi_file = self.storage_dir / "midi_state.json"
        self.transport_file = self.storage_dir / "transport_state.json"
        self.mixer_file = self.storage_dir / "mixer_state.json"
        self.phase1_file = self.storage_dir / "phase1_status.json"
        self.log_file = self.storage_dir / "activity_log.json"

        # Initialize state
        self.audio_state = self._load_audio_state()
        self.midi_state = self._load_midi_state()
        self.transport_info = self._load_transport_info()
        self.mixer_state = self._load_mixer_state()
        self.phase1_status = self._load_phase1_status()

    def _load_json(self, file_path: Path) -> Optional[Dict]:
        """Load JSON from file."""
        if file_path.exists():
            try:
                with open(file_path, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return None
        return None

    def _save_json(self, file_path: Path, data: Dict):
        """Save JSON to file."""
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)

    # =========================================================================
    # Audio State
    # =========================================================================

    def _load_audio_state(self) -> AudioEngineState:
        """Load audio engine state from file."""
        data = self._load_json(self.audio_file)
        if data:
            return AudioEngineState(
                running=data.get("running", False),
                sample_rate=data.get("sample_rate", 48000),
                buffer_size=data.get("buffer_size", 256),
                input_device_id=data.get("input_device_id"),
                output_device_id=data.get("output_device_id"),
                cpu_usage=data.get("cpu_usage", 0.0),
                xrun_count=data.get("xrun_count", 0),
                latency_samples=data.get("latency_samples", 0),
            )
        return AudioEngineState()

    def save_audio_state(self):
        """Save audio engine state to file."""
        self._save_json(self.audio_file, self.audio_state.to_dict())

    def update_audio_state(self, **kwargs) -> AudioEngineState:
        """Update audio engine state."""
        for key, value in kwargs.items():
            if hasattr(self.audio_state, key):
                setattr(self.audio_state, key, value)
        self.save_audio_state()
        self._log_activity("audio", "state_updated", kwargs)
        return self.audio_state

    # =========================================================================
    # MIDI State
    # =========================================================================

    def _load_midi_state(self) -> MIDIState:
        """Load MIDI state from file."""
        data = self._load_json(self.midi_file)
        if data:
            return MIDIState(
                clock_sync_enabled=data.get("clock_sync_enabled", False),
                internal_clock=data.get("internal_clock", True),
                tempo_bpm=data.get("tempo_bpm", 120.0),
                playing=data.get("playing", False),
                position_beats=data.get("position_beats", 0.0),
                cc_values=data.get("cc_values", {}),
            )
        return MIDIState()

    def save_midi_state(self):
        """Save MIDI state to file."""
        self._save_json(self.midi_file, self.midi_state.to_dict())

    def update_midi_state(self, **kwargs) -> MIDIState:
        """Update MIDI state."""
        for key, value in kwargs.items():
            if hasattr(self.midi_state, key):
                setattr(self.midi_state, key, value)
        self.save_midi_state()
        self._log_activity("midi", "state_updated", kwargs)
        return self.midi_state

    # =========================================================================
    # Transport State
    # =========================================================================

    def _load_transport_info(self) -> TransportInfo:
        """Load transport info from file."""
        data = self._load_json(self.transport_file)
        if data:
            state_str = data.get("state", "stopped")
            try:
                state = TransportState(state_str)
            except ValueError:
                state = TransportState.STOPPED

            return TransportInfo(
                state=state,
                position_samples=data.get("position_samples", 0),
                position_beats=data.get("position_beats", 0.0),
                tempo_bpm=data.get("tempo_bpm", 120.0),
                time_signature_num=data.get("time_signature_num", 4),
                time_signature_denom=data.get("time_signature_denom", 4),
                recording=data.get("recording", False),
            )
        return TransportInfo()

    def save_transport_info(self):
        """Save transport info to file."""
        self._save_json(self.transport_file, self.transport_info.to_dict())

    def update_transport(self, **kwargs) -> TransportInfo:
        """Update transport state."""
        if "state" in kwargs and isinstance(kwargs["state"], str):
            kwargs["state"] = TransportState(kwargs["state"])
        for key, value in kwargs.items():
            if hasattr(self.transport_info, key):
                setattr(self.transport_info, key, value)
        self.save_transport_info()
        self._log_activity("transport", "state_updated", {k: str(v) for k, v in kwargs.items()})
        return self.transport_info

    # =========================================================================
    # Mixer State
    # =========================================================================

    def _load_mixer_state(self) -> MixerState:
        """Load mixer state from file."""
        data = self._load_json(self.mixer_file)
        if data:
            channels = []
            for ch_data in data.get("channels", []):
                channels.append(ChannelStrip(
                    id=ch_data.get("id", 0),
                    name=ch_data.get("name", "Channel"),
                    gain_db=ch_data.get("gain_db", 0.0),
                    pan=ch_data.get("pan", 0.0),
                    mute=ch_data.get("mute", False),
                    solo=ch_data.get("solo", False),
                    input_meter_db=ch_data.get("input_meter_db", -100.0),
                    output_meter_db=ch_data.get("output_meter_db", -100.0),
                    aux_sends=ch_data.get("aux_sends", {}),
                ))
            return MixerState(
                master_gain_db=data.get("master_gain_db", 0.0),
                master_mute=data.get("master_mute", False),
                master_meter_db=data.get("master_meter_db", -100.0),
                channels=channels,
                aux_returns=data.get("aux_returns", {}),
                solo_mode=data.get("solo_mode", "afl"),
            )
        return MixerState()

    def save_mixer_state(self):
        """Save mixer state to file."""
        self._save_json(self.mixer_file, self.mixer_state.to_dict())

    def add_channel(self, name: str) -> ChannelStrip:
        """Add a new mixer channel."""
        new_id = len(self.mixer_state.channels)
        channel = ChannelStrip(id=new_id, name=name)
        self.mixer_state.channels.append(channel)
        self.save_mixer_state()
        self._log_activity("mixer", "channel_added", {"id": new_id, "name": name})
        return channel

    def update_channel(self, channel_id: int, **kwargs) -> Optional[ChannelStrip]:
        """Update a mixer channel."""
        for channel in self.mixer_state.channels:
            if channel.id == channel_id:
                for key, value in kwargs.items():
                    if hasattr(channel, key):
                        setattr(channel, key, value)
                self.save_mixer_state()
                self._log_activity("mixer", "channel_updated", {"id": channel_id, **kwargs})
                return channel
        return None

    def remove_channel(self, channel_id: int) -> bool:
        """Remove a mixer channel."""
        for i, channel in enumerate(self.mixer_state.channels):
            if channel.id == channel_id:
                self.mixer_state.channels.pop(i)
                self.save_mixer_state()
                self._log_activity("mixer", "channel_removed", {"id": channel_id})
                return True
        return False

    # =========================================================================
    # Phase 1 Status
    # =========================================================================

    def _load_phase1_status(self) -> Phase1Status:
        """Load Phase 1 status from file."""
        data = self._load_json(self.phase1_file)
        if data and "components" in data:
            return Phase1Status(components=data["components"])
        return Phase1Status()

    def save_phase1_status(self):
        """Save Phase 1 status to file."""
        self._save_json(self.phase1_file, self.phase1_status.to_dict())

    def update_phase1_component(
        self,
        component: str,
        status: str = None,
        progress: float = None,
        note: str = None,
        blocker: str = None,
    ) -> Dict[str, Any]:
        """Update a Phase 1 component status."""
        self.phase1_status.update_component(component, status, progress, note, blocker)
        self.save_phase1_status()
        self._log_activity("phase1", "component_updated", {
            "component": component,
            "status": status,
            "progress": progress,
        })
        return self.phase1_status.to_dict()

    # =========================================================================
    # Activity Logging
    # =========================================================================

    def _log_activity(self, category: str, action: str, details: Dict[str, Any]):
        """Log activity for debugging and tracking."""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "category": category,
            "action": action,
            "details": details,
        }

        # Load existing log
        log_data = self._load_json(self.log_file) or {"entries": []}

        # Add new entry (keep last 1000 entries)
        log_data["entries"].append(log_entry)
        if len(log_data["entries"]) > 1000:
            log_data["entries"] = log_data["entries"][-1000:]

        self._save_json(self.log_file, log_data)

    def get_recent_activity(self, limit: int = 50) -> list:
        """Get recent activity log entries."""
        log_data = self._load_json(self.log_file) or {"entries": []}
        return log_data["entries"][-limit:]


# Global storage instance
_storage: Optional[Phase1Storage] = None


def get_storage() -> Phase1Storage:
    """Get the global storage instance."""
    global _storage
    if _storage is None:
        _storage = Phase1Storage()
    return _storage
