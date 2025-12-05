#!/usr/bin/env python3
"""
MCP Roadmap CLI

Command-line interface for managing the iDAWi project roadmap.

Usage:
    python -m mcp_roadmap.cli <command> [options]
    mcp-roadmap <command> [options]
"""

import argparse
import json
import sys
from typing import Optional

from .storage import RoadmapStorage
from .models import TaskStatus, Priority


def get_storage() -> RoadmapStorage:
    """Get the roadmap storage instance."""
    return RoadmapStorage()


def cmd_overview(args):
    """Show roadmap overview."""
    storage = get_storage()
    roadmap = storage.get_roadmap()

    print("=" * 60)
    print(f"  {roadmap.name}")
    print("=" * 60)
    print()
    print(f"Timeline: {roadmap.start_date} to {roadmap.end_date}")
    print(f"Progress: {roadmap.overall_progress * 100:.1f}%")
    print(f"Phases:   {roadmap.phases_completed}/{len(roadmap.phases)} complete")
    print()

    current = roadmap.get_current_phase()
    if current:
        print(f"Current Phase: {current.id} - {current.name}")
        print(f"  Progress: {current.progress * 100:.1f}%")
        print(f"  Tasks: {current.completed_tasks}/{current.total_tasks}")
    else:
        print("All phases complete!")

    print()


def cmd_summary(args):
    """Show roadmap summary."""
    storage = get_storage()
    summary = storage.get_summary()

    print("=" * 60)
    print("  iDAWi Roadmap Summary")
    print("=" * 60)
    print()
    print(f"Overall Progress:  {summary['overall_progress']}")
    print(f"Total Tasks:       {summary['total_tasks']}")
    print(f"Completed:         {summary['completed_tasks']}")
    print(f"In Progress:       {summary['in_progress_tasks']}")
    print(f"Blocked:           {summary['blocked_tasks']}")
    print(f"Pending:           {summary['pending_tasks']}")
    print()
    print(f"Phases Complete:   {summary['phases_completed']}/{summary['total_phases']}")
    print()
    print("Phase Breakdown:")
    print("-" * 60)

    for phase in summary["phases"]:
        status_icon = {
            "completed": "[x]",
            "in_progress": "[>]",
            "blocked": "[!]",
            "not_started": "[ ]",
        }.get(phase["status"], "[ ]")

        print(f"  {status_icon} Phase {phase['id']}: {phase['name']}")
        print(f"      {phase['progress']} ({phase['tasks']} tasks)")

    print()
    print(f"Last Updated: {summary['last_updated']}")


def cmd_progress(args):
    """Show progress view."""
    storage = get_storage()
    print(storage.get_progress_view())


def cmd_phases(args):
    """List all phases."""
    storage = get_storage()

    phases = storage.roadmap.phases
    if args.status:
        status = TaskStatus(args.status)
        phases = [p for p in phases if p.status == status]

    print("=" * 70)
    print("  Development Phases")
    print("=" * 70)
    print()
    print(f"{'ID':<4} {'Name':<35} {'Status':<12} {'Progress':<10} {'Tasks'}")
    print("-" * 70)

    for phase in phases:
        status_str = phase.status.value.replace("_", " ").title()
        progress_str = f"{phase.progress * 100:.0f}%"
        tasks_str = f"{phase.completed_tasks}/{phase.total_tasks}"

        print(f"{phase.id:<4} {phase.name[:35]:<35} {status_str:<12} {progress_str:<10} {tasks_str}")

    print()


def cmd_phase(args):
    """Show phase details."""
    storage = get_storage()
    phase = storage.get_phase(args.phase_id)

    if not phase:
        print(f"Error: Phase {args.phase_id} not found")
        sys.exit(1)

    print("=" * 70)
    print(f"  Phase {phase.id}: {phase.name}")
    print("=" * 70)
    print()
    print(f"Type:        {phase.phase_type.value}")
    print(f"Status:      {phase.status.value}")
    print(f"Progress:    {phase.progress * 100:.1f}%")
    print(f"Tasks:       {phase.completed_tasks}/{phase.total_tasks}")

    if phase.dependencies:
        print(f"Depends on:  Phases {', '.join(map(str, phase.dependencies))}")

    print()
    print("Milestones:")
    print("-" * 70)

    for milestone in phase.milestones:
        status_icon = {
            TaskStatus.COMPLETED: "[x]",
            TaskStatus.IN_PROGRESS: "[>]",
            TaskStatus.BLOCKED: "[!]",
            TaskStatus.NOT_STARTED: "[ ]",
        }.get(milestone.status, "[ ]")

        print(f"\n  {status_icon} {milestone.id} {milestone.title}")
        print(f"      Progress: {milestone.progress * 100:.0f}%")

        if args.verbose:
            for task in milestone.tasks:
                task_icon = "[x]" if task.status == TaskStatus.COMPLETED else "[ ]"
                priority_tag = f" ({task.priority.value})" if task.priority else ""
                print(f"        - {task_icon} {task.title}{priority_tag}")

    print()


