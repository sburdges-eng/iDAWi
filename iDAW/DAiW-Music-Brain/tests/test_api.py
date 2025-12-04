"""Tests for Music Brain API."""

import pytest
import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from music_brain.api import MusicBrain, GeneratedMusic
from music_brain.session.intent_schema import (
    CompleteSongIntent,
    SongRoot,
    SongIntent,
    TechnicalConstraints,
)


def test_music_brain_initialization():
    """Test MusicBrain initializes correctly."""
    brain = MusicBrain()
    assert brain.text_analyzer is not None
    assert brain.emotion_mapper is not None


def test_generate_from_text():
    """Test generating music from text."""
    brain = MusicBrain()
    music = brain.generate_from_text("grief and loss")

    assert isinstance(music, GeneratedMusic)
    assert music.emotional_state is not None
    assert music.musical_params is not None
    assert music.mixer_params is not None


def test_generate_from_text_anger():
    """Test generating music from angry text."""
    brain = MusicBrain()
    music = brain.generate_from_text("furious enraged angry")

    # Anger should have high arousal (>= 0.5 due to rounding)
    assert music.emotional_state.arousal >= 0.5
    # Anger should have negative valence
    assert music.emotional_state.valence < 0


def test_generate_from_text_joy():
    """Test generating music from joyful text."""
    brain = MusicBrain()
    music = brain.generate_from_text("joyful and euphoric")

    # Joy should have positive valence
    assert music.emotional_state.valence > 0


def test_generate_from_intent():
    """Test generating music from complete intent."""
    brain = MusicBrain()

    intent = CompleteSongIntent(
        song_root=SongRoot(
            core_event="Test event",
            core_longing="Test longing",
        ),
        song_intent=SongIntent(
            mood_primary="grief",
            mood_secondary_tension=0.5,
        ),
        technical_constraints=TechnicalConstraints(
            technical_key="F",
            technical_mode="major",
            technical_tempo_range=(80, 90),
        ),
    )

    music = brain.generate_from_intent(intent)

    assert isinstance(music, GeneratedMusic)
    assert music.musical_params.key_suggested == "F"
    assert music.musical_params.mode_suggested == "major"


def test_export_to_logic():
    """Test exporting to Logic Pro format."""
    brain = MusicBrain()
    music = brain.generate_from_text("grief")

    result = brain.export_to_logic(music, "test_export")

    assert "automation" in result
    automation_path = Path(result["automation"])
    assert automation_path.exists()

    # Verify JSON content
    with open(automation_path) as f:
        data = json.load(f)

    assert "project" in data
    assert "mixer_automation" in data

    # Cleanup
    automation_path.unlink()


def test_generated_music_to_dict():
    """Test GeneratedMusic serialization."""
    brain = MusicBrain()
    music = brain.generate_from_text("grief")

    data = music.to_dict()

    assert "emotional_state" in data
    assert "musical_params" in data
    assert "mixer_params" in data
    assert "valence" in data["emotional_state"]


def test_analyze_emotion():
    """Test emotion analysis API method."""
    brain = MusicBrain()
    matches = brain.analyze_emotion("bereaved and heartbroken")

    assert len(matches) > 0
    assert "emotion" in matches[0]
    assert "confidence" in matches[0]
    assert matches[0]["category"] == "sad"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
