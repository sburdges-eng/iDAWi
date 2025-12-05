# GitHub Copilot Instructions for DAiW-Music-Brain

## Project Overview

**DAiW-Music-Brain** is a Python toolkit and knowledge base for emotionally-driven music composition. The core philosophy is **"Interrogate Before Generate"** - emotional/creative intent should drive technical decisions, not the other way around.

### Core Philosophy

> "The tool shouldn't finish art for people. It should make them braver."

- **Emotional intent drives technical choices** - Never generate without understanding the "why"
- **Rules are broken intentionally** - Every rule break requires emotional justification
- **Human imperfection is valued** - Lo-fi, pitch drift, timing variation are features
- **Phase 0 must come first** - Technical decisions can't be made without emotional clarity
- **Teaching over finishing** - Educate and empower, not just generate

---

## Key Concepts

### Three-Phase Intent Schema

1. **Phase 0: Core Wound/Desire** - Deep interrogation
   - `core_event` - What happened?
   - `core_resistance` - What holds you back?
   - `core_longing` - What do you want to feel?
   - `core_stakes` - What's at risk?
   - `core_transformation` - How should you feel when done?

2. **Phase 1: Emotional Intent** - Validated by Phase 0
   - `mood_primary` - Dominant emotion (grief, anxiety, nostalgia, etc.)
   - `mood_secondary_tension` - Internal conflict (0.0-1.0)
   - `vulnerability_scale` - Low/Medium/High
   - `narrative_arc` - Climb-to-Climax, Slow Reveal, Repetitive Despair, etc.

3. **Phase 2: Technical Constraints** - Implementation
   - `technical_genre`, `technical_key`, `technical_mode`
   - `technical_rule_to_break` - Intentional rule violation
   - `rule_breaking_justification` - WHY break this rule (required!)

### Rule-Breaking Categories

When suggesting code that breaks music theory rules, ALWAYS provide emotional justification:

- **HARMONY_AvoidTonicResolution** - Unresolved yearning
- **HARMONY_ModalInterchange** - Bittersweet color (e.g., Bbm in F major = "borrowed sadness")
- **HARMONY_ParallelMotion** - Power, unity, medieval quality
- **RHYTHM_ConstantDisplacement** - Anxiety, unease
- **RHYTHM_TempoFluctuation** - Organic breathing, human intimacy
- **ARRANGEMENT_BuriedVocals** - Dissociation, dreamlike distance
- **PRODUCTION_PitchImperfection** - Emotional honesty, vulnerability

### Groove System

**Philosophy:** *"Feel isn't random - it's systematic deviation from the grid."*

- **Swing**: 50% = straight, 58-62% = funk/soul, 66% = jazz triplet
- **Push/Pull**: Per-instrument timing (kick +15ms = ahead, snare -8ms = laid back)
- **Humanization**: Slight velocity/timing variations (±5 velocity, ±30ms timing)

Genre templates available: funk, boom-bap, dilla, trap, straight

---

## Code Structure

### Main Package: `music_brain/`

```
music_brain/
├── __init__.py              # Public API exports
├── cli.py                   # CLI entry point (daiw command)
├── data/                    # JSON/YAML data files
│   ├── chord_progressions.json
│   ├── genre_pocket_maps.json
│   ├── song_intent_schema.yaml
│   ├── emotional_mapping.py        # Emotion → musical parameters
│   ├── chord_progression_families.json  # Comprehensive progressions
│   └── music_vernacular_database.md     # Casual language → technical
├── groove/                  # Groove extraction & application
│   ├── extractor.py         # extract_groove(), GrooveTemplate
│   ├── applicator.py        # apply_groove()
│   └── templates.py         # Genre templates
├── structure/               # Harmonic analysis
│   ├── chord.py             # Chord, ChordProgression, analyze_chords()
│   ├── progression.py       # diagnose_progression(), generate_reharmonizations()
│   └── sections.py          # Section detection
├── session/                 # Intent schema & teaching
│   ├── intent_schema.py     # CompleteSongIntent, rule-breaking enums
│   ├── intent_processor.py  # process_intent(), IntentProcessor
│   ├── teaching.py          # RuleBreakingTeacher
│   └── interrogator.py      # SongInterrogator
├── audio/                   # Audio feel analysis
│   └── feel.py              # analyze_feel(), AudioFeatures
└── utils/                   # Utilities
    ├── midi_io.py           # MIDI file handling
    ├── instruments.py       # Instrument mappings
    └── ppq.py               # PPQ normalization
```

