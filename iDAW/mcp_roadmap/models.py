"""
MCP Roadmap - Data Models

Defines the data structures for roadmap tracking:
- Phase: Major development phases (0-14)
- Quarter: Quarterly milestones (Q1 2025 - H1 2026)
- Milestone: Individual milestones within phases
- Task: Individual tasks/items within milestones
"""

from dataclasses import dataclass, field
from datetime import datetime, date
from enum import Enum
from typing import List, Optional, Dict, Any
import json


class TaskStatus(Enum):
    """Status of a roadmap task."""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    BLOCKED = "blocked"
    DEFERRED = "deferred"


class Priority(Enum):
    """Priority levels for tasks."""
    P0 = "P0"  # Critical for MVP
    P1 = "P1"  # Essential for beta
    P2 = "P2"  # Needed for 1.0
    P3 = "P3"  # Nice to have
    P4 = "P4"  # Future versions


class PhaseType(Enum):
    """Types of development phases."""
    FOUNDATION = "foundation"
    AUDIO_ENGINE = "audio_engine"
    PLUGIN_SYSTEM = "plugin_system"
    AI_ML = "ai_ml"
    DESKTOP_APP = "desktop_app"
    PROJECT_MGMT = "project_mgmt"
    ADVANCED = "advanced"
    TESTING = "testing"
    DOCUMENTATION = "documentation"
    PACKAGING = "packaging"
    OPTIMIZATION = "optimization"
    SECURITY = "security"
    ACCESSIBILITY = "accessibility"
    LOCALIZATION = "localization"
    FUTURE = "future"


@dataclass
class Task:
    """Individual task within a milestone."""
    id: str
    title: str
    status: TaskStatus = TaskStatus.NOT_STARTED
    priority: Optional[Priority] = None
    description: str = ""
    assigned_to: Optional[str] = None
    completed_date: Optional[date] = None
    notes: List[str] = field(default_factory=list)
    subtasks: List["Task"] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "status": self.status.value,
            "priority": self.priority.value if self.priority else None,
            "description": self.description,
            "assigned_to": self.assigned_to,
            "completed_date": self.completed_date.isoformat() if self.completed_date else None,
            "notes": self.notes,
            "subtasks": [st.to_dict() for st in self.subtasks],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Task":
        """Create from dictionary."""
        return cls(
            id=data["id"],
            title=data["title"],
            status=TaskStatus(data.get("status", "not_started")),
            priority=Priority(data["priority"]) if data.get("priority") else None,
            description=data.get("description", ""),
            assigned_to=data.get("assigned_to"),
            completed_date=date.fromisoformat(data["completed_date"]) if data.get("completed_date") else None,
            notes=data.get("notes", []),
            subtasks=[cls.from_dict(st) for st in data.get("subtasks", [])],
        )


@dataclass
class Milestone:
    """A milestone within a phase (e.g., Week 1-2, Month 1)."""
    id: str
    title: str
    description: str = ""
    tasks: List[Task] = field(default_factory=list)
    target_date: Optional[date] = None
    completed_date: Optional[date] = None
    performance_targets: Dict[str, str] = field(default_factory=dict)

    @property
    def status(self) -> TaskStatus:
        """Calculate milestone status from tasks."""
        if not self.tasks:
            return TaskStatus.NOT_STARTED

        statuses = [t.status for t in self.tasks]
        if all(s == TaskStatus.COMPLETED for s in statuses):
            return TaskStatus.COMPLETED
        elif any(s == TaskStatus.IN_PROGRESS for s in statuses):
            return TaskStatus.IN_PROGRESS
        elif any(s == TaskStatus.BLOCKED for s in statuses):
            return TaskStatus.BLOCKED
        else:
            return TaskStatus.NOT_STARTED

    @property
    def progress(self) -> float:
        """Calculate completion percentage."""
        if not self.tasks:
            return 0.0
        completed = sum(1 for t in self.tasks if t.status == TaskStatus.COMPLETED)
        return completed / len(self.tasks)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "tasks": [t.to_dict() for t in self.tasks],
            "target_date": self.target_date.isoformat() if self.target_date else None,
            "completed_date": self.completed_date.isoformat() if self.completed_date else None,
            "performance_targets": self.performance_targets,
            "status": self.status.value,
            "progress": self.progress,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Milestone":
        """Create from dictionary."""
        return cls(
            id=data["id"],
            title=data["title"],
            description=data.get("description", ""),
            tasks=[Task.from_dict(t) for t in data.get("tasks", [])],
            target_date=date.fromisoformat(data["target_date"]) if data.get("target_date") else None,
            completed_date=date.fromisoformat(data["completed_date"]) if data.get("completed_date") else None,
            performance_targets=data.get("performance_targets", {}),
        )


