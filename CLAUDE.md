# CLAUDE.md - AI Assistant Guide for iDAWi

> Comprehensive guide for AI assistants working with the iDAWi (Intelligent Digital Audio Workstation interface) monorepo.

## Project Philosophy

**"Interrogate Before Generate"** - The tool shouldn't finish art for people. It should make them braver.

iDAWi is a unified platform combining three major components into an intelligent music production ecosystem:
- **Real-time C++ audio processing** (JUCE-based, penta-core engine)
- **Python-based music intelligence** (AI-assisted composition, analysis)
- **Multi-AI collaboration orchestration** (MCP protocol)
- **Intent-driven creative workflows** (emotional intent drives technical choices)

---

## Repository Structure

This is a **unified monorepo** containing three main components:

```
iDAWi/
├── iDAW/                      # Main iDAW platform
│   ├── music_brain/           # Core Python package (v0.2.0)
│   ├── mcp_workstation/       # Multi-AI orchestration server
│   ├── mcp_todo/              # Cross-AI task management
│   ├── mcp_plugin_host/       # Plugin management system
│   ├── penta_core_music-brain/# MCP Swarm (multi-AI aggregation)
│   ├── iDAWi/                 # Tauri desktop application (React/TypeScript)
│   ├── tests_music-brain/     # Python integration tests
│   ├── Data_Files/            # JSON data (progressions, genres)
│   ├── vault/                 # Obsidian knowledge base
│   └── [guides & docs]        # Production/songwriting guides
│
├── DAiW-Music-Brain/          # Standalone Music AI toolkit
│   ├── music_brain/           # Python package
│   ├── vault/                 # Knowledge base
│   ├── app.py                 # Streamlit UI
│   └── launcher.py            # Desktop wrapper
│
├── penta-core/                # C++ Real-time audio engine
│   ├── include/penta/         # C++ headers
│   ├── src/                   # C++ implementation
│   ├── bindings/              # pybind11 Python bindings
│   ├── plugins/               # JUCE VST3/AU plugins
│   ├── python/penta_core/     # Python API & rules
│   ├── tests/                 # C++ unit tests
│   └── docs/                  # Architecture documentation
│
├── build.sh / build.ps1       # Build scripts
├── test.sh                    # Test runner
└── .github/workflows/         # CI/CD pipelines
```

### Component-Specific Guides

Each major component has its own detailed CLAUDE.md:
- `iDAW/CLAUDE.md` - Main platform guide (MCP servers, plugins, data files)
- `DAiW-Music-Brain/CLAUDE.md` - Music toolkit guide (intent schema, rule-breaking)
- `penta-core/README.md` - C++ engine documentation

---

## Technology Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| **C++ Core** | C++17/C++20, JUCE 8.0.10, CMake 3.22+ | Real-time audio, DSP, plugins |
| **Python Backend** | Python 3.9+, mido, numpy, librosa | Music intelligence, analysis, AI |
| **Desktop UI** | React 18, TypeScript, Tauri 2.0, TailwindCSS | Native desktop application |
| **Web UI** | Streamlit, pywebview | Rapid prototyping, web access |
| **AI Orchestration** | MCP Protocol | Multi-AI collaboration |
| **CI/CD** | GitHub Actions, Docker | Testing, deployment |

---

## Core Architecture

### Dual-Engine Design

```
┌─────────────────────────────────────────────────────────────┐
│  Side A (C++ "Work State")       Side B (Python "Dream State") │
│  ─────────────────────────       ───────────────────────────── │
│  • Real-time audio                • AI generation              │
│  • Deterministic execution        • Dynamic, may block         │
│  • Lock-free data structures      • Flexible allocation        │
│  • 4GB pre-allocated buffer       • No RT constraints          │
│  • Never blocks on Side B         • Writes to ring buffer      │
│                                                                 │
│            ←── Lock-free Ring Buffer ───                        │
└─────────────────────────────────────────────────────────────────┘
```

### Intent-Driven Composition (Three-Phase Schema)

1. **Phase 0: Core Wound/Desire** - Deep emotional interrogation
   - `core_event` - What happened?
   - `core_resistance` - What holds you back?
   - `core_longing` - What do you want to feel?

2. **Phase 1: Emotional Intent** - Mood and narrative
   - `mood_primary`, `vulnerability_scale`, `narrative_arc`

3. **Phase 2: Technical Constraints** - Implementation
   - `technical_genre`, `technical_key`, `technical_rule_to_break`
   - **Rule-breaking requires explicit justification**

### Rule-Breaking Categories

| Category | Examples | Emotional Effect |
|----------|----------|------------------|
| **Harmony** | `HARMONY_AvoidTonicResolution` | Unresolved yearning |
| **Rhythm** | `RHYTHM_ConstantDisplacement` | Anxiety, restlessness |
| **Arrangement** | `ARRANGEMENT_BuriedVocals` | Dissociation |
| **Production** | `PRODUCTION_PitchImperfection` | Emotional honesty |

