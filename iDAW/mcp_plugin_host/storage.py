"""
MCP Plugin Host - Storage Backend

JSON file-based storage for plugin database, presets, and instance tracking.
Supports concurrent access with file locking.
"""

import json
import os
import fcntl
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime

from .models import (
    Plugin, PluginPreset, PluginInstance, PluginChain, PluginStatus,
    PluginFormat, PluginType, PluginCategory, InstrumentRack,
    get_builtin_plugins
)


class PluginStorage:
    """
    File-based storage for plugin database and presets.

    Features:
    - Plugin database with caching
    - Preset management
    - Instance tracking
    - Plugin chains
    - Blacklist management
    - Recently used / favorites
    """

    def __init__(self, storage_dir: Optional[str] = None):
        """
        Initialize storage.

        Args:
            storage_dir: Directory for plugin storage. Defaults to ~/.mcp_plugin_host/
        """
        if storage_dir:
            self.storage_dir = Path(storage_dir)
        else:
            self.storage_dir = Path.home() / ".mcp_plugin_host"

        self.storage_dir.mkdir(parents=True, exist_ok=True)

        # Storage files
        self.plugins_file = self.storage_dir / "plugins.json"
        self.presets_file = self.storage_dir / "presets.json"
        self.instances_file = self.storage_dir / "instances.json"
        self.chains_file = self.storage_dir / "chains.json"
        self.blacklist_file = self.storage_dir / "blacklist.json"
        self.racks_file = self.storage_dir / "instrument_racks.json"

        # Initialize files
        self._ensure_files_exist()

        # Cache built-in plugins
        self._register_builtin_plugins()

    def _ensure_files_exist(self):
        """Create default files if they don't exist."""
        defaults = {
            self.plugins_file: {"plugins": {}, "scan_paths": [], "last_scan": None},
            self.presets_file: {"presets": {}, "by_plugin": {}},
            self.instances_file: {"instances": {}},
            self.chains_file: {"chains": {}},
            self.blacklist_file: {"blacklisted": [], "reasons": {}},
            self.racks_file: {"racks": {}},
        }

        for file_path, default_data in defaults.items():
            if not file_path.exists():
                self._save_data(default_data, file_path)

    def _register_builtin_plugins(self):
        """Register built-in art-themed plugins in the database."""
        builtin = get_builtin_plugins()
        data = self._load_data(self.plugins_file)

        for plugin in builtin:
            data["plugins"][plugin.id] = plugin.to_dict()

        self._save_data(data, self.plugins_file)

    def _load_data(self, file_path: Path) -> Dict[str, Any]:
        """Load data with file locking."""
        if not file_path.exists():
            return {}

        with open(file_path, "r") as f:
            try:
                fcntl.flock(f.fileno(), fcntl.LOCK_SH)
                data = json.load(f)
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)

        return data

    def _save_data(self, data: Dict[str, Any], file_path: Path) -> None:
        """Save data with file locking and backup."""
        # Create backup if file exists
        if file_path.exists():
            backup_path = file_path.with_suffix(".json.bak")
            with open(file_path, "r") as src:
                with open(backup_path, "w") as dst:
                    dst.write(src.read())

        # Write with lock
        with open(file_path, "w") as f:
            try:
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                json.dump(data, f, indent=2)
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)

    # =========================================================================
    # Plugin Database Operations
    # =========================================================================

    def add_plugin(self, plugin: Plugin) -> Plugin:
        """Add or update a plugin in the database."""
        data = self._load_data(self.plugins_file)
        data["plugins"][plugin.id] = plugin.to_dict()
        self._save_data(data, self.plugins_file)
        return plugin

    def get_plugin(self, plugin_id: str) -> Optional[Plugin]:
        """Get a plugin by ID."""
        data = self._load_data(self.plugins_file)
        plugin_data = data.get("plugins", {}).get(plugin_id)
        if plugin_data:
            return Plugin.from_dict(plugin_data)
        return None

    def list_plugins(
        self,
        format: Optional[PluginFormat] = None,
        plugin_type: Optional[PluginType] = None,
        category: Optional[PluginCategory] = None,
        favorites_only: bool = False,
        recently_used: bool = False,
        search_query: Optional[str] = None,
    ) -> List[Plugin]:
        """
        List plugins with optional filters.

        Args:
            format: Filter by plugin format
            plugin_type: Filter by type (effect/instrument)
            category: Filter by category
            favorites_only: Only return favorites
            recently_used: Only return recently used
            search_query: Fuzzy search in name/vendor/description

        Returns:
            List of matching plugins
        """
        data = self._load_data(self.plugins_file)
        plugins = []

        for plugin_data in data.get("plugins", {}).values():
            plugin = Plugin.from_dict(plugin_data)

            # Apply filters
            if format and plugin.format != format:
                continue
            if plugin_type and plugin.plugin_type != plugin_type:
                continue
            if category and plugin.category != category:
                continue
            if favorites_only and not plugin.is_favorite:
                continue
            if recently_used and not plugin.is_recently_used:
                continue
            if search_query:
                query = search_query.lower()
                searchable = f"{plugin.name} {plugin.vendor} {plugin.description}".lower()
                if query not in searchable:
                    continue

            plugins.append(plugin)

        # Sort by use_count for recently used, otherwise by name
        if recently_used:
            plugins.sort(key=lambda p: p.use_count, reverse=True)
        else:
            plugins.sort(key=lambda p: p.name.lower())

        return plugins

    def search_plugins(self, query: str, limit: int = 20) -> List[Plugin]:
        """
        Fuzzy search for plugins.

        Uses simple substring matching. Returns sorted by relevance.
        """
        data = self._load_data(self.plugins_file)
        results = []
        query_lower = query.lower()

        for plugin_data in data.get("plugins", {}).values():
            plugin = Plugin.from_dict(plugin_data)

            # Calculate relevance score
            name_match = query_lower in plugin.name.lower()
            vendor_match = query_lower in plugin.vendor.lower()
            desc_match = query_lower in plugin.description.lower()
            tag_match = any(query_lower in t.lower() for t in plugin.tags)

            if name_match or vendor_match or desc_match or tag_match:
                # Score: name > vendor > tags > description
                score = 0
                if name_match:
                    score += 100
                    if plugin.name.lower().startswith(query_lower):
                        score += 50
                if vendor_match:
                    score += 30
                if tag_match:
                    score += 20
                if desc_match:
                    score += 10

                results.append((score, plugin))

        # Sort by score descending
        results.sort(key=lambda x: x[0], reverse=True)
        return [p for _, p in results[:limit]]

    def set_favorite(self, plugin_id: str, is_favorite: bool) -> bool:
        """Set plugin favorite status."""
        data = self._load_data(self.plugins_file)
        if plugin_id in data.get("plugins", {}):
            data["plugins"][plugin_id]["is_favorite"] = is_favorite
            self._save_data(data, self.plugins_file)
            return True
        return False

    def mark_used(self, plugin_id: str) -> bool:
        """Mark plugin as recently used."""
        data = self._load_data(self.plugins_file)
        if plugin_id in data.get("plugins", {}):
            data["plugins"][plugin_id]["is_recently_used"] = True
            data["plugins"][plugin_id]["use_count"] = data["plugins"][plugin_id].get("use_count", 0) + 1
            data["plugins"][plugin_id]["last_used"] = datetime.now().isoformat()
            self._save_data(data, self.plugins_file)
            return True
        return False

    def add_tag(self, plugin_id: str, tag: str) -> bool:
        """Add a tag to a plugin."""
        data = self._load_data(self.plugins_file)
        if plugin_id in data.get("plugins", {}):
            tags = data["plugins"][plugin_id].get("tags", [])
            if tag not in tags:
                tags.append(tag)
                data["plugins"][plugin_id]["tags"] = tags
                self._save_data(data, self.plugins_file)
            return True
        return False

    def remove_tag(self, plugin_id: str, tag: str) -> bool:
        """Remove a tag from a plugin."""
        data = self._load_data(self.plugins_file)
        if plugin_id in data.get("plugins", {}):
            tags = data["plugins"][plugin_id].get("tags", [])
            if tag in tags:
                tags.remove(tag)
                data["plugins"][plugin_id]["tags"] = tags
                self._save_data(data, self.plugins_file)
            return True
        return False

    def get_summary(self) -> Dict[str, Any]:
        """Get plugin database summary."""
        data = self._load_data(self.plugins_file)
        plugins = list(data.get("plugins", {}).values())

        by_format = {}
        by_type = {}
        by_category = {}
        favorites_count = 0
        blacklisted_count = len(self._load_data(self.blacklist_file).get("blacklisted", []))

        for p in plugins:
            fmt = p.get("format", "unknown")
            by_format[fmt] = by_format.get(fmt, 0) + 1

            ptype = p.get("plugin_type", "unknown")
            by_type[ptype] = by_type.get(ptype, 0) + 1

            cat = p.get("category", "unknown")
            by_category[cat] = by_category.get(cat, 0) + 1

            if p.get("is_favorite"):
                favorites_count += 1

        return {
            "total_plugins": len(plugins),
            "by_format": by_format,
            "by_type": by_type,
            "by_category": by_category,
            "favorites": favorites_count,
            "blacklisted": blacklisted_count,
            "last_scan": data.get("last_scan"),
        }

    # =========================================================================
    # Scan Path Management
    # =========================================================================

    def get_scan_paths(self) -> List[str]:
        """Get configured plugin scan paths."""
        data = self._load_data(self.plugins_file)
        return data.get("scan_paths", [])

    def add_scan_path(self, path: str) -> bool:
        """Add a plugin scan path."""
        data = self._load_data(self.plugins_file)
        paths = data.get("scan_paths", [])
        if path not in paths:
            paths.append(path)
            data["scan_paths"] = paths
            self._save_data(data, self.plugins_file)
            return True
        return False

    def remove_scan_path(self, path: str) -> bool:
        """Remove a plugin scan path."""
        data = self._load_data(self.plugins_file)
        paths = data.get("scan_paths", [])
        if path in paths:
            paths.remove(path)
            data["scan_paths"] = paths
            self._save_data(data, self.plugins_file)
            return True
        return False

    def update_last_scan(self):
        """Update the last scan timestamp."""
        data = self._load_data(self.plugins_file)
        data["last_scan"] = datetime.now().isoformat()
        self._save_data(data, self.plugins_file)

    # =========================================================================
    # Blacklist Management
    # =========================================================================

    def is_blacklisted(self, plugin_id: str) -> bool:
        """Check if a plugin is blacklisted."""
        data = self._load_data(self.blacklist_file)
        return plugin_id in data.get("blacklisted", [])

    def blacklist_plugin(self, plugin_id: str, reason: str = "") -> bool:
        """Add a plugin to the blacklist."""
        data = self._load_data(self.blacklist_file)
        blacklisted = data.get("blacklisted", [])
        reasons = data.get("reasons", {})

        if plugin_id not in blacklisted:
            blacklisted.append(plugin_id)
            data["blacklisted"] = blacklisted

        if reason:
            reasons[plugin_id] = reason
            data["reasons"] = reasons

        self._save_data(data, self.blacklist_file)

        # Update plugin status
        plugin_data = self._load_data(self.plugins_file)
        if plugin_id in plugin_data.get("plugins", {}):
            plugin_data["plugins"][plugin_id]["status"] = PluginStatus.BLACKLISTED.value
            self._save_data(plugin_data, self.plugins_file)

        return True

    def unblacklist_plugin(self, plugin_id: str) -> bool:
        """Remove a plugin from the blacklist."""
        data = self._load_data(self.blacklist_file)
        blacklisted = data.get("blacklisted", [])

        if plugin_id in blacklisted:
            blacklisted.remove(plugin_id)
            data["blacklisted"] = blacklisted

            if plugin_id in data.get("reasons", {}):
                del data["reasons"][plugin_id]

            self._save_data(data, self.blacklist_file)

            # Update plugin status
            plugin_data = self._load_data(self.plugins_file)
            if plugin_id in plugin_data.get("plugins", {}):
                plugin_data["plugins"][plugin_id]["status"] = PluginStatus.VALID.value
                self._save_data(plugin_data, self.plugins_file)

            return True
        return False

    def get_blacklist(self) -> List[Dict[str, Any]]:
        """Get all blacklisted plugins with reasons."""
        data = self._load_data(self.blacklist_file)
        blacklisted = data.get("blacklisted", [])
        reasons = data.get("reasons", {})

        return [
            {"plugin_id": pid, "reason": reasons.get(pid, "")}
            for pid in blacklisted
        ]

    # =========================================================================
    # Preset Management
    # =========================================================================

    def save_preset(self, preset: PluginPreset) -> PluginPreset:
        """Save a plugin preset."""
        data = self._load_data(self.presets_file)

        # Add to presets
        data["presets"][preset.id] = preset.to_dict()

        # Index by plugin
        by_plugin = data.get("by_plugin", {})
        plugin_presets = by_plugin.get(preset.plugin_id, [])
        if preset.id not in plugin_presets:
            plugin_presets.append(preset.id)
        by_plugin[preset.plugin_id] = plugin_presets
        data["by_plugin"] = by_plugin

        self._save_data(data, self.presets_file)
        return preset

    def get_preset(self, preset_id: str) -> Optional[PluginPreset]:
        """Get a preset by ID."""
        data = self._load_data(self.presets_file)
        preset_data = data.get("presets", {}).get(preset_id)
        if preset_data:
            return PluginPreset.from_dict(preset_data)
        return None

    def list_presets(
        self,
        plugin_id: Optional[str] = None,
        favorites_only: bool = False,
        factory_only: bool = False,
    ) -> List[PluginPreset]:
        """List presets with optional filters."""
        data = self._load_data(self.presets_file)
        presets = []

        # Filter by plugin if specified
        if plugin_id:
            preset_ids = data.get("by_plugin", {}).get(plugin_id, [])
            for pid in preset_ids:
                preset_data = data.get("presets", {}).get(pid)
                if preset_data:
                    preset = PluginPreset.from_dict(preset_data)
                    if favorites_only and not preset.is_favorite:
                        continue
                    if factory_only and not preset.is_factory:
                        continue
                    presets.append(preset)
        else:
            for preset_data in data.get("presets", {}).values():
                preset = PluginPreset.from_dict(preset_data)
                if favorites_only and not preset.is_favorite:
                    continue
                if factory_only and not preset.is_factory:
                    continue
                presets.append(preset)

        return presets

    def delete_preset(self, preset_id: str) -> bool:
        """Delete a preset."""
        data = self._load_data(self.presets_file)

        if preset_id in data.get("presets", {}):
            preset_data = data["presets"][preset_id]
            plugin_id = preset_data.get("plugin_id")

            # Remove from presets
            del data["presets"][preset_id]

            # Remove from index
            if plugin_id and plugin_id in data.get("by_plugin", {}):
                presets = data["by_plugin"][plugin_id]
                if preset_id in presets:
                    presets.remove(preset_id)
                    data["by_plugin"][plugin_id] = presets

            self._save_data(data, self.presets_file)
            return True
        return False

    # =========================================================================
    # Plugin Chain Management
    # =========================================================================

    def save_chain(self, chain: PluginChain) -> PluginChain:
        """Save a plugin chain preset."""
        data = self._load_data(self.chains_file)
        chain.updated_at = datetime.now().isoformat()
        data["chains"][chain.id] = chain.to_dict()
        self._save_data(data, self.chains_file)
        return chain

    def get_chain(self, chain_id: str) -> Optional[PluginChain]:
        """Get a plugin chain by ID."""
        data = self._load_data(self.chains_file)
        chain_data = data.get("chains", {}).get(chain_id)
        if chain_data:
            return PluginChain.from_dict(chain_data)
        return None

    def list_chains(self, favorites_only: bool = False) -> List[PluginChain]:
        """List plugin chains."""
        data = self._load_data(self.chains_file)
        chains = []

        for chain_data in data.get("chains", {}).values():
            chain = PluginChain.from_dict(chain_data)
            if favorites_only and not chain.is_favorite:
                continue
            chains.append(chain)

        return chains

    def delete_chain(self, chain_id: str) -> bool:
        """Delete a plugin chain."""
        data = self._load_data(self.chains_file)
        if chain_id in data.get("chains", {}):
            del data["chains"][chain_id]
            self._save_data(data, self.chains_file)
            return True
        return False

    # =========================================================================
    # Instance Tracking
    # =========================================================================

    def register_instance(self, instance: PluginInstance) -> PluginInstance:
        """Register a new plugin instance."""
        data = self._load_data(self.instances_file)
        data["instances"][instance.id] = instance.to_dict()
        self._save_data(data, self.instances_file)

        # Mark plugin as used
        self.mark_used(instance.plugin_id)

        return instance

    def get_instance(self, instance_id: str) -> Optional[PluginInstance]:
        """Get an instance by ID."""
        data = self._load_data(self.instances_file)
        instance_data = data.get("instances", {}).get(instance_id)
        if instance_data:
            return PluginInstance.from_dict(instance_data)
        return None

    def update_instance(self, instance: PluginInstance) -> PluginInstance:
        """Update an instance."""
        data = self._load_data(self.instances_file)
        data["instances"][instance.id] = instance.to_dict()
        self._save_data(data, self.instances_file)
        return instance

    def release_instance(self, instance_id: str) -> bool:
        """Release/remove an instance."""
        data = self._load_data(self.instances_file)
        if instance_id in data.get("instances", {}):
            del data["instances"][instance_id]
            self._save_data(data, self.instances_file)
            return True
        return False

    def list_instances(self) -> List[PluginInstance]:
        """List all active instances."""
        data = self._load_data(self.instances_file)
        return [
            PluginInstance.from_dict(inst_data)
            for inst_data in data.get("instances", {}).values()
        ]

    # =========================================================================
    # Instrument Rack Management
    # =========================================================================

    def save_rack(self, rack: InstrumentRack) -> InstrumentRack:
        """Save an instrument rack."""
        data = self._load_data(self.racks_file)
        rack.updated_at = datetime.now().isoformat()
        data["racks"][rack.id] = rack.to_dict()
        self._save_data(data, self.racks_file)
        return rack

    def get_rack(self, rack_id: str) -> Optional[InstrumentRack]:
        """Get an instrument rack by ID."""
        data = self._load_data(self.racks_file)
        rack_data = data.get("racks", {}).get(rack_id)
        if rack_data:
            return InstrumentRack.from_dict(rack_data)
        return None

    def list_racks(self) -> List[InstrumentRack]:
        """List all instrument racks."""
        data = self._load_data(self.racks_file)
        return [
            InstrumentRack.from_dict(rack_data)
            for rack_data in data.get("racks", {}).values()
        ]

    def delete_rack(self, rack_id: str) -> bool:
        """Delete an instrument rack."""
        data = self._load_data(self.racks_file)
        if rack_id in data.get("racks", {}):
            del data["racks"][rack_id]
            self._save_data(data, self.racks_file)
            return True
        return False
