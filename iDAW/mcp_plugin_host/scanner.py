"""
MCP Plugin Host - Plugin Scanner

Discovers and validates plugins from system paths.
Supports VST3, AU, LV2, and CLAP formats.
"""

import os
import platform
import asyncio
from pathlib import Path
from typing import List, Optional, Dict, Any, Callable
from datetime import datetime
import logging

from .models import (
    Plugin, PluginFormat, PluginType, PluginCategory, PluginStatus
)
from .storage import PluginStorage


logger = logging.getLogger(__name__)


# =============================================================================
# Default Plugin Paths by Platform
# =============================================================================

def get_default_vst3_paths() -> List[str]:
    """Get default VST3 plugin search paths for the current platform."""
    system = platform.system()

    if system == "Darwin":  # macOS
        return [
            "/Library/Audio/Plug-Ins/VST3",
            os.path.expanduser("~/Library/Audio/Plug-Ins/VST3"),
        ]
    elif system == "Windows":
        return [
            "C:\\Program Files\\Common Files\\VST3",
            "C:\\Program Files (x86)\\Common Files\\VST3",
            os.path.expanduser("~\\VST3"),
        ]
    else:  # Linux
        return [
            "/usr/lib/vst3",
            "/usr/local/lib/vst3",
            os.path.expanduser("~/.vst3"),
        ]


def get_default_au_paths() -> List[str]:
    """Get default Audio Unit paths (macOS only)."""
    if platform.system() != "Darwin":
        return []

    return [
        "/Library/Audio/Plug-Ins/Components",
        os.path.expanduser("~/Library/Audio/Plug-Ins/Components"),
    ]


def get_default_lv2_paths() -> List[str]:
    """Get default LV2 plugin paths (Linux primarily)."""
    system = platform.system()

    if system == "Linux":
        return [
            "/usr/lib/lv2",
            "/usr/local/lib/lv2",
            os.path.expanduser("~/.lv2"),
        ]
    elif system == "Darwin":
        return [
            "/Library/Audio/Plug-Ins/LV2",
            os.path.expanduser("~/Library/Audio/Plug-Ins/LV2"),
        ]
    else:
        return []


def get_default_clap_paths() -> List[str]:
    """Get default CLAP plugin paths."""
    system = platform.system()

    if system == "Darwin":
        return [
            "/Library/Audio/Plug-Ins/CLAP",
            os.path.expanduser("~/Library/Audio/Plug-Ins/CLAP"),
        ]
    elif system == "Windows":
        return [
            "C:\\Program Files\\Common Files\\CLAP",
            os.path.expanduser("~\\CLAP"),
        ]
    else:  # Linux
        return [
            "/usr/lib/clap",
            "/usr/local/lib/clap",
            os.path.expanduser("~/.clap"),
        ]


def get_all_default_paths() -> Dict[PluginFormat, List[str]]:
    """Get all default plugin paths organized by format."""
    return {
        PluginFormat.VST3: get_default_vst3_paths(),
        PluginFormat.AU: get_default_au_paths(),
        PluginFormat.LV2: get_default_lv2_paths(),
        PluginFormat.CLAP: get_default_clap_paths(),
    }


# =============================================================================
# Plugin File Detection
# =============================================================================

PLUGIN_EXTENSIONS = {
    PluginFormat.VST3: [".vst3"],
    PluginFormat.AU: [".component"],
    PluginFormat.LV2: [".lv2"],
    PluginFormat.CLAP: [".clap"],
}


def detect_plugin_format(path: str) -> Optional[PluginFormat]:
    """Detect plugin format from file path."""
    path_lower = path.lower()

    for fmt, extensions in PLUGIN_EXTENSIONS.items():
        for ext in extensions:
            if path_lower.endswith(ext):
                return fmt

    return None


def guess_category_from_name(name: str) -> PluginCategory:
    """Guess plugin category from its name."""
    name_lower = name.lower()

    # Dynamics
    if any(kw in name_lower for kw in ["compressor", "limiter", "gate", "expander", "dynamics"]):
        return PluginCategory.DYNAMICS

    # EQ
    if any(kw in name_lower for kw in ["eq", "equalizer", "filter"]):
        return PluginCategory.EQ

    # Distortion
    if any(kw in name_lower for kw in ["distortion", "overdrive", "amp", "saturate", "fuzz"]):
        return PluginCategory.DISTORTION

    # Modulation
    if any(kw in name_lower for kw in ["chorus", "flanger", "phaser", "tremolo", "vibrato", "mod"]):
        return PluginCategory.MODULATION

    # Delay
    if any(kw in name_lower for kw in ["delay", "echo"]):
        return PluginCategory.DELAY

    # Reverb
    if any(kw in name_lower for kw in ["reverb", "room", "hall", "plate", "spring"]):
        return PluginCategory.REVERB

    # Pitch
    if any(kw in name_lower for kw in ["pitch", "tune", "autotune", "harmonizer"]):
        return PluginCategory.PITCH

    # Synth
    if any(kw in name_lower for kw in ["synth", "synthesizer", "osc"]):
        return PluginCategory.SYNTH

    # Sampler
    if any(kw in name_lower for kw in ["sampler", "sample", "rompler"]):
        return PluginCategory.SAMPLER

    # Analyzer
    if any(kw in name_lower for kw in ["analyzer", "meter", "spectrum", "scope"]):
        return PluginCategory.ANALYZER

    return PluginCategory.OTHER


