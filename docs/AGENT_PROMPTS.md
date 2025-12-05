# iDAW Agent Prompts & Quick Commands

> Comprehensive guide for AI assistants and developers working with the iDAW project.

## Quick Copy-Paste Setup

### One-Liner Full Setup
```bash
curl -sSL https://raw.githubusercontent.com/sburdges-eng/iDAWi/main/setup-idaw.sh | bash -s full
```

### Manual Setup (Copy All)
```bash
# Clone and enter repo
git clone https://github.com/sburdges-eng/iDAWi.git && cd iDAWi

# Build all components
./build.sh --debug

# Or build individually
cd penta-core && cmake -B build -DCMAKE_BUILD_TYPE=Debug && cmake --build build
cd DAiW-Music-Brain && pip install -e .[audio,theory]
cd iDAW && npm install && npm run dev
```

---

## Claude Code Prompts

### Session Start Prompt
```
I'm working on iDAW, a professional DAW with emotion-driven music generation.

Stack: C++20 (penta-core audio engine) + React/TypeScript (UI) + Python (ML generation)

Key directories:
- penta-core/src/audio/ - C++ audio processing (lock-free, real-time safe)
- penta-core/include/penta/audio/ - C++ headers
- DAiW-Music-Brain/music_brain/emotion/ - Python emotion thesaurus (6×6×6 = 216 nodes)
- iDAW/src/stores/ - Zustand state management
- iDAW/src/emotion/ - TypeScript emotion mapping

Rules:
1. Audio thread: No allocations, no locks, no blocking
2. Parameters: Use SmoothedParameter with atomics
3. IPC: Debounce backend calls (16ms minimum)
4. Python: Async generation, return MIDI bytes only

Current task: [DESCRIBE YOUR TASK]
```

### C++ Audio Processor Prompt
```
Create a C++ audio processor for [EFFECT_NAME].

Requirements:
1. Follow existing patterns in penta-core/include/penta/ (groove, harmony, midi, transport)
2. Parameters: [LIST: e.g., gain (0-2), frequency (20-20000Hz)]
3. Use SmoothedParameter for all controllable values
4. Include unit tests with Google Test

Location: penta-core/src/[module]/ and penta-core/include/penta/[module]/
```

### React Component Prompt
```
Create a React component for [COMPONENT_NAME].

Requirements:
1. TypeScript with strict types
2. Use Zustand store for state management
3. WebSocket/IPC for backend communication (debounce 16ms)
4. Tailwind CSS (core utilities only)
5. Proper memoization with useMemo/useCallback

Location: iDAW/src/components/
Connect to: [STORE_SLICE or BACKEND_ENDPOINT]
```

### Emotion Mapping Prompt
```
Add emotion mapping for [EMOTION_NAME].

V-A-D coordinates: valence=[X], arousal=[Y], dominance=[Z]

Update these files:
1. DAiW-Music-Brain/music_brain/emotion/thesaurus.py - Add to emotion nodes
2. iDAW/src/emotion/thesaurus.ts - TypeScript mapping (if frontend)

Musical characteristics: [DESCRIBE: tempo, mode, dynamics, etc.]

Follow 6×6×6 grid convention (216 total nodes):
- Valence: 6 levels (-1 to +1)
- Arousal: 6 levels (-1 to +1)
- Dominance: 6 levels (-1 to +1)
```

---

## Copilot Chat Prompts

### @workspace Commands
```
@workspace /explain the groove engine processing in penta-core/src/groove/GrooveEngine.cpp

@workspace /fix the latency compensation calculation for parallel plugin chains

@workspace /tests for the HarmonyEngine class in penta-core

@workspace /new create a new harmony processor following the project conventions
```

### Inline Suggestions Setup
Add to `.vscode/settings.json`:
```json
{
  "github.copilot.advanced": {
    "inlineSuggestCount": 3,
    "listCount": 10
  },
  "github.copilot.editor.enableAutoCompletions": true,
  "github.copilot.editor.enableCodeActions": true
}
```

### Copilot Comment Triggers