### Key Files

- **`data/emotional_mapping.py`** (565 lines) - Maps emotional states (valence, arousal) to musical parameters (tempo, mode, dissonance, timing feel)
- **`data/chord_progression_families.json`** (349 lines) - Genre/emotion-tagged progressions
- **`data/music_vernacular_database.md`** (388 lines) - "boots and cats" → technical parameters
- **`session/intent_schema.py`** - Heart of the three-phase intent system
- **`groove/templates.py`** - Genre groove definitions
- **`structure/progression.py`** - Chord parsing and diagnosis

### Tools

- **`tools/audio_cataloger/`** - Scan audio files, detect BPM/key with librosa

### Vault (Knowledge Base)

- **`vault/Songwriting_Guides/`** - Intent schema docs, rule-breaking guides
- **`vault/Theory_Reference/`** - Music theory reference
- **`vault/Songs/when-i-found-you-sleeping/`** - Complete Kelly song project documentation

---

## Coding Guidelines

### Data Classes Over Dicts

```python
from dataclasses import dataclass

@dataclass
class EmotionalState:
    valence: float  # -1 (negative) to +1 (positive)
    arousal: float  # 0 (calm) to 1 (energetic)
    primary_emotion: str
```

### Enums for Categories

```python
from enum import Enum

class HarmonyRuleBreak(Enum):
    MODAL_INTERCHANGE = "HARMONY_ModalInterchange"
    PARALLEL_MOTION = "HARMONY_ParallelMotion"
    UNRESOLVED_DISSONANCE = "HARMONY_UnresolvedDissonance"
```

### Serialization Pattern

```python
def to_dict(self) -> dict:
    """Convert to dictionary for JSON serialization."""
    ...

@classmethod
def from_dict(cls, data: dict):
    """Load from dictionary."""
    ...
```

### Lazy Imports for CLI

```python
def get_harmony_module():
    """Lazy import to speed up CLI startup."""
    from music_brain.structure import progression
    return progression
```

---

## Common Patterns

### 1. Intent-Based Generation

```python
from music_brain.session.intent_schema import CompleteSongIntent
from music_brain.session.intent_processor import process_intent

intent = CompleteSongIntent(
    song_root=SongRoot(core_event="Finding someone I loved after they chose to leave"),
    song_intent=SongIntent(mood_primary="Grief", vulnerability_scale="High"),
    technical_constraints=TechnicalConstraints(
        technical_key="F",
        technical_rule_to_break="HARMONY_ModalInterchange",
        rule_breaking_justification="Bbm makes hope feel earned and bittersweet"
    )
)

result = process_intent(intent)
```

### 2. Groove Application

```python
from music_brain.groove.applicator import GrooveApplicator

applicator = GrooveApplicator()
funk_groove = applicator.get_genre_template('funk')

applicator.apply_groove(
    input_midi_path="drums_quantized.mid",
    output_midi_path="drums_funky.mid",
    groove=funk_groove,
    intensity=0.8  # 80% of groove effect
)
```

### 3. Chord Progression Analysis

```python
from music_brain.structure.progression import diagnose_progression

result = diagnose_progression("F-C-Dm-Bbm", key="F major")
# Returns emotional character, rule breaks, suggestions
```

