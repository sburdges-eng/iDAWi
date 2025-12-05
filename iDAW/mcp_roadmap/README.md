# MCP Roadmap Server

Model Context Protocol (MCP) server for managing the iDAWi project roadmap. Provides tools for querying, tracking, and updating project phases, milestones, and tasks across multiple AI assistants.

## Features

- **Multi-AI Compatible**: Works with Claude (Desktop/Code), ChatGPT, Gemini, and Cursor/VSCode with Copilot
- **Roadmap Management**: Track phases, milestones, quarters, and individual tasks
- **Progress Tracking**: Real-time progress calculations and status updates
- **Task Prioritization**: P0-P4 priority levels with filtering
- **CLI & MCP Server**: Both command-line and MCP protocol interfaces

## Installation

The mcp_roadmap package is part of the iDAWi project. No separate installation required.

```bash
# From the iDAW directory
cd /path/to/iDAWi/iDAW

# Run CLI
python -m mcp_roadmap overview
python -m mcp_roadmap summary
python -m mcp_roadmap phases

# Run MCP server
python -m mcp_roadmap server
```

## CLI Commands

```bash
# Overview Commands
mcp-roadmap overview          # High-level roadmap overview
mcp-roadmap summary           # Detailed summary with statistics
mcp-roadmap progress          # Formatted progress view

# Phase Commands
mcp-roadmap phases            # List all phases
mcp-roadmap phases --status in_progress
mcp-roadmap phase 1           # Show Phase 1 details
mcp-roadmap phase 1 -v        # Show with all tasks

# Quarter Commands
mcp-roadmap quarters          # Show 18-month quarters

# Task Commands
mcp-roadmap tasks             # List all tasks
mcp-roadmap tasks --phase 1   # Filter by phase
mcp-roadmap tasks --priority P0  # Filter by priority
mcp-roadmap task 1.1.1        # Show task details
mcp-roadmap search "MIDI"     # Search tasks

# Update Commands
mcp-roadmap update 1.1.1 --status in_progress
mcp-roadmap assign 1.1.1 claude
mcp-roadmap next --limit 5    # Show next tasks to work on

# Export & Metrics
mcp-roadmap metrics           # Show success metrics
mcp-roadmap export --format json
```

## MCP Tools

The server exposes 20+ tools for roadmap management:

### Overview Tools
- `roadmap_overview` - Get high-level overview
- `roadmap_summary` - Get statistics
- `roadmap_progress` - Get formatted progress view

### Phase Tools
- `phase_list` - List phases with filters
- `phase_get` - Get phase details
- `phase_current` - Get current active phase

### Quarter Tools
- `quarter_list` - List 18-month quarters
- `quarter_get` - Get quarter details

### Task Tools
- `task_list` - List tasks with filters
- `task_get` - Get task details
- `task_search` - Search tasks
- `task_update_status` - Update task status
- `task_assign` - Assign task
- `task_add_note` - Add note to task

### Priority Tools
- `priority_tasks` - Get tasks by priority
- `next_tasks` - Get next tasks to work on

### Metrics Tools
- `metrics_get` - Get success metrics

### Export Tools
- `roadmap_export` - Export in various formats

## Configuration

### Claude Desktop

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "mcp-roadmap": {
      "command": "python",
      "args": ["-m", "mcp_roadmap.server"],
      "cwd": "/path/to/iDAWi/iDAW"
    }
  }
}
```

### Claude Code

Add to your project's MCP configuration:

```json
{
  "mcpServers": {
    "mcp-roadmap": {
      "command": "python",
      "args": ["-m", "mcp_roadmap.server"],
      "cwd": "/path/to/iDAWi/iDAW"
    }
  }
}
```

### Cursor

Add to `.cursor/mcp.json`:

```json
{
  "mcp-roadmap": {
    "command": "python",
    "args": ["-m", "mcp_roadmap.server"],
    "cwd": "/path/to/iDAWi/iDAW"
  }
}
```

## Data Storage

Roadmap data is stored in JSON format at `~/.mcp_roadmap/roadmap.json`. The storage is initialized from the project's markdown roadmap files and can be reset using:

```bash
mcp-roadmap reinit --confirm
```

## Priority Levels

| Priority | Description |
|----------|-------------|
| P0 | Critical for MVP - must have |
| P1 | High - essential for beta |
| P2 | Medium - needed for 1.0 |
| P3 | Low - nice to have |
| P4 | Future - planned for later |

## Task Statuses

- `not_started` - Task not yet begun
- `in_progress` - Currently being worked on
- `completed` - Task finished
- `blocked` - Task blocked by dependencies
- `deferred` - Task postponed

## Architecture

```
mcp_roadmap/
├── __init__.py       # Package initialization
├── __main__.py       # Module entry point
├── models.py         # Data models (Phase, Milestone, Task, etc.)
├── storage.py        # Storage and markdown parser
├── server.py         # MCP server implementation
├── cli.py            # Command-line interface
├── configs/          # AI client configurations
│   ├── claude_desktop_config.json
│   ├── claude_code_config.json
│   ├── cursor_mcp.json
│   └── vscode_settings.json
└── README.md
```

## Integration with Other MCP Servers

The roadmap server works alongside other iDAWi MCP servers:

- **mcp_todo**: Task management across AIs
- **mcp_workstation**: Multi-AI orchestration and proposals

Tasks from the roadmap can be linked to TODOs in mcp_todo for day-to-day tracking.

## License

Part of the iDAWi project.
