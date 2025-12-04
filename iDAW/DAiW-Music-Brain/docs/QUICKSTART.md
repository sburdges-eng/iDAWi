# Music Brain - Logic Pro: Quick Start

## Installation
```bash
git clone https://github.com/sburdges-eng/DAiW-Music-Brain.git
cd DAiW-Music-Brain
pip install -r requirements.txt
pip install click  # For CLI
```

## 5-Minute Tutorial

### Step 1: Generate from Text
```bash
python bin/daiw-logic generate "grief and loss" -o my_sad_song --verbose
```

This creates `my_sad_song_automation.json` with mixer settings.

### Step 2: Import to Logic Pro

1. Open Logic Pro X
2. Create new project (82 BPM, F major)
3. Open `my_sad_song_automation.json`
4. Apply settings manually:
   - Channel EQ: Set presence/air based on JSON
   - Compressor: Set ratio/threshold/attack/release
   - Reverb: Set mix/decay/predelay

### Step 3: Create Music

- Add software instruments
- Record or program your parts
- Mix with the emotional automation as starting point

## CLI Commands

### Generate
```bash
daiw-logic generate "explosive anger" -o angry_track
daiw-logic generate "anxiety" -o anxious --verbose
daiw-logic generate "nostalgia" -o memory -t 70 -k Dm
```

### Analyze
```bash
daiw-logic analyze "I feel deeply bereaved and heartbroken"
```

### Explore
```bash
daiw-logic list-emotions
```

## UI
```bash
pip install streamlit
streamlit run ui/emotion_to_logic.py
```

Then open http://localhost:8501

## Python API
```python
from music_brain.api import MusicBrain

brain = MusicBrain()
music = brain.generate_from_text("grief and loss")
brain.export_to_logic(music, "my_song")
```

## Next Steps

- See `docs/ADVANCED.md` for advanced features
- See `examples/` for complete examples
- See `docs/LOGIC_PRO_INTEGRATION.md` for automation details
