"""
Tests for the emotion thesaurus module.

Run with: pytest tests/test_emotion_thesaurus.py -v
"""

import pytest
import math
from music_brain.emotion.thesaurus import (
    EmotionCategory,
    MusicalMode,
    DynamicLevel,
    Articulation,
    VADCoordinates,
    MusicalCharacteristics,
    EmotionNode,
    EMOTION_NODES,
    vad_to_musical_characteristics,
    find_emotion_by_name,
    find_emotion_by_synonym,
    get_emotions_by_category,
    get_emotions_by_intensity,
    find_closest_emotion,
    interpolate_emotions,
    get_all_emotion_names,
)


class TestVADCoordinates:
    """Test VAD coordinate functionality."""
    
    def test_vad_creation(self):
        """Test basic VAD creation."""
        vad = VADCoordinates(0.5, -0.3, 0.2)
        assert vad.valence == 0.5
        assert vad.arousal == -0.3
        assert vad.dominance == 0.2
    
    def test_vad_clamping(self):
        """Test that values are clamped to -1 to 1 range."""
        vad = VADCoordinates(2.0, -3.0, 1.5)
        assert vad.valence == 1.0
        assert vad.arousal == -1.0
        assert vad.dominance == 1.0
    
    def test_vad_to_grid_position(self):
        """Test conversion to 6x6x6 grid position."""
        # Center of grid
        vad = VADCoordinates(0.0, 0.0, 0.0)
        pos = vad.to_grid_position()
        assert all(0 <= p <= 5 for p in pos)
        
        # Extreme negative
        vad = VADCoordinates(-1.0, -1.0, -1.0)
        pos = vad.to_grid_position()
        assert pos == (0, 0, 0)
        
        # Extreme positive
        vad = VADCoordinates(1.0, 1.0, 1.0)
        pos = vad.to_grid_position()
        assert pos == (5, 5, 5)
    
    def test_vad_distance(self):
        """Test distance calculation between VAD points."""
        vad1 = VADCoordinates(0.0, 0.0, 0.0)
        vad2 = VADCoordinates(1.0, 0.0, 0.0)
        
        distance = vad1.distance_to(vad2)
        assert abs(distance - 1.0) < 0.001
        
        # Distance to self is 0
        assert vad1.distance_to(vad1) == 0.0


class TestMusicalCharacteristics:
    """Test musical characteristics generation."""
    
    def test_tempo_range_by_arousal(self):
        """Test that tempo increases with arousal."""
        low_arousal = vad_to_musical_characteristics(VADCoordinates(0.0, -0.8, 0.0))
        high_arousal = vad_to_musical_characteristics(VADCoordinates(0.0, 0.8, 0.0))
        
        assert low_arousal.tempo_range[0] < high_arousal.tempo_range[0]
        assert low_arousal.tempo_range[1] < high_arousal.tempo_range[1]
    
    def test_mode_by_valence(self):
        """Test that mode changes with valence."""
        positive = vad_to_musical_characteristics(VADCoordinates(0.8, 0.0, 0.0))
        negative = vad_to_musical_characteristics(VADCoordinates(-0.8, 0.0, 0.0))
        
        # Positive valence tends toward major modes
        assert positive.mode in [MusicalMode.MAJOR, MusicalMode.LYDIAN]
        # Negative valence tends toward minor modes
        assert negative.mode in [MusicalMode.AEOLIAN, MusicalMode.PHRYGIAN, MusicalMode.DORIAN]
    
    def test_dynamics_by_dominance(self):
        """Test that dynamics change with dominance."""
        submissive = vad_to_musical_characteristics(VADCoordinates(0.0, 0.0, -0.8))
        dominant = vad_to_musical_characteristics(VADCoordinates(0.0, 0.0, 0.8))
        
        # Submissive tends toward softer dynamics
        assert submissive.dynamics in [DynamicLevel.PP, DynamicLevel.P, DynamicLevel.MP]
        # Dominant tends toward louder dynamics
        assert dominant.dynamics in [DynamicLevel.F, DynamicLevel.FF]
    
    def test_articulation_high_arousal(self):
        """Test articulation for high arousal emotions."""
        high_arousal_dominant = vad_to_musical_characteristics(VADCoordinates(0.0, 0.8, 0.5))
        assert high_arousal_dominant.articulation in [Articulation.MARCATO, Articulation.STACCATO]
    
    def test_instruments_selection(self):
        """Test instrument selection based on emotion."""
        joyful = vad_to_musical_characteristics(VADCoordinates(0.8, 0.5, 0.3))
        assert len(joyful.instruments) > 0
        assert any(inst in joyful.instruments for inst in ["piano", "strings", "brass"])