def guess_plugin_type_from_name(name: str) -> PluginType:
    """Guess if plugin is an effect or instrument from name."""
    name_lower = name.lower()

    instrument_keywords = [
        "synth", "synthesizer", "sampler", "piano", "organ", "bass",
        "guitar", "drum", "strings", "brass", "woodwind", "instrument"
    ]

    if any(kw in name_lower for kw in instrument_keywords):
        return PluginType.INSTRUMENT

    return PluginType.EFFECT


# =============================================================================
# Plugin Scanner
# =============================================================================

class PluginScanner:
    """
    Discovers and validates audio plugins.

    Supports background scanning with progress callbacks.
    """

    def __init__(self, storage: PluginStorage):
        self.storage = storage
        self._scan_running = False
        self._scan_cancelled = False
        self._scan_progress = 0.0
        self._plugins_found = 0

    @property
    def is_scanning(self) -> bool:
        return self._scan_running

    @property
    def scan_progress(self) -> float:
        return self._scan_progress

    @property
    def plugins_found(self) -> int:
        return self._plugins_found

    def cancel_scan(self):
        """Request scan cancellation."""
        self._scan_cancelled = True

    def discover_plugin_files(
        self,
        paths: Optional[List[str]] = None,
        formats: Optional[List[PluginFormat]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Discover plugin files in the given paths.

        Args:
            paths: Paths to scan. Uses defaults if not specified.
            formats: Formats to scan for. Scans all if not specified.

        Returns:
            List of dicts with 'path', 'format', and 'name' keys
        """
        discovered = []

        # Get paths to scan
        if paths:
            scan_paths = {fmt: paths for fmt in (formats or list(PluginFormat))}
        else:
            scan_paths = get_all_default_paths()
            if formats:
                scan_paths = {fmt: scan_paths.get(fmt, []) for fmt in formats}

        # Scan each format
        for fmt, fmt_paths in scan_paths.items():
            if fmt == PluginFormat.BUILTIN:
                continue  # Skip built-in plugins

            extensions = PLUGIN_EXTENSIONS.get(fmt, [])

            for base_path in fmt_paths:
                if not os.path.exists(base_path):
                    continue

                for root, dirs, files in os.walk(base_path):
                    # For bundle formats, check directory names
                    for d in dirs:
                        for ext in extensions:
                            if d.lower().endswith(ext):
                                full_path = os.path.join(root, d)
                                name = os.path.splitext(d)[0]
                                discovered.append({
                                    "path": full_path,
                                    "format": fmt,
                                    "name": name,
                                })
                                break

                    # Also check files (some formats are single files)
                    for f in files:
                        for ext in extensions:
                            if f.lower().endswith(ext):
                                full_path = os.path.join(root, f)
                                name = os.path.splitext(f)[0]
                                discovered.append({
                                    "path": full_path,
                                    "format": fmt,
                                    "name": name,
                                })
                                break

        return discovered

    def create_plugin_from_discovery(self, discovery: Dict[str, Any]) -> Plugin:
        """
        Create a Plugin object from discovery data.

        Note: Full validation requires loading the plugin, which is
        not done here. This creates metadata based on file inspection.
        """
        name = discovery["name"]
        path = discovery["path"]
        fmt = discovery["format"]

        # Guess type and category from name
        plugin_type = guess_plugin_type_from_name(name)
        category = guess_category_from_name(name)

        plugin = Plugin(
            name=name,
            vendor="Unknown",  # Would need to load plugin to get this
            version="",
            description="",
            format=fmt,
            plugin_type=plugin_type,
            category=category,
            path=path,
            status=PluginStatus.VALID,  # Assume valid, would verify on load
            last_scanned=datetime.now().isoformat(),
            is_synth=plugin_type == PluginType.INSTRUMENT,
            supports_midi=plugin_type == PluginType.INSTRUMENT,
        )

        return plugin

    def scan_sync(
        self,
        paths: Optional[List[str]] = None,
        formats: Optional[List[PluginFormat]] = None,
        progress_callback: Optional[Callable[[float, int], None]] = None,
    ) -> List[Plugin]:
        """
        Synchronously scan for plugins.

        Args:
            paths: Paths to scan
            formats: Formats to scan for
            progress_callback: Called with (progress_percent, plugins_found)

        Returns:
            List of discovered plugins
        """
        self._scan_running = True
        self._scan_cancelled = False
        self._plugins_found = 0
        self._scan_progress = 0.0

        try:
            # Discover plugin files
            discovered = self.discover_plugin_files(paths, formats)
            total = len(discovered)

            plugins = []
            for i, disc in enumerate(discovered):
                if self._scan_cancelled:
                    break

                # Check blacklist
                if self.storage.is_blacklisted(disc["path"]):
                    continue

                # Create plugin object
                plugin = self.create_plugin_from_discovery(disc)

                # Save to storage
                self.storage.add_plugin(plugin)
                plugins.append(plugin)

                self._plugins_found = len(plugins)
                self._scan_progress = (i + 1) / total if total > 0 else 1.0

                if progress_callback:
                    progress_callback(self._scan_progress, self._plugins_found)

            # Update last scan time
            self.storage.update_last_scan()

            return plugins

        finally:
            self._scan_running = False

    async def scan_async(
        self,
        paths: Optional[List[str]] = None,
        formats: Optional[List[PluginFormat]] = None,
        progress_callback: Optional[Callable[[float, int], None]] = None,
    ) -> List[Plugin]:
        """
        Asynchronously scan for plugins.

        Runs the scan in a thread executor to avoid blocking.
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            lambda: self.scan_sync(paths, formats, progress_callback)
        )

    def validate_plugin(self, plugin_id: str) -> Dict[str, Any]:
        """
        Validate a plugin by attempting to load it.

        Returns validation result with status and any errors.

        Note: Actual plugin loading requires JUCE/C++ integration.
        This is a placeholder that checks file existence.
        """
        plugin = self.storage.get_plugin(plugin_id)
        if not plugin:
            return {
                "valid": False,
                "error": "Plugin not found in database",
            }

        # Check if file exists
        if plugin.format != PluginFormat.BUILTIN:
            if not os.path.exists(plugin.path):
                plugin.status = PluginStatus.INVALID
                plugin.validation_error = "Plugin file not found"
                self.storage.add_plugin(plugin)
                return {
                    "valid": False,
                    "error": "Plugin file not found",
                    "path": plugin.path,
                }

        # Current: File-based validation (checks existence and format)
        # Future: Full validation via JUCE plugin loading for metadata extraction
        # and compatibility testing (requires C++ integration)
        plugin.status = PluginStatus.VALID
        plugin.validation_error = ""
        plugin.last_scanned = datetime.now().isoformat()
        self.storage.add_plugin(plugin)

        return {
            "valid": True,
            "plugin_id": plugin.id,
            "name": plugin.name,
            "format": plugin.format.value,
        }

    def get_scan_status(self) -> Dict[str, Any]:
        """Get current scan status."""
        return {
            "is_scanning": self._scan_running,
            "progress": self._scan_progress,
            "plugins_found": self._plugins_found,
        }

    def get_system_plugin_paths(self) -> Dict[str, List[str]]:
        """Get detected system plugin paths."""
        result = {}
        for fmt, paths in get_all_default_paths().items():
            existing = [p for p in paths if os.path.exists(p)]
            if existing:
                result[fmt.value] = existing
        return result


# =============================================================================
# Performance Profiler
# =============================================================================

class PluginProfiler:
    """
    Profiles plugin CPU and memory usage.

    Note: Actual profiling requires C++ integration with the audio engine.
    This provides the interface and placeholder implementation.
    """

    def __init__(self, storage: PluginStorage):
        self.storage = storage

    def profile_plugin(self, plugin_id: str, duration_seconds: float = 5.0) -> Dict[str, Any]:
        """
        Profile a plugin's resource usage.

        Args:
            plugin_id: Plugin to profile
            duration_seconds: How long to profile

        Returns:
            Profile results with CPU and memory stats
        """
        plugin = self.storage.get_plugin(plugin_id)
        if not plugin:
            return {"error": "Plugin not found"}

        # Placeholder - actual profiling needs audio engine integration
        # This would:
        # 1. Create a plugin instance
        # 2. Process silent audio for duration_seconds
        # 3. Measure CPU time and memory allocation
        # 4. Calculate average and peak values

        return {
            "plugin_id": plugin_id,
            "plugin_name": plugin.name,
            "duration_seconds": duration_seconds,
            "avg_cpu_percent": 0.0,  # Would be measured
            "peak_cpu_percent": 0.0,
            "avg_memory_mb": 0.0,
            "peak_memory_mb": 0.0,
            "note": "Profiling requires C++ audio engine integration",
        }

    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary for all profiled plugins."""
        plugins = self.storage.list_plugins()

        summary = {
            "total_plugins": len(plugins),
            "profiled_count": 0,
            "high_cpu_plugins": [],
            "high_memory_plugins": [],
        }

        for plugin in plugins:
            if plugin.avg_cpu_percent > 0:
                summary["profiled_count"] += 1

            if plugin.avg_cpu_percent > 10.0:  # >10% CPU
                summary["high_cpu_plugins"].append({
                    "id": plugin.id,
                    "name": plugin.name,
                    "cpu_percent": plugin.avg_cpu_percent,
                })

            if plugin.avg_memory_mb > 100.0:  # >100MB
                summary["high_memory_plugins"].append({
                    "id": plugin.id,
                    "name": plugin.name,
                    "memory_mb": plugin.avg_memory_mb,
                })

        return summary