#### C++
```cpp
// Generate: AudioProcessor for parametric EQ with 3 bands
// Each band has: frequency (20-20000Hz log), gain (-12 to +12 dB), Q (0.1 to 10)

// Implement: Lock-free ring buffer for audio streaming
// Size: configurable, Thread-safe: yes, Overwrite: oldest on full

// PERF: Optimize this loop with SIMD (SSE/AVX)
```

#### TypeScript
```typescript
// Create: Zustand slice for mixer state with tracks, sends, and master

// Component: Waveform display with canvas rendering and zoom/scroll

// Hook: useAudioEngine that syncs transport state with C++ backend
```

#### Python
```python
# Generate: Async emotion-to-MIDI converter using VAD coordinates
# Map valence to mode, arousal to tempo, dominance to dynamics
```

---

## GitHub Copilot Agent Workflows

### Issue Commands
Create issues with these titles for Copilot to understand:

```markdown
## [Feature] Add reverb audio processor
@copilot implement

Create a reverb effect with:
- Room size parameter (0-1)
- Damping parameter (0-1)
- Wet/dry mix (0-1)
- Pre-delay (0-100ms)

Follow AudioProcessor trait pattern.
```

```markdown
## [Bug] Parameter smoothing causes clicks at fast changes
@copilot review

SmoothedParameter produces audible clicks when target changes rapidly.

Expected: Smooth transitions regardless of rate
Actual: Clicks when changing >10x per second
```

### PR Review Commands
```markdown
@copilot review this PR for:
- Real-time safety (no allocations in audio thread)
- Proper error handling
- Type safety
- Performance concerns
```

### Auto-labeling Workflow
```yaml
# .github/workflows/auto-label.yml
name: Auto Label

on:
  issues:
    types: [opened]
  pull_request:
    types: [opened]

jobs:
  label:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      issues: write
      pull-requests: write
    steps:
      - uses: actions/labeler@v5
        with:
          repo-token: ${{ secrets.GITHUB_TOKEN }}
          configuration-path: .github/labeler.yml
```

---

## Codespace Quick Actions

### Start Development
```bash
# Build all components
./build.sh --debug

# Or build individually
cd penta-core && cmake -B build -DCMAKE_BUILD_TYPE=Debug && cmake --build build
cd DAiW-Music-Brain && pip install -e .[audio,theory]
cd iDAW && npm install && npm run dev
```

### Run All Tests
```bash
# Full test suite
./test.sh

# Individual components
cd penta-core/build && ctest -V
cd DAiW-Music-Brain && pytest tests/ -v
cd iDAW && npm run test
```

### Format All Code
```bash
# C++ (clang-format)
cd penta-core && find src include -type f \( -name '*.cpp' -o -name '*.h' \) -exec clang-format -i {} \;

# Python (black)
cd DAiW-Music-Brain && black music_brain/ tests/ --line-length=100

# TypeScript/React (prettier)
cd iDAW && npx prettier --write "src/**/*.{ts,tsx}"
```

### Pre-commit Check
```bash
# C++ lint
cd penta-core && cppcheck --project=build/compile_commands.json --enable=warning,style

# Python lint
cd DAiW-Music-Brain && black --check music_brain/ && mypy music_brain/ --ignore-missing-imports

# TypeScript lint
cd iDAW && npm run lint && npm run type-check
```

---

## File Templates

> **Note**: See the "C++ Audio Processor Template" section below for project-specific C++ templates.
> The following are generic templates for reference.

### New React Component
```bash
cat > iDAW/src/components/NewComponent.tsx << 'EOF'
import React, { useMemo, useCallback } from 'react';
import { useDAWStore } from '../stores/dawStore';

interface NewComponentProps {
  trackId: string;
}

export function NewComponent({ trackId }: NewComponentProps) {
  const track = useDAWStore((state) => state.tracks.get(trackId));
  const setTrackVolume = useDAWStore((state) => state.setTrackVolume);

  const handleVolumeChange = useCallback((value: number) => {
    setTrackVolume(trackId, value);
    // Debounce backend communication
  }, [trackId, setTrackVolume]);

  if (!track) return null;

  return (
    <div className="flex flex-col p-4 bg-gray-800 rounded-lg">
      <span className="text-white font-medium">{track.name}</span>
      <input
        type="range"
        min={0}
        max={1}
        step={0.01}
        value={track.volume}
        onChange={(e) => handleVolumeChange(parseFloat(e.target.value))}
        className="w-full mt-2"
      />
    </div>
  );
}

function linearToDb(linear: number): number {
  return 20 * Math.log10(Math.max(linear, 0.0001));
}
EOF
```

