"""
MCP Plugin Host - Data Models

Defines plugin formats, plugin metadata, presets, instances, and instrument models.
Supports VST3, AU, LV2, CLAP formats and built-in art-themed plugins.
"""

from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Any
import uuid


class PluginFormat(str, Enum):
    """Supported plugin formats."""
    VST3 = "vst3"
    AU = "au"           # Audio Unit (macOS)
    LV2 = "lv2"         # Linux
    CLAP = "clap"       # Cross-platform
    BUILTIN = "builtin"  # iDAWi built-in plugins


class PluginCategory(str, Enum):
    """Plugin categories for organization."""
    # Effects
    DYNAMICS = "dynamics"
    EQ = "eq"
    FILTER = "filter"
    DISTORTION = "distortion"
    MODULATION = "modulation"
    DELAY = "delay"
    REVERB = "reverb"
    PITCH = "pitch"
    UTILITY = "utility"
    SPECTRAL = "spectral"
    LOFI = "lofi"
    CREATIVE = "creative"

    # Instruments
    SYNTH = "synth"
    SAMPLER = "sampler"
    DRUM_MACHINE = "drum_machine"
    KEYS = "keys"
    ORCHESTRAL = "orchestral"

    # Other
    ANALYZER = "analyzer"
    GENERATOR = "generator"
    MIDI_EFFECT = "midi_effect"
    OTHER = "other"


class PluginType(str, Enum):
    """Plugin type classification."""
    EFFECT = "effect"
    INSTRUMENT = "instrument"
    MIDI_EFFECT = "midi_effect"
    ANALYZER = "analyzer"


class PluginStatus(str, Enum):
    """Plugin validation status."""
    UNKNOWN = "unknown"
    VALID = "valid"
    INVALID = "invalid"
    BLACKLISTED = "blacklisted"
    SCANNING = "scanning"


class InstanceStatus(str, Enum):
    """Plugin instance runtime status."""
    LOADING = "loading"
    READY = "ready"
    PROCESSING = "processing"
    BYPASSED = "bypassed"
    ERROR = "error"
    RELEASED = "released"


@dataclass
class PluginParameter:
    """A single plugin parameter."""
    id: str
    name: str
    value: float = 0.0
    default_value: float = 0.0
    min_value: float = 0.0
    max_value: float = 1.0
    step: float = 0.0  # 0 = continuous
    unit: str = ""
    is_automatable: bool = True
    is_hidden: bool = False
    group: str = ""  # Parameter group name

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PluginParameter":
        return cls(**data)


@dataclass
class PluginPreset:
    """A plugin preset/state."""
    id: str = ""
    name: str = ""
    plugin_id: str = ""
    plugin_format: PluginFormat = PluginFormat.VST3
    parameters: Dict[str, float] = field(default_factory=dict)
    state_data: str = ""  # Base64 encoded plugin state
    is_factory: bool = False
    is_favorite: bool = False
    tags: List[str] = field(default_factory=list)
    created_at: str = ""
    updated_at: str = ""

    def __post_init__(self):
        if not self.id:
            self.id = str(uuid.uuid4())[:8]
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
        self.updated_at = datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["plugin_format"] = self.plugin_format.value
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PluginPreset":
        if isinstance(data.get("plugin_format"), str):
            data["plugin_format"] = PluginFormat(data["plugin_format"])
        return cls(**data)


