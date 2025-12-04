# iDAWi Import Manifest

> Comprehensive catalog of unique information to import from iDAW monorepo into iDAWi

**Generated:** 2025-12-04
**Branch:** claude/fix-idaw-import-todo-014PpwDhMw39mzcKtcQaRbUs

---

## Table of Contents

1. [Summary Statistics](#summary-statistics)
2. [Data Files (JSON)](#data-files-json)
3. [Python Music Brain Modules](#python-music-brain-modules)
4. [Python Penta-Core Modules](#python-penta-core-modules)
5. [C++ Engine Headers](#c-engine-headers)
6. [C++ Engine Source](#c-engine-source)
7. [JUCE Plugin Suite](#juce-plugin-suite)
8. [MCP Servers](#mcp-servers)
9. [GitHub Workflows](#github-workflows)
10. [Documentation](#documentation)
11. [External Dependencies](#external-dependencies)
12. [Import Priority Matrix](#import-priority-matrix)

---

## Summary Statistics

| Category | File Count | Description |
|----------|------------|-------------|
| Data Files (JSON) | 5 | Music theory and genre data |
| Python Music Brain | 75 | Core music intelligence modules |
| Python Penta-Core | 49 | Advanced rules and ML bindings |
| C++ Headers | 21 | RT-safe audio engine headers |
| C++ Source | 20 | Engine implementations |
| JUCE Plugins | 33 | 11 art-themed audio plugins |
| MCP Servers | 20 | Multi-AI orchestration |
| GitHub Workflows | 5 | CI/CD pipelines |
| Documentation | 22+ | Vault, guides, references |
| External Deps | 3 | oscpack, readerwriterqueue |
| **TOTAL** | **253+** | |

---

## Data Files (JSON)

**Source:** `/home/user/iDAW/Data_Files/`
**Target:** `/home/user/iDAW/iDAWi/data/`

| File | Size | Description | Priority |
|------|------|-------------|----------|
| `chord_progression_families.json` | 349 lines | Universal/Jazz/Blues/Rock/Modal progressions with examples | HIGH |
| `genre_pocket_maps.json` | 563 lines | 15 genres with timing, swing, push/pull, velocity data | HIGH |
| `genre_mix_fingerprints.json` | 416 lines | Frequency balance, dynamics, transients by genre | HIGH |
| `chord_progressions_db.json` | - | Complete chord progression database | MEDIUM |
| `common_progressions.json` | - | Frequently used progressions | MEDIUM |

### Unique Data in chord_progression_families.json:
- **Universal progressions:** I-IV-V-I, I-V-vi-IV (Pop/Axis), I-vi-IV-V (50s Doo-Wop), vi-IV-I-V
- **Jazz progressions:** ii-V-I, I-vi-ii-V (Rhythm Changes), iii-vi-ii-V (Circle of Fifths), Neo-Soul
- **Blues progressions:** 12-bar, 8-bar, minor blues
- **Rock progressions:** Mixolydian vamp (I-bVII-IV), Aeolian (i-bVI-bIII-bVII)
- **Modal progressions:** Dorian, Mixolydian, Lydian, Phrygian vamps
- **EDM/Hip-Hop/Gospel progressions** with examples and emotional descriptors
- **Cadence types:** Authentic, Plagal, Half, Deceptive

### Unique Data in genre_pocket_maps.json:
- **15 Genres:** hip-hop, trap, rnb, funk, jazz, rock, metal, reggae, house, techno, lofi, gospel, country
- **Per-genre:** BPM range, swing percentages, push/pull offsets per instrument, velocity ranges
- **Stagger timing:** Relationships between kick, snare, hihat, bass, keys

### Unique Data in genre_mix_fingerprints.json:
- **15 Genres** with frequency balance (sub to air), dynamics (RMS swing, crest factor)
- **Reference tracks** per genre (e.g., "Dr. Dre - Still D.R.E.", "Miles Davis - Kind of Blue")

---

## Python Music Brain Modules

**Source:** `/home/user/iDAW/music_brain/`
**Target:** `/home/user/iDAW/iDAWi/music-brain/music_brain/`

### Groove Package (6 files)
| File | Functions | Description |
|------|-----------|-------------|
| `groove/__init__.py` | - | Package exports |
| `groove/extractor.py` | `GrooveExtractor` | Extract groove from MIDI |
| `groove/applicator.py` | `GrooveApplicator` | Apply groove to tracks |
| `groove/groove_engine.py` | `GrooveEngine` | Main groove processing |
| `groove/templates.py` | Genre templates | Preset groove patterns |

### Structure Package (6 files)
| File | Functions | Description |
|------|-----------|-------------|
| `structure/__init__.py` | - | Package exports |
| `structure/chord.py` | `ChordAnalyzer` | Chord detection and analysis |
| `structure/progression.py` | `ProgressionAnalyzer` | Progression patterns |
| `structure/sections.py` | `SectionAnalyzer` | Song structure detection |
| `structure/tension_curve.py` | `TensionCurve` | Harmonic tension mapping |
| `structure/comprehensive_engine.py` | Full engine | Combined structure analysis |

### Session Package (5 files)
| File | Functions | Description |
|------|-----------|-------------|
| `session/__init__.py` | - | Package exports |
| `session/intent_schema.py` | `IntentSchema`, `RuleBreakingCategory` | 3-phase intent model |
| `session/intent_processor.py` | `IntentProcessor` | Process intent to music |
| `session/interrogator.py` | `Interrogator` | Question-based intent capture |
| `session/teaching.py` | `TeachingMode` | Interactive rule-breaking education |
| `session/generator.py` | `SessionGenerator` | Generate session configs |

### Audio Package (6 files)
| File | Functions | Description |
|------|-----------|-------------|
| `audio/__init__.py` | - | Package exports |
| `audio/feel.py` | `FeelAnalyzer` | Audio feel analysis |
| `audio/analyzer.py` | `AudioAnalyzer` | Core audio analysis |
| `audio/frequency_analysis.py` | Spectrum tools | FFT/frequency analysis |
| `audio/chord_detection.py` | Chord from audio | Audio-based chord detection |
| `audio/reference_dna.py` | Reference matching | Compare to reference tracks |

### DAW Integration Package (7 files)
| File | Functions | Description |
|------|-----------|-------------|
| `daw/__init__.py` | - | Package exports |
| `daw/logic.py` | `LogicProIntegration` | Logic Pro X integration |
| `daw/pro_tools.py` | `ProToolsIntegration` | Pro Tools integration |
| `daw/reaper.py` | `ReaperIntegration` | Reaper integration |
| `daw/fl_studio.py` | `FLStudioIntegration` | FL Studio integration |
| `daw/markers.py` | `MarkerManager` | Section markers |
| `daw/mixer_params.py` | `MixerParams` | Mixer parameter mapping |

### Voice Package (5 files)
| File | Functions | Description |
|------|-----------|-------------|
| `voice/__init__.py` | - | Package exports |
| `voice/synth.py` | `VoiceSynth` | Voice synthesis |
| `voice/auto_tune.py` | `AutoTune` | Pitch correction |
| `voice/modulator.py` | `VoiceModulator` | Voice modulation effects |
| `voice/synthesizer.py` | `Synthesizer` | Full voice synthesizer |

### Agents Package (5 files)
| File | Functions | Description |
|------|-----------|-------------|
| `agents/__init__.py` | - | Package exports |
| `agents/unified_hub.py` | `UnifiedHub` | Central agent coordinator |
| `agents/crewai_music_agents.py` | CrewAI integration | Multi-agent music production |
| `agents/ableton_bridge.py` | `AbletonBridge` | Ableton Live integration |
| `agents/voice_profiles.py` | `VoiceProfiles` | Voice character profiles |

### Arrangement Package (5 files)
| File | Functions | Description |
|------|-----------|-------------|
| `arrangement/__init__.py` | - | Package exports |
| `arrangement/energy_arc.py` | `EnergyArc` | Song energy mapping |
| `arrangement/bass_generator.py` | `BassGenerator` | Bass line generation |
| `arrangement/templates.py` | Arrangement templates | Song structure templates |
| `arrangement/generator.py` | `ArrangementGenerator` | Full arrangement generation |

### Orchestrator Package (8 files)
| File | Functions | Description |
|------|-----------|-------------|
| `orchestrator/__init__.py` | - | Package exports |
| `orchestrator/orchestrator.py` | `Orchestrator` | Central processing coordinator |
| `orchestrator/pipeline.py` | `Pipeline` | Processing pipeline |
| `orchestrator/bridge_api.py` | `BridgeAPI` | External API bridge |
| `orchestrator/interfaces.py` | Type interfaces | Shared interfaces |
| `orchestrator/logging_utils.py` | Logging | Structured logging |
| `orchestrator/processors/base.py` | `BaseProcessor` | Processor base class |
| `orchestrator/processors/groove.py` | `GrooveProcessor` | Groove processing |
| `orchestrator/processors/harmony.py` | `HarmonyProcessor` | Harmony processing |
| `orchestrator/processors/intent.py` | `IntentProcessor` | Intent processing |

### Collaboration Package (5 files)
| File | Functions | Description |
|------|-----------|-------------|
| `collaboration/__init__.py` | - | Package exports |
| `collaboration/session.py` | `CollabSession` | Collaborative session |
| `collaboration/comments.py` | `CommentSystem` | Track comments |
| `collaboration/version_control.py` | `VersionControl` | Project versioning |
| `collaboration/websocket.py` | `WebSocketServer` | Real-time sync |
| `collaboration/editing.py` | `CollabEditing` | Collaborative editing |

### Other Root Modules (8 files)
| File | Functions | Description |
|------|-----------|-------------|
| `__init__.py` | - | Package exports (v0.2.0) |
| `cli.py` | `daiw` command | CLI entry point |
| `api.py` | Public API | Main API module |
| `emotion_api.py` | Emotion processing | Emotion-to-music mapping |
| `harmony.py` | Harmony utilities | Core harmony functions |
| `groove_engine.py` | Groove utilities | Core groove functions |
| `text/lyrical_mirror.py` | Lyric analysis | Text-to-emotion mapping |
| `data/emotional_mapping.py` | Emotion data | Emotion-music mappings |
| `integrations/penta_core.py` | Penta-Core bridge | C++ engine bridge |
| `utils/midi_io.py` | MIDI utilities | MIDI file I/O |
| `utils/instruments.py` | Instrument mapping | GM instrument definitions |
| `utils/ppq.py` | PPQ utilities | Timing calculations |

---

## Python Penta-Core Modules

**Source:** `/home/user/iDAW/python/penta_core/`
**Target:** `/home/user/iDAW/iDAWi/penta-core/`

### Rules Package (11 files)
| File | Classes | Description |
|------|---------|-------------|
| `rules/__init__.py` | - | Package exports |
| `rules/base.py` | `Rule`, `RuleViolation` | Base rule classes |
| `rules/harmony_rules.py` | `HarmonyRule` | Harmony validation rules |
| `rules/rhythm_rules.py` | `RhythmRule` | Rhythm validation rules |
| `rules/counterpoint_rules.py` | `CounterpointRule` | Voice leading rules |
| `rules/voice_leading.py` | `VoiceLeadingAnalyzer` | Voice leading analysis |
| `rules/species.py` | `SpeciesCounterpoint` | Species counterpoint rules |
| `rules/emotion.py` | `EmotionRule` | Emotion-based rules |
| `rules/timing.py` | `TimingRule` | Timing/groove rules |
| `rules/severity.py` | `Severity` enum | Violation severity levels |
| `rules/context.py` | `RuleContext` | Rule evaluation context |

### Teachers Package (5 files)
| File | Classes | Description |
|------|---------|-------------|
| `teachers/rule_breaking_teacher.py` | `RuleBreakingTeacher` | Interactive rule-breaking education |
| `teachers/voice_leading_rules.py` | VL teaching | Voice leading instruction |
| `teachers/counterpoint_rules.py` | CP teaching | Counterpoint instruction |
| `teachers/harmony_rules.py` | Harmony teaching | Harmony instruction |
| `teachers/rule_reference.py` | Reference docs | Rule documentation |

### Groove Package (6 files)
| File | Classes | Description |
|------|---------|-------------|
| `groove/__init__.py` | - | Package exports |
| `groove/groove_dna.py` | `GrooveDNA` | Groove fingerprinting |
| `groove/humanization.py` | `Humanizer` | Add human feel |
| `groove/drum_replacement.py` | `DrumReplacer` | Drum sound replacement |
| `groove/polyrhythm.py` | `PolyrhythmGenerator` | Polyrhythm generation |
| `groove/performance.py` | `PerformanceAnalyzer` | Performance analysis |

### Harmony Package (6 files)
| File | Classes | Description |
|------|---------|-------------|
| `harmony/__init__.py` | - | Package exports |
| `harmony/jazz_voicings.py` | `JazzVoicings` | Jazz chord voicings |
| `harmony/counterpoint.py` | `CounterpointEngine` | Counterpoint generation |
| `harmony/neo_riemannian.py` | `NeoRiemannian` | Neo-Riemannian transformations |
| `harmony/tension.py` | `TensionCalculator` | Harmonic tension analysis |
| `harmony/microtonal.py` | `MicrotonalSystem` | Microtonal support |

### ML Package (6 files)
| File | Classes | Description |
|------|---------|-------------|
| `ml/__init__.py` | - | Package exports |
| `ml/chord_predictor.py` | `ChordPredictor` | ML chord prediction |
| `ml/style_transfer.py` | `StyleTransfer` | Style transfer model |
| `ml/model_registry.py` | `ModelRegistry` | Model management |
| `ml/inference.py` | `InferenceEngine` | ML inference |
| `ml/gpu_utils.py` | GPU utilities | GPU acceleration |

### DSP Package (3 files)
| File | Classes | Description |
|------|---------|-------------|
| `dsp/__init__.py` | - | Package exports |
| `dsp/parrot_dsp.py` | `ParrotDSP` | Parrot plugin DSP |
| `dsp/trace_dsp.py` | `TraceDSP` | Trace plugin DSP |

### Collaboration Package (4 files)
| File | Classes | Description |
|------|---------|-------------|
| `collaboration/__init__.py` | - | Package exports |
| `collaboration/websocket_server.py` | `WebSocketServer` | Real-time server |
| `collaboration/collab_ui.py` | `CollabUI` | Collaboration UI |
| `collaboration/intent_versioning.py` | `IntentVersioning` | Intent history |

### Phases Package (5 files)
| File | Classes | Description |
|------|---------|-------------|
| `phases/__init__.py` | - | Package exports |
| `phases/phase1_infrastructure.py` | Phase 1 | Infrastructure setup |
| `phases/phase2_python_api.py` | Phase 2 | Python API |
| `phases/phase3_cpp_engine.py` | Phase 3 | C++ engine |
| `phases/phase4_plugin.py` | Phase 4 | Plugin integration |

### Root Modules (3 files)
| File | Classes | Description |
|------|---------|-------------|
| `__init__.py` | - | Package exports |
| `server.py` | `PentaCoreServer` | MCP server |
| `utilities.py` | Utility functions | Common utilities |

---

## C++ Engine Headers

**Source:** `/home/user/iDAW/include/penta/`
**Target:** `/home/user/iDAW/iDAWi/native/include/penta/`

### Common (4 files)
| File | Classes | Description |
|------|---------|-------------|
| `common/RTTypes.h` | RT type aliases | Real-time safe types |
| `common/RTLogger.h` | `RTLogger` | Lock-free logging |
| `common/RTMemoryPool.h` | `RTMemoryPool` | Pre-allocated memory |
| `common/SIMDKernels.h` | SIMD functions | AVX2 optimizations |

### Groove (4 files)
| File | Classes | Description |
|------|---------|-------------|
| `groove/GrooveEngine.h` | `GrooveEngine` | Main groove processor |
| `groove/OnsetDetector.h` | `OnsetDetector` | Beat detection |
| `groove/TempoEstimator.h` | `TempoEstimator` | BPM estimation |
| `groove/RhythmQuantizer.h` | `RhythmQuantizer` | Quantization |

### Harmony (4 files)
| File | Classes | Description |
|------|---------|-------------|
| `harmony/HarmonyEngine.h` | `HarmonyEngine` | Main harmony processor |
| `harmony/ChordAnalyzer.h` | `ChordAnalyzer` | Chord detection |
| `harmony/ScaleDetector.h` | `ScaleDetector` | Scale detection |
| `harmony/VoiceLeading.h` | `VoiceLeading` | Voice leading analysis |

### Diagnostics (3 files)
| File | Classes | Description |
|------|---------|-------------|
| `diagnostics/DiagnosticsEngine.h` | `DiagnosticsEngine` | Main diagnostics |
| `diagnostics/AudioAnalyzer.h` | `AudioAnalyzer` | Audio analysis |
| `diagnostics/PerformanceMonitor.h` | `PerformanceMonitor` | Performance metrics |

### OSC (5 files)
| File | Classes | Description |
|------|---------|-------------|
| `osc/OSCHub.h` | `OSCHub` | Central OSC routing |
| `osc/OSCClient.h` | `OSCClient` | OSC sender |
| `osc/OSCServer.h` | `OSCServer` | OSC receiver |
| `osc/OSCMessage.h` | `OSCMessage` | Message types |
| `osc/RTMessageQueue.h` | `RTMessageQueue` | Lock-free queue |

### ML (1 file)
| File | Classes | Description |
|------|---------|-------------|
| `ml/MLInterface.h` | `MLInterface` | ML model interface |

---

## C++ Engine Source

**Source:** `/home/user/iDAW/src_penta-core/`
**Target:** `/home/user/iDAW/iDAWi/native/src/`

| Directory | Files | Description |
|-----------|-------|-------------|
| `common/` | `RTMemoryPool.cpp`, `RTLogger.cpp` | Core utilities |
| `groove/` | `GrooveEngine.cpp`, `OnsetDetector.cpp`, `TempoEstimator.cpp`, `RhythmQuantizer.cpp` | Groove processing |
| `harmony/` | `HarmonyEngine.cpp`, `ChordAnalyzer.cpp`, `ChordAnalyzerSIMD.cpp`, `ScaleDetector.cpp`, `VoiceLeading.cpp` | Harmony processing |
| `diagnostics/` | `DiagnosticsEngine.cpp`, `AudioAnalyzer.cpp`, `PerformanceMonitor.cpp` | Diagnostics |
| `osc/` | `OSCHub.cpp`, `OSCClient.cpp`, `OSCServer.cpp`, `OSCMessage.cpp`, `RTMessageQueue.cpp` | OSC communication |
| `ml/` | `MLInterface.cpp` | ML integration |

---

## JUCE Plugin Suite

**Source:** `/home/user/iDAW/iDAW_Core/`
**Target:** `/home/user/iDAW/iDAWi/native/plugins/`

### Core Components (6 files)
| File | Classes | Description |
|------|---------|-------------|
| `include/MemoryManager.h` | `MemoryManager` | Dual-heap memory |
| `include/PythonBridge.h` | `PythonBridge` | Python embedding |
| `include/DreamStateComponent.h` | `DreamStateComponent` | AI generation UI |
| `include/SafetyUtils.h` | Safety utilities | RT-safety checks |
| `include/Version.h` | Version info | Build version |
| `src/*.cpp` | Implementations | |

### Plugins (11 plugins, 22 files)
| Plugin | Priority | Description |
|--------|----------|-------------|
| **Pencil** | HIGH | Sketching/drafting audio ideas |
| **Eraser** | HIGH | Audio removal/cleanup |
| **Press** | HIGH | Dynamics/compression |
| **Palette** | MID | Tonal coloring/mixing |
| **Smudge** | MID | Audio blending/smoothing |
| **Chalk** | LOW | Lo-fi/bitcrusher effect |
| **Brush** | LOW | Modulated filter effect |
| **Trace** | LOW | Pattern following/automation |
| **Parrot** | LOW | Sample playback/mimicry |
| **Stencil** | LOW | Sidechain/ducking effect |
| **Stamp** | LOW | Stutter/repeater effect |

---

## MCP Servers

**Source:** `/home/user/iDAW/mcp_*/`
**Target:** `/home/user/iDAW/iDAWi/mcp/`

### mcp_workstation (11 files)
| File | Classes | Description |
|------|---------|-------------|
| `__init__.py` | - | Package exports (v1.0.0) |
| `cli.py` | CLI commands | Workstation CLI |
| `orchestrator.py` | `Workstation` | Central coordinator |
| `models.py` | `AIAgent`, `Proposal`, `Phase` | Data models |
| `proposals.py` | `ProposalManager` | Proposal management |
| `phases.py` | `PhaseTracker` | Phase tracking |
| `cpp_planner.py` | `CppPlanner` | C++ transition planning |
| `ai_specializations.py` | AI capabilities | Task assignment |
| `server.py` | MCP server | MCP protocol server |
| `debug.py` | Debug logging | Debug protocol |
| `__main__.py` | Entry point | Package entry |

### mcp_todo (10 files)
| File | Classes | Description |
|------|---------|-------------|
| `__init__.py` | - | Package exports |
| `cli.py` | CLI commands | TODO CLI |
| `server.py` | MCP server | MCP protocol server |
| `http_server.py` | HTTP server | REST API server |
| `storage.py` | `TodoStorage` | File-based storage |
| `models.py` | `Todo`, `Project` | Data models |
| `mcp_routes.py` | MCP routes | Route definitions |
| `roadmap.py` | `Roadmap` | Project roadmap |
| `__main__.py` | Entry point | Package entry |

---

## GitHub Workflows

**Source:** `/home/user/iDAW/.github/workflows/`
**Target:** `/home/user/iDAW/iDAWi/.github/workflows/`

| File | Jobs | Description |
|------|------|-------------|
| `ci.yml` | Python tests, C++ builds, Valgrind, Performance | Main CI pipeline |
| `release.yml` | Desktop builds, Python dist, C++ libs | Release pipeline |
| `sprint_suite.yml` | 8 sprint jobs | Comprehensive testing |
| `platform_support.yml` | Matrix tests | Cross-platform (3.9-3.13) |
| `test.yml` | Quick tests | PR testing |

---

## Documentation

**Source:** Various locations
**Target:** `/home/user/iDAW/iDAWi/docs/`

### Vault (Obsidian Knowledge Base)
| Directory | Files | Description |
|-----------|-------|-------------|
| `vault/Production_Guides/` | 7 | Drum, Bass, Guitar, EQ, Compression, Dynamics, Groove guides |
| `vault/Songwriting_Guides/` | 3 | Rule breaking, Intent schema |
| `vault/Songs/when-i-found-you-sleeping/` | 9 | Example song project |
| `vault/Templates/` | 1 | Task board template |

### Root Documentation
| File | Description |
|------|-------------|
| `CLAUDE.md` | AI assistant guide (18.4 KB) |
| `README.md` | Main repository documentation |
| `MERGE_SUMMARY.md` | Merge strategy documentation |
| `MERGE_COMPLETE.md` | Merge completion report |
| `INTEGRATION_GUIDE.md` | Developer workflow guide |

---

## External Dependencies

**Source:** `/home/user/iDAW/external/`
**Target:** `/home/user/iDAW/iDAWi/native/external/`

| File | Description |
|------|-------------|
| `oscpack-stub/oscpack.h` | OSC protocol library stub |
| `readerwriterqueue-stub/readerwriterqueue.h` | Lock-free queue stub |
| `CMakeLists.txt` | External deps build config |

---

## Import Priority Matrix

### Phase 1: Critical (Required for Basic Functionality)
| Component | Files | Rationale |
|-----------|-------|-----------|
| Data_Files/*.json | 5 | Core music theory data |
| music_brain/session/* | 5 | Intent processing |
| music_brain/groove/* | 5 | Groove extraction |
| music_brain/structure/* | 6 | Chord/progression analysis |

### Phase 2: High (Enhanced Features)
| Component | Files | Rationale |
|-----------|-------|-----------|
| python/penta_core/rules/* | 11 | Rule validation system |
| python/penta_core/teachers/* | 5 | Interactive teaching |
| music_brain/orchestrator/* | 8 | Pipeline processing |
| mcp_todo/* | 10 | Task management |

### Phase 3: Medium (Advanced Features)
| Component | Files | Rationale |
|-----------|-------|-----------|
| include/penta/* | 21 | C++ engine headers |
| src_penta-core/* | 20 | C++ implementations |
| music_brain/audio/* | 6 | Audio analysis |
| music_brain/daw/* | 7 | DAW integration |
| python/penta_core/harmony/* | 6 | Advanced harmony |
| python/penta_core/ml/* | 6 | ML features |

### Phase 4: Low (Future/Optional)
| Component | Files | Rationale |
|-----------|-------|-----------|
| iDAW_Core/* | 33 | JUCE plugins |
| mcp_workstation/* | 11 | Multi-AI orchestration |
| vault/* | 22 | Documentation |
| .github/workflows/* | 5 | CI/CD |

---

## Next Steps

1. **Copy Data_Files** to `iDAWi/data/`
2. **Expand music-brain** with full module set
3. **Add penta_core** Python bindings
4. **Update requirements.txt** with all dependencies
5. **Create native/ directory** for C++ components
6. **Add MCP servers** for AI orchestration
7. **Import documentation** to docs/
8. **Configure CI/CD** workflows

---

*This manifest was generated by analyzing 253+ files across the iDAW monorepo.*
