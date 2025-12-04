#!/usr/bin/env python3
"""
MCP Roadmap Server

Model Context Protocol server for iDAWi project roadmap management.
Provides tools to query, track, and update project phases and milestones.

Run with:
    python -m mcp_roadmap.server
    # or
    mcp-roadmap-server
"""

import json
import sys
import asyncio
from typing import Any, Dict, List, Optional

from .storage import RoadmapStorage
from .models import TaskStatus, Priority


class MCPRoadmapServer:
    """
    MCP-compliant Roadmap server.

    Implements the Model Context Protocol for tool-based interaction
    with AI assistants for roadmap management.
    """

    def __init__(self, storage_dir: Optional[str] = None, project_root: Optional[str] = None):
        self.storage = RoadmapStorage(storage_dir, project_root)
        self.server_info = {
            "name": "mcp-roadmap",
            "version": "1.0.0",
            "description": "iDAWi project roadmap management server",
        }

    def get_tools(self) -> List[Dict[str, Any]]:
        """Return the list of available MCP tools."""
        return [
            # Overview Tools
            {
                "name": "roadmap_overview",
                "description": "Get a high-level overview of the entire iDAWi roadmap including progress, phases, and timeline.",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                },
            },
            {
                "name": "roadmap_summary",
                "description": "Get a summary of roadmap progress with statistics on tasks, phases, and completion rates.",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                },
            },
            {
                "name": "roadmap_progress",
                "description": "Get a formatted progress view showing all phases and their completion status.",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                },
            },

            # Phase Tools
            {
                "name": "phase_list",
                "description": "List all development phases with their status and progress.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "status": {
                            "type": "string",
                            "enum": ["not_started", "in_progress", "completed", "blocked"],
                            "description": "Filter by phase status",
                        },
                    },
                },
            },
            {
                "name": "phase_get",
                "description": "Get detailed information about a specific phase including all milestones and tasks.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "phase_id": {
                            "type": "integer",
                            "description": "The phase ID (0-14)",
                        },
                    },
                    "required": ["phase_id"],
                },
            },
            {
                "name": "phase_current",
                "description": "Get the currently active phase (in-progress or next to start).",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                },
            },

            # Quarter/Timeline Tools
            {
                "name": "quarter_list",
                "description": "List all quarterly milestones from the 18-month roadmap.",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                },
            },
            {
                "name": "quarter_get",
                "description": "Get details about a specific quarter (e.g., Q1_2025, H1_2026).",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "quarter_id": {
                            "type": "string",
                            "description": "Quarter ID (e.g., Q1_2025, Q2_2025, H1_2026)",
                        },
                    },
                    "required": ["quarter_id"],
                },
            },

            # Milestone Tools
            {
                "name": "milestone_get",
                "description": "Get details about a specific milestone within a phase.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "phase_id": {
                            "type": "integer",
                            "description": "The phase ID",
                        },
                        "milestone_id": {
                            "type": "string",
                            "description": "The milestone ID (e.g., '1.1', '2.3')",
                        },
                    },
                    "required": ["phase_id", "milestone_id"],
                },
            },

            # Task Tools
            {
                "name": "task_list",
                "description": "List tasks with optional filters by status, priority, or phase.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "phase_id": {
                            "type": "integer",
                            "description": "Filter by phase ID",
                        },
                        "status": {
                            "type": "string",
                            "enum": ["not_started", "in_progress", "completed", "blocked", "deferred"],
                            "description": "Filter by task status",
                        },
                        "priority": {
                            "type": "string",
                            "enum": ["P0", "P1", "P2", "P3", "P4"],
                            "description": "Filter by priority (P0=critical, P4=future)",
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of tasks to return",
                        },
                    },
                },
            },
            {
                "name": "task_get",
                "description": "Get detailed information about a specific task.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "task_id": {
                            "type": "string",
                            "description": "The task ID (e.g., '1.1.1', '2.3.5')",
                        },
                    },
                    "required": ["task_id"],
                },
            },
            {
                "name": "task_search",
                "description": "Search for tasks by keyword in title or description.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query",
                        },
                    },
                    "required": ["query"],
                },
            },
            {
                "name": "task_update_status",
                "description": "Update a task's status (not_started, in_progress, completed, blocked).",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "task_id": {
                            "type": "string",
                            "description": "The task ID to update",
                        },
                        "status": {
                            "type": "string",
                            "enum": ["not_started", "in_progress", "completed", "blocked", "deferred"],
                            "description": "New status",
                        },
                        "notes": {
                            "type": "string",
                            "description": "Optional notes about the status change",
                        },
                    },
                    "required": ["task_id", "status"],
                },
            },
            {
                "name": "task_assign",
                "description": "Assign a task to a team member or AI agent.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "task_id": {
                            "type": "string",
                            "description": "The task ID to assign",
                        },
                        "assignee": {
                            "type": "string",
                            "description": "Name of assignee (e.g., 'claude', 'chatgpt', 'developer')",
                        },
                    },
                    "required": ["task_id", "assignee"],
                },
            },
            {
                "name": "task_add_note",
                "description": "Add a note or comment to a task.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "task_id": {
                            "type": "string",
                            "description": "The task ID",
                        },
                        "note": {
                            "type": "string",
                            "description": "The note to add",
                        },
                    },
                    "required": ["task_id", "note"],
                },
            },

            # Priority Views
            {
                "name": "priority_tasks",
                "description": "Get all tasks of a specific priority level.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "priority": {
                            "type": "string",
                            "enum": ["P0", "P1", "P2", "P3", "P4"],
                            "description": "Priority level (P0=MVP critical, P4=future)",
                        },
                    },
                    "required": ["priority"],
                },
            },
            {
                "name": "next_tasks",
                "description": "Get the next tasks to work on (highest priority pending tasks).",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of tasks to return (default: 10)",
                        },
                    },
                },
            },

            # Metrics Tools
            {
                "name": "metrics_get",
                "description": "Get success metrics and targets for the project.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "category": {
                            "type": "string",
                            "enum": ["performance", "quality", "robustness"],
                            "description": "Metrics category",
                        },
                    },
                },
            },

            # Export Tools
            {
                "name": "roadmap_export",
                "description": "Export the roadmap in a specified format.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "format": {
                            "type": "string",
                            "enum": ["markdown", "json", "summary"],
                            "description": "Export format",
                        },
                    },
                },
            },

            # Management Tools
            {
                "name": "roadmap_reinitialize",
                "description": "Reinitialize the roadmap from source markdown files (resets all progress).",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "confirm": {
                            "type": "boolean",
                            "description": "Must be true to confirm reinitialization",
                        },
                    },
                    "required": ["confirm"],
                },
            },
        ]

    def handle_tool_call(
        self,
        tool_name: str,
        arguments: Dict[str, Any],
        ai_source: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Handle a tool call and return the result.

        Args:
            tool_name: Name of the tool to call
            arguments: Tool arguments
            ai_source: Which AI is making the call

        Returns:
            Tool result as a dictionary
        """
        try:
            # Overview Tools
            if tool_name == "roadmap_overview":
                roadmap = self.storage.get_roadmap()
                return {
                    "success": True,
                    "roadmap": {
                        "name": roadmap.name,
                        "description": roadmap.description,
                        "timeline": f"{roadmap.start_date} to {roadmap.end_date}",
                        "overall_progress": f"{roadmap.overall_progress * 100:.1f}%",
                        "phases_completed": f"{roadmap.phases_completed}/{len(roadmap.phases)}",
                        "current_phase": roadmap.get_current_phase().name if roadmap.get_current_phase() else "All complete",
                        "quarters": [q.to_dict() for q in roadmap.quarters],
                    },
                }

            elif tool_name == "roadmap_summary":
                return {
                    "success": True,
                    "summary": self.storage.get_summary(),
                }

            elif tool_name == "roadmap_progress":
                return {
                    "success": True,
                    "progress_view": self.storage.get_progress_view(),
                }

            # Phase Tools
            elif tool_name == "phase_list":
                phases = self.storage.roadmap.phases
                if "status" in arguments:
                    status = TaskStatus(arguments["status"])
                    phases = [p for p in phases if p.status == status]

                return {
                    "success": True,
                    "count": len(phases),
                    "phases": [
                        {
                            "id": p.id,
                            "name": p.name,
                            "status": p.status.value,
                            "progress": f"{p.progress * 100:.1f}%",
                            "tasks": f"{p.completed_tasks}/{p.total_tasks}",
                            "type": p.phase_type.value,
                        }
                        for p in phases
                    ],
                }

            elif tool_name == "phase_get":
                phase = self.storage.get_phase(arguments["phase_id"])
                if phase:
                    return {
                        "success": True,
                        "phase": phase.to_dict(),
                    }
                return {
                    "success": False,
                    "error": f"Phase not found: {arguments['phase_id']}",
                }

            elif tool_name == "phase_current":
                phase = self.storage.get_current_phase()
                if phase:
                    return {
                        "success": True,
                        "current_phase": phase.to_dict(),
                    }
                return {
                    "success": True,
                    "message": "All phases are complete!",
                    "current_phase": None,
                }

            # Quarter Tools
            elif tool_name == "quarter_list":
                return {
                    "success": True,
                    "quarters": [q.to_dict() for q in self.storage.roadmap.quarters],
                }

            elif tool_name == "quarter_get":
                quarter = self.storage.get_quarter(arguments["quarter_id"])
                if quarter:
                    return {
                        "success": True,
                        "quarter": quarter.to_dict(),
                    }
                return {
                    "success": False,
                    "error": f"Quarter not found: {arguments['quarter_id']}",
                }

            # Milestone Tools
            elif tool_name == "milestone_get":
                phase = self.storage.get_phase(arguments["phase_id"])
                if not phase:
                    return {"success": False, "error": f"Phase not found: {arguments['phase_id']}"}

                for milestone in phase.milestones:
                    if milestone.id == arguments["milestone_id"]:
                        return {
                            "success": True,
                            "milestone": milestone.to_dict(),
                        }
                return {
                    "success": False,
                    "error": f"Milestone not found: {arguments['milestone_id']}",
                }

            # Task Tools
            elif tool_name == "task_list":
                tasks = []
                for phase in self.storage.roadmap.phases:
                    if "phase_id" in arguments and phase.id != arguments["phase_id"]:
                        continue
                    for milestone in phase.milestones:
                        for task in milestone.tasks:
                            # Apply filters
                            if "status" in arguments and task.status.value != arguments["status"]:
                                continue
                            if "priority" in arguments:
                                if not task.priority or task.priority.value != arguments["priority"]:
                                    continue

                            tasks.append({
                                "id": task.id,
                                "title": task.title,
                                "status": task.status.value,
                                "priority": task.priority.value if task.priority else None,
                                "phase": phase.name,
                                "milestone": milestone.title,
                                "assigned_to": task.assigned_to,
                            })

                # Apply limit
                limit = arguments.get("limit", 100)
                tasks = tasks[:limit]

                return {
                    "success": True,
                    "count": len(tasks),
                    "tasks": tasks,
                }

            elif tool_name == "task_get":
                task_id = arguments["task_id"]
                for phase in self.storage.roadmap.phases:
                    for milestone in phase.milestones:
                        for task in milestone.tasks:
                            if task.id == task_id:
                                return {
                                    "success": True,
                                    "task": task.to_dict(),
                                    "phase": phase.name,
                                    "milestone": milestone.title,
                                }
                return {
                    "success": False,
                    "error": f"Task not found: {task_id}",
                }

            elif tool_name == "task_search":
                results = self.storage.search_tasks(arguments["query"])
                return {
                    "success": True,
                    "count": len(results),
                    "tasks": [
                        {
                            "id": task.id,
                            "title": task.title,
                            "status": task.status.value,
                            "phase": phase.name,
                            "milestone": milestone.title,
                        }
                        for phase, milestone, task in results
                    ],
                }

            elif tool_name == "task_update_status":
                task = self.storage.update_task_status(
                    arguments["task_id"],
                    TaskStatus(arguments["status"]),
                    arguments.get("notes"),
                )
                if task:
                    return {
                        "success": True,
                        "message": f"Updated task {task.id} to {task.status.value}",
                        "task": task.to_dict(),
                    }
                return {
                    "success": False,
                    "error": f"Task not found: {arguments['task_id']}",
                }

            elif tool_name == "task_assign":
                task = self.storage.assign_task(
                    arguments["task_id"],
                    arguments["assignee"],
                )
                if task:
                    return {
                        "success": True,
                        "message": f"Assigned task {task.id} to {task.assigned_to}",
                        "task": task.to_dict(),
                    }
                return {
                    "success": False,
                    "error": f"Task not found: {arguments['task_id']}",
                }

            elif tool_name == "task_add_note":
                task = self.storage.add_task_note(
                    arguments["task_id"],
                    arguments["note"],
                )
                if task:
                    return {
                        "success": True,
                        "message": "Note added",
                        "task": task.to_dict(),
                    }
                return {
                    "success": False,
                    "error": f"Task not found: {arguments['task_id']}",
                }

            # Priority Views
            elif tool_name == "priority_tasks":
                priority = Priority(arguments["priority"])
                results = self.storage.get_tasks_by_priority(priority)
                return {
                    "success": True,
                    "priority": priority.value,
                    "count": len(results),
                    "tasks": [
                        {
                            "id": task.id,
                            "title": task.title,
                            "status": task.status.value,
                            "phase": phase.name,
                            "milestone": milestone.title,
                        }
                        for phase, milestone, task in results
                    ],
                }

            elif tool_name == "next_tasks":
                limit = arguments.get("limit", 10)
                # Get pending tasks sorted by priority
                all_pending = self.storage.get_pending_tasks()

                # Sort by priority (P0 first)
                def priority_key(item):
                    _, _, task = item
                    if not task.priority:
                        return 99
                    return ["P0", "P1", "P2", "P3", "P4"].index(task.priority.value)

                all_pending.sort(key=priority_key)
                tasks = all_pending[:limit]

                return {
                    "success": True,
                    "count": len(tasks),
                    "tasks": [
                        {
                            "id": task.id,
                            "title": task.title,
                            "priority": task.priority.value if task.priority else None,
                            "phase": phase.name,
                            "milestone": milestone.title,
                        }
                        for phase, milestone, task in tasks
                    ],
                }

            # Metrics Tools
            elif tool_name == "metrics_get":
                metrics = self.storage.roadmap.success_metrics
                if "category" in arguments:
                    category = arguments["category"]
                    if category in metrics:
                        return {
                            "success": True,
                            "category": category,
                            "metrics": metrics[category],
                        }
                    return {
                        "success": False,
                        "error": f"Unknown category: {category}",
                    }
                return {
                    "success": True,
                    "metrics": metrics,
                }

            # Export Tools
            elif tool_name == "roadmap_export":
                format_type = arguments.get("format", "summary")

                if format_type == "json":
                    return {
                        "success": True,
                        "format": "json",
                        "content": self.storage.roadmap.to_dict(),
                    }
                elif format_type == "markdown":
                    return {
                        "success": True,
                        "format": "markdown",
                        "content": self._export_markdown(),
                    }
                else:  # summary
                    return {
                        "success": True,
                        "format": "summary",
                        "content": self.storage.get_progress_view(),
                    }

            # Management Tools
            elif tool_name == "roadmap_reinitialize":
                if not arguments.get("confirm"):
                    return {
                        "success": False,
                        "error": "Must set confirm=true to reinitialize",
                    }
                self.storage.reinitialize()
                return {
                    "success": True,
                    "message": "Roadmap reinitialized from source files",
                }

            else:
                return {
                    "success": False,
                    "error": f"Unknown tool: {tool_name}",
                }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }

    def _export_markdown(self) -> str:
        """Export roadmap as markdown."""
        lines = []
        roadmap = self.storage.roadmap

        lines.append(f"# {roadmap.name}")
        lines.append("")
        lines.append(f"**Timeline:** {roadmap.start_date} to {roadmap.end_date}")
        lines.append(f"**Overall Progress:** {roadmap.overall_progress * 100:.1f}%")
        lines.append("")

        for phase in roadmap.phases:
            status_icon = {
                TaskStatus.COMPLETED: "[x]",
                TaskStatus.IN_PROGRESS: "[>]",
                TaskStatus.BLOCKED: "[!]",
                TaskStatus.NOT_STARTED: "[ ]",
            }.get(phase.status, "[ ]")

            lines.append(f"## Phase {phase.id}: {phase.name} {status_icon}")
            lines.append(f"*{phase.description}*")
            lines.append(f"Progress: {phase.progress * 100:.1f}%")
            lines.append("")

            for milestone in phase.milestones:
                lines.append(f"### {milestone.id} {milestone.title}")
                for task in milestone.tasks:
                    task_icon = "[x]" if task.status == TaskStatus.COMPLETED else "[ ]"
                    priority_tag = f" ({task.priority.value})" if task.priority else ""
                    lines.append(f"- {task_icon} {task.title}{priority_tag}")
                lines.append("")

        return "\n".join(lines)

    async def handle_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Handle an MCP protocol message."""
        method = message.get("method", "")
        msg_id = message.get("id")
        params = message.get("params", {})

        if method == "initialize":
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "serverInfo": self.server_info,
                    "capabilities": {
                        "tools": {"listChanged": False},
                    },
                },
            }

        elif method == "tools/list":
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "tools": self.get_tools(),
                },
            }

        elif method == "tools/call":
            tool_name = params.get("name", "")
            arguments = params.get("arguments", {})
            ai_source = params.get("_meta", {}).get("ai_source")

            result = self.handle_tool_call(tool_name, arguments, ai_source)

            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps(result, indent=2),
                        }
                    ],
                },
            }

        elif method == "notifications/initialized":
            return None

        else:
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "error": {
                    "code": -32601,
                    "message": f"Method not found: {method}",
                },
            }

    async def run_stdio(self):
        """Run the server using stdio transport."""
        print(f"MCP Roadmap Server v{self.server_info['version']} starting...", file=sys.stderr)

        while True:
            try:
                line = await asyncio.get_event_loop().run_in_executor(
                    None, sys.stdin.readline
                )
                if not line:
                    break

                line = line.strip()
                if not line:
                    continue

                message = json.loads(line)
                response = await self.handle_message(message)

                if response:
                    print(json.dumps(response), flush=True)

            except json.JSONDecodeError as e:
                error_response = {
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {
                        "code": -32700,
                        "message": f"Parse error: {str(e)}",
                    },
                }
                print(json.dumps(error_response), flush=True)
            except Exception as e:
                print(f"Error: {e}", file=sys.stderr)


def main():
    """Entry point for the MCP server."""
    import argparse

    parser = argparse.ArgumentParser(description="MCP Roadmap Server")
    parser.add_argument(
        "--storage-dir",
        help="Directory for roadmap storage",
        default=None,
    )
    parser.add_argument(
        "--project-root",
        help="Path to iDAWi project root",
        default=None,
    )
    args = parser.parse_args()

    server = MCPRoadmapServer(
        storage_dir=args.storage_dir,
        project_root=args.project_root,
    )
    asyncio.run(server.run_stdio())


if __name__ == "__main__":
    main()