@dataclass
class Plugin:
    """
    Plugin metadata from discovery/scanning.

    Represents a plugin on disk, not a running instance.
    """
    id: str = ""
    name: str = ""
    vendor: str = ""
    version: str = ""
    description: str = ""

    # Format and type
    format: PluginFormat = PluginFormat.VST3
    plugin_type: PluginType = PluginType.EFFECT
    category: PluginCategory = PluginCategory.OTHER

    # File location
    path: str = ""
    bundle_path: str = ""  # For AU bundles

    # Status and validation
    status: PluginStatus = PluginStatus.UNKNOWN
    validation_error: str = ""
    last_scanned: str = ""

    # Capabilities
    has_editor: bool = True
    supports_midi: bool = False
    supports_mpe: bool = False
    is_synth: bool = False
    latency_samples: int = 0
    tail_samples: int = 0

    # Audio configuration
    num_inputs: int = 2
    num_outputs: int = 2
    num_aux_inputs: int = 0
    num_aux_outputs: int = 0

    # Organization
    tags: List[str] = field(default_factory=list)
    is_favorite: bool = False
    is_recently_used: bool = False
    use_count: int = 0
    last_used: Optional[str] = None

    # Performance stats
    avg_cpu_percent: float = 0.0
    peak_cpu_percent: float = 0.0
    avg_memory_mb: float = 0.0

    # Presets
    factory_presets: List[str] = field(default_factory=list)
    user_presets: List[str] = field(default_factory=list)

    def __post_init__(self):
        if not self.id:
            self.id = str(uuid.uuid4())[:8]

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["format"] = self.format.value
        data["plugin_type"] = self.plugin_type.value
        data["category"] = self.category.value
        data["status"] = self.status.value
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Plugin":
        if isinstance(data.get("format"), str):
            data["format"] = PluginFormat(data["format"])
        if isinstance(data.get("plugin_type"), str):
            data["plugin_type"] = PluginType(data["plugin_type"])
        if isinstance(data.get("category"), str):
            data["category"] = PluginCategory(data["category"])
        if isinstance(data.get("status"), str):
            data["status"] = PluginStatus(data["status"])
        return cls(**data)

    @property
    def display_name(self) -> str:
        """Format-qualified display name."""
        return f"{self.name} ({self.format.value.upper()})"

    def mark_used(self):
        """Mark plugin as recently used."""
        self.is_recently_used = True
        self.use_count += 1
        self.last_used = datetime.now().isoformat()


@dataclass
class PluginInstance:
    """
    A running plugin instance.

    Tracks instance state, parameters, and audio routing.
    """
    id: str = ""
    plugin_id: str = ""
    plugin_name: str = ""

    # Instance state
    status: InstanceStatus = InstanceStatus.LOADING
    is_bypassed: bool = False
    is_active: bool = True

    # Audio configuration
    sample_rate: float = 44100.0
    block_size: int = 512

    # Parameters (id -> value)
    parameters: Dict[str, float] = field(default_factory=dict)

    # Routing
    input_channel: int = 0
    output_channel: int = 0
    sidechain_input: Optional[int] = None

    # Current preset
    current_preset_id: Optional[str] = None
    current_preset_name: str = ""

    # Runtime metrics
    cpu_percent: float = 0.0
    memory_mb: float = 0.0

    # Timestamps
    created_at: str = ""

    def __post_init__(self):
        if not self.id:
            self.id = str(uuid.uuid4())[:8]
        if not self.created_at:
            self.created_at = datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["status"] = self.status.value
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PluginInstance":
        if isinstance(data.get("status"), str):
            data["status"] = InstanceStatus(data["status"])
        return cls(**data)


@dataclass
class PluginChain:
    """A chain of plugins for preset storage."""
    id: str = ""
    name: str = ""
    description: str = ""
    plugins: List[Dict[str, Any]] = field(default_factory=list)  # Plugin configs
    tags: List[str] = field(default_factory=list)
    is_favorite: bool = False
    created_at: str = ""
    updated_at: str = ""

    def __post_init__(self):
        if not self.id:
            self.id = str(uuid.uuid4())[:8]
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
        self.updated_at = datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PluginChain":
        return cls(**data)


# =============================================================================
# Instrument Hosting Models
# =============================================================================

class VoiceAllocationMode(str, Enum):
    """Voice allocation strategies for polyphonic instruments."""
    POLYPHONIC = "polyphonic"
    MONOPHONIC = "mono"
    LEGATO = "legato"
    UNISON = "unison"


class InstrumentLayerMode(str, Enum):
    """How multiple instruments are layered."""
    LAYER = "layer"      # Play all simultaneously
    SPLIT = "split"      # Keyboard split
    VELOCITY = "velocity"  # Velocity switch


@dataclass
class MIDIMapping:
    """MIDI CC to parameter mapping."""
    cc_number: int
    parameter_id: str
    min_value: float = 0.0
    max_value: float = 1.0
    is_inverted: bool = False
    curve: str = "linear"  # linear, exponential, logarithmic

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MIDIMapping":
        return cls(**data)


@dataclass
class InstrumentLayer:
    """A layer in an instrument rack."""
    id: str = ""
    name: str = ""
    plugin_instance_id: str = ""

    # Layer settings
    enabled: bool = True
    volume: float = 1.0
    pan: float = 0.0
    transpose: int = 0  # Semitones

    # Key range (for split)
    key_range_low: int = 0
    key_range_high: int = 127

    # Velocity range
    velocity_low: int = 0
    velocity_high: int = 127

    def __post_init__(self):
        if not self.id:
            self.id = str(uuid.uuid4())[:8]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "InstrumentLayer":
        return cls(**data)