### New Emotion Node
```bash
# Update Python emotion thesaurus
cat >> DAiW-Music-Brain/music_brain/emotion/thesaurus.py << 'EOF'

# Add new emotion node:
# EMOTION_NODES['new_emotion'] = EmotionNode(
#     name='NewEmotionName',
#     valence=X.X,  # -1 to 1
#     arousal=X.X,  # -1 to 1
#     dominance=X.X,  # -1 to 1
# )
EOF
```

---

## Debugging Commands

### C++ Audio Engine (penta-core)
```bash
# Run with debug logging
cd penta-core && PENTA_LOG_LEVEL=debug ./build/bin/penta_test

# Run tests with verbose output
cd penta-core/build && ctest -V --output-on-failure

# Debug with GDB
cd penta-core/build && gdb -ex run -ex bt -ex quit ./bin/test_audio_io

# Profile with perf
cd penta-core/build && perf record -g ./bin/benchmark && perf report

# Memory leak detection (Valgrind)
cd penta-core/build && valgrind --tool=memcheck --leak-check=full ./bin/test_audio_io

# Memory profiling (Massif)
cd penta-core/build && valgrind --tool=massif ./bin/test_audio_io && ms_print massif.out.*
```

### Python Generator (DAiW-Music-Brain)
```bash
# Test generation directly
cd DAiW-Music-Brain && python -c "
from music_brain.emotion import emotion_to_params
print(emotion_to_params(valence=0.5, arousal=0.3, dominance=0.2))
"

# Run with debug logging
cd DAiW-Music-Brain && python -m pytest tests/ -v -s --log-cli-level=DEBUG

# Profile generation
cd DAiW-Music-Brain && python -m cProfile -s cumtime -m music_brain

# Type checking
cd DAiW-Music-Brain && mypy music_brain/ --ignore-missing-imports
```

### React Frontend (iDAW)
```bash
# Start development server
cd iDAW && npm run dev

# Build for production
cd iDAW && npm run build

# Run tests
cd iDAW && npm run test

# Type check
cd iDAW && npm run type-check
```

---

## Environment Variables

```bash
# Development
export PENTA_LOG_LEVEL=debug
export PYTHONPATH="${PWD}/DAiW-Music-Brain:${PYTHONPATH}"

# C++ Build
export CMAKE_BUILD_TYPE=Debug  # or Release
export CMAKE_CXX_STANDARD=20
export CMAKE_GENERATOR=Ninja

# Python
export PYTHONDONTWRITEBYTECODE=1
export VIRTUAL_ENV="${PWD}/DAiW-Music-Brain/venv"

# Audio testing
export PENTA_AUDIO_BACKEND=dummy  # For headless testing
export PENTA_SAMPLE_RATE=44100
export PENTA_BUFFER_SIZE=512
```

---

## Git Workflow

```bash
# Feature branch
git checkout -b feature/[feature-name]

# Commit with conventional format
git commit -m "feat(audio): add parametric EQ processor"
git commit -m "fix(ui): resolve waveform rendering at high zoom"
git commit -m "docs: update emotion mapping documentation"

# Push and create PR
git push -u origin feature/[feature-name]
gh pr create --fill
```

---

## C++ Component Template (penta-core)

Since this project uses C++20 for the audio engine (penta-core), use this template pattern based on existing modules (groove, harmony, midi, transport):