class TestEmotionNodes:
    """Test emotion node collection."""
    
    def test_emotion_nodes_exist(self):
        """Test that emotion nodes are defined."""
        assert len(EMOTION_NODES) > 0
    
    def test_minimum_emotions(self):
        """Test minimum required emotions exist."""
        required = ["joyful", "melancholy", "angry", "anxious", "neutral"]
        for emotion in required:
            assert emotion in EMOTION_NODES, f"Missing emotion: {emotion}"
    
    def test_all_categories_present(self):
        """Test that all emotion categories are represented."""
        categories = set(e.category for e in EMOTION_NODES.values())
        expected = {EmotionCategory.JOY, EmotionCategory.SADNESS, EmotionCategory.ANGER, 
                    EmotionCategory.FEAR, EmotionCategory.SURPRISE, EmotionCategory.DISGUST, 
                    EmotionCategory.NEUTRAL}
        assert categories == expected
    
    def test_intensity_levels(self):
        """Test that intensity levels are in valid range."""
        for emotion in EMOTION_NODES.values():
            assert 1 <= emotion.intensity_level <= 6
    
    def test_vad_values_in_range(self):
        """Test that all VAD values are in valid range."""
        for emotion in EMOTION_NODES.values():
            assert -1 <= emotion.vad.valence <= 1
            assert -1 <= emotion.vad.arousal <= 1
            assert -1 <= emotion.vad.dominance <= 1
    
    def test_synonyms_exist(self):
        """Test that emotions have synonyms."""
        for emotion in EMOTION_NODES.values():
            assert len(emotion.synonyms) > 0, f"{emotion.name} has no synonyms"


class TestEmotionLookup:
    """Test emotion lookup functions."""
    
    def test_find_by_name(self):
        """Test finding emotion by name."""
        emotion = find_emotion_by_name("joyful")
        assert emotion is not None
        assert emotion.name == "Joyful"
    
    def test_find_by_name_case_insensitive(self):
        """Test that name lookup is case-insensitive."""
        upper = find_emotion_by_name("JOYFUL")
        lower = find_emotion_by_name("joyful")
        mixed = find_emotion_by_name("JoYfUl")
        
        assert upper is not None
        assert lower is not None
        assert mixed is not None
    
    def test_find_nonexistent_name(self):
        """Test that finding non-existent name returns None."""
        result = find_emotion_by_name("nonexistent_emotion")
        assert result is None
    
    def test_find_by_synonym(self):
        """Test finding emotion by synonym."""
        emotion = find_emotion_by_synonym("euphoric")
        assert emotion is not None
        assert emotion.name == "Ecstatic"  # euphoric is a synonym for ecstatic
    
    def test_find_by_synonym_case_insensitive(self):
        """Test that synonym lookup is case-insensitive."""
        emotion = find_emotion_by_synonym("EUPHORIC")
        assert emotion is not None
    
    def test_find_nonexistent_synonym(self):
        """Test that finding non-existent synonym returns None."""
        result = find_emotion_by_synonym("nonexistent_synonym_xyz")
        assert result is None


class TestEmotionFiltering:
    """Test emotion filtering functions."""
    
    def test_get_by_category(self):
        """Test getting emotions by category."""
        joy_emotions = get_emotions_by_category(EmotionCategory.JOY)
        assert len(joy_emotions) > 0
        assert all(e.category == EmotionCategory.JOY for e in joy_emotions)
    
    def test_get_by_intensity(self):
        """Test getting emotions by intensity level."""
        intense = get_emotions_by_intensity(6)
        assert len(intense) > 0
        assert all(e.intensity_level == 6 for e in intense)
    
    def test_get_all_names(self):
        """Test getting all emotion names."""
        names = get_all_emotion_names()
        assert len(names) == len(EMOTION_NODES)
        assert all(isinstance(n, str) for n in names)