def cmd_quarters(args):
    """List quarters from 18-month roadmap."""
    storage = get_storage()

    print("=" * 70)
    print("  18-Month Roadmap Quarters")
    print("=" * 70)
    print()

    for quarter in storage.roadmap.quarters:
        status_icon = {
            TaskStatus.COMPLETED: "[x]",
            TaskStatus.IN_PROGRESS: "[>]",
            TaskStatus.NOT_STARTED: "[ ]",
        }.get(quarter.status, "[ ]")

        print(f"{status_icon} {quarter.name}")
        print(f"   Focus: {quarter.focus}")
        print(f"   Period: {quarter.start_date} to {quarter.end_date}")
        print(f"   Deliverables:")
        for deliverable in quarter.key_deliverables:
            print(f"     - {deliverable}")
        print()


def cmd_tasks(args):
    """List tasks with filters."""
    storage = get_storage()

    tasks = []
    for phase in storage.roadmap.phases:
        if args.phase is not None and phase.id != args.phase:
            continue
        for milestone in phase.milestones:
            for task in milestone.tasks:
                if args.status and task.status.value != args.status:
                    continue
                if args.priority and (not task.priority or task.priority.value != args.priority):
                    continue

                tasks.append({
                    "task": task,
                    "phase": phase,
                    "milestone": milestone,
                })

    # Apply limit
    if args.limit:
        tasks = tasks[:args.limit]

    if not tasks:
        print("No tasks found matching criteria.")
        return

    print("=" * 80)
    print("  Tasks")
    print("=" * 80)
    print()
    print(f"{'ID':<10} {'Title':<40} {'Status':<12} {'Priority'}")
    print("-" * 80)

    for item in tasks:
        task = item["task"]
        status_str = task.status.value.replace("_", " ")[:12]
        priority_str = task.priority.value if task.priority else "-"
        print(f"{task.id:<10} {task.title[:40]:<40} {status_str:<12} {priority_str}")

    print()
    print(f"Total: {len(tasks)} tasks")


def cmd_task(args):
    """Show task details."""
    storage = get_storage()

    for phase in storage.roadmap.phases:
        for milestone in phase.milestones:
            for task in milestone.tasks:
                if task.id == args.task_id:
                    print("=" * 60)
                    print(f"  Task: {task.id}")
                    print("=" * 60)
                    print()
                    print(f"Title:       {task.title}")
                    print(f"Status:      {task.status.value}")
                    print(f"Priority:    {task.priority.value if task.priority else 'Not set'}")
                    print(f"Phase:       {phase.name}")
                    print(f"Milestone:   {milestone.title}")
                    print(f"Assigned to: {task.assigned_to or 'Unassigned'}")

                    if task.description:
                        print(f"\nDescription:\n  {task.description}")

                    if task.notes:
                        print("\nNotes:")
                        for note in task.notes:
                            print(f"  - {note}")

                    if task.completed_date:
                        print(f"\nCompleted:   {task.completed_date}")

                    print()
                    return

    print(f"Error: Task {args.task_id} not found")
    sys.exit(1)


def cmd_search(args):
    """Search for tasks."""
    storage = get_storage()
    results = storage.search_tasks(args.query)

    if not results:
        print(f"No tasks found matching '{args.query}'")
        return

    print(f"Found {len(results)} tasks matching '{args.query}':")
    print()

    for phase, milestone, task in results:
        status_icon = "[x]" if task.status == TaskStatus.COMPLETED else "[ ]"
        print(f"  {status_icon} {task.id}: {task.title}")
        print(f"      Phase: {phase.name} | Milestone: {milestone.title}")


def cmd_update(args):
    """Update a task's status."""
    storage = get_storage()
    task = storage.update_task_status(
        args.task_id,
        TaskStatus(args.status),
        args.notes,
    )

    if task:
        print(f"Updated task {task.id} to {task.status.value}")
    else:
        print(f"Error: Task {args.task_id} not found")
        sys.exit(1)


def cmd_assign(args):
    """Assign a task."""
    storage = get_storage()
    task = storage.assign_task(args.task_id, args.assignee)

    if task:
        print(f"Assigned task {task.id} to {task.assigned_to}")
    else:
        print(f"Error: Task {args.task_id} not found")
        sys.exit(1)


def cmd_next(args):
    """Show next tasks to work on."""
    storage = get_storage()
    pending = storage.get_pending_tasks()

    # Sort by priority
    def priority_key(item):
        _, _, task = item
        if not task.priority:
            return 99
        return ["P0", "P1", "P2", "P3", "P4"].index(task.priority.value)

    pending.sort(key=priority_key)
    tasks = pending[:args.limit]

    if not tasks:
        print("No pending tasks!")
        return

    print("=" * 70)
    print("  Next Tasks to Work On")
    print("=" * 70)
    print()

    for phase, milestone, task in tasks:
        priority_str = f"[{task.priority.value}]" if task.priority else "[--]"
        print(f"  {priority_str} {task.id}: {task.title}")
        print(f"          Phase: {phase.name}")
        print()


