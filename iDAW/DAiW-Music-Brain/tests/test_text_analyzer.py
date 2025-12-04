"""Tests for text-to-emotion analyzer."""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from music_brain.emotion.text_analyzer import TextEmotionAnalyzer


def test_analyzer_initialization():
    """Test analyzer loads emotion data."""
    analyzer = TextEmotionAnalyzer()
    assert len(analyzer.emotion_data) >= 1  # At least one category
    assert len(analyzer.keyword_map) > 100  # Many keywords


def test_simple_grief_detection():
    """Test detecting grief from text."""
    analyzer = TextEmotionAnalyzer()
    matches = analyzer.analyze("bereaved heartbroken grief")

    assert len(matches) > 0
    assert matches[0].category == "sad"
    assert matches[0].confidence > 0.3


def test_anger_detection():
    """Test detecting anger."""
    analyzer = TextEmotionAnalyzer()
    matches = analyzer.analyze("furious enraged angry")

    assert len(matches) > 0
    assert matches[0].category == "anger"


def test_fear_detection():
    """Test detecting fear."""
    analyzer = TextEmotionAnalyzer()
    matches = analyzer.analyze("terrified and anxious")

    assert len(matches) > 0
    assert matches[0].category == "fear"


def test_joy_detection():
    """Test detecting joy."""
    analyzer = TextEmotionAnalyzer()
    matches = analyzer.analyze("joyful and euphoric")

    assert len(matches) > 0
    assert matches[0].category == "joy"


def test_emotional_state_generation():
    """Test converting text to emotional state."""
    analyzer = TextEmotionAnalyzer()
    state = analyzer.text_to_emotional_state("bereaved heartbroken grief")

    assert state.primary_emotion is not None
    assert state.valence < 0  # Grief is negative valence
    assert 0 <= state.arousal <= 1


def test_multiple_keywords():
    """Test confidence increases with more keywords."""
    analyzer = TextEmotionAnalyzer()

    matches1 = analyzer.analyze("sad")
    matches2 = analyzer.analyze("bereaved heartbroken devastated")

    # More keywords should give higher confidence
    if matches1 and matches2:
        assert matches2[0].confidence >= matches1[0].confidence


def test_no_match():
    """Test handling text with no emotion keywords."""
    analyzer = TextEmotionAnalyzer()
    matches = analyzer.analyze("the quick brown fox")

    assert len(matches) == 0


def test_emotional_state_defaults():
    """Test default values when no match found."""
    analyzer = TextEmotionAnalyzer()
    state = analyzer.text_to_emotional_state("xyz xyz xyz")

    assert state.primary_emotion == "neutral"
    assert state.valence == 0.0
    assert state.arousal == 0.5


def test_all_categories_loaded():
    """Test all 6 emotion categories are loaded."""
    analyzer = TextEmotionAnalyzer()
    expected_categories = {"sad", "joy", "anger", "fear", "surprise", "disgust"}
    actual_categories = set(analyzer.emotion_data.keys())

    assert expected_categories == actual_categories


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