class TestEmotionSpatial:
    """Test spatial emotion functions."""
    
    def test_find_closest_emotion(self):
        """Test finding closest emotion to VAD coordinates."""
        # Near joyful
        vad = VADCoordinates(0.8, 0.7, 0.5)
        closest = find_closest_emotion(vad)
        assert closest.name == "Joyful"
    
    def test_find_closest_extreme_values(self):
        """Test finding closest emotion at extreme values."""
        # Extreme positive valence and arousal
        vad = VADCoordinates(1.0, 1.0, 0.8)
        closest = find_closest_emotion(vad)
        assert closest.name == "Ecstatic"
    
    def test_find_closest_neutral(self):
        """Test finding closest emotion at neutral position."""
        vad = VADCoordinates(0.0, 0.0, 0.0)
        closest = find_closest_emotion(vad)
        # Should be neutral or a nearby emotion
        assert closest is not None
    
    def test_interpolate_emotions(self):
        """Test interpolating between two emotions."""
        joy = EMOTION_NODES["joyful"]
        sad = EMOTION_NODES["melancholy"]
        
        # Midpoint
        mid = interpolate_emotions(joy, sad, 0.5)
        expected_v = (joy.vad.valence + sad.vad.valence) / 2
        expected_a = (joy.vad.arousal + sad.vad.arousal) / 2
        expected_d = (joy.vad.dominance + sad.vad.dominance) / 2
        
        assert abs(mid.valence - expected_v) < 0.001
        assert abs(mid.arousal - expected_a) < 0.001
        assert abs(mid.dominance - expected_d) < 0.001
    
    def test_interpolate_at_extremes(self):
        """Test interpolation at t=0 and t=1."""
        joy = EMOTION_NODES["joyful"]
        sad = EMOTION_NODES["melancholy"]
        
        # t=0 should be emotion1
        start = interpolate_emotions(joy, sad, 0.0)
        assert abs(start.valence - joy.vad.valence) < 0.001
        
        # t=1 should be emotion2
        end = interpolate_emotions(joy, sad, 1.0)
        assert abs(end.valence - sad.vad.valence) < 0.001
    
    def test_interpolate_clamping(self):
        """Test that interpolation clamps t to [0, 1]."""
        joy = EMOTION_NODES["joyful"]
        sad = EMOTION_NODES["melancholy"]
        
        below = interpolate_emotions(joy, sad, -0.5)
        above = interpolate_emotions(joy, sad, 1.5)
        
        # Should clamp to endpoints
        assert abs(below.valence - joy.vad.valence) < 0.001
        assert abs(above.valence - sad.vad.valence) < 0.001


class TestMusicalModeMapping:
    """Test musical mode mapping logic."""
    
    def test_positive_valence_modes(self):
        """Test that positive valence maps to major-family modes."""
        for v in [0.6, 0.8, 1.0]:
            music = vad_to_musical_characteristics(VADCoordinates(v, 0.0, 0.0))
            assert music.mode in [MusicalMode.MAJOR, MusicalMode.LYDIAN]
    
    def test_negative_valence_modes(self):
        """Test that negative valence maps to minor-family modes."""
        for v in [-0.6, -0.8, -1.0]:
            music = vad_to_musical_characteristics(VADCoordinates(v, 0.0, 0.0))
            assert music.mode in [MusicalMode.AEOLIAN, MusicalMode.PHRYGIAN, MusicalMode.DORIAN]
    
    def test_neutral_valence_modes(self):
        """Test that neutral valence maps to mixolydian or dorian."""
        music = vad_to_musical_characteristics(VADCoordinates(0.0, 0.0, 0.0))
        assert music.mode in [MusicalMode.MIXOLYDIAN, MusicalMode.DORIAN]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