### Header File Example
```bash
# Create header (following GrooveEngine.h pattern)
cat > penta-core/include/penta/[module]/NewComponent.h << 'EOF'
#pragma once

#include "penta/common/RTTypes.h"
#include <memory>
#include <vector>

namespace penta::[module] {

/**
 * Component description
 */
class NewComponent {
public:
    struct Config {
        double sampleRate;
        size_t hopSize;
        
        Config()
            : sampleRate(kDefaultSampleRate)
            , hopSize(512)
        {}
    };
    
    explicit NewComponent(const Config& config = Config{});
    ~NewComponent();
    
    // Non-copyable, movable
    NewComponent(const NewComponent&) = delete;
    NewComponent& operator=(const NewComponent&) = delete;
    NewComponent(NewComponent&&) noexcept = default;
    NewComponent& operator=(NewComponent&&) noexcept = default;
    
    // RT-safe: Process audio buffer
    void processAudio(const float* buffer, size_t frames) noexcept;
    
    // Non-RT: Update configuration
    void updateConfig(const Config& config);
    
    // Non-RT: Reset state
    void reset();
    
private:
    Config config_;
};

} // namespace penta::[module]
EOF
```

### Implementation File Example
```bash
# Create implementation
cat > penta-core/src/[module]/NewComponent.cpp << 'EOF'
#include "penta/[module]/NewComponent.h"

namespace penta::[module] {

NewComponent::NewComponent(const Config& config)
    : config_(config) {}

NewComponent::~NewComponent() = default;

void NewComponent::processAudio(const float* buffer, size_t frames) noexcept {
    // RT-safe processing - no allocations, no locks
    for (size_t i = 0; i < frames; ++i) {
        // Process audio...
    }
}

void NewComponent::updateConfig(const Config& config) {
    config_ = config;
}

void NewComponent::reset() {
    // Reset internal state
}

} // namespace penta::[module]
EOF
```

### C++ Test Template
```bash
cat > penta-core/tests/unit/[module]/TestNewComponent.cpp << 'EOF'
#include <gtest/gtest.h>
#include "penta/[module]/NewComponent.h"

using namespace penta::[module];

class NewComponentTest : public ::testing::Test {
protected:
    void SetUp() override {
        NewComponent::Config config;
        config.sampleRate = 44100;
        component_ = std::make_unique<NewComponent>(config);
    }

    std::unique_ptr<NewComponent> component_;
};

TEST_F(NewComponentTest, ProcessAudio) {
    std::vector<float> buffer(512, 1.0f);
    component_->processAudio(buffer.data(), buffer.size());
    // Add assertions
}

TEST_F(NewComponentTest, Reset) {
    component_->reset();
    // Verify state is reset
}
EOF
```

---

## Python Emotion Generator Template

```bash
cat > DAiW-Music-Brain/music_brain/generators/new_generator.py << 'EOF'
"""New music generator following project conventions."""
from typing import Optional
from dataclasses import dataclass
import numpy as np
from numpy.typing import NDArray

FloatArray = NDArray[np.float32]


@dataclass
class GenerationParams:
    """Parameters for music generation."""
    valence: float  # -1 to 1
    arousal: float  # -1 to 1
    dominance: float  # -1 to 1
    duration: float  # seconds
    tempo: Optional[float] = None


@dataclass
class GenerationResult:
    """Result of music generation."""
    midi_data: bytes
    tempo: float
    key: str
    time_signature: tuple[int, int]


def emotion_to_params(v: float, a: float, d: float) -> dict:
    """Map VAD coordinates to musical parameters.

    Args:
        v: Valence (-1 to 1), affects mode/harmony
        a: Arousal (-1 to 1), affects tempo/rhythm
        d: Dominance (-1 to 1), affects dynamics/intensity

    Returns:
        Dictionary of musical parameters.
    """
    return {
        'tempo': _map_arousal_to_tempo(a),
        'mode': 'major' if v > 0 else 'minor',
        'dynamics': _map_dominance_to_dynamics(d),
        'rhythmic_complexity': abs(a),
        'harmonic_tension': 1.0 - v if v < 0 else 0.3,
    }


def _map_arousal_to_tempo(arousal: float) -> float:
    """Map arousal to tempo (BPM)."""
    # Low arousal: 60-90 BPM, High arousal: 120-180 BPM
    return 60 + (arousal + 1) * 60


def _map_dominance_to_dynamics(dominance: float) -> float:
    """Map dominance to dynamics (0-1)."""
    return (dominance + 1) / 2


async def generate(params: GenerationParams) -> GenerationResult:
    """Generate music asynchronously.

    Never blocks the audio thread - all generation is async.

    Args:
        params: Generation parameters including emotion coordinates.

    Returns:
        GenerationResult with MIDI data and metadata.
    """
    import asyncio

    musical_params = emotion_to_params(
        params.valence, params.arousal, params.dominance
    )

    # Run CPU-intensive generation in thread pool
    midi_data = await asyncio.to_thread(
        _generate_midi, musical_params, params.duration
    )

    return GenerationResult(
        midi_data=midi_data,
        tempo=musical_params['tempo'],
        key='C' if musical_params['mode'] == 'major' else 'Am',
        time_signature=(4, 4),
    )


def _generate_midi(params: dict, duration: float) -> bytes:
    """Generate MIDI data (CPU-intensive, runs in thread)."""
    from midiutil import MIDIFile

    midi = MIDIFile(1)
    midi.addTempo(0, 0, params['tempo'])

    # Add notes based on parameters
    # ... implementation here ...

    import io
    output = io.BytesIO()
    midi.writeFile(output)
    return output.getvalue()
EOF
```

