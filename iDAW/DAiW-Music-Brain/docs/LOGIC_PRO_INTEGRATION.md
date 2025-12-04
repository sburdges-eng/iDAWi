# Logic Pro Integration Guide

## Overview

Music Brain generates JSON automation files that describe mixer settings for Logic Pro X. These files contain:

1. **Emotional Context**: The detected emotion and valence/arousal values
2. **Suggested Settings**: Tempo, key, and mode
3. **Mixer Automation**: Detailed EQ, compression, reverb, and effects settings

## Automation File Format

```json
{
    "project": "my_song",
    "emotional_context": {
        "primary_emotion": "bereaved",
        "valence": -0.7,
        "arousal": 0.3
    },
    "suggested_settings": {
        "tempo": 82,
        "key": "F",
        "mode": "major"
    },
    "mixer_automation": {
        "eq": {
            "sub_bass": 0.0,
            "bass": 2.0,
            "low_mid": 1.0,
            "mid": 0.0,
            "high_mid": 0.0,
            "presence": -2.0,
            "air": -3.0
        },
        "compression": {
            "ratio": 2.5,
            "threshold": -12.0,
            "attack": 30.0,
            "release": 200.0,
            "makeup": 0.0
        },
        "reverb": {
            "mix": 0.5,
            "decay": 3.0,
            "predelay": 40.0,
            "size": 0.7,
            "damping": 0.5
        },
        "delay": {
            "mix": 0.0,
            "time": 250.0,
            "feedback": 0.3
        },
        "saturation": 0.1,
        "stereo_width": 0.8,
        "limiter_ceiling": -0.3
    }
}
```

## Applying Settings in Logic Pro

### Step 1: Create Project
1. Open Logic Pro X
2. Create new project with suggested tempo and key
3. Add audio/MIDI tracks as needed

### Step 2: Set Up Channel Strip
For each channel that should receive the emotion-driven mix:

#### Channel EQ (7-band)
| Band | Frequency | Automation Value |
|------|-----------|------------------|
| Low Cut | 20-60 Hz | eq.sub_bass |
| Low | 60-250 Hz | eq.bass |
| Low Mid | 250-500 Hz | eq.low_mid |
| Mid | 500-2000 Hz | eq.mid |
| High Mid | 2-6 kHz | eq.high_mid |
| High | 6-12 kHz | eq.presence |
| Air | 12-20 kHz | eq.air |

#### Compressor
| Parameter | Automation Value |
|-----------|------------------|
| Ratio | compression.ratio |
| Threshold | compression.threshold (dB) |
| Attack | compression.attack (ms) |
| Release | compression.release (ms) |
| Makeup | compression.makeup (dB) |

#### Space Designer / Reverb
| Parameter | Automation Value |
|-----------|------------------|
| Dry/Wet | reverb.mix (0-100%) |
| Decay | reverb.decay (seconds) |
| Predelay | reverb.predelay (ms) |
| Size | reverb.size (0-100%) |
| Damping | reverb.damping (0-100%) |

### Step 3: Master Bus
Apply to master:
- Limiter ceiling: limiter_ceiling (dB)
- Stereo spread: stereo_width (0-2, where 1=normal)

## Emotional Mapping Reference

### Grief/Sadness
- More reverb (decay 2-4s)
- Darker EQ (reduced presence/air)
- Slower attack compression
- Narrower stereo width

### Anger/Rage
- Heavy compression (6:1 - 10:1)
- Fast attack/release
- More saturation
- Boosted low-mid/presence

### Joy/Euphoria
- Bright EQ (boosted presence/air)
- Moderate compression
- Wide stereo image
- Less reverb, more clarity

### Fear/Anxiety
- Heavy sub-bass
- Cut low-mids
- Long reverb with predelay
- Delay with feedback

## Automation Over Time

For dynamic emotional arcs, consider automating these parameters:

1. **Build (tension)**: Gradually increase compression ratio, reduce reverb mix
2. **Release (catharsis)**: Open up reverb, widen stereo
3. **Intimate moments**: Reduce stereo width, increase saturation
4. **Climax**: Maximum compression, full frequency spectrum

## Tips

1. **Start Subtle**: Begin with 50% of suggested EQ values and adjust
2. **A/B Compare**: Bypass effects to check emotional impact
3. **Trust Your Ears**: The automation is a starting point, not a rule
4. **Consider Genre**: Lo-fi allows more "imperfection", pop needs clarity

## Example Workflow

```bash
# 1. Generate automation
python bin/daiw-logic generate "grief and loss" -o sad_ballad --verbose

# 2. View the file
cat sad_ballad_automation.json

# 3. Open Logic Pro
# 4. Create project at suggested tempo/key
# 5. Apply mixer settings
# 6. Record and produce
```

## Philosophy

> "The audience doesn't hear 'reverb set to 50%'.
> They hear 'that part made me feel something.'"

The automation values are derived from the emotional intent, not arbitrary. Use them as a starting point that already carries emotional meaning.
