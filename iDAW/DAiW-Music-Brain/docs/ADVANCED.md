# Advanced Usage

## Complete Intent Workflow

For maximum control, use the complete three-phase intent system.

### Phase 0: Core Wound/Desire

Define WHY the song exists:

```python
from music_brain.session.intent_schema import SongRoot

root = SongRoot(
    core_event="The moment I realized she was gone forever",
    core_resistance="I keep expecting her to walk through the door",
    core_longing="To feel her presence one more time",
    core_stakes="My sense of connection to the past",
    core_transformation="From raw grief to gentle remembrance",
)
```

### Phase 1: Emotional Intent

Define the emotional landscape:

```python
from music_brain.session.intent_schema import SongIntent

intent = SongIntent(
    mood_primary="grief",
    mood_secondary_tension=0.4,  # 0-1 scale
    imagery_texture="Faded photographs in autumn light",
    vulnerability_scale="High",  # Low/Medium/High
    narrative_arc="Slow Reveal",
)
```

### Phase 2: Technical Constraints

Define the musical implementation:

```python
from music_brain.session.intent_schema import TechnicalConstraints

constraints = TechnicalConstraints(
    technical_genre="lo-fi bedroom emo",
    technical_tempo_range=(78, 85),
    technical_key="F",
    technical_mode="major",
    technical_groove_feel="Laid Back",
    technical_rule_to_break="HARMONY_AvoidTonicResolution",
    rule_breaking_justification="The song should never feel resolved because grief doesn't resolve",
)
```

### Complete Generation

```python
from music_brain.api import MusicBrain
from music_brain.session.intent_schema import CompleteSongIntent

intent = CompleteSongIntent(
    title="For Kelly",
    song_root=root,
    song_intent=intent,
    technical_constraints=constraints,
)

brain = MusicBrain()
music = brain.generate_from_intent(intent)
brain.export_to_logic(music, "kelly_song")
```

## Rule Breaking Options

### Harmony Rules
- `HARMONY_AvoidTonicResolution` - Unresolved yearning
- `HARMONY_ParallelMotion` - Raw power, defiance
- `HARMONY_ModalInterchange` - Emotional complexity
- `HARMONY_TritoneSubstitution` - Jazz sophistication
- `HARMONY_Polytonality` - Internal conflict
- `HARMONY_UnresolvedDissonance` - Lingering tension

### Rhythm Rules
- `RHYTHM_ConstantDisplacement` - Anxiety, instability
- `RHYTHM_TempoFluctuation` - Human feel
- `RHYTHM_MetricModulation` - Mental state change
- `RHYTHM_PolyrhythmicLayers` - Complexity
- `RHYTHM_DroppedBeats` - Surprise, emphasis

### Production Rules
- `PRODUCTION_PitchImperfection` - Emotional honesty
- `PRODUCTION_RoomNoise` - Intimacy
- `PRODUCTION_Distortion` - Aggression
- `PRODUCTION_LoFiDegradation` - Nostalgia
- `PRODUCTION_SilenceAsInstrument` - Impact

## Custom Emotion Mapping

You can extend the emotion thesaurus:

```python
# Add custom emotion to sad.json
{
    "sub_emotions": {
        "your_custom_emotion": {
            "description": "Your description",
            "sub_sub_emotions": {
                "specific_feeling": {
                    "intensity_tiers": {
                        "1_subtle": ["word1", "word2"],
                        "2_mild": ["word3", "word4"],
                        "3_moderate": ["word5", "word6"],
                        "4_intense": ["word7", "word8"],
                        "5_overwhelming": ["word9", "word10"]
                    }
                }
            }
        }
    }
}
```

## Mixer Parameter Presets

Create custom mixer presets:

```python
from music_brain.daw.mixer_params import MixerParams

# Lo-fi preset
lofi = MixerParams(
    eq_bass=2.0,
    eq_low_mid=3.0,
    eq_presence=-3.0,
    eq_air=-5.0,
    compression_ratio=2.0,
    reverb_mix=0.4,
    reverb_decay=2.5,
    saturation=0.3,
    stereo_width=0.7,
)

# Export
lofi_json = lofi.to_json()
```

## API Reference

### MusicBrain

```python
class MusicBrain:
    def generate_from_text(self, text: str) -> GeneratedMusic
    def generate_from_intent(self, intent: CompleteSongIntent) -> GeneratedMusic
    def export_to_logic(self, music: GeneratedMusic, name: str) -> dict
    def analyze_emotion(self, text: str) -> list
```

### GeneratedMusic

```python
@dataclass
class GeneratedMusic:
    emotional_state: EmotionalState
    musical_params: MusicalParameters
    mixer_params: MixerParams
    intent: Optional[CompleteSongIntent]

    def to_dict(self) -> dict
```

### TextEmotionAnalyzer

```python
class TextEmotionAnalyzer:
    def analyze(self, text: str) -> List[EmotionMatch]
    def text_to_emotional_state(self, text: str) -> EmotionalState
```
