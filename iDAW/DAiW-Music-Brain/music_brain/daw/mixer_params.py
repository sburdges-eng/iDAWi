"""
Mixer Parameters for Logic Pro Integration.

Provides dataclasses and mappings for DAW mixer settings.
"""

from dataclasses import dataclass, field
from typing import Dict, Optional
import json


@dataclass
class MixerParams:
    """
    Complete mixer parameter set for Logic Pro.

    All values normalized to 0.0-1.0 range unless otherwise noted.
    """
    # EQ Parameters (dB values, -12 to +12)
    eq_sub_bass: float = 0.0       # 20-60 Hz
    eq_bass: float = 0.0           # 60-250 Hz
    eq_low_mid: float = 0.0        # 250-500 Hz
    eq_mid: float = 0.0            # 500-2000 Hz
    eq_high_mid: float = 0.0       # 2-6 kHz
    eq_presence: float = 0.0       # 6-12 kHz
    eq_air: float = 0.0            # 12-20 kHz

    # Compression
    compression_ratio: float = 2.0      # 1:1 to 20:1
    compression_threshold: float = -12.0  # dB
    compression_attack: float = 10.0      # ms
    compression_release: float = 100.0    # ms
    compression_makeup: float = 0.0       # dB

    # Reverb
    reverb_mix: float = 0.3          # 0-1 wet/dry
    reverb_decay: float = 1.5        # seconds
    reverb_predelay: float = 20.0    # ms
    reverb_size: float = 0.5         # 0-1
    reverb_damping: float = 0.5      # 0-1 high freq rolloff

    # Delay
    delay_mix: float = 0.0           # 0-1 wet/dry
    delay_time: float = 250.0        # ms
    delay_feedback: float = 0.3      # 0-1

    # Saturation/Warmth
    saturation: float = 0.0          # 0-1

    # Stereo Width
    stereo_width: float = 1.0        # 0-2 (1 = normal, 0 = mono, 2 = wide)

    # Dynamics
    limiter_ceiling: float = -0.3    # dB

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON export."""
        return {
            "eq": {
                "sub_bass": self.eq_sub_bass,
                "bass": self.eq_bass,
                "low_mid": self.eq_low_mid,
                "mid": self.eq_mid,
                "high_mid": self.eq_high_mid,
                "presence": self.eq_presence,
                "air": self.eq_air,
            },
            "compression": {
                "ratio": self.compression_ratio,
                "threshold": self.compression_threshold,
                "attack": self.compression_attack,
                "release": self.compression_release,
                "makeup": self.compression_makeup,
            },
            "reverb": {
                "mix": self.reverb_mix,
                "decay": self.reverb_decay,
                "predelay": self.reverb_predelay,
                "size": self.reverb_size,
                "damping": self.reverb_damping,
            },
            "delay": {
                "mix": self.delay_mix,
                "time": self.delay_time,
                "feedback": self.delay_feedback,
            },
            "saturation": self.saturation,
            "stereo_width": self.stereo_width,
            "limiter_ceiling": self.limiter_ceiling,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "MixerParams":
        """Create from dictionary."""
        params = cls()

        if "eq" in data:
            eq = data["eq"]
            params.eq_sub_bass = eq.get("sub_bass", 0.0)
            params.eq_bass = eq.get("bass", 0.0)
            params.eq_low_mid = eq.get("low_mid", 0.0)
            params.eq_mid = eq.get("mid", 0.0)
            params.eq_high_mid = eq.get("high_mid", 0.0)
            params.eq_presence = eq.get("presence", 0.0)
            params.eq_air = eq.get("air", 0.0)

        if "compression" in data:
            comp = data["compression"]
            params.compression_ratio = comp.get("ratio", 2.0)
            params.compression_threshold = comp.get("threshold", -12.0)
            params.compression_attack = comp.get("attack", 10.0)
            params.compression_release = comp.get("release", 100.0)
            params.compression_makeup = comp.get("makeup", 0.0)

        if "reverb" in data:
            rev = data["reverb"]
            params.reverb_mix = rev.get("mix", 0.3)
            params.reverb_decay = rev.get("decay", 1.5)
            params.reverb_predelay = rev.get("predelay", 20.0)
            params.reverb_size = rev.get("size", 0.5)
            params.reverb_damping = rev.get("damping", 0.5)

        if "delay" in data:
            delay = data["delay"]
            params.delay_mix = delay.get("mix", 0.0)
            params.delay_time = delay.get("time", 250.0)
            params.delay_feedback = delay.get("feedback", 0.3)

        params.saturation = data.get("saturation", 0.0)
        params.stereo_width = data.get("stereo_width", 1.0)
        params.limiter_ceiling = data.get("limiter_ceiling", -0.3)

        return params

    def to_json(self, indent: int = 2) -> str:
        """Export to JSON string."""
        return json.dumps(self.to_dict(), indent=indent)

    @classmethod
    def from_json(cls, json_str: str) -> "MixerParams":
        """Create from JSON string."""
        return cls.from_dict(json.loads(json_str))


class EmotionToMixerMapper:
    """
    Maps emotional states to mixer parameters.
    """

    # Emotion category presets
    EMOTION_PRESETS = {
        "grief": {
            "eq_bass": 2.0,
            "eq_low_mid": 1.0,
            "eq_presence": -2.0,
            "eq_air": -3.0,
            "compression_ratio": 2.5,
            "compression_attack": 30.0,
            "compression_release": 200.0,
            "reverb_mix": 0.5,
            "reverb_decay": 3.0,
            "reverb_predelay": 40.0,
            "reverb_size": 0.7,
            "saturation": 0.1,
            "stereo_width": 0.8,
        },
        "joy": {
            "eq_bass": -1.0,
            "eq_mid": 1.0,
            "eq_presence": 3.0,
            "eq_air": 4.0,
            "compression_ratio": 4.0,
            "compression_attack": 5.0,
            "compression_release": 50.0,
            "reverb_mix": 0.25,
            "reverb_decay": 1.0,
            "reverb_size": 0.4,
            "saturation": 0.2,
            "stereo_width": 1.3,
        },
        "anger": {
            "eq_bass": 3.0,
            "eq_low_mid": 2.0,
            "eq_mid": 1.0,
            "eq_high_mid": 4.0,
            "eq_presence": 2.0,
            "compression_ratio": 8.0,
            "compression_threshold": -18.0,
            "compression_attack": 1.0,
            "compression_release": 30.0,
            "reverb_mix": 0.15,
            "reverb_decay": 0.5,
            "saturation": 0.5,
            "stereo_width": 1.0,
        },
        "fear": {
            "eq_sub_bass": 3.0,
            "eq_bass": 2.0,
            "eq_low_mid": -2.0,
            "eq_presence": 2.0,
            "compression_ratio": 3.0,
            "compression_attack": 50.0,
            "reverb_mix": 0.4,
            "reverb_decay": 2.5,
            "reverb_predelay": 60.0,
            "delay_mix": 0.2,
            "delay_feedback": 0.5,
            "stereo_width": 0.6,
        },
        "surprise": {
            "eq_mid": 2.0,
            "eq_high_mid": 3.0,
            "eq_presence": 4.0,
            "eq_air": 3.0,
            "compression_ratio": 6.0,
            "compression_attack": 0.5,
            "reverb_mix": 0.35,
            "reverb_decay": 1.8,
            "delay_mix": 0.15,
            "stereo_width": 1.4,
        },
        "disgust": {
            "eq_bass": 4.0,
            "eq_low_mid": 3.0,
            "eq_mid": -2.0,
            "eq_presence": -3.0,
            "compression_ratio": 2.0,
            "reverb_mix": 0.2,
            "reverb_decay": 0.8,
            "saturation": 0.4,
            "stereo_width": 0.7,
        },
    }

    def map_emotion_to_mixer(
        self,
        emotional_state,
        musical_params=None
    ) -> MixerParams:
        """
        Map an emotional state to mixer parameters.

        Args:
            emotional_state: EmotionalState object
            musical_params: Optional MusicalParameters for additional context

        Returns:
            MixerParams object
        """
        # Start with default parameters
        params = MixerParams()

        # Find matching emotion category
        primary = emotional_state.primary_emotion.lower()

        # Check direct match
        preset = None
        for emotion, preset_data in self.EMOTION_PRESETS.items():
            if emotion in primary or primary in emotion:
                preset = preset_data
                break

        # Fall back to valence-based selection
        if preset is None:
            if emotional_state.valence < -0.3:
                if emotional_state.arousal > 0.5:
                    preset = self.EMOTION_PRESETS["anger"]
                else:
                    preset = self.EMOTION_PRESETS["grief"]
            else:
                preset = self.EMOTION_PRESETS["joy"]

        # Apply preset
        for key, value in preset.items():
            if hasattr(params, key):
                setattr(params, key, value)

        # Adjust based on arousal
        arousal = emotional_state.arousal

        # High arousal = more compression, brighter
        if arousal > 0.7:
            params.compression_ratio *= 1.2
            params.eq_presence += 1.0
            params.reverb_decay *= 0.8

        # Low arousal = more reverb, darker
        elif arousal < 0.3:
            params.reverb_mix *= 1.3
            params.reverb_decay *= 1.2
            params.eq_air -= 2.0

        # Adjust based on musical params if provided
        if musical_params:
            params.reverb_mix = musical_params.reverb_amount

            # Brightness
            brightness_boost = (musical_params.brightness - 0.5) * 6.0
            params.eq_presence += brightness_boost
            params.eq_air += brightness_boost * 0.5

        return params


# Convenience instance
emotion_mapper = EmotionToMixerMapper()
