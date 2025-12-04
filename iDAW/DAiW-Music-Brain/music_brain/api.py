"""
Music Brain Public API.

High-level interface for emotion-to-music generation and Logic Pro export.
"""

import json
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, Optional, List

from music_brain.data.emotional_mapping import (
    EmotionalState,
    MusicalParameters,
    get_parameters_for_state,
)
from music_brain.daw.mixer_params import MixerParams, EmotionToMixerMapper
from music_brain.emotion.text_analyzer import TextEmotionAnalyzer
from music_brain.session.intent_schema import (
    CompleteSongIntent,
    SongRoot,
    SongIntent,
    TechnicalConstraints,
    AFFECT_MODE_MAP,
)


@dataclass
class GeneratedMusic:
    """
    Complete generated music specification.
    """
    emotional_state: EmotionalState
    musical_params: MusicalParameters
    mixer_params: MixerParams
    intent: Optional[CompleteSongIntent] = None

    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return {
            "emotional_state": {
                "valence": self.emotional_state.valence,
                "arousal": self.emotional_state.arousal,
                "primary_emotion": self.emotional_state.primary_emotion,
                "secondary_emotions": self.emotional_state.secondary_emotions,
            },
            "musical_params": {
                "tempo": self.musical_params.tempo_suggested,
                "key": self.musical_params.key_suggested,
                "mode": self.musical_params.mode_suggested,
                "dissonance": self.musical_params.dissonance,
                "density": self.musical_params.density,
                "timing_feel": self.musical_params.timing_feel.value,
                "dynamics_range": self.musical_params.dynamics_range,
                "reverb_amount": self.musical_params.reverb_amount,
                "brightness": self.musical_params.brightness,
            },
            "mixer_params": self.mixer_params.to_dict(),
        }