---

## MCP Servers

### MCP Workstation (`mcp_workstation/`)

Orchestrates multi-AI collaboration on iDAW development.

```bash
python -m mcp_workstation status              # Show dashboard
python -m mcp_workstation register claude     # Register as Claude
python -m mcp_workstation propose claude "Title" "Desc" architecture
python -m mcp_workstation vote claude PROP_ID 1
python -m mcp_workstation phases              # Show phase progress
python -m mcp_workstation server              # Run MCP server
```

**AI Agents:**
- `claude` - Code architecture, real-time safety, complex debugging
- `chatgpt` - Theory analysis, explanations, documentation
- `gemini` - Cross-language patterns, multi-modal analysis
- `github_copilot` - Code completion, boilerplate generation

### MCP TODO (`mcp_todo/`)

Cross-AI task synchronization. Tasks created in one AI are available in all others.

```bash
python -m mcp_todo.cli add "Task" --priority high --tags "code,urgent"
python -m mcp_todo.cli list --status pending
python -m mcp_todo.cli complete <id>
```

### Penta-Core Swarm (`penta_core_music-brain/`)

Multi-AI aggregation server:
- `consult_architect` - OpenAI GPT-4o (design patterns)
- `consult_developer` - Anthropic Claude (clean code)
- `consult_researcher` - Google Gemini (deep analysis)
- `consult_maverick` - xAI Grok (creative red teaming)

---

## Development Setup

### Python Installation

```bash
cd iDAW

# Core installation
pip install -e .

# With optional dependencies
pip install -e ".[dev]"      # pytest, black, flake8, mypy
pip install -e ".[audio]"    # librosa, soundfile
pip install -e ".[theory]"   # music21
pip install -e ".[ui]"       # streamlit
pip install -e ".[desktop]"  # streamlit + pywebview
pip install -e ".[all]"      # Everything
```

### C++ Build

```bash
cd penta-core
mkdir build && cd build
cmake .. -DCMAKE_BUILD_TYPE=Release -G Ninja
ninja penta_core           # Build library
ninja penta_tests          # Build tests
ctest --output-on-failure  # Run tests
```

### Desktop App (Tauri)

```bash
cd iDAW/iDAWi
npm install
npm run tauri dev          # Development mode
npm run tauri build        # Production build
```

### Requirements

- **Python**: 3.9+ (tested 3.9-3.13)
- **C++**: C++17 standard (C++20 for some features)
- **CMake**: 3.22+
- **JUCE**: 8.0.10
- **Node.js**: 18+ (for Tauri desktop app)

---

## Running Tests

### Python Tests

```bash
# From iDAW directory
pytest tests_music-brain/ -v

# With coverage
pytest tests_music-brain/ -v --cov=music_brain --cov-report=term-missing

# DAiW-Music-Brain internal tests
pytest DAiW-Music-Brain/tests/ -v
```

### C++ Tests

```bash
cd penta-core/build
ctest --output-on-failure

# Specific test suites
./penta_tests --gtest_filter="*Harmony*"
./penta_tests --gtest_filter="*Groove*"
```

### Full Test Suite

```bash
./test.sh  # Runs both Python and C++ tests
```

---

## CI/CD Workflows

| Workflow | Purpose |
|----------|---------|
| `ci.yml` | Python tests, C++ builds, Valgrind memory checking, performance regression |
| `sprint_suite.yml` | Comprehensive sprint-based testing (8 jobs) |
| `platform_support.yml` | Cross-platform Python testing (3.9-3.13, Linux/macOS/Windows) |
| `release.yml` | Desktop builds, Python distribution, C++ libraries |

---

## CLI Commands

### daiw (Main CLI)

```bash
# Groove operations
daiw extract drums.mid                    # Extract groove from MIDI
daiw apply --genre funk track.mid         # Apply genre groove template

# Chord analysis
daiw analyze --chords song.mid            # Analyze chord progression
daiw diagnose "F-C-Am-Dm"                 # Diagnose harmonic issues
daiw reharm "F-C-Am-Dm" --style jazz      # Generate reharmonizations

# Intent-based generation
daiw intent new --title "My Song"         # Create intent template
daiw intent process my_intent.json        # Generate from intent
daiw intent suggest grief                 # Suggest rules to break
daiw intent list                          # List rule-breaking options

# Teaching
daiw teach rulebreaking                   # Interactive teaching mode
```

---

## Code Style & Conventions

### Python

- **Line length**: 100 characters
- **Formatter**: black
- **Type hints**: Required for public APIs
- **Lazy imports**: In CLI for fast startup

```bash
black music_brain/ tests/      # Format
mypy music_brain/              # Type check
flake8 music_brain/ tests/     # Lint
```

### C++