### 4. Emotional → Musical Mapping

```python
from music_brain.data.emotional_mapping import EmotionalState, get_parameters_for_state

state = EmotionalState(
    valence=-0.8,  # Very negative
    arousal=0.3,   # Low energy
    primary_emotion="grief"
)

params = get_parameters_for_state(state)
# Returns: tempo_suggested=72, mode_weights={'minor': 0.6, 'dorian': 0.3}, etc.
```

---

## Important Conventions

### Tempo Ranges by Emotion

```python
EMOTIONAL_PRESETS = {
    "grief": (60-82 BPM, minor/dorian, behind beat, 30% dissonance),
    "anxiety": (100-140 BPM, phrygian/locrian, ahead beat, 60% dissonance),
    "nostalgia": (70-90 BPM, mixolydian, behind beat, 25% dissonance),
    "anger": (120-160 BPM, phrygian, ahead beat, 50% dissonance),
    "calm": (60-80 BPM, major/lydian, behind beat, 10% dissonance)
}
```

### Timing Feel

- **Behind the beat**: Laid back, reflective (lo-fi, bedroom emo) - offset +10 to +30ms
- **On the beat**: Precise, focused (pop, electronic) - offset ±5ms
- **Ahead of the beat**: Urgent, anxious (punk, thrash) - offset -10 to -30ms

### Vernacular Translations

When users say casual terms, translate to technical:
- "fat and laid back" → `eq.low_mid: +3dB, groove.pocket: "behind", swing: 0.55`
- "boots and cats" → Basic 4/4 beat pattern
- "chugga chugga" → Palm-muted power chords, 8th notes
- "Axis of Awesome" → I-V-vi-IV progression

---

## Reference Examples

### The Misdirection Technique (Kelly Song)

```python
# F-C-Am-Dm in D minor context
# Progression appears major-leaning (hopeful) but resolves to minor tonic (grief)

progression = {
    "chords": ["F", "C", "Am", "Dm"],
    "key": "D minor",
    "emotional_arc": "Hope → reality check",
    "technique": "Major progression → Minor tonic gut punch",
    "rule_break": "HARMONY_ModalInterchange"
}
```

This is the core of lo-fi bedroom emo: vulnerability through harmonic subversion.

### Interval Tension Mapping

```python
INTERVAL_EMOTIONS = {
    "P1": 0.0,    # No tension
    "m2": 0.9,    # High tension, cluster
    "M3": 0.1,    # Bright, consonant
    "tritone": 1.0,  # Maximum tension
    "P5": 0.1,    # Very stable
    "m7": 0.6,    # Bluesy tension
    "M7": 0.85    # Sharp dissonance
}
```

---

## CLI Commands Reference

```bash
# Groove operations
daiw extract drums.mid
daiw apply --genre funk track.mid

# Chord analysis
daiw analyze --chords song.mid
daiw diagnose "F-C-Am-Dm"
daiw reharm "F-C-Am-Dm" --style jazz

# Intent-based generation
daiw intent new --title "My Song"
daiw intent process my_intent.json
daiw intent suggest grief
daiw intent validate my_intent.json

# Teaching
daiw teach rulebreaking
```

---

## Testing Patterns

```python
import pytest
from music_brain.structure.chord import Chord

def test_chord_parsing():
    chord = Chord.from_string("Cmaj7")
    assert chord.root == "C"
    assert chord.quality == "maj7"
```

---

## Meta Principles for Copilot

When generating code:

1. **Always ask "why" before "how"** - If user wants Bbm in F major, ask about emotional intent
2. **Preserve imperfection** - Don't quantize to perfect grid unless explicitly requested
3. **Teach theory in context** - Explain rule-breaking with emotional justification
4. **Match emotion to harmony** - Use emotional_mapping.py as reference
5. **Natural language first** - Support vernacular input (music_vernacular_database.md)

### Example Interaction

**User:** "Make it sound sad"

