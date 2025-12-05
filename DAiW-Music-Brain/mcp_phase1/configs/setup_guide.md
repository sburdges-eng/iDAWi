# MCP Phase 1 Server Setup Guide

This guide covers setting up the MCP Phase 1 server for different AI assistants.

## Overview

The Phase 1 MCP server provides tools for developing and testing the iDAWi real-time audio engine:

- **Audio I/O**: Device management, buffer configuration, latency testing
- **MIDI**: Device control, event processing, clock synchronization
- **Transport**: Playback control, position tracking, loop management
- **Mixer**: Channel routing, gain/pan control, metering

## Available Tools (50+ tools)

### Audio Tools
- `audio_list_devices` - List available audio devices
- `audio_select_device` - Select input/output device
- `audio_configure` - Set sample rate, buffer size
- `audio_start` / `audio_stop` - Control audio engine
- `audio_status` - Get engine status
- `audio_latency_test` - Measure latency
- `audio_stress_test` - Test for xruns/dropouts
- `audio_reset` - Reset to defaults

### MIDI Tools
- `midi_list_devices` - List MIDI devices
- `midi_open_device` / `midi_close_device` - Device control
- `midi_send_event` - Send MIDI events
- `midi_clock_config` - Configure clock sync
- `midi_clock_start` / `midi_clock_stop` - Clock control
- `midi_cc_set` / `midi_cc_get` - CC value management
- `midi_learn` - MIDI learn mode
- `midi_reset` - Reset MIDI state

### Transport Tools
- `transport_play` / `transport_pause` / `transport_stop`
- `transport_record` - Start recording
- `transport_status` - Get transport state
- `transport_position_set` / `transport_position_get`
- `transport_tempo_set` - Set BPM
- `transport_time_signature_set` - Set time signature
- `transport_loop_set` / `transport_loop_toggle`
- `transport_locate` - Locate to markers
- `transport_nudge` - Nudge position

### Mixer Tools
- `mixer_status` - Get mixer state
- `mixer_channel_add` / `mixer_channel_remove`
- `mixer_gain_set` / `mixer_pan_set`
- `mixer_mute_toggle` / `mixer_solo_toggle`
- `mixer_solo_clear` - Clear all solos
- `mixer_aux_send_set` - Set aux sends
- `mixer_meters_get` - Get meter readings
- `mixer_reset` - Reset mixer

### Phase 1 Status Tools
- `phase1_status` - Get overall status
- `phase1_component_update` - Update component progress
- `phase1_checklist` - View completion checklist
- `phase1_activity_log` - View activity log

---

## Setup Instructions

### Claude Desktop

1. Open Claude Desktop settings
2. Navigate to the MCP Servers configuration
3. Add the following configuration:

```json
{
  "mcpServers": {
    "phase1-audio-engine": {
      "command": "python",
      "args": ["-m", "mcp_phase1.server"],
      "cwd": "/path/to/iDAWi/DAiW-Music-Brain",
      "env": {
        "PYTHONPATH": "/path/to/iDAWi/DAiW-Music-Brain"
      }
    }
  }
}
```

### Cursor

1. Open Cursor settings (Cmd+, or Ctrl+,)
2. Search for "MCP"
3. Add the server configuration from `cursor.json`

### VS Code with Copilot

1. Open VS Code settings.json
2. Add the configuration from `vscode_settings.json`

---

## Testing the Server

Run the server manually to test:

```bash
cd /path/to/iDAWi/DAiW-Music-Brain
python -m mcp_phase1.server
```

You should see:
```
MCP Phase 1 Server v1.0.0 starting...
Tools: Audio I/O, MIDI, Transport, Mixer, Phase 1 Status
```

---

## State Storage

The server stores state in `~/.mcp_phase1/`:

- `audio_state.json` - Audio engine state
- `midi_state.json` - MIDI engine state
- `transport_state.json` - Transport state
- `mixer_state.json` - Mixer state
- `phase1_status.json` - Phase 1 development progress
- `activity_log.json` - Activity log

This enables cross-AI collaboration on Phase 1 development.

---

## Example Usage

### Start Audio Engine
```
Use audio_configure to set sample_rate=48000, buffer_size=256
Then use audio_start to start the engine
```

### Check Latency
```
Use audio_latency_test with duration_seconds=5
```

### Update Phase 1 Progress
```
Use phase1_component_update with:
- component: "audio_io"
- status: "in_progress"
- progress: 0.5
- note: "CoreAudio backend implemented"
```

---

## Integration with C++ Development

This MCP server simulates the audio engine for testing. As you implement the actual C++ components in `penta-core/`, you can:

1. Update Phase 1 status to track progress
2. Use the simulated tools to design API interfaces
3. Compare simulated behavior with actual implementation
4. Coordinate across multiple AI assistants

The state files in `~/.mcp_phase1/` serve as a shared workspace for all AI assistants working on Phase 1.