---

## Project-Specific Quick Commands

### Build Commands (iDAW Project)
```bash
# Full build (optimized)
./build.sh --release

# Debug build
./build.sh --debug

# penta-core only
cd penta-core && cmake -B build -DCMAKE_BUILD_TYPE=Release -GNinja && cmake --build build

# Python package
cd DAiW-Music-Brain && pip install -e .[audio,theory]
```

### Test Commands (iDAW Project)
```bash
# All tests
./test.sh

# C++ tests only
cd penta-core/build && ctest -V --output-on-failure

# Python tests
cd DAiW-Music-Brain && pytest tests/ -v --tb=short

# Specific test pattern
cd penta-core/build && ctest -R 'Audio|MIDI' -V
```

### Lint Commands (iDAW Project)
```bash
# C++ static analysis
cd penta-core && cppcheck --project=build/compile_commands.json

# Python style
cd DAiW-Music-Brain && black --check music_brain/ && mypy music_brain/

# Format all
cd penta-core && find src include -type f \( -name '*.cpp' -o -name '*.h' \) -exec clang-format -i {} \;
cd DAiW-Music-Brain && black music_brain/ tests/
```

---

## Project Structure Reference

```
iDAWi/
├── setup-idaw.sh              # Quick setup script
├── build.sh                   # Build script
├── test.sh                    # Test runner
├── .github/
│   ├── workflows/             # CI/CD workflows
│   │   └── auto-label.yml     # Auto-labeling for PRs
│   └── labeler.yml            # Label configuration
├── .vscode/
│   └── settings.json          # IDE settings with Copilot config
├── docs/
│   └── AGENT_PROMPTS.md       # This file
├── penta-core/                # C++20 audio engine
│   ├── include/penta/         # C++ headers
│   │   ├── groove/            # Groove analysis (GrooveEngine, OnsetDetector, etc.)
│   │   ├── harmony/           # Harmony analysis (ChordAnalyzer, HarmonyEngine, etc.)
│   │   ├── midi/              # MIDI processing
│   │   ├── transport/         # Transport control
│   │   └── common/            # Shared types (RTTypes.h)
│   ├── src/                   # C++ implementation
│   │   ├── groove/
│   │   ├── harmony/
│   │   ├── midi/
│   │   └── transport/
│   └── tests/                 # C++ unit tests
├── DAiW-Music-Brain/          # Python AI/ML
│   └── music_brain/
│       ├── emotion/           # Emotion thesaurus
│       └── generators/        # Music generators
└── iDAW/                      # React/TypeScript frontend
    └── src/
        ├── components/        # UI components
        ├── emotion/           # TypeScript emotion mapping
        ├── hooks/             # React hooks
        └── stores/            # Zustand state
```

---

## Notes

This project uses:
- **penta-core**: C++20 audio engine (real-time DSP)
- **DAiW-Music-Brain**: Python AI/ML (emotion-driven generation)
- **iDAW**: React/TypeScript frontend

Use the C++ templates above for actual penta-core development.
