"""
Emotion Analysis and Mapping Module.

Provides text-to-emotion analysis and emotional state mapping.
"""

from music_brain.data.emotional_mapping import (
    EmotionalState,
    MusicalParameters,
    TimingFeel,
    get_parameters_for_state,
    emotion_to_valence_arousal,
)

__all__ = [
    "EmotionalState",
    "MusicalParameters",
    "TimingFeel",
    "get_parameters_for_state",
    "emotion_to_valence_arousal",
]