@dataclass
class Phase:
    """A major development phase."""
    id: int
    name: str
    description: str = ""
    phase_type: PhaseType = PhaseType.FOUNDATION
    milestones: List[Milestone] = field(default_factory=list)
    start_date: Optional[date] = None
    target_end_date: Optional[date] = None
    actual_end_date: Optional[date] = None
    dependencies: List[int] = field(default_factory=list)  # Phase IDs

    @property
    def status(self) -> TaskStatus:
        """Calculate phase status from milestones."""
        if not self.milestones:
            return TaskStatus.NOT_STARTED

        statuses = [m.status for m in self.milestones]
        if all(s == TaskStatus.COMPLETED for s in statuses):
            return TaskStatus.COMPLETED
        elif any(s == TaskStatus.IN_PROGRESS for s in statuses):
            return TaskStatus.IN_PROGRESS
        elif any(s == TaskStatus.BLOCKED for s in statuses):
            return TaskStatus.BLOCKED
        elif any(s == TaskStatus.COMPLETED for s in statuses):
            return TaskStatus.IN_PROGRESS
        else:
            return TaskStatus.NOT_STARTED

    @property
    def progress(self) -> float:
        """Calculate completion percentage."""
        if not self.milestones:
            return 0.0
        total_tasks = sum(len(m.tasks) for m in self.milestones)
        if total_tasks == 0:
            return 0.0
        completed_tasks = sum(
            sum(1 for t in m.tasks if t.status == TaskStatus.COMPLETED)
            for m in self.milestones
        )
        return completed_tasks / total_tasks

    @property
    def total_tasks(self) -> int:
        """Total number of tasks in phase."""
        return sum(len(m.tasks) for m in self.milestones)

    @property
    def completed_tasks(self) -> int:
        """Number of completed tasks."""
        return sum(
            sum(1 for t in m.tasks if t.status == TaskStatus.COMPLETED)
            for m in self.milestones
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "phase_type": self.phase_type.value,
            "milestones": [m.to_dict() for m in self.milestones],
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "target_end_date": self.target_end_date.isoformat() if self.target_end_date else None,
            "actual_end_date": self.actual_end_date.isoformat() if self.actual_end_date else None,
            "dependencies": self.dependencies,
            "status": self.status.value,
            "progress": self.progress,
            "total_tasks": self.total_tasks,
            "completed_tasks": self.completed_tasks,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Phase":
        """Create from dictionary."""
        return cls(
            id=data["id"],
            name=data["name"],
            description=data.get("description", ""),
            phase_type=PhaseType(data.get("phase_type", "foundation")),
            milestones=[Milestone.from_dict(m) for m in data.get("milestones", [])],
            start_date=date.fromisoformat(data["start_date"]) if data.get("start_date") else None,
            target_end_date=date.fromisoformat(data["target_end_date"]) if data.get("target_end_date") else None,
            actual_end_date=date.fromisoformat(data["actual_end_date"]) if data.get("actual_end_date") else None,
            dependencies=data.get("dependencies", []),
        )


@dataclass
class Quarter:
    """Quarterly roadmap milestone (from 18-month roadmap)."""
    id: str  # e.g., "Q1_2025", "H1_2026"
    name: str  # e.g., "Q1 2025: Core Foundation"
    focus: str  # Main focus area
    key_deliverables: List[str] = field(default_factory=list)
    status: TaskStatus = TaskStatus.NOT_STARTED
    months: List[str] = field(default_factory=list)  # Month IDs
    start_date: Optional[date] = None
    end_date: Optional[date] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "focus": self.focus,
            "key_deliverables": self.key_deliverables,
            "status": self.status.value,
            "months": self.months,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "end_date": self.end_date.isoformat() if self.end_date else None,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Quarter":
        """Create from dictionary."""
        return cls(
            id=data["id"],
            name=data["name"],
            focus=data.get("focus", ""),
            key_deliverables=data.get("key_deliverables", []),
            status=TaskStatus(data.get("status", "not_started")),
            months=data.get("months", []),
            start_date=date.fromisoformat(data["start_date"]) if data.get("start_date") else None,
            end_date=date.fromisoformat(data["end_date"]) if data.get("end_date") else None,
        )


@dataclass
class Roadmap:
    """Complete project roadmap."""
    name: str
    description: str
    start_date: date
    end_date: date
    phases: List[Phase] = field(default_factory=list)
    quarters: List[Quarter] = field(default_factory=list)
    success_metrics: Dict[str, Dict[str, str]] = field(default_factory=dict)
    last_updated: datetime = field(default_factory=datetime.now)

    @property
    def overall_progress(self) -> float:
        """Calculate overall roadmap progress."""
        if not self.phases:
            return 0.0
        total = sum(p.total_tasks for p in self.phases)
        if total == 0:
            return 0.0
        completed = sum(p.completed_tasks for p in self.phases)
        return completed / total

    @property
    def phases_completed(self) -> int:
        """Number of completed phases."""
        return sum(1 for p in self.phases if p.status == TaskStatus.COMPLETED)

    def get_current_phase(self) -> Optional[Phase]:
        """Get the current active phase."""
        for phase in self.phases:
            if phase.status == TaskStatus.IN_PROGRESS:
                return phase
        # If no in-progress, return first not-started
        for phase in self.phases:
            if phase.status == TaskStatus.NOT_STARTED:
                return phase
        return None

    def get_phase(self, phase_id: int) -> Optional[Phase]:
        """Get a phase by ID."""
        for phase in self.phases:
            if phase.id == phase_id:
                return phase
        return None

    def get_quarter(self, quarter_id: str) -> Optional[Quarter]:
        """Get a quarter by ID."""
        for quarter in self.quarters:
            if quarter.id == quarter_id:
                return quarter
        return None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "description": self.description,
            "start_date": self.start_date.isoformat(),
            "end_date": self.end_date.isoformat(),
            "phases": [p.to_dict() for p in self.phases],
            "quarters": [q.to_dict() for q in self.quarters],
            "success_metrics": self.success_metrics,
            "last_updated": self.last_updated.isoformat(),
            "overall_progress": self.overall_progress,
            "phases_completed": self.phases_completed,
            "total_phases": len(self.phases),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Roadmap":
        """Create from dictionary."""
        return cls(
            name=data["name"],
            description=data.get("description", ""),
            start_date=date.fromisoformat(data["start_date"]),
            end_date=date.fromisoformat(data["end_date"]),
            phases=[Phase.from_dict(p) for p in data.get("phases", [])],
            quarters=[Quarter.from_dict(q) for q in data.get("quarters", [])],
            success_metrics=data.get("success_metrics", {}),
            last_updated=datetime.fromisoformat(data["last_updated"]) if data.get("last_updated") else datetime.now(),
        )