@dataclass
class InstrumentRack:
    """
    Multi-instrument rack with layering and splits.

    Supports macro controls for unified parameter adjustment.
    """
    id: str = ""
    name: str = ""

    # Layers
    layers: List[InstrumentLayer] = field(default_factory=list)
    layer_mode: InstrumentLayerMode = InstrumentLayerMode.LAYER

    # Macro controls (1-8 macros)
    macros: Dict[str, float] = field(default_factory=dict)
    macro_mappings: Dict[str, List[Dict[str, Any]]] = field(default_factory=dict)

    # Voice settings
    max_voices: int = 64
    voice_mode: VoiceAllocationMode = VoiceAllocationMode.POLYPHONIC

    # MPE support
    mpe_enabled: bool = False
    mpe_zone: str = "lower"  # lower, upper, both

    # MIDI mappings
    midi_mappings: List[MIDIMapping] = field(default_factory=list)

    # State
    is_frozen: bool = False
    frozen_audio_path: Optional[str] = None

    created_at: str = ""
    updated_at: str = ""

    def __post_init__(self):
        if not self.id:
            self.id = str(uuid.uuid4())[:8]
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
        self.updated_at = datetime.now().isoformat()
        # Initialize 8 macros
        for i in range(1, 9):
            if f"macro_{i}" not in self.macros:
                self.macros[f"macro_{i}"] = 0.0

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["layer_mode"] = self.layer_mode.value
        data["voice_mode"] = self.voice_mode.value
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "InstrumentRack":
        if isinstance(data.get("layer_mode"), str):
            data["layer_mode"] = InstrumentLayerMode(data["layer_mode"])
        if isinstance(data.get("voice_mode"), str):
            data["voice_mode"] = VoiceAllocationMode(data["voice_mode"])
        if "layers" in data:
            data["layers"] = [InstrumentLayer.from_dict(l) for l in data["layers"]]
        if "midi_mappings" in data:
            data["midi_mappings"] = [MIDIMapping.from_dict(m) for m in data["midi_mappings"]]
        return cls(**data)


# =============================================================================
# Built-in Art-Themed Plugin Definitions
# =============================================================================

@dataclass
class BuiltinPluginSpec:
    """Specification for a built-in art-themed plugin."""
    name: str
    theme: str
    category: PluginCategory
    plugin_type: PluginType
    description: str
    parameters: List[Dict[str, Any]] = field(default_factory=list)
    priority: str = "medium"  # high, medium, low

    def to_plugin(self) -> Plugin:
        """Convert spec to Plugin instance."""
        return Plugin(
            id=f"builtin_{self.name.lower()}",
            name=self.name,
            vendor="iDAWi",
            version="1.0.0",
            description=self.description,
            format=PluginFormat.BUILTIN,
            plugin_type=self.plugin_type,
            category=self.category,
            path=f"builtin://{self.name.lower()}",
            status=PluginStatus.VALID,
            has_editor=True,
            supports_midi=self.plugin_type == PluginType.INSTRUMENT,
            tags=[self.theme, "builtin", "art-themed"]
        )