- **Standard**: C++17 (C++20 for some features)
- **Naming**: PascalCase (classes), camelCase (methods), snake_case (variables)
- **RT-Safety**: Mark audio callbacks `noexcept`, no allocations
- **Memory**: Use `std::pmr` containers
- **SIMD**: AVX2 optimizations with scalar fallback

### TypeScript/React

- **Strict mode**: Enabled
- **State management**: Zustand
- **Styling**: TailwindCSS
- **Linting**: ESLint

---

## Key Design Decisions

1. **Emotional intent drives technical choices** - Never generate without understanding "why"
2. **Rules are broken intentionally** - Every rule break requires justification
3. **RT-safety is paramount** - Audio thread never waits on UI/AI
4. **Human imperfection is valued** - Lo-fi, pitch drift are features, not bugs
5. **Teaching over finishing** - The tool educates and empowers
6. **Phase 0 must come first** - Technical decisions can't be made without emotional clarity

---

## Common Development Tasks

### Adding a New Groove Genre

1. Add entry to `iDAW/Data_Files/genre_pocket_maps.json`
2. Add template in `music_brain/groove/templates.py`
3. Add to CLI choices in `music_brain/cli.py`

### Adding a Rule-Breaking Option

1. Add enum value in `music_brain/session/intent_schema.py`
2. Add entry in `RULE_BREAKING_EFFECTS` dict
3. Implement in `intent_processor.py`

### Adding a Penta-Core Engine

1. Create header in `penta-core/include/penta/<subsystem>/`
2. Implement in `penta-core/src/<subsystem>/`
3. Update `penta-core/CMakeLists.txt`
4. Add Python bindings in `penta-core/bindings/`
5. Add tests in `penta-core/tests/`

### Adding Music Theory Rules

1. Create rule class in `penta-core/python/penta_core/rules/`
2. Add to appropriate module (harmony, rhythm, etc.)
3. Add teacher support in `penta-core/python/penta_core/teachers/`

---

## iDAW_Core Plugins (JUCE-based)

Art-themed audio plugins:

| Plugin | Purpose | Priority |
|--------|---------|----------|
| **Pencil** | Sketching/drafting audio | HIGH |
| **Eraser** | Audio removal/cleanup | HIGH |
| **Palette** | Tonal coloring | MID |
| **Smudge** | Audio blending | MID |
| **Press** | Dynamics/compression | HIGH |
| **Trace** | Pattern following | LOW |
| **Parrot** | Sample playback | LOW |

---

## Data Files

### Location: `iDAW/Data_Files/`

| File | Purpose |
|------|---------|
| `chord_progression_families.json` | Chord family definitions |
| `chord_progressions_db.json` | Progression database |
| `common_progressions.json` | Frequently used progressions |
| `genre_mix_fingerprints.json` | Genre mixing characteristics |
| `genre_pocket_maps.json` | Genre-specific groove maps |

---

## Vault (Knowledge Base)

Obsidian-compatible markdown files:

```
vault/
├── Songwriting_Guides/    # Intent schema, rule-breaking guides
├── Songs/                 # Song-specific project files
├── Templates/             # Task boards and templates
└── Theory_Reference/      # Music theory reference
```

Uses `[[wiki links]]` for cross-referencing.

---

## Troubleshooting

### Python Import Errors

```bash
pip install -e .           # Ensure installed
python --version           # Requires 3.9+
```

### C++ Build Failures

```bash
cmake --version            # Requires 3.22+
g++ --version              # Requires C++17 support
grep avx2 /proc/cpuinfo    # Check AVX2 support (optional)
```

### Audio Thread Issues

- Verify no allocations in `processBlock()`
- Check `isAudioThread()` assertions
- Use `assertNotAudioThread()` before blocking operations

### MCP Server Issues

```bash
python -m mcp_todo.server --help
python -m mcp_workstation.server --help
```

---

## Data Flow

```
User Intent → Intent Schema → Intent Processor → Musical Elements
                                              ├── GeneratedProgression
                                              ├── GeneratedGroove
                                              └── GeneratedArrangement

Text Prompt → PythonBridge → Ring Buffer → Audio Engine
(Side B)                                   (Side A)

AI Proposal → Voting → Approved → Task Assignment → Implementation

MCP TODO: Claude ←→ JSON Storage ←→ ChatGPT/Cursor/Gemini
```

---

## Project Status

- **Phase 0**: Complete (Foundation & Architecture)
- **Phase 1**: Core implementation in progress
- **penta-core**: C++ headers and implementations complete
- **MCP Servers**: Workstation, TODO, Plugin Host operational
- **Desktop App**: Tauri scaffold ready

---

## Meta Principle

> "The audience doesn't hear 'borrowed from Dorian.' They hear 'that part made me cry.'"

Technical implementation serves emotional expression. The tool educates and empowers - it doesn't just generate.
