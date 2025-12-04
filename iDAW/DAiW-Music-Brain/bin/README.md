# CLI Tools

## Installation

Add to your PATH:
```bash
export PATH="$PATH:/path/to/DAiW-Music-Brain/bin"
```

Or use directly with Python:
```bash
python bin/daiw-logic --help
```

## Usage

### Generate from text:
```bash
daiw-logic generate "grief and loss" -o sad_song
daiw-logic generate "explosive anger" -o angry_song -t 140
daiw-logic generate "anxiety" -o anxious --verbose
```

### Analyze text:
```bash
daiw-logic analyze "I feel deeply bereaved and heartbroken"
```

### List all emotions:
```bash
daiw-logic list-emotions
```

### Generate from intent file:
```bash
daiw-logic from-intent kelly_intent.json -o kelly_song
```

## Dependencies

Requires `click` for CLI:
```bash
pip install click
```