# Define the 11 art-themed plugins
ART_THEMED_PLUGINS: List[BuiltinPluginSpec] = [
    BuiltinPluginSpec(
        name="Pencil",
        theme="Sketching",
        category=PluginCategory.CREATIVE,
        plugin_type=PluginType.EFFECT,
        description="Waveform drawing and audio drafting. Sketch ideas quickly with freehand waveform editing.",
        priority="high",
        parameters=[
            {"id": "stroke_width", "name": "Stroke Width", "default": 0.5, "min": 0.0, "max": 1.0},
            {"id": "pressure", "name": "Pressure", "default": 0.7, "min": 0.0, "max": 1.0},
            {"id": "smoothing", "name": "Smoothing", "default": 0.3, "min": 0.0, "max": 1.0},
            {"id": "erase_mode", "name": "Erase Mode", "default": 0.0, "min": 0.0, "max": 1.0},
        ]
    ),
    BuiltinPluginSpec(
        name="Eraser",
        theme="Cleanup",
        category=PluginCategory.SPECTRAL,
        plugin_type=PluginType.EFFECT,
        description="Noise removal and spectral editing. Clean up recordings by erasing unwanted frequencies.",
        priority="high",
        parameters=[
            {"id": "threshold", "name": "Threshold", "default": 0.3, "min": 0.0, "max": 1.0},
            {"id": "strength", "name": "Strength", "default": 0.5, "min": 0.0, "max": 1.0},
            {"id": "smoothness", "name": "Smoothness", "default": 0.4, "min": 0.0, "max": 1.0},
            {"id": "frequency_band", "name": "Frequency Band", "default": 0.5, "min": 0.0, "max": 1.0},
        ]
    ),
    BuiltinPluginSpec(
        name="Press",
        theme="Dynamics",
        category=PluginCategory.DYNAMICS,
        plugin_type=PluginType.EFFECT,
        description="Multi-band compressor and limiter. Press audio into shape with dynamic control.",
        priority="high",
        parameters=[
            {"id": "threshold", "name": "Threshold", "default": 0.5, "min": 0.0, "max": 1.0},
            {"id": "ratio", "name": "Ratio", "default": 0.4, "min": 0.0, "max": 1.0},
            {"id": "attack", "name": "Attack", "default": 0.2, "min": 0.0, "max": 1.0},
            {"id": "release", "name": "Release", "default": 0.3, "min": 0.0, "max": 1.0},
            {"id": "makeup_gain", "name": "Makeup Gain", "default": 0.5, "min": 0.0, "max": 1.0},
            {"id": "num_bands", "name": "Bands", "default": 0.5, "min": 0.0, "max": 1.0},
        ]
    ),
    BuiltinPluginSpec(
        name="Palette",
        theme="Coloring",
        category=PluginCategory.EQ,
        plugin_type=PluginType.EFFECT,
        description="Tonal shaping and harmonic enhancement. Color your sound with spectral control.",
        priority="medium",
        parameters=[
            {"id": "warmth", "name": "Warmth", "default": 0.5, "min": 0.0, "max": 1.0},
            {"id": "brightness", "name": "Brightness", "default": 0.5, "min": 0.0, "max": 1.0},
            {"id": "saturation", "name": "Saturation", "default": 0.3, "min": 0.0, "max": 1.0},
            {"id": "harmonics", "name": "Harmonics", "default": 0.4, "min": 0.0, "max": 1.0},
            {"id": "color_blend", "name": "Color Blend", "default": 0.5, "min": 0.0, "max": 1.0},
        ]
    ),
    BuiltinPluginSpec(
        name="Smudge",
        theme="Blending",
        category=PluginCategory.CREATIVE,
        plugin_type=PluginType.EFFECT,
        description="Audio morphing and crossfading. Smudge between sounds for seamless transitions.",
        priority="medium",
        parameters=[
            {"id": "morph_amount", "name": "Morph Amount", "default": 0.5, "min": 0.0, "max": 1.0},
            {"id": "blend_time", "name": "Blend Time", "default": 0.4, "min": 0.0, "max": 1.0},
            {"id": "spectral_blend", "name": "Spectral Blend", "default": 0.5, "min": 0.0, "max": 1.0},
            {"id": "transient_preserve", "name": "Transient Preserve", "default": 0.6, "min": 0.0, "max": 1.0},
        ]
    ),
    BuiltinPluginSpec(
        name="Trace",
        theme="Automation",
        category=PluginCategory.UTILITY,
        plugin_type=PluginType.EFFECT,
        description="Pattern following and envelope shaping. Trace audio dynamics to create automation.",
        priority="low",
        parameters=[
            {"id": "sensitivity", "name": "Sensitivity", "default": 0.5, "min": 0.0, "max": 1.0},
            {"id": "smoothing", "name": "Smoothing", "default": 0.3, "min": 0.0, "max": 1.0},
            {"id": "attack", "name": "Attack", "default": 0.2, "min": 0.0, "max": 1.0},
            {"id": "release", "name": "Release", "default": 0.4, "min": 0.0, "max": 1.0},
            {"id": "output_mode", "name": "Output Mode", "default": 0.0, "min": 0.0, "max": 1.0},
        ]
    ),
    BuiltinPluginSpec(
        name="Parrot",
        theme="Sampling",
        category=PluginCategory.SAMPLER,
        plugin_type=PluginType.INSTRUMENT,
        description="Sample playback and phrase sampling. Capture and replay audio like a musical parrot.",
        priority="low",
        parameters=[
            {"id": "sample_start", "name": "Sample Start", "default": 0.0, "min": 0.0, "max": 1.0},
            {"id": "sample_end", "name": "Sample End", "default": 1.0, "min": 0.0, "max": 1.0},
            {"id": "loop_enabled", "name": "Loop", "default": 0.0, "min": 0.0, "max": 1.0},
            {"id": "pitch_shift", "name": "Pitch Shift", "default": 0.5, "min": 0.0, "max": 1.0},
            {"id": "time_stretch", "name": "Time Stretch", "default": 0.5, "min": 0.0, "max": 1.0},
        ]
    ),
    BuiltinPluginSpec(
        name="Stencil",
        theme="Sidechain",
        category=PluginCategory.DYNAMICS,
        plugin_type=PluginType.EFFECT,
        description="Sidechain ducking and pumping effects. Cut out space using the stencil of another signal.",
        priority="low",
        parameters=[
            {"id": "depth", "name": "Depth", "default": 0.7, "min": 0.0, "max": 1.0},
            {"id": "attack", "name": "Attack", "default": 0.1, "min": 0.0, "max": 1.0},
            {"id": "release", "name": "Release", "default": 0.3, "min": 0.0, "max": 1.0},
            {"id": "hold", "name": "Hold", "default": 0.1, "min": 0.0, "max": 1.0},
            {"id": "threshold", "name": "Threshold", "default": 0.4, "min": 0.0, "max": 1.0},
        ]
    ),
    BuiltinPluginSpec(
        name="Chalk",
        theme="Lo-fi",
        category=PluginCategory.LOFI,
        plugin_type=PluginType.EFFECT,
        description="Bitcrushing and audio degradation. Add gritty, textured character like chalk on concrete.",
        priority="low",
        parameters=[
            {"id": "bit_depth", "name": "Bit Depth", "default": 0.8, "min": 0.0, "max": 1.0},
            {"id": "sample_rate", "name": "Sample Rate", "default": 0.8, "min": 0.0, "max": 1.0},
            {"id": "noise", "name": "Noise", "default": 0.2, "min": 0.0, "max": 1.0},
            {"id": "grit", "name": "Grit", "default": 0.3, "min": 0.0, "max": 1.0},
            {"id": "wow_flutter", "name": "Wow/Flutter", "default": 0.1, "min": 0.0, "max": 1.0},
        ]
    ),
    BuiltinPluginSpec(
        name="Brush",
        theme="Modulation",
        category=PluginCategory.MODULATION,
        plugin_type=PluginType.EFFECT,
        description="Filtered modulation and sweeps. Paint with moving filters like brush strokes.",
        priority="low",
        parameters=[
            {"id": "rate", "name": "Rate", "default": 0.3, "min": 0.0, "max": 1.0},
            {"id": "depth", "name": "Depth", "default": 0.5, "min": 0.0, "max": 1.0},
            {"id": "filter_type", "name": "Filter Type", "default": 0.5, "min": 0.0, "max": 1.0},
            {"id": "resonance", "name": "Resonance", "default": 0.4, "min": 0.0, "max": 1.0},
            {"id": "wave_shape", "name": "Wave Shape", "default": 0.0, "min": 0.0, "max": 1.0},
        ]
    ),
    BuiltinPluginSpec(
        name="Stamp",
        theme="Repeater",
        category=PluginCategory.CREATIVE,
        plugin_type=PluginType.EFFECT,
        description="Stutter, beat repeat, and glitch effects. Stamp patterns repeatedly like a rubber stamp.",
        priority="low",
        parameters=[
            {"id": "rate", "name": "Rate", "default": 0.5, "min": 0.0, "max": 1.0},
            {"id": "repeats", "name": "Repeats", "default": 0.4, "min": 0.0, "max": 1.0},
            {"id": "decay", "name": "Decay", "default": 0.7, "min": 0.0, "max": 1.0},
            {"id": "pitch_shift", "name": "Pitch Shift", "default": 0.5, "min": 0.0, "max": 1.0},
            {"id": "filter", "name": "Filter", "default": 0.5, "min": 0.0, "max": 1.0},
            {"id": "random", "name": "Random", "default": 0.0, "min": 0.0, "max": 1.0},
        ]
    ),
]


def get_builtin_plugins() -> List[Plugin]:
    """Get all built-in art-themed plugins as Plugin instances."""
    return [spec.to_plugin() for spec in ART_THEMED_PLUGINS]


def get_builtin_plugin_specs() -> List[BuiltinPluginSpec]:
    """Get the raw specifications for built-in plugins."""
    return ART_THEMED_PLUGINS
