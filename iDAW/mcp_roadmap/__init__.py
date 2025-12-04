"""
MCP Roadmap Server

Model Context Protocol server for iDAWi project roadmap management.
Provides tools to query, track, and update project roadmap phases and milestones.

Compatible with Claude, ChatGPT, Gemini, and Cursor/VSCode with Copilot.
"""

__version__ = "1.0.0"
__all__ = ["MCPRoadmapServer", "RoadmapStorage", "Phase", "Quarter", "Milestone", "Task"]

from .models import Phase, Quarter, Milestone, Task, TaskStatus
from .storage import RoadmapStorage
from .server import MCPRoadmapServer