**Bad Response:** ✗ Generate Am chord progression

**Good Response:** ✓
1. Ask: "What kind of sad? Grief (minor, 60-82 BPM), melancholy (dorian, 70-90 BPM), or bittersweet (modal interchange)?"
2. Suggest rule-breaking: "Would unresolved cadences (ending on IV or vi) serve the emotion?"
3. Offer interrogation prompts from emotional_mapping.py

---

## Important Notes

- **Line length**: 100 characters (configured in pyproject.toml)
- **Formatter**: black
- **Linter**: flake8, mypy
- **Python version**: 3.9+
- **Dependencies**: mido, numpy (core); librosa, soundfile (optional audio)

---

## Project Status

- **Phase 1**: 92% complete (core systems implemented)
- **Current focus**: Integration, CLI commands, test coverage
- **Kelly song**: Ready for production (MIDI files in examples/midi/)

---

## Quick References

### Emotion Presets (emotional_mapping.py)
- grief, anxiety, nostalgia, anger, calm

### Genre Grooves (groove/templates.py)
- funk (58% swing), boom-bap (54%), dilla (62%), trap (51%), straight

### Rule Breaks (intent_schema.py)
- Harmony: 12+ types (modal interchange, parallel motion, etc.)
- Rhythm: 8+ types (meter ambiguity, constant displacement, etc.)
- Arrangement: 6+ types (buried vocals, extreme dynamics, etc.)
- Production: 5+ types (pitch imperfection, excessive mud, etc.)

### Chord Progressions (chord_progression_families.json)
- Universal: I-IV-V-I, I-V-vi-IV, etc.
- Jazz: ii-V-I, rhythm changes
- Blues: 12-bar, 8-bar, minor blues
- Rock: Mixolydian vamp, power progressions
- EDM: Minor anthems, festival builds
- Gospel: Turnarounds, walkdowns

---

## Quick Commands for iDAW

Project-specific prompts for common development tasks. Copy and customize as needed.

### TypeScript Component Creation

```
/create-component [COMPONENT_NAME]

Create a new React component for iDAW with:
- TypeScript with strict types
- Use Zustand store from `src/store/useStore.ts` for state management
- WebSocket/IPC communication with 16ms debounce for backend calls
- Tailwind CSS using core utilities only (no custom classes)
- Framer Motion for animations (if needed)
- Place in `src/components/SideA/` (audio) or `src/components/SideB/` (emotion)

Example structure:
```tsx
import { useStore } from '../../store/useStore';
import { motion } from 'framer-motion';

interface Props {
  // Props with strict types
}

export const [COMPONENT_NAME]: React.FC<Props> = (props) => {
  const { /* destructure needed state */ } = useStore();
  // Component logic
  return <div className="/* Tailwind classes */">...</div>;
};
```
```

### Zustand Slice Pattern

```
/create-slice [SLICE_NAME]

Add a new slice to the Zustand store in `src/store/useStore.ts`:

1. Define TypeScript interface for the slice state
2. Add state properties with defaults
3. Add action methods following existing patterns
4. Include in the persist partialize if needed

Pattern:
```typescript
// Types
export interface [SLICE_NAME]State {
  // State properties
}

// In AppState interface, add:
// [sliceName]: [SLICE_NAME]State;
// update[SliceName]: (updates: Partial<[SLICE_NAME]State>) => void;

// In create():
[sliceName]: { /* defaults */ },
update[SliceName]: (updates) => set((state) => ({
  [sliceName]: { ...state.[sliceName], ...updates },
})),
```
```

### Emotion Mapping Commands

