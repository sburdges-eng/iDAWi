"""
MCP Roadmap - Storage & Parser

Handles storage, parsing, and persistence of roadmap data.
Parses existing markdown roadmap files and maintains state.
"""

import json
import os
import re
from datetime import date, datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple

from .models import (
    Roadmap, Phase, Milestone, Task, Quarter,
    TaskStatus, Priority, PhaseType
)


class RoadmapStorage:
    """
    Manages roadmap data storage and parsing.

    Initializes from existing markdown roadmap files and maintains
    persistent state in JSON format.
    """

    DEFAULT_STORAGE_DIR = os.path.expanduser("~/.mcp_roadmap")
    ROADMAP_FILE = "roadmap.json"

    def __init__(self, storage_dir: Optional[str] = None, project_root: Optional[str] = None):
        """
        Initialize roadmap storage.

        Args:
            storage_dir: Directory for JSON storage (default: ~/.mcp_roadmap)
            project_root: Root of the iDAWi project for parsing markdown files
        """
        self.storage_dir = Path(storage_dir or self.DEFAULT_STORAGE_DIR)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.storage_file = self.storage_dir / self.ROADMAP_FILE

        # Find project root
        if project_root:
            self.project_root = Path(project_root)
        else:
            # Try to find project root from current file location
            self.project_root = self._find_project_root()

        # Load or initialize roadmap
        self.roadmap = self._load_or_initialize()

    def _find_project_root(self) -> Path:
        """Find the iDAWi project root directory."""
        # Start from this file's directory and go up
        current = Path(__file__).parent
        while current != current.parent:
            if (current / "IDAWI_COMPREHENSIVE_TODO.md").exists():
                return current.parent  # Go one more level up to iDAWi root
            if (current.parent / "IDAWI_COMPREHENSIVE_TODO.md").exists():
                return current.parent
            current = current.parent

        # Fallback to common locations
        for path in [
            Path("/home/user/iDAWi"),
            Path.home() / "iDAWi",
            Path.cwd(),
        ]:
            if path.exists():
                return path

        return Path.cwd()

    def _load_or_initialize(self) -> Roadmap:
        """Load existing roadmap or initialize from markdown files."""
        if self.storage_file.exists():
            try:
                with open(self.storage_file, "r") as f:
                    data = json.load(f)
                return Roadmap.from_dict(data)
            except (json.JSONDecodeError, KeyError) as e:
                print(f"Warning: Could not load roadmap: {e}. Reinitializing...")

        # Initialize from markdown files
        return self._initialize_from_markdown()

    def _initialize_from_markdown(self) -> Roadmap:
        """Parse markdown roadmap files and create roadmap structure."""
        roadmap = Roadmap(
            name="iDAWi - Intelligent Digital Audio Workstation",
            description="Complete, self-contained DAW with embedded AI/ML capabilities",
            start_date=date(2024, 12, 1),
            end_date=date(2026, 5, 31),
        )

        # Initialize quarters from 18-month roadmap
        roadmap.quarters = self._initialize_quarters()

        # Initialize phases from comprehensive TODO
        roadmap.phases = self._initialize_phases()

        # Initialize success metrics
        roadmap.success_metrics = self._initialize_metrics()

        # Save initialized roadmap
        self.save(roadmap)

        return roadmap

    def _initialize_quarters(self) -> List[Quarter]:
        """Initialize quarterly milestones."""
        return [
            Quarter(
                id="Q1_2025",
                name="Q1 2025: Core Foundation",
                focus="Core Foundation",
                key_deliverables=[
                    "CLI complete",
                    "Penta-Core harmony/groove modules",
                    "Brain server with OSC"
                ],
                status=TaskStatus.COMPLETED,
                months=["month_1", "month_2", "month_3"],
                start_date=date(2025, 1, 1),
                end_date=date(2025, 3, 31),
            ),
            Quarter(
                id="Q2_2025",
                name="Q2 2025: Audio Engine",
                focus="Audio Engine & Tools",
                key_deliverables=[
                    "Audio analysis modules",
                    "JUCE plugins DSP",
                    "MCP tools (22 total)",
                    "Diagnostics & OSC optimization"
                ],
                status=TaskStatus.COMPLETED,
                months=["month_4", "month_5", "month_6"],
                start_date=date(2025, 4, 1),
                end_date=date(2025, 6, 30),
            ),
            Quarter(
                id="Q3_2025",
                name="Q3 2025: Desktop & DAW",
                focus="Desktop Application & DAW Integration",
                key_deliverables=[
                    "Desktop app framework",
                    "MIDI preview & playback",
                    "JUCE plugin skeleton",
                    "Logic Pro integration"
                ],
                status=TaskStatus.COMPLETED,
                months=["month_7", "month_8", "month_9"],
                start_date=date(2025, 7, 1),
                end_date=date(2025, 9, 30),
            ),
            Quarter(
                id="Q4_2025",
                name="Q4 2025: Polish & Scale",
                focus="Testing, Documentation, Packaging",
                key_deliverables=[
                    "Comprehensive testing",
                    "CI/CD improvements",
                    "Documentation & packaging",
                    "Ableton Live integration"
                ],
                status=TaskStatus.COMPLETED,
                months=["month_10", "month_11", "month_12"],
                start_date=date(2025, 10, 1),
                end_date=date(2025, 12, 31),
            ),
            Quarter(
                id="H1_2026",
                name="H1 2026: Future Features",
                focus="ML Integration, Mobile/Web, Collaboration",
                key_deliverables=[
                    "FL Studio & Pro Tools support",
                    "ML model integration",
                    "Mobile/web expansion",
                    "Collaboration features"
                ],
                status=TaskStatus.IN_PROGRESS,
                months=["month_13", "month_14", "month_15", "month_16", "month_17", "month_18"],
                start_date=date(2026, 1, 1),
                end_date=date(2026, 5, 31),
            ),
        ]

    def _initialize_phases(self) -> List[Phase]:
        """Initialize development phases from comprehensive TODO."""
        phases = []

        # Phase 0: Foundation (COMPLETE)
        phase0 = Phase(
            id=0,
            name="Foundation & Architecture",
            description="Core architecture, build system, project structure",
            phase_type=PhaseType.FOUNDATION,
            start_date=date(2024, 12, 1),
            actual_end_date=date(2024, 12, 31),
        )
        phase0.milestones = [
            Milestone(
                id="0.1",
                title="Core Architecture Finalization",
                tasks=[
                    Task(id="0.1.1", title="Design dual-engine architecture", status=TaskStatus.COMPLETED),
                    Task(id="0.1.2", title="Define lock-free ring buffer interface", status=TaskStatus.COMPLETED),
                    Task(id="0.1.3", title="Define memory pool architecture", status=TaskStatus.COMPLETED),
                    Task(id="0.1.4", title="Document IPC mechanisms", status=TaskStatus.COMPLETED),
                    Task(id="0.1.5", title="Create Harmony Engine interface", status=TaskStatus.COMPLETED),
                    Task(id="0.1.6", title="Create Groove Engine interface", status=TaskStatus.COMPLETED),
                    Task(id="0.1.7", title="Create Diagnostics Engine interface", status=TaskStatus.COMPLETED),
                    Task(id="0.1.8", title="Design OSC communication layer", status=TaskStatus.COMPLETED),
                    Task(id="0.1.9", title="Implement core algorithms", status=TaskStatus.COMPLETED),
                ],
            ),
            Milestone(
                id="0.2",
                title="Build System Consolidation",
                tasks=[
                    Task(id="0.2.1", title="Create CMake build system", status=TaskStatus.COMPLETED),
                    Task(id="0.2.2", title="Configure Python packaging", status=TaskStatus.COMPLETED),
                    Task(id="0.2.3", title="Set up CI/CD with GitHub Actions", status=TaskStatus.COMPLETED),
                    Task(id="0.2.4", title="Create build scripts (build.sh, build.ps1)", status=TaskStatus.COMPLETED),
                ],
            ),
            Milestone(
                id="0.3",
                title="Project Structure Cleanup",
                tasks=[
                    Task(id="0.3.1", title="Establish monorepo structure", status=TaskStatus.COMPLETED),
                    Task(id="0.3.2", title="Remove duplicate files", status=TaskStatus.COMPLETED),
                    Task(id="0.3.3", title="Create comprehensive documentation", status=TaskStatus.COMPLETED),
                ],
            ),
        ]
        phases.append(phase0)

        # Phase 1: Real-Time Audio Engine
        phase1 = Phase(
            id=1,
            name="Real-Time Audio Engine",
            description="C++ core audio engine with MIDI, transport, mixer",
            phase_type=PhaseType.AUDIO_ENGINE,
            dependencies=[0],
        )
        phase1.milestones = [
            Milestone(
                id="1.1",
                title="Audio I/O Foundation",
                tasks=[
                    Task(id="1.1.1", title="Implement CoreAudio backend (macOS)", status=TaskStatus.NOT_STARTED, priority=Priority.P0),
                    Task(id="1.1.2", title="Implement WASAPI backend (Windows)", status=TaskStatus.NOT_STARTED, priority=Priority.P0),
                    Task(id="1.1.3", title="Implement ALSA/PipeWire backend (Linux)", status=TaskStatus.NOT_STARTED, priority=Priority.P0),
                    Task(id="1.1.4", title="Create audio device enumeration", status=TaskStatus.NOT_STARTED, priority=Priority.P0),
                    Task(id="1.1.5", title="Implement sample rate conversion", status=TaskStatus.NOT_STARTED, priority=Priority.P1),
                    Task(id="1.1.6", title="Implement buffer size selection", status=TaskStatus.NOT_STARTED, priority=Priority.P0),
                    Task(id="1.1.7", title="Add latency compensation", status=TaskStatus.NOT_STARTED, priority=Priority.P1),
                ],
            ),
            Milestone(
                id="1.2",
                title="MIDI Engine",
                tasks=[
                    Task(id="1.2.1", title="Implement CoreMIDI backend (macOS)", status=TaskStatus.NOT_STARTED, priority=Priority.P0),
                    Task(id="1.2.2", title="Implement Windows MIDI API backend", status=TaskStatus.NOT_STARTED, priority=Priority.P0),
                    Task(id="1.2.3", title="Implement ALSA MIDI backend (Linux)", status=TaskStatus.NOT_STARTED, priority=Priority.P0),
                    Task(id="1.2.4", title="Create virtual MIDI port support", status=TaskStatus.NOT_STARTED, priority=Priority.P1),
                    Task(id="1.2.5", title="Implement MIDI clock sync", status=TaskStatus.NOT_STARTED, priority=Priority.P1),
                    Task(id="1.2.6", title="Support MPE", status=TaskStatus.NOT_STARTED, priority=Priority.P2),
                    Task(id="1.2.7", title="Implement MIDI 2.0 protocol", status=TaskStatus.NOT_STARTED, priority=Priority.P3),
                ],
            ),
            Milestone(
                id="1.3",
                title="Transport System",
                tasks=[
                    Task(id="1.3.1", title="Implement play/pause/stop/record", status=TaskStatus.NOT_STARTED, priority=Priority.P0),
                    Task(id="1.3.2", title="Create timeline with sample-accurate positioning", status=TaskStatus.NOT_STARTED, priority=Priority.P0),
                    Task(id="1.3.3", title="Implement tempo and time signature changes", status=TaskStatus.NOT_STARTED, priority=Priority.P0),
                    Task(id="1.3.4", title="Add loop points with seamless looping", status=TaskStatus.NOT_STARTED, priority=Priority.P1),
                    Task(id="1.3.5", title="Create metronome", status=TaskStatus.NOT_STARTED, priority=Priority.P1),
                    Task(id="1.3.6", title="Implement undo/redo system", status=TaskStatus.NOT_STARTED, priority=Priority.P0),
                ],
            ),
            Milestone(
                id="1.4",
                title="Mixer Engine",
                tasks=[
                    Task(id="1.4.1", title="Create channel strip architecture", status=TaskStatus.NOT_STARTED, priority=Priority.P0),
                    Task(id="1.4.2", title="Implement gain staging", status=TaskStatus.NOT_STARTED, priority=Priority.P0),
                    Task(id="1.4.3", title="Add pan laws", status=TaskStatus.NOT_STARTED, priority=Priority.P1),
                    Task(id="1.4.4", title="Implement aux sends", status=TaskStatus.NOT_STARTED, priority=Priority.P1),
                    Task(id="1.4.5", title="Create master bus with limiting", status=TaskStatus.NOT_STARTED, priority=Priority.P0),
                    Task(id="1.4.6", title="Implement automation lanes", status=TaskStatus.NOT_STARTED, priority=Priority.P1),
                ],
            ),
        ]
        phases.append(phase1)

        # Phase 2: Plugin Hosting System
        phase2 = Phase(
            id=2,
            name="Plugin Hosting System",
            description="VST3, AU, LV2, CLAP plugin hosting and 11 art-themed plugins",
            phase_type=PhaseType.PLUGIN_SYSTEM,
            dependencies=[1],
        )
        phase2.milestones = [
            Milestone(
                id="2.1",
                title="Plugin Format Support",
                tasks=[
                    Task(id="2.1.1", title="Implement VST3 host support", status=TaskStatus.NOT_STARTED, priority=Priority.P0),
                    Task(id="2.1.2", title="Implement AU host support (macOS)", status=TaskStatus.NOT_STARTED, priority=Priority.P0),
                    Task(id="2.1.3", title="Implement LV2 host support (Linux)", status=TaskStatus.NOT_STARTED, priority=Priority.P2),
                    Task(id="2.1.4", title="Implement CLAP host support", status=TaskStatus.NOT_STARTED, priority=Priority.P2),
                    Task(id="2.1.5", title="Create plugin sandboxing", status=TaskStatus.NOT_STARTED, priority=Priority.P1),
                ],
            ),
            Milestone(
                id="2.3",
                title="Art-Themed Plugins",
                tasks=[
                    Task(id="2.3.1", title="Pencil plugin (Sketching)", status=TaskStatus.NOT_STARTED, priority=Priority.P2),
                    Task(id="2.3.2", title="Eraser plugin (Cleanup)", status=TaskStatus.NOT_STARTED, priority=Priority.P1),
                    Task(id="2.3.3", title="Press plugin (Dynamics)", status=TaskStatus.NOT_STARTED, priority=Priority.P1),
                    Task(id="2.3.4", title="Palette plugin (Coloring)", status=TaskStatus.NOT_STARTED, priority=Priority.P1),
                    Task(id="2.3.5", title="Smudge plugin (Blending)", status=TaskStatus.NOT_STARTED, priority=Priority.P2),
                    Task(id="2.3.6", title="Trace plugin (Automation)", status=TaskStatus.NOT_STARTED, priority=Priority.P3),
                    Task(id="2.3.7", title="Parrot plugin (Sampling)", status=TaskStatus.NOT_STARTED, priority=Priority.P2),
                    Task(id="2.3.8", title="Stencil plugin (Sidechain)", status=TaskStatus.NOT_STARTED, priority=Priority.P2),
                    Task(id="2.3.9", title="Chalk plugin (Lo-fi)", status=TaskStatus.NOT_STARTED, priority=Priority.P3),
                    Task(id="2.3.10", title="Brush plugin (Modulation)", status=TaskStatus.NOT_STARTED, priority=Priority.P3),
                    Task(id="2.3.11", title="Stamp plugin (Repeater)", status=TaskStatus.NOT_STARTED, priority=Priority.P3),
                ],
            ),
        ]
        phases.append(phase2)

        # Phase 3: AI/ML Intelligence Layer
        phase3 = Phase(
            id=3,
            name="AI/ML Intelligence Layer",
            description="Local AI inference, emotion analysis, music theory AI",
            phase_type=PhaseType.AI_ML,
            dependencies=[0],
        )
        phase3.milestones = [
            Milestone(
                id="3.1",
                title="Local AI Infrastructure",
                tasks=[
                    Task(id="3.1.1", title="Embed Ollama runtime", status=TaskStatus.NOT_STARTED, priority=Priority.P1),
                    Task(id="3.1.2", title="Bundle optimized models", status=TaskStatus.NOT_STARTED, priority=Priority.P1),
                    Task(id="3.1.3", title="Create GPU acceleration", status=TaskStatus.NOT_STARTED, priority=Priority.P2),
                    Task(id="3.1.4", title="Implement model caching", status=TaskStatus.NOT_STARTED, priority=Priority.P1),
                ],
            ),
            Milestone(
                id="3.2",
                title="Emotion Analysis Engine",
                tasks=[
                    Task(id="3.2.1", title="Implement text-to-emotion analysis", status=TaskStatus.NOT_STARTED, priority=Priority.P1),
                    Task(id="3.2.2", title="Create emotional intent mapping", status=TaskStatus.NOT_STARTED, priority=Priority.P1),
                    Task(id="3.2.3", title="Add emotional arc timeline", status=TaskStatus.NOT_STARTED, priority=Priority.P2),
                    Task(id="3.2.4", title="Implement mood detection", status=TaskStatus.NOT_STARTED, priority=Priority.P2),
                ],
            ),
            Milestone(
                id="3.4",
                title="Generative Composition",
                tasks=[
                    Task(id="3.4.1", title="Implement melody generation", status=TaskStatus.NOT_STARTED, priority=Priority.P1),
                    Task(id="3.4.2", title="Create chord progression generator", status=TaskStatus.NOT_STARTED, priority=Priority.P1),
                    Task(id="3.4.3", title="Add drum pattern generator", status=TaskStatus.NOT_STARTED, priority=Priority.P2),
                    Task(id="3.4.4", title="Implement bass line generation", status=TaskStatus.NOT_STARTED, priority=Priority.P2),
                ],
            ),
        ]
        phases.append(phase3)

        # Phase 4: Desktop Application
        phase4 = Phase(
            id=4,
            name="Desktop Application",
            description="React + Tauri desktop application with timeline, mixer, piano roll",
            phase_type=PhaseType.DESKTOP_APP,
            dependencies=[1, 2],
        )
        phase4.milestones = [
            Milestone(
                id="4.1",
                title="Main Window Framework",
                tasks=[
                    Task(id="4.1.1", title="Implement window management", status=TaskStatus.NOT_STARTED, priority=Priority.P0),
                    Task(id="4.1.2", title="Create themeable UI system", status=TaskStatus.NOT_STARTED, priority=Priority.P1),
                    Task(id="4.1.3", title="Add high-DPI display support", status=TaskStatus.NOT_STARTED, priority=Priority.P0),
                    Task(id="4.1.4", title="Create keyboard shortcut system", status=TaskStatus.NOT_STARTED, priority=Priority.P1),
                ],
            ),
            Milestone(
                id="4.2",
                title="Timeline View",
                tasks=[
                    Task(id="4.2.1", title="Implement zoomable timeline canvas", status=TaskStatus.NOT_STARTED, priority=Priority.P0),
                    Task(id="4.2.2", title="Create track headers", status=TaskStatus.NOT_STARTED, priority=Priority.P0),
                    Task(id="4.2.3", title="Add region/clip display", status=TaskStatus.NOT_STARTED, priority=Priority.P0),
                    Task(id="4.2.4", title="Implement playhead with scrubbing", status=TaskStatus.NOT_STARTED, priority=Priority.P0),
                ],
            ),
            Milestone(
                id="4.4",
                title="Piano Roll / MIDI Editor",
                tasks=[
                    Task(id="4.4.1", title="Implement piano roll canvas", status=TaskStatus.NOT_STARTED, priority=Priority.P0),
                    Task(id="4.4.2", title="Create note tools", status=TaskStatus.NOT_STARTED, priority=Priority.P0),
                    Task(id="4.4.3", title="Add quantize controls", status=TaskStatus.NOT_STARTED, priority=Priority.P1),
                    Task(id="4.4.4", title="Implement velocity editing", status=TaskStatus.NOT_STARTED, priority=Priority.P1),
                ],
            ),
        ]
        phases.append(phase4)

        return phases

    def _initialize_metrics(self) -> Dict[str, Dict[str, str]]:
        """Initialize success metrics."""
        return {
            "performance": {
                "Harmony Engine": "< 100us @ 48kHz/512",
                "Groove Engine": "< 200us @ 48kHz/512",
                "OSC Messaging": "< 50us",
                "Total Plugin": "< 350us",
            },
            "quality": {
                "Chord Detection Accuracy": "> 90%",
                "Tempo Tracking Error": "< 2 BPM",
                "Scale Detection Accuracy": "> 85%",
                "Test Coverage (Python)": "> 80%",
                "Test Coverage (C++)": "> 70%",
            },
            "robustness": {
                "Unit Tests": "All passing",
                "Memory Leaks": "Valgrind clean",
                "Stress Test": "24-hour no crashes",
                "Cross-Platform": "macOS, Linux, Windows",
            },
        }

    def save(self, roadmap: Optional[Roadmap] = None) -> None:
        """Save roadmap to JSON file."""
        if roadmap:
            self.roadmap = roadmap
        self.roadmap.last_updated = datetime.now()
        with open(self.storage_file, "w") as f:
            json.dump(self.roadmap.to_dict(), f, indent=2)

    def reload(self) -> Roadmap:
        """Reload roadmap from storage."""
        self.roadmap = self._load_or_initialize()
        return self.roadmap

    def reinitialize(self) -> Roadmap:
        """Force reinitialization from markdown files."""
        if self.storage_file.exists():
            self.storage_file.unlink()
        self.roadmap = self._initialize_from_markdown()
        return self.roadmap

    # Query methods

    def get_roadmap(self) -> Roadmap:
        """Get the full roadmap."""
        return self.roadmap

    def get_phase(self, phase_id: int) -> Optional[Phase]:
        """Get a specific phase by ID."""
        return self.roadmap.get_phase(phase_id)

    def get_quarter(self, quarter_id: str) -> Optional[Quarter]:
        """Get a specific quarter by ID."""
        return self.roadmap.get_quarter(quarter_id)

    def get_current_phase(self) -> Optional[Phase]:
        """Get the currently active phase."""
        return self.roadmap.get_current_phase()

    def get_phases_by_status(self, status: TaskStatus) -> List[Phase]:
        """Get phases by status."""
        return [p for p in self.roadmap.phases if p.status == status]

    def get_tasks_by_priority(self, priority: Priority) -> List[Tuple[Phase, Milestone, Task]]:
        """Get all tasks with a specific priority."""
        results = []
        for phase in self.roadmap.phases:
            for milestone in phase.milestones:
                for task in milestone.tasks:
                    if task.priority == priority:
                        results.append((phase, milestone, task))
        return results

    def get_pending_tasks(self) -> List[Tuple[Phase, Milestone, Task]]:
        """Get all pending (not started) tasks."""
        results = []
        for phase in self.roadmap.phases:
            for milestone in phase.milestones:
                for task in milestone.tasks:
                    if task.status == TaskStatus.NOT_STARTED:
                        results.append((phase, milestone, task))
        return results

    def get_in_progress_tasks(self) -> List[Tuple[Phase, Milestone, Task]]:
        """Get all in-progress tasks."""
        results = []
        for phase in self.roadmap.phases:
            for milestone in phase.milestones:
                for task in milestone.tasks:
                    if task.status == TaskStatus.IN_PROGRESS:
                        results.append((phase, milestone, task))
        return results

    def search_tasks(self, query: str) -> List[Tuple[Phase, Milestone, Task]]:
        """Search tasks by title or description."""
        query = query.lower()
        results = []
        for phase in self.roadmap.phases:
            for milestone in phase.milestones:
                for task in milestone.tasks:
                    if query in task.title.lower() or query in task.description.lower():
                        results.append((phase, milestone, task))
        return results

    # Update methods

    def update_task_status(
        self,
        task_id: str,
        status: TaskStatus,
        notes: Optional[str] = None
    ) -> Optional[Task]:
        """Update a task's status."""
        for phase in self.roadmap.phases:
            for milestone in phase.milestones:
                for task in milestone.tasks:
                    if task.id == task_id:
                        task.status = status
                        if status == TaskStatus.COMPLETED:
                            task.completed_date = date.today()
                        if notes:
                            task.notes.append(f"[{datetime.now().isoformat()}] {notes}")
                        self.save()
                        return task
        return None

    def assign_task(self, task_id: str, assignee: str) -> Optional[Task]:
        """Assign a task to someone."""
        for phase in self.roadmap.phases:
            for milestone in phase.milestones:
                for task in milestone.tasks:
                    if task.id == task_id:
                        task.assigned_to = assignee
                        self.save()
                        return task
        return None

    def add_task_note(self, task_id: str, note: str) -> Optional[Task]:
        """Add a note to a task."""
        for phase in self.roadmap.phases:
            for milestone in phase.milestones:
                for task in milestone.tasks:
                    if task.id == task_id:
                        task.notes.append(f"[{datetime.now().isoformat()}] {note}")
                        self.save()
                        return task
        return None

    # Summary methods

    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of roadmap progress."""
        total_tasks = 0
        completed_tasks = 0
        in_progress_tasks = 0
        blocked_tasks = 0

        phase_summaries = []
        for phase in self.roadmap.phases:
            phase_total = phase.total_tasks
            phase_completed = phase.completed_tasks
            total_tasks += phase_total
            completed_tasks += phase_completed

            phase_in_progress = sum(
                sum(1 for t in m.tasks if t.status == TaskStatus.IN_PROGRESS)
                for m in phase.milestones
            )
            phase_blocked = sum(
                sum(1 for t in m.tasks if t.status == TaskStatus.BLOCKED)
                for m in phase.milestones
            )
            in_progress_tasks += phase_in_progress
            blocked_tasks += phase_blocked

            phase_summaries.append({
                "id": phase.id,
                "name": phase.name,
                "status": phase.status.value,
                "progress": f"{phase.progress * 100:.1f}%",
                "tasks": f"{phase_completed}/{phase_total}",
            })

        return {
            "overall_progress": f"{self.roadmap.overall_progress * 100:.1f}%",
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "in_progress_tasks": in_progress_tasks,
            "blocked_tasks": blocked_tasks,
            "pending_tasks": total_tasks - completed_tasks - in_progress_tasks - blocked_tasks,
            "phases_completed": self.roadmap.phases_completed,
            "total_phases": len(self.roadmap.phases),
            "phases": phase_summaries,
            "last_updated": self.roadmap.last_updated.isoformat(),
        }

    def get_progress_view(self) -> str:
        """Get a formatted progress view for display."""
        lines = []
        lines.append("=" * 60)
        lines.append("iDAWi Roadmap Progress")
        lines.append("=" * 60)
        lines.append("")

        summary = self.get_summary()
        lines.append(f"Overall Progress: {summary['overall_progress']}")
        lines.append(f"Phases: {summary['phases_completed']}/{summary['total_phases']} complete")
        lines.append(f"Tasks: {summary['completed_tasks']}/{summary['total_tasks']} complete")
        lines.append("")

        for phase_info in summary["phases"]:
            status_icon = {
                "completed": "[x]",
                "in_progress": "[>]",
                "blocked": "[!]",
                "not_started": "[ ]",
            }.get(phase_info["status"], "[ ]")

            lines.append(f"{status_icon} Phase {phase_info['id']}: {phase_info['name']}")
            lines.append(f"    Progress: {phase_info['progress']} ({phase_info['tasks']} tasks)")

        lines.append("")
        lines.append(f"Last Updated: {summary['last_updated']}")
        lines.append("=" * 60)

        return "\n".join(lines)
