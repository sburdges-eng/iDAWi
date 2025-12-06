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

from .thesaurus import (
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

__all__ = [
    # From emotional_mapping
    "EmotionalState",
    "MusicalParameters",
    "TimingFeel",
    "get_parameters_for_state",
    "emotion_to_valence_arousal",
    # From thesaurus
    "EmotionCategory",
    "MusicalMode",
    "DynamicLevel",
    "Articulation",
    "VADCoordinates",
    "MusicalCharacteristics",
    "EmotionNode",
    "EMOTION_NODES",
    "vad_to_musical_characteristics",
    "find_emotion_by_name",
    "find_emotion_by_synonym",
    "get_emotions_by_category",
    "get_emotions_by_intensity",
    "find_closest_emotion",
    "interpolate_emotions",
    "get_all_emotion_names",
]
