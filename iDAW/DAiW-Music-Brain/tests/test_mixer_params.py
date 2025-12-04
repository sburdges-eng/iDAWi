"""Tests for mixer parameters."""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from music_brain.daw.mixer_params import MixerParams, EmotionToMixerMapper
from music_brain.data.emotional_mapping import EmotionalState


def test_mixer_params_defaults():
    """Test MixerParams has sensible defaults."""
    params = MixerParams()

    assert params.compression_ratio >= 1.0
    assert 0 <= params.reverb_mix <= 1.0
    assert -1.0 <= params.limiter_ceiling <= 0.0


def test_mixer_params_to_dict():
    """Test MixerParams serialization."""
    params = MixerParams()
    data = params.to_dict()

    assert "eq" in data
    assert "compression" in data
    assert "reverb" in data
    assert "saturation" in data


def test_mixer_params_from_dict():
    """Test MixerParams deserialization."""
    original = MixerParams(
        eq_bass=3.0,
        compression_ratio=6.0,
        reverb_mix=0.5,
    )

    data = original.to_dict()
    restored = MixerParams.from_dict(data)

    assert restored.eq_bass == 3.0
    assert restored.compression_ratio == 6.0
    assert restored.reverb_mix == 0.5


def test_mixer_params_json():
    """Test JSON round-trip."""
    params = MixerParams(eq_presence=4.0)
    json_str = params.to_json()
    restored = MixerParams.from_json(json_str)

    assert restored.eq_presence == 4.0


def test_emotion_to_mixer_mapper():
    """Test emotion mapping to mixer."""
    mapper = EmotionToMixerMapper()

    # Test grief mapping
    state = EmotionalState(
        valence=-0.7,
        arousal=0.3,
        primary_emotion="bereaved"
    )

    params = mapper.map_emotion_to_mixer(state)

    # Grief should have more reverb
    assert params.reverb_mix > 0.3
    # Grief should have darker EQ
    assert params.eq_air < 0


def test_emotion_to_mixer_anger():
    """Test anger mapping to mixer."""
    mapper = EmotionToMixerMapper()

    state = EmotionalState(
        valence=-0.6,
        arousal=0.9,
        primary_emotion="furious"
    )

    params = mapper.map_emotion_to_mixer(state)

    # Anger should have more compression
    assert params.compression_ratio > 4.0
    # Anger should have more saturation
    assert params.saturation > 0.2


def test_emotion_to_mixer_joy():
    """Test joy mapping to mixer."""
    mapper = EmotionToMixerMapper()

    state = EmotionalState(
        valence=0.8,
        arousal=0.7,
        primary_emotion="elated"
    )

    params = mapper.map_emotion_to_mixer(state)

    # Joy should have brighter EQ
    assert params.eq_presence > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