class MusicBrain:
    """
    Main Music Brain API class.

    Provides high-level methods for:
    - Text to emotion analysis
    - Emotion to musical parameters
    - Logic Pro export
    """

    def __init__(self):
        self.text_analyzer = TextEmotionAnalyzer()
        self.emotion_mapper = EmotionToMixerMapper()

    def generate_from_text(
        self,
        emotional_text: str
    ) -> GeneratedMusic:
        """
        Generate music from emotional text description.
        Uses sophisticated 216-node emotion analysis.

        Args:
            emotional_text: Natural language emotional description

        Returns:
            GeneratedMusic object with all parameters
        """
        # Use text analyzer
        emotional_state = self.text_analyzer.text_to_emotional_state(emotional_text)

        # Get musical parameters
        musical_params = get_parameters_for_state(emotional_state)

        # Map to mixer
        mixer_params = self.emotion_mapper.map_emotion_to_mixer(
            emotional_state,
            musical_params
        )

        return GeneratedMusic(
            emotional_state=emotional_state,
            musical_params=musical_params,
            mixer_params=mixer_params
        )

    def generate_from_intent(
        self,
        intent: CompleteSongIntent
    ) -> GeneratedMusic:
        """
        Generate music from a complete song intent.

        Args:
            intent: CompleteSongIntent object with all phases

        Returns:
            GeneratedMusic object
        """
        # Extract primary mood
        primary_mood = intent.song_intent.mood_primary.lower()

        # Get affect mapping if available
        affect_mapping = AFFECT_MODE_MAP.get(primary_mood, {})

        # Build emotional state from intent
        valence_map = {
            "grief": -0.8,
            "longing": -0.4,
            "defiance": -0.3,
            "hope": 0.5,
            "rage": -0.7,
            "tenderness": 0.6,
            "anxiety": -0.5,
            "euphoria": 0.9,
            "melancholy": -0.5,
            "nostalgia": 0.1,
            "catharsis": 0.3,
            "dissociation": -0.2,
            "determination": 0.4,
            "surrender": -0.3,
        }

        arousal_map = {
            "grief": 0.3,
            "longing": 0.4,
            "defiance": 0.8,
            "hope": 0.5,
            "rage": 1.0,
            "tenderness": 0.3,
            "anxiety": 0.8,
            "euphoria": 0.9,
            "melancholy": 0.2,
            "nostalgia": 0.3,
            "catharsis": 0.7,
            "dissociation": 0.2,
            "determination": 0.7,
            "surrender": 0.2,
        }

        emotional_state = EmotionalState(
            valence=valence_map.get(primary_mood, 0.0),
            arousal=arousal_map.get(primary_mood, 0.5),
            primary_emotion=primary_mood
        )

        # Get base musical params
        musical_params = get_parameters_for_state(emotional_state)

        # Override with technical constraints
        tc = intent.technical_constraints
        if tc.technical_tempo_range:
            musical_params.tempo_suggested = tc.technical_tempo_range[0]
        if tc.technical_key:
            musical_params.key_suggested = tc.technical_key
        if tc.technical_mode:
            musical_params.mode_suggested = tc.technical_mode

        # Map to mixer
        mixer_params = self.emotion_mapper.map_emotion_to_mixer(
            emotional_state,
            musical_params
        )

        return GeneratedMusic(
            emotional_state=emotional_state,
            musical_params=musical_params,
            mixer_params=mixer_params,
            intent=intent
        )

    def export_to_logic(
        self,
        music: GeneratedMusic,
        output_name: str,
        output_dir: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Export generated music to Logic Pro automation files.

        Args:
            music: GeneratedMusic object
            output_name: Base filename for output
            output_dir: Output directory (default: current directory)

        Returns:
            Dict with paths to generated files
        """
        if output_dir:
            out_path = Path(output_dir)
        else:
            out_path = Path.cwd()

        out_path.mkdir(parents=True, exist_ok=True)

        # Create automation JSON
        automation_file = out_path / f"{output_name}_automation.json"

        automation_data = {
            "project": output_name,
            "emotional_context": {
                "primary_emotion": music.emotional_state.primary_emotion,
                "valence": music.emotional_state.valence,
                "arousal": music.emotional_state.arousal,
            },
            "suggested_settings": {
                "tempo": music.musical_params.tempo_suggested,
                "key": music.musical_params.key_suggested,
                "mode": music.musical_params.mode_suggested,
            },
            "mixer_automation": music.mixer_params.to_dict(),
            "application_guide": {
                "step_1": "Create new Logic Pro project",
                "step_2": f"Set tempo to {music.musical_params.tempo_suggested} BPM",
                "step_3": f"Set key to {music.musical_params.key_suggested} {music.musical_params.mode_suggested}",
                "step_4": "Apply EQ settings from mixer_automation.eq",
                "step_5": "Configure compression from mixer_automation.compression",
                "step_6": "Set up reverb from mixer_automation.reverb",
            }
        }

        with open(automation_file, "w") as f:
            json.dump(automation_data, f, indent=2)

        return {
            "automation": str(automation_file),
        }

    def analyze_emotion(self, text: str) -> List[Dict]:
        """
        Analyze emotional text and return matches.

        Args:
            text: Text to analyze

        Returns:
            List of emotion match dictionaries
        """
        matches = self.text_analyzer.analyze(text)
        return [
            {
                "emotion": m.emotion,
                "category": m.category,
                "sub_emotion": m.sub_emotion,
                "confidence": m.confidence,
                "keywords": m.keywords_matched,
            }
            for m in matches
        ]


# Example usage
if __name__ == "__main__":
    brain = MusicBrain()

    print("=" * 70)
    print("MUSIC BRAIN API TEST")
    print("=" * 70)

    # Test text generation
    print("\n1. Generate from text:")
    music = brain.generate_from_text("grief and loss")

    print(f"   Primary emotion: {music.emotional_state.primary_emotion}")
    print(f"   Valence: {music.emotional_state.valence:.2f}")
    print(f"   Arousal: {music.emotional_state.arousal:.2f}")
    print(f"   Suggested tempo: {music.musical_params.tempo_suggested} BPM")
    print(f"   Suggested key: {music.musical_params.key_suggested}")
    print(f"   Reverb mix: {music.mixer_params.reverb_mix:.1%}")

    # Test export
    print("\n2. Export to Logic:")
    result = brain.export_to_logic(music, "test_output")
    print(f"   Created: {result['automation']}")

    print("\nPhase 1 verified!")
