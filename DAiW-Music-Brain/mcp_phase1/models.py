"""
MCP Phase 1 - Data Models

Data models for Phase 1 audio engine development tools.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Dict, Any
from datetime import datetime
import json


# =============================================================================
# Audio Device Models
# =============================================================================

class AudioBackend(Enum):
    """Audio backend types."""
    CORE_AUDIO = "coreaudio"
    WASAPI = "wasapi"
    ALSA = "alsa"
    PULSEAUDIO = "pulseaudio"
    PIPEWIRE = "pipewire"
    JACK = "jack"
    DUMMY = "dummy"


class DeviceType(Enum):
    """Audio device types."""
    INPUT = "input"
    OUTPUT = "output"
    DUPLEX = "duplex"


@dataclass
class AudioDeviceInfo:
    """Audio device information."""
    id: int
    name: str
    backend: AudioBackend
    device_type: DeviceType
    input_channels: int
    output_channels: int
    sample_rates: List[int]
    current_sample_rate: int
    buffer_sizes: List[int]
    current_buffer_size: int
    latency_ms: float
    is_default: bool = False
    is_active: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "backend": self.backend.value,
            "device_type": self.device_type.value,
            "input_channels": self.input_channels,
            "output_channels": self.output_channels,
            "sample_rates": self.sample_rates,
            "current_sample_rate": self.current_sample_rate,
            "buffer_sizes": self.buffer_sizes,
            "current_buffer_size": self.current_buffer_size,
            "latency_ms": self.latency_ms,
            "is_default": self.is_default,
            "is_active": self.is_active,
        }


@dataclass
class AudioEngineState:
    """Audio engine state."""
    running: bool = False
    sample_rate: int = 48000
    buffer_size: int = 256
    input_device_id: Optional[int] = None
    output_device_id: Optional[int] = None
    cpu_usage: float = 0.0
    xrun_count: int = 0
    latency_samples: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "running": self.running,
            "sample_rate": self.sample_rate,
            "buffer_size": self.buffer_size,
            "input_device_id": self.input_device_id,
            "output_device_id": self.output_device_id,
            "cpu_usage": self.cpu_usage,
            "xrun_count": self.xrun_count,
            "latency_samples": self.latency_samples,
            "latency_ms": (self.latency_samples / self.sample_rate * 1000) if self.sample_rate > 0 else 0,
        }


# =============================================================================
# MIDI Models
# =============================================================================

class MIDIEventType(Enum):
    """MIDI event types."""
    NOTE_ON = "note_on"
    NOTE_OFF = "note_off"
    CONTROL_CHANGE = "control_change"
    PROGRAM_CHANGE = "program_change"
    PITCH_BEND = "pitch_bend"
    AFTERTOUCH = "aftertouch"
    POLY_AFTERTOUCH = "poly_aftertouch"
    SYSEX = "sysex"
    CLOCK = "clock"
    START = "start"
    STOP = "stop"
    CONTINUE = "continue"


@dataclass
class MIDIDeviceInfo:
    """MIDI device information."""
    id: int
    name: str
    is_input: bool
    is_output: bool
    is_virtual: bool = False
    is_open: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "is_input": self.is_input,
            "is_output": self.is_output,
            "is_virtual": self.is_virtual,
            "is_open": self.is_open,
        }


@dataclass
class MIDIEvent:
    """MIDI event."""
    event_type: MIDIEventType
    channel: int
    data1: int
    data2: int = 0
    timestamp: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_type": self.event_type.value,
            "channel": self.channel,
            "data1": self.data1,
            "data2": self.data2,
            "timestamp": self.timestamp,
        }


@dataclass
class MIDIState:
    """MIDI engine state."""
    clock_sync_enabled: bool = False
    internal_clock: bool = True
    tempo_bpm: float = 120.0
    playing: bool = False
    position_beats: float = 0.0
    cc_values: Dict[int, Dict[int, int]] = field(default_factory=dict)  # channel -> cc_num -> value

    def to_dict(self) -> Dict[str, Any]:
        return {
            "clock_sync_enabled": self.clock_sync_enabled,
            "internal_clock": self.internal_clock,
            "tempo_bpm": self.tempo_bpm,
            "playing": self.playing,
            "position_beats": self.position_beats,
            "cc_values": self.cc_values,
        }


# =============================================================================
# Transport Models
# =============================================================================

class TransportState(Enum):
    """Transport state."""
    STOPPED = "stopped"
    PLAYING = "playing"
    PAUSED = "paused"
    RECORDING = "recording"


@dataclass
class LoopRegion:
    """Loop region definition."""
    start_samples: int
    end_samples: int
    enabled: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "start_samples": self.start_samples,
            "end_samples": self.end_samples,
            "enabled": self.enabled,
        }


@dataclass
class TransportInfo:
    """Transport information."""
    state: TransportState = TransportState.STOPPED
    position_samples: int = 0
    position_beats: float = 0.0
    tempo_bpm: float = 120.0
    time_signature_num: int = 4
    time_signature_denom: int = 4
    loop: Optional[LoopRegion] = None
    recording: bool = False
    punch_in_enabled: bool = False
    punch_out_enabled: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "state": self.state.value,
            "position_samples": self.position_samples,
            "position_beats": self.position_beats,
            "tempo_bpm": self.tempo_bpm,
            "time_signature": f"{self.time_signature_num}/{self.time_signature_denom}",
            "loop": self.loop.to_dict() if self.loop else None,
            "recording": self.recording,
            "punch_in_enabled": self.punch_in_enabled,
            "punch_out_enabled": self.punch_out_enabled,
        }


# =============================================================================
# Mixer Models
# =============================================================================

@dataclass
class ChannelStrip:
    """Mixer channel strip."""
    id: int
    name: str
    gain_db: float = 0.0
    pan: float = 0.0  # -1.0 to +1.0
    mute: bool = False
    solo: bool = False
    input_meter_db: float = -100.0
    output_meter_db: float = -100.0
    aux_sends: Dict[int, float] = field(default_factory=dict)  # aux_id -> level_db

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "gain_db": self.gain_db,
            "pan": self.pan,
            "mute": self.mute,
            "solo": self.solo,
            "input_meter_db": self.input_meter_db,
            "output_meter_db": self.output_meter_db,
            "aux_sends": self.aux_sends,
        }


@dataclass
class MixerState:
    """Mixer state."""
    master_gain_db: float = 0.0
    master_mute: bool = False
    master_meter_db: float = -100.0
    channels: List[ChannelStrip] = field(default_factory=list)
    aux_returns: Dict[int, float] = field(default_factory=dict)
    solo_mode: str = "afl"  # "afl" (after fader) or "pfl" (pre fader)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "master_gain_db": self.master_gain_db,
            "master_mute": self.master_mute,
            "master_meter_db": self.master_meter_db,
            "channels": [ch.to_dict() for ch in self.channels],
            "aux_returns": self.aux_returns,
            "solo_mode": self.solo_mode,
            "channel_count": len(self.channels),
        }


# =============================================================================
# Phase 1 Development Status
# =============================================================================

class Phase1Component(Enum):
    """Phase 1 development components."""
    AUDIO_IO = "audio_io"
    MIDI_ENGINE = "midi_engine"
    TRANSPORT = "transport"
    MIXER = "mixer"
    DSP_GRAPH = "dsp_graph"
    RECORDING = "recording"


class ComponentStatus(Enum):
    """Component development status."""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    TESTING = "testing"
    COMPLETE = "complete"
    BLOCKED = "blocked"


@dataclass
class Phase1Status:
    """Phase 1 development status tracking."""
    components: Dict[str, Dict[str, Any]] = field(default_factory=dict)

    def __post_init__(self):
        if not self.components:
            self.components = {
                Phase1Component.AUDIO_IO.value: {
                    "status": ComponentStatus.NOT_STARTED.value,
                    "progress": 0.0,
                    "notes": [],
                    "blockers": [],
                },
                Phase1Component.MIDI_ENGINE.value: {
                    "status": ComponentStatus.NOT_STARTED.value,
                    "progress": 0.0,
                    "notes": [],
                    "blockers": [],
                },
                Phase1Component.TRANSPORT.value: {
                    "status": ComponentStatus.NOT_STARTED.value,
                    "progress": 0.0,
                    "notes": [],
                    "blockers": [],
                },
                Phase1Component.MIXER.value: {
                    "status": ComponentStatus.NOT_STARTED.value,
                    "progress": 0.0,
                    "notes": [],
                    "blockers": [],
                },
                Phase1Component.DSP_GRAPH.value: {
                    "status": ComponentStatus.NOT_STARTED.value,
                    "progress": 0.0,
                    "notes": [],
                    "blockers": [],
                },
                Phase1Component.RECORDING.value: {
                    "status": ComponentStatus.NOT_STARTED.value,
                    "progress": 0.0,
                    "notes": [],
                    "blockers": [],
                },
            }

    def update_component(self, component: str, status: str = None, progress: float = None, note: str = None, blocker: str = None):
        if component in self.components:
            if status:
                self.components[component]["status"] = status
            if progress is not None:
                self.components[component]["progress"] = progress
            if note:
                self.components[component]["notes"].append({
                    "text": note,
                    "timestamp": datetime.now().isoformat(),
                })
            if blocker:
                self.components[component]["blockers"].append({
                    "text": blocker,
                    "timestamp": datetime.now().isoformat(),
                })

    def get_overall_progress(self) -> float:
        if not self.components:
            return 0.0
        total = sum(c.get("progress", 0) for c in self.components.values())
        return total / len(self.components)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "components": self.components,
            "overall_progress": self.get_overall_progress(),
            "overall_progress_pct": f"{self.get_overall_progress() * 100:.1f}%",
        }
