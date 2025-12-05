# MCP Phase 1 - Real-Time Audio Engine Development Tools

Model Context Protocol (MCP) server for Phase 1 of the iDAWi project: building the real-time audio engine.

## Overview

This MCP server provides a comprehensive set of tools for developing and testing Phase 1 components:

| Module | Tools | Description |
|--------|-------|-------------|
| **Audio Engine** | 9 tools | Device management, I/O testing, latency measurement |
| **MIDI Tools** | 12 tools | Device control, event processing, clock synchronization |
| **Transport** | 13 tools | Playback control, position tracking, loop management |
| **Mixer** | 14 tools | Channel routing, gain/pan, metering |
| **Phase 1 Status** | 4 tools | Development tracking and progress monitoring |

**Total: 52 tools** for comprehensive Phase 1 development support.

## Quick Start

### 1. Install Dependencies

```bash
cd /path/to/iDAWi/DAiW-Music-Brain
pip install -e .
```

### 2. Run the Server

```bash
python -m mcp_phase1.server
```

### 3. Configure Your AI Assistant

See `configs/` directory for configuration files for:
- Claude Desktop (`claude_desktop.json`)
- Cursor (`cursor.json`)
- VS Code with Copilot (`vscode_settings.json`)

## Architecture

```
mcp_phase1/
├── __init__.py          # Package initialization
├── server.py            # Main MCP server (unified entry point)
├── models.py            # Data models (AudioDevice, MIDI, Transport, Mixer)
├── storage.py           # Persistent state storage
├── audio_engine.py      # Audio I/O tools
├── midi_tools.py        # MIDI engine tools
├── transport.py         # Transport control tools
├── mixer.py             # Mixer tools
├── configs/             # AI assistant configurations
│   ├── claude_desktop.json
│   ├── cursor.json
│   ├── vscode_settings.json
│   └── setup_guide.md
└── tests/               # Test suite
```

## Available Tools

### Audio Engine Tools

| Tool | Description |
|------|-------------|
| `audio_list_devices` | List available audio devices |
| `audio_select_device` | Select input/output device |
| `audio_configure` | Set sample rate, buffer size |
| `audio_start` | Start the audio engine |
| `audio_stop` | Stop the audio engine |
| `audio_status` | Get engine status (CPU, latency, xruns) |
| `audio_latency_test` | Run latency measurement |
| `audio_stress_test` | Run xrun/dropout stress test |
| `audio_reset` | Reset to default settings |

### MIDI Tools

| Tool | Description |
|------|-------------|
| `midi_list_devices` | List MIDI devices |
| `midi_open_device` | Open MIDI device |
| `midi_close_device` | Close MIDI device |
| `midi_send_event` | Send MIDI event |
| `midi_clock_config` | Configure clock sync |
| `midi_clock_start` | Start MIDI clock |
| `midi_clock_stop` | Stop MIDI clock |
| `midi_status` | Get MIDI state |
| `midi_cc_set` | Set CC value |
| `midi_cc_get` | Get CC values |
| `midi_learn` | Enable MIDI learn |
| `midi_reset` | Reset MIDI state |

### Transport Tools

| Tool | Description |
|------|-------------|
| `transport_play` | Start playback |
| `transport_pause` | Pause playback |
| `transport_stop` | Stop and return to start |
| `transport_record` | Start recording |
| `transport_status` | Get transport state |
| `transport_position_set` | Set position (samples/beats/bars) |
| `transport_position_get` | Get position in all formats |
| `transport_tempo_set` | Set tempo (BPM) |
| `transport_time_signature_set` | Set time signature |
| `transport_loop_set` | Set loop region |
| `transport_loop_toggle` | Toggle loop on/off |
| `transport_locate` | Locate to marker |
| `transport_nudge` | Nudge position |

### Mixer Tools

| Tool | Description |
|------|-------------|
| `mixer_status` | Get mixer state |
| `mixer_channel_add` | Add new channel |
| `mixer_channel_remove` | Remove channel |
| `mixer_channel_get` | Get channel settings |
| `mixer_gain_set` | Set gain (channel or master) |
| `mixer_pan_set` | Set pan position |
| `mixer_mute_toggle` | Toggle mute |
| `mixer_solo_toggle` | Toggle solo |
| `mixer_solo_clear` | Clear all solos |
| `mixer_aux_send_set` | Set aux send level |
| `mixer_meters_get` | Get meter readings |
| `mixer_solo_mode_set` | Set AFL/PFL mode |
| `mixer_reset` | Reset mixer |
| `mixer_channel_rename` | Rename channel |
| `mixer_routing_set` | Set output routing |

### Phase 1 Status Tools

| Tool | Description |
|------|-------------|
| `phase1_status` | Get overall Phase 1 status |
| `phase1_component_update` | Update component progress |
| `phase1_checklist` | View completion checklist |
| `phase1_activity_log` | View activity log |

## State Storage

State is persisted in `~/.mcp_phase1/` for cross-AI synchronization:

```
~/.mcp_phase1/
├── audio_state.json      # Audio engine configuration
├── midi_state.json       # MIDI engine state
├── transport_state.json  # Transport position/tempo
├── mixer_state.json      # Mixer channels/settings
├── phase1_status.json    # Development progress
└── activity_log.json     # Activity history
```

## Phase 1 Components

Track development progress for each Phase 1 component:

| Component | Description |
|-----------|-------------|
| `audio_io` | Audio I/O backends (CoreAudio, WASAPI, ALSA) |
| `midi_engine` | MIDI input/output and clock |
| `transport` | Playback control system |
| `mixer` | Channel routing and mixing |
| `dsp_graph` | Processing graph compilation |
| `recording` | Audio recording functionality |

## Example Usage

### Configure and Start Audio

```python
# List available devices
audio_list_devices()

# Configure engine
audio_configure(sample_rate=48000, buffer_size=256)

# Select output device
audio_select_device(device_id=0, role="output")

# Start engine
audio_start()

# Check status
audio_status()
```

### Track Development Progress

```python
# Update component status
phase1_component_update(
    component="audio_io",
    status="in_progress",
    progress=0.5,
    note="CoreAudio backend completed, starting WASAPI"
)

# View checklist
phase1_checklist()
```

## Integration with penta-core C++

This MCP server simulates the Phase 1 audio engine for testing and development coordination. As you implement the actual C++ components in `penta-core/`:

1. Use the MCP tools to design and validate API interfaces
2. Track progress using `phase1_component_update`
3. Compare simulated vs actual behavior
4. Coordinate across multiple AI assistants

## Multi-AI Collaboration

The MCP Phase 1 server enables collaboration between AI assistants:

- **Claude**: Architecture design, code review
- **ChatGPT**: Algorithm implementation, documentation
- **Gemini**: Testing, optimization
- **GitHub Copilot**: Code completion, refactoring

All assistants share state through the storage files, enabling seamless handoffs and parallel development.

## Related Documentation

- [Phase 1 Implementation Guide](../../PHASE1_AUDIO_ENGINE_GUIDE.md)
- [penta-core C++ README](../../penta-core/README.md)
- [MCP TODO Server](../mcp_todo/README.md)
- [MCP Workstation](../mcp_workstation/README.md)

## License

Part of the iDAWi project. See root LICENSE file.