```
/add-emotion [EMOTION_NAME]

Add emotion mapping to the project:

1. Update Python thesaurus (`emotion_thesaurus.py`):
   - Add to BASE_EMOTIONS if new base emotion
   - Add sub_emotions and sub_sub_emotions with intensity tiers
   - Include synonyms for each intensity tier (1-6)

2. Update TypeScript frontend (`src/store/useStore.ts`):
   - Add to SongIntent interface if extending core emotions
   - Update coreEmotion/subEmotion defaults if needed

3. Emotion characteristics to define:
   - valence: negative/mixed/positive
   - arousal_range: [low, high] from 0.0 to 1.0
   - tempo_range: BPM range
   - mode_weights: minor/dorian/phrygian/major/lydian/mixolydian
   - timing_feel: ahead/on/behind
   - dissonance_level: percentage 0-100%
```

```
/map-emotion-to-params [EMOTION]

Get musical parameters for an emotion:
- Reference `data/emotional_mapping.py` for emotion → parameter mapping
- Check `DAiW_Cheat_Sheet.md` for quick lookup table
- Apply the Three-Phase Intent Schema (Phase 0 → 1 → 2)
```

### Debugging Commands

```
/debug-audio

Check audio engine issues:
1. Verify RT-safety: No allocations in audio callbacks
2. Check for lock-free communication between Side A and Side B
3. Verify `isAudioThread()` assertions
4. Check ring buffer flow: Side B → Side A

Files to inspect:
- `iDAW_Core/` for JUCE plugin issues
- `python/penta_core/` for Python bindings
- `external/readerwriterqueue/` for lock-free queue issues
```

```
/debug-state

Check Zustand state issues:
1. Verify state shape in `src/store/useStore.ts`
2. Check persist configuration for local storage
3. Verify selector optimization (avoid re-renders)
4. Check action immutability patterns

Console debug:
```typescript
// Add to component for state debugging
const state = useStore.getState();
console.log('Current state:', state);
```
```

```
/debug-ipc

Check Tauri IPC communication:
1. Verify command definitions in `src-tauri/src/`
2. Check invoke calls use correct command names
3. Verify payload serialization matches Rust types
4. Check 16ms debounce is applied for frequent updates
```

### Build & Test Commands

```
/build-check

Run full build verification:
```bash
# TypeScript check
cd iDAW/iDAWi && npm run type-check

# Lint check
cd iDAW/iDAWi && npm run lint

# Full build
cd iDAW/iDAWi && npm run build

# Python tests
pytest tests_music-brain/ -v

# C++ build (if available)
mkdir -p build && cd build && cmake .. && make
```
```

```
/test-emotion

Test emotion-related functionality:
```bash
# From iDAW directory:
cd iDAW

# Python emotion thesaurus
python -c "from emotion_thesaurus import EmotionThesaurus; t = EmotionThesaurus(); print(t.stats())"

# Test synonym lookup
python -c "from emotion_thesaurus import lookup; print(lookup('melancholy'))"

# Test music_brain CLI (requires pip install -e .)
daiw intent suggest grief
daiw diagnose "F-C-Am-Dm"
```
```

### Rule-Breaking Prompts

```
/suggest-rule-break [EMOTION]

Suggest rule-breaking options for emotional effect:

Reference mapping:
- bittersweet → HARMONY_ModalInterchange (iv chord, ♭VII)
- longing/grief → STRUCTURE_NonResolution (avoid tonic)
- power → HARMONY_ParallelMotion (parallel fifths)
- anxiety → RHYTHM_ConstantDisplacement (syncopation)
- vulnerability → PRODUCTION_PitchImperfection (slight detune)
- dissociation → ARRANGEMENT_BuriedVocals (dry, distant)

ALWAYS require emotional justification before implementing.
```

### MCP Server Commands

```
/mcp-status

Check MCP server status:
```bash
# Workstation status
python -m mcp_workstation status

# TODO server
python -m mcp_todo.cli summary

# Penta-Core swarm
python -m penta_core_music-brain.server --help
```
```

---

*"The audience doesn't hear 'borrowed from Dorian.' They hear 'that part made me cry.'"*

End of Copilot Instructions.