def cmd_metrics(args):
    """Show success metrics."""
    storage = get_storage()
    metrics = storage.roadmap.success_metrics

    print("=" * 60)
    print("  Success Metrics")
    print("=" * 60)
    print()

    for category, items in metrics.items():
        print(f"[{category.upper()}]")
        for metric, target in items.items():
            print(f"  {metric}: {target}")
        print()


def cmd_export(args):
    """Export roadmap."""
    storage = get_storage()

    if args.format == "json":
        print(json.dumps(storage.roadmap.to_dict(), indent=2))
    elif args.format == "summary":
        print(storage.get_progress_view())
    else:
        print("Markdown export not yet implemented")


def cmd_reinit(args):
    """Reinitialize roadmap."""
    if not args.confirm:
        print("Warning: This will reset all progress!")
        print("Use --confirm to proceed.")
        sys.exit(1)

    storage = get_storage()
    storage.reinitialize()
    print("Roadmap reinitialized from source files.")


def cmd_server(args):
    """Run MCP server."""
    from .server import main
    main()


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="iDAWi Roadmap Management CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Commands:
  overview    Show roadmap overview
  summary     Show detailed summary
  progress    Show progress view
  phases      List all phases
  phase       Show phase details
  quarters    Show 18-month quarters
  tasks       List tasks with filters
  task        Show task details
  search      Search tasks
  update      Update task status
  assign      Assign task
  next        Show next tasks to work on
  metrics     Show success metrics
  export      Export roadmap
  reinit      Reinitialize from source
  server      Run MCP server

Examples:
  mcp-roadmap overview
  mcp-roadmap phases --status in_progress
  mcp-roadmap tasks --priority P0
  mcp-roadmap task 1.1.1
  mcp-roadmap update 1.1.1 --status completed
  mcp-roadmap next --limit 5
""",
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # overview
    subparsers.add_parser("overview", help="Show roadmap overview")

    # summary
    subparsers.add_parser("summary", help="Show detailed summary")

    # progress
    subparsers.add_parser("progress", help="Show progress view")

    # phases
    phases_parser = subparsers.add_parser("phases", help="List all phases")
    phases_parser.add_argument("--status", choices=["not_started", "in_progress", "completed", "blocked"])

    # phase
    phase_parser = subparsers.add_parser("phase", help="Show phase details")
    phase_parser.add_argument("phase_id", type=int, help="Phase ID (0-14)")
    phase_parser.add_argument("-v", "--verbose", action="store_true", help="Show all tasks")

    # quarters
    subparsers.add_parser("quarters", help="Show 18-month quarters")

    # tasks
    tasks_parser = subparsers.add_parser("tasks", help="List tasks")
    tasks_parser.add_argument("--phase", type=int, help="Filter by phase ID")
    tasks_parser.add_argument("--status", choices=["not_started", "in_progress", "completed", "blocked", "deferred"])
    tasks_parser.add_argument("--priority", choices=["P0", "P1", "P2", "P3", "P4"])
    tasks_parser.add_argument("--limit", type=int, default=50, help="Max tasks to show")

    # task
    task_parser = subparsers.add_parser("task", help="Show task details")
    task_parser.add_argument("task_id", help="Task ID (e.g., 1.1.1)")

    # search
    search_parser = subparsers.add_parser("search", help="Search tasks")
    search_parser.add_argument("query", help="Search query")

    # update
    update_parser = subparsers.add_parser("update", help="Update task status")
    update_parser.add_argument("task_id", help="Task ID")
    update_parser.add_argument("--status", required=True,
                               choices=["not_started", "in_progress", "completed", "blocked", "deferred"])
    update_parser.add_argument("--notes", help="Notes about the change")

    # assign
    assign_parser = subparsers.add_parser("assign", help="Assign task")
    assign_parser.add_argument("task_id", help="Task ID")
    assign_parser.add_argument("assignee", help="Assignee name")

    # next
    next_parser = subparsers.add_parser("next", help="Show next tasks")
    next_parser.add_argument("--limit", type=int, default=10, help="Max tasks to show")

    # metrics
    subparsers.add_parser("metrics", help="Show success metrics")

    # export
    export_parser = subparsers.add_parser("export", help="Export roadmap")
    export_parser.add_argument("--format", choices=["json", "markdown", "summary"], default="summary")

    # reinit
    reinit_parser = subparsers.add_parser("reinit", help="Reinitialize roadmap")
    reinit_parser.add_argument("--confirm", action="store_true", help="Confirm reinitialization")

    # server
    subparsers.add_parser("server", help="Run MCP server")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Route to command handler
    commands = {
        "overview": cmd_overview,
        "summary": cmd_summary,
        "progress": cmd_progress,
        "phases": cmd_phases,
        "phase": cmd_phase,
        "quarters": cmd_quarters,
        "tasks": cmd_tasks,
        "task": cmd_task,
        "search": cmd_search,
        "update": cmd_update,
        "assign": cmd_assign,
        "next": cmd_next,
        "metrics": cmd_metrics,
        "export": cmd_export,
        "reinit": cmd_reinit,
        "server": cmd_server,
    }

    handler = commands.get(args.command)
    if handler:
        handler(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
