#!/usr/bin/env python3
"""
Kelly Song Logic Pro Export Example

Demonstrates the complete workflow from emotional intent
to Logic Pro automation using Music Brain.

Kelly's song is about:
- Core wound: Loss of a loved one
- Primary mood: Grief with moments of hope
- Technical: F major, 82 BPM, lo-fi bedroom emo
- Rule to break: Unresolved harmony (yearning)
"""

import sys
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from music_brain.api import MusicBrain
from music_brain.session.intent_schema import (
    CompleteSongIntent,
    SongRoot,
    SongIntent,
    TechnicalConstraints,
    SystemDirective,
)


def create_kelly_intent() -> CompleteSongIntent:
    """Create Kelly's complete song intent."""
    return CompleteSongIntent(
        title="For Kelly",
        song_root=SongRoot(
            core_event="The moment I realized she was gone forever",
            core_resistance="I keep expecting her to walk through the door",
            core_longing="To feel her presence one more time",
            core_stakes="My sense of connection to the past",
            core_transformation="From raw grief to gentle remembrance",
        ),
        song_intent=SongIntent(
            mood_primary="grief",
            mood_secondary_tension=0.4,
            imagery_texture="Faded photographs in autumn light",
            vulnerability_scale="High",
            narrative_arc="Slow Reveal",
        ),
        technical_constraints=TechnicalConstraints(
            technical_genre="lo-fi bedroom emo",
            technical_tempo_range=(78, 85),
            technical_key="F",
            technical_mode="major",
            technical_groove_feel="Laid Back",
            technical_rule_to_break="HARMONY_AvoidTonicResolution",
            rule_breaking_justification="The song should never feel 'resolved' because grief doesn't resolve",
        ),
        system_directive=SystemDirective(
            output_target="Logic Pro automation file",
            output_feedback_loop="Emotional mapping, mixer params",
        ),
    )


def main():
    print("=" * 70)
    print("KELLY SONG - EMOTION TO LOGIC PRO")
    print("=" * 70)

    # Create intent
    print("\n1. Creating song intent...")
    intent = create_kelly_intent()
    print(f"   Title: {intent.title}")
    print(f"   Core wound: {intent.song_root.core_event[:50]}...")
    print(f"   Primary mood: {intent.song_intent.mood_primary}")
    print(f"   Rule to break: {intent.technical_constraints.technical_rule_to_break}")

    # Initialize Music Brain
    print("\n2. Initializing Music Brain...")
    brain = MusicBrain()

    # Generate from intent
    print("\n3. Generating music parameters...")
    music = brain.generate_from_intent(intent)

    print(f"\n   EMOTIONAL STATE:")
    print(f"   - Primary emotion: {music.emotional_state.primary_emotion}")
    print(f"   - Valence: {music.emotional_state.valence:.2f} (negative=grief)")
    print(f"   - Arousal: {music.emotional_state.arousal:.2f} (low=slow)")

    print(f"\n   MUSICAL PARAMETERS:")
    print(f"   - Tempo: {music.musical_params.tempo_suggested} BPM")
    print(f"   - Key: {music.musical_params.key_suggested} {music.musical_params.mode_suggested}")
    print(f"   - Dissonance: {music.musical_params.dissonance:.1%}")
    print(f"   - Timing feel: {music.musical_params.timing_feel.value}")

    print(f"\n   MIXER SETTINGS (key values):")
    print(f"   - EQ Presence: {music.mixer_params.eq_presence:+.1f} dB")
    print(f"   - EQ Air: {music.mixer_params.eq_air:+.1f} dB")
    print(f"   - Compression ratio: {music.mixer_params.compression_ratio:.1f}:1")
    print(f"   - Reverb mix: {music.mixer_params.reverb_mix:.1%}")
    print(f"   - Reverb decay: {music.mixer_params.reverb_decay:.1f}s")
    print(f"   - Stereo width: {music.mixer_params.stereo_width:.1f}")

    # Export to Logic
    print("\n4. Exporting to Logic Pro...")
    result = brain.export_to_logic(music, "kelly_song", output_dir="output")

    print(f"\n   Created: {result['automation']}")

    # Show application guide
    print("\n5. APPLICATION GUIDE:")
    print("   a) Open Logic Pro X")
    print(f"   b) Create new project at 82 BPM in F major")
    print("   c) Open the automation JSON file")
    print("   d) Apply settings:")
    print(f"      - Channel EQ: Set presence to {music.mixer_params.eq_presence:+.1f} dB")
    print(f"      - Reverb: Mix {music.mixer_params.reverb_mix:.0%}, Decay {music.mixer_params.reverb_decay:.1f}s")
    print(f"      - Compressor: {music.mixer_params.compression_ratio:.1f}:1 ratio")
    print("   e) Record with the emotional intent in mind")

    print("\n" + "=" * 70)
    print("REMEMBER: 'The audience doesn't hear unresolved harmony.")
    print("          They hear that the song made them cry.'")
    print("=" * 70)


if __name__ == "__main__":
    main()
