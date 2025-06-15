"""
Plugin Manager for SilentCodingLegend AI Agent
Handles plugin loading, registration, lifecycle management, and hot-swapping
"""

import os
import sys
import json
import importlib
import importlib.util
from typing import Dict, List, Any, Optional, Type
from pathlib import Path
import asyncio
import aiofiles
from datetime import datetime
import zipfile
import tempfile
import shutil
import logging

from .base_plugin import BasePlugin, PluginMetadata, PluginType
from .tool_registry import ToolRegistry, tool_registry

# Use standard logging to avoid circular imports
logger = logging.getLogger(__name__)

class PluginManager:
    """Manages plugin lifecycle, loading, and hot-swapping"""
    
    def __init__(self, plugins_dir: str = "plugins", 
                 marketplace_dir: str = "marketplace"):
        self.plugins_dir = Path(plugins_dir)
        self.marketplace_dir = Path(marketplace_dir)
        self.tool_registry = tool_registry
        
        # Plugin state
        self._loaded_plugins: Dict[str, BasePlugin] = {}
        self._plugin_configs: Dict[str, Dict[str, Any]] = {}
        self._plugin_metadata: Dict[str, PluginMetadata] = {}
        
        # Event system
        self._event_handlers: Dict[str, List[callable]] = {}
        
        # Ensure directories exist
        self.plugins_dir.mkdir(exist_ok=True)
        self.marketplace_dir.mkdir(exist_ok=True)
        
        logger.info(f"PluginManager initialized with plugins_dir: {self.plugins_dir}")
    
    async def initialize(self, agent=None) -> None:
        """Initialize the plugin manager and load all plugins"""
        self.agent = agent
        
        # Create default directories structure
        await self._ensure_plugin_structure()
        
        # Load plugin configurations
        await self._load_plugin_configs()
        
        # Discover and load plugins
        await self.discover_plugins()
        await self.load_all_plugins()
        
        logger.info(f"Plugin manager initialized with {len(self._loaded_plugins)} plugins")
    
    async def _ensure_plugin_structure(self) -> None:
        """Ensure proper plugin directory structure exists"""
        subdirs = ["core", "community", "custom", "disabled"]
        
        for subdir in subdirs:
            (self.plugins_dir / subdir).mkdir(exist_ok=True)
            
        # Create marketplace structure
        (self.marketplace_dir / "downloaded").mkdir(exist_ok=True)
        (self.marketplace_dir / "cache").mkdir(exist_ok=True)
    
    async def _load_plugin_configs(self) -> None:
        """Load plugin configurations from config files"""
        config_file = self.plugins_dir / "config.json"
        
        if config_file.exists():
            try:
                async with aiofiles.open(config_file, 'r') as f:
                    content = await f.read()
                    self._plugin_configs = json.loads(content)
            except Exception as e:
                logger.error(f"Failed to load plugin configs: {e}")
                self._plugin_configs = {}
        else:
            # Create default config
            self._plugin_configs = {
                "auto_load": True,
                "enable_hot_reload": True,
                "plugins": {}
            }
            await self._save_plugin_configs()
    
    async def _save_plugin_configs(self) -> None:
        """Save plugin configurations to file"""
        config_file = self.plugins_dir / "config.json"
        
        try:
            async with aiofiles.open(config_file, 'w') as f:
                await f.write(json.dumps(self._plugin_configs, indent=2))
        except Exception as e:
            logger.error(f"Failed to save plugin configs: {e}")
    
    async def discover_plugins(self) -> List[PluginMetadata]:
        """Discover all available plugins in the plugins directory"""
        discovered = []
        
        for plugin_dir in self.plugins_dir.rglob("*"):
            if not plugin_dir.is_dir() or plugin_dir.name.startswith('.'):
                continue
                
            # Look for metadata.json metadata file
            metadata_file = plugin_dir / "metadata.json"
            if metadata_file.exists():
                try:
                    async with aiofiles.open(metadata_file, 'r') as f:
                        content = await f.read()
                        metadata_dict = json.loads(content)
                        metadata = PluginMetadata.from_dict(metadata_dict)
                        
                        self._plugin_metadata[metadata.name] = metadata
                        discovered.append(metadata)
                        
                        logger.info(f"Discovered plugin: {metadata.name} v{metadata.version}")
                        
                except Exception as e:
                    logger.error(f"Failed to load plugin metadata from {metadata_file}: {e}")
        
        return discovered
    
    async def load_plugin(self, plugin_name: str) -> bool:
        """Load a specific plugin by name"""
        if plugin_name in self._loaded_plugins:
            logger.warning(f"Plugin {plugin_name} already loaded")
            return True
        
        metadata = self._plugin_metadata.get(plugin_name)
        if not metadata:
            logger.error(f"Plugin metadata not found for {plugin_name}")
            return False
        
        try:
            # Find plugin directory
            plugin_dir = None
            for dir_path in self.plugins_dir.rglob("*"):
                if (dir_path / "metadata.json").exists():
                    async with aiofiles.open(dir_path / "metadata.json", 'r') as f:
                        content = await f.read()
                        meta_dict = json.loads(content)
                        if meta_dict.get("name") == plugin_name:
                            plugin_dir = dir_path
                            break
            
            if not plugin_dir:
                logger.error(f"Plugin directory not found for {plugin_name}")
                return False
            
            # Load plugin module
            plugin_module = await self._load_plugin_module(plugin_dir, plugin_name)
            if not plugin_module:
                return False
            
            # Get plugin class
            plugin_class = getattr(plugin_module, metadata.name + "Plugin", None)
            if not plugin_class:
                # Try common naming conventions
                for attr_name in dir(plugin_module):
                    attr = getattr(plugin_module, attr_name)
                    if (isinstance(attr, type) and 
                        issubclass(attr, BasePlugin) and 
                        attr != BasePlugin):
                        plugin_class = attr
                        break
            
            if not plugin_class:
                logger.error(f"Plugin class not found in {plugin_name}")
                return False
            
            # Instantiate plugin
            plugin_instance = plugin_class()
            plugin_instance.agent = self.agent
            
            # Initialize plugin
            if await plugin_instance.initialize():
                self._loaded_plugins[plugin_name] = plugin_instance
                
                # Register plugin tools
                tools = plugin_instance.get_tools()
                if isinstance(tools, list):
                    for tool in tools:
                        self.tool_registry.register_tool(tool)
                elif isinstance(tools, dict):
                    for tool_name, tool in tools.items():
                        self.tool_registry.register_tool(tool)
                
                # Emit plugin loaded event
                await self._emit_event("plugin_loaded", plugin_name, plugin_instance)
                
                logger.info(f"Successfully loaded plugin: {plugin_name}")
                return True
            else:
                logger.error(f"Plugin initialization failed: {plugin_name}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to load plugin {plugin_name}: {e}")
            return False
    
    async def _load_plugin_module(self, plugin_dir: Path, plugin_name: str):
        """Load plugin module from directory"""
        # Look for main plugin file (prioritize plugin.py)
        possible_files = [
            plugin_dir / "plugin.py",
            plugin_dir / f"{plugin_name}.py",
            plugin_dir / "main.py",
            plugin_dir / "__init__.py"
        ]
        
        plugin_file = None
        for file_path in possible_files:
            if file_path.exists():
                plugin_file = file_path
                break
        
        if not plugin_file:
            logger.error(f"Plugin main file not found in {plugin_dir}")
            return None
        
        # Load module
        spec = importlib.util.spec_from_file_location(plugin_name, plugin_file)
        if not spec or not spec.loader:
            logger.error(f"Failed to create module spec for {plugin_name}")
            return None
        
        module = importlib.util.module_from_spec(spec)
        sys.modules[plugin_name] = module
        
        try:
            spec.loader.exec_module(module)
            return module
        except Exception as e:
            logger.error(f"Failed to execute plugin module {plugin_name}: {e}")
            if plugin_name in sys.modules:
                del sys.modules[plugin_name]
            return None
    
    async def unload_plugin(self, plugin_name: str) -> bool:
        """Unload a specific plugin"""
        if plugin_name not in self._loaded_plugins:
            logger.warning(f"Plugin {plugin_name} not loaded")
            return True
        
        try:
            plugin = self._loaded_plugins[plugin_name]
            
            # Cleanup plugin
            await plugin.cleanup()
            
            # Unregister tools
            self.tool_registry.unregister_plugin_tools(plugin_name)
            
            # Remove from loaded plugins
            del self._loaded_plugins[plugin_name]
            
            # Remove from sys.modules if present
            if plugin_name in sys.modules:
                del sys.modules[plugin_name]
            
            # Emit plugin unloaded event
            await self._emit_event("plugin_unloaded", plugin_name)
            
            logger.info(f"Successfully unloaded plugin: {plugin_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to unload plugin {plugin_name}: {e}")
            return False
    
    async def reload_plugin(self, plugin_name: str) -> bool:
        """Hot-reload a plugin (unload and load again)"""
        logger.info(f"Reloading plugin: {plugin_name}")
        
        if await self.unload_plugin(plugin_name):
            # Re-discover metadata
            await self.discover_plugins()
            return await self.load_plugin(plugin_name)
        
        return False
    
    async def load_all_plugins(self) -> None:
        """Load all discovered plugins"""
        for plugin_name in self._plugin_metadata.keys():
            # Check if plugin is enabled in config
            plugin_config = self._plugin_configs.get("plugins", {}).get(plugin_name, {})
            if plugin_config.get("enabled", True):
                await self.load_plugin(plugin_name)
    
    async def install_plugin(self, plugin_path: str) -> bool:
        """Install a plugin from a file or URL"""
        try:
            plugin_path = Path(plugin_path)
            
            if plugin_path.suffix == '.zip':
                return await self._install_from_zip(plugin_path)
            elif plugin_path.is_dir():
                return await self._install_from_directory(plugin_path)
            else:
                logger.error(f"Unsupported plugin format: {plugin_path}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to install plugin from {plugin_path}: {e}")
            return False
    
    async def _install_from_zip(self, zip_path: Path) -> bool:
        """Install plugin from ZIP file"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Extract ZIP
            with zipfile.ZipFile(zip_path, 'r') as zip_file:
                zip_file.extractall(temp_dir)
            
            # Find plugin.json
            for root, dirs, files in os.walk(temp_dir):
                if "plugin.json" in files:
                    plugin_dir = Path(root)
                    return await self._install_from_directory(plugin_dir)
            
            logger.error("plugin.json not found in ZIP file")
            return False
    
    async def _install_from_directory(self, source_dir: Path) -> bool:
        """Install plugin from directory"""
        metadata_file = source_dir / "plugin.json"
        if not metadata_file.exists():
            logger.error("plugin.json not found in source directory")
            return False
        
        # Load metadata
        async with aiofiles.open(metadata_file, 'r') as f:
            content = await f.read()
            metadata_dict = json.loads(content)
            metadata = PluginMetadata.from_dict(metadata_dict)
        
        # Determine installation directory
        install_dir = self.plugins_dir / "custom" / metadata.name
        
        # Copy plugin files
        if install_dir.exists():
            shutil.rmtree(install_dir)
        
        shutil.copytree(source_dir, install_dir)
        
        logger.info(f"Installed plugin {metadata.name} to {install_dir}")
        
        # Re-discover and load
        await self.discover_plugins()
        return await self.load_plugin(metadata.name)
    
    async def uninstall_plugin(self, plugin_name: str) -> bool:
        """Uninstall a plugin"""
        try:
            # Unload if loaded
            if plugin_name in self._loaded_plugins:
                await self.unload_plugin(plugin_name)
            
            # Find and remove plugin directory
            for plugin_dir in self.plugins_dir.rglob("*"):
                if (plugin_dir / "plugin.json").exists():
                    async with aiofiles.open(plugin_dir / "plugin.json", 'r') as f:
                        content = await f.read()
                        meta_dict = json.loads(content)
                        if meta_dict.get("name") == plugin_name:
                            shutil.rmtree(plugin_dir)
                            logger.info(f"Uninstalled plugin: {plugin_name}")
                            break
            
            # Remove from metadata
            if plugin_name in self._plugin_metadata:
                del self._plugin_metadata[plugin_name]
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to uninstall plugin {plugin_name}: {e}")
            return False
    
    def get_loaded_plugins(self) -> Dict[str, BasePlugin]:
        """Get all loaded plugins"""
        return self._loaded_plugins.copy()
    
    def get_plugin(self, plugin_name: str) -> Optional[BasePlugin]:
        """Get a specific loaded plugin"""
        return self._loaded_plugins.get(plugin_name)
    
    def get_plugin_metadata(self, plugin_name: str) -> Optional[PluginMetadata]:
        """Get metadata for a plugin"""
        return self._plugin_metadata.get(plugin_name)
    
    def list_available_plugins(self) -> List[PluginMetadata]:
        """List all available (discovered) plugins"""
        return list(self._plugin_metadata.values())
    
    def get_plugin_status(self) -> Dict[str, Any]:
        """Get overall plugin system status"""
        return {
            "total_discovered": len(self._plugin_metadata),
            "total_loaded": len(self._loaded_plugins),
            "loaded_plugins": [p.get_status() for p in self._loaded_plugins.values()],
            "tool_registry_stats": self.tool_registry.get_stats()
        }
    
    async def enable_plugin(self, plugin_name: str) -> bool:
        """Enable a plugin"""
        if plugin_name not in self._plugin_configs.get("plugins", {}):
            self._plugin_configs.setdefault("plugins", {})[plugin_name] = {}
        
        self._plugin_configs["plugins"][plugin_name]["enabled"] = True
        await self._save_plugin_configs()
        
        # Load if not already loaded
        if plugin_name not in self._loaded_plugins:
            return await self.load_plugin(plugin_name)
        
        return True
    
    async def disable_plugin(self, plugin_name: str) -> bool:
        """Disable a plugin"""
        if plugin_name not in self._plugin_configs.get("plugins", {}):
            self._plugin_configs.setdefault("plugins", {})[plugin_name] = {}
        
        self._plugin_configs["plugins"][plugin_name]["enabled"] = False
        await self._save_plugin_configs()
        
        # Unload if loaded
        if plugin_name in self._loaded_plugins:
            return await self.unload_plugin(plugin_name)
        
        return True
    
    def register_event_handler(self, event: str, handler: callable) -> None:
        """Register an event handler"""
        if event not in self._event_handlers:
            self._event_handlers[event] = []
        self._event_handlers[event].append(handler)
    
    async def _emit_event(self, event: str, *args, **kwargs) -> None:
        """Emit an event to all registered handlers"""
        if event in self._event_handlers:
            for handler in self._event_handlers[event]:
                try:
                    await handler(*args, **kwargs)
                except Exception as e:
                    logger.error(f"Event handler error for {event}: {e}")

# Global plugin manager instance
plugin_manager = PluginManager()
