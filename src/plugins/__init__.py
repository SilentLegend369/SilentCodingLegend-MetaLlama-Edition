"""
Plugin System for SilentCodingLegend AI Agent
Extensible plugin architecture with tool calling capabilities
"""

from .plugin_manager import PluginManager
from .base_plugin import BasePlugin, PluginMetadata, PluginType
from .tool_registry import ToolRegistry, Tool, ToolParameter
from .marketplace import PluginMarketplace

__all__ = [
    'PluginManager',
    'BasePlugin', 
    'PluginMetadata',
    'PluginType',
    'ToolRegistry',
    'Tool',
    'ToolParameter',
    'PluginMarketplace'
]
