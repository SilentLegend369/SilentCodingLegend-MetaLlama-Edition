"""
Base Plugin Architecture for SilentCodingLegend AI Agent
Defines the foundation for all plugins with tool calling support
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
import json
from datetime import datetime

class PluginType(Enum):
    """Types of plugins supported by the system"""
    TOOL = "tool"                    # Function/tool plugins
    INTERFACE = "interface"          # UI/interaction plugins  
    PROCESSOR = "processor"          # Data processing plugins
    INTEGRATION = "integration"      # External service plugins
    ANALYZER = "analyzer"           # Code/text analysis plugins
    GENERATOR = "generator"         # Content generation plugins

@dataclass
class PluginMetadata:
    """Metadata for plugin registration and discovery"""
    name: str
    version: str
    description: str
    author: str
    plugin_type: PluginType
    dependencies: List[str] = field(default_factory=list)
    entry_point: str = "plugin.py"
    min_agent_version: str = "1.0.0"
    max_agent_version: str = "999.0.0"
    tags: List[str] = field(default_factory=list)
    license: str = "MIT"
    homepage: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metadata to dictionary"""
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "author": self.author,
            "plugin_type": self.plugin_type.value,
            "dependencies": self.dependencies,
            "entry_point": self.entry_point,
            "min_agent_version": self.min_agent_version,
            "max_agent_version": self.max_agent_version,
            "tags": self.tags,
            "license": self.license,
            "homepage": self.homepage,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PluginMetadata':
        """Create metadata from dictionary"""
        return cls(
            name=data["name"],
            version=data["version"], 
            description=data["description"],
            author=data["author"],
            plugin_type=PluginType(data["plugin_type"]),
            dependencies=data.get("dependencies", []),
            entry_point=data.get("entry_point", "plugin.py"),
            min_agent_version=data.get("min_agent_version", "1.0.0"),
            max_agent_version=data.get("max_agent_version", "999.0.0"),
            tags=data.get("tags", []),
            license=data.get("license", "MIT"),
            homepage=data.get("homepage", ""),
            created_at=datetime.fromisoformat(data.get("created_at", datetime.now().isoformat())),
            updated_at=datetime.fromisoformat(data.get("updated_at", datetime.now().isoformat()))
        )

class BasePlugin(ABC):
    """Base class for all plugins"""
    
    def __init__(self, metadata: PluginMetadata):
        self.metadata = metadata
        self.enabled = True
        self.agent = None  # Will be set by PluginManager
        self._tools = {}   # Registered tools
        self._hooks = {}   # Event hooks
        
    @abstractmethod
    async def initialize(self) -> bool:
        """Initialize the plugin. Return True if successful."""
        pass
    
    @abstractmethod
    async def cleanup(self) -> None:
        """Cleanup plugin resources"""
        pass
    
    def is_compatible(self, agent_version: str) -> bool:
        """Check if plugin is compatible with agent version"""
        # Simple version comparison - in production, use semantic versioning
        return (self.metadata.min_agent_version <= agent_version <= 
                self.metadata.max_agent_version)
    
    def register_tool(self, tool_name: str, tool_func: Callable, 
                     description: str, parameters: Dict[str, Any]) -> None:
        """Register a tool with the plugin"""
        from .tool_registry import Tool, ToolParameter, ParameterType
        
        # Convert parameters to ToolParameter objects
        tool_params = []
        for param_name, param_info in parameters.items():
            # Convert string type to ParameterType enum
            type_str = param_info.get("type", "string")
            if isinstance(type_str, str):
                # Map string types to ParameterType enums
                type_mapping = {
                    "string": ParameterType.STRING,
                    "integer": ParameterType.INTEGER,
                    "number": ParameterType.NUMBER,
                    "boolean": ParameterType.BOOLEAN,
                    "array": ParameterType.ARRAY,
                    "object": ParameterType.OBJECT
                }
                param_type = type_mapping.get(type_str.lower(), ParameterType.STRING)
            else:
                param_type = type_str  # Already a ParameterType enum
                
            tool_params.append(ToolParameter(
                name=param_name,
                type=param_type,
                description=param_info.get("description", ""),
                required=param_info.get("required", False),
                default=param_info.get("default")
            ))
        
        tool = Tool(
            name=tool_name,
            description=description,
            parameters=tool_params,
            function=tool_func,
            plugin_name=self.metadata.name
        )
        
        self._tools[tool_name] = tool
    
    def register_hook(self, event: str, callback: Callable) -> None:
        """Register an event hook"""
        if event not in self._hooks:
            self._hooks[event] = []
        self._hooks[event].append(callback)
    
    async def execute_hooks(self, event: str, *args, **kwargs) -> List[Any]:
        """Execute all hooks for an event"""
        results = []
        if event in self._hooks:
            for callback in self._hooks[event]:
                try:
                    result = await callback(*args, **kwargs)
                    results.append(result)
                except Exception as e:
                    print(f"Hook execution error in {self.metadata.name}: {e}")
        return results
    
    def get_tools(self) -> Dict[str, Any]:
        """Get all tools registered by this plugin"""
        return self._tools.copy()
    
    def enable(self) -> None:
        """Enable the plugin"""
        self.enabled = True
    
    def disable(self) -> None:
        """Disable the plugin"""
        self.enabled = False
    
    def get_status(self) -> Dict[str, Any]:
        """Get plugin status information"""
        return {
            "name": self.metadata.name,
            "version": self.metadata.version,
            "enabled": self.enabled,
            "tools_count": len(self._tools),
            "hooks_count": sum(len(hooks) for hooks in self._hooks.values()),
            "type": self.metadata.plugin_type.value
        }

class ToolPlugin(BasePlugin):
    """Specialized base class for tool plugins"""
    
    def __init__(self, metadata: PluginMetadata):
        super().__init__(metadata)
        if metadata.plugin_type != PluginType.TOOL:
            raise ValueError("ToolPlugin must have plugin_type=TOOL")
    
    @abstractmethod
    async def get_available_tools(self) -> List[Dict[str, Any]]:
        """Get list of available tools in Llama tool calling format"""
        pass

class IntegrationPlugin(BasePlugin):
    """Specialized base class for integration plugins"""
    
    def __init__(self, metadata: PluginMetadata):
        super().__init__(metadata)
        if metadata.plugin_type != PluginType.INTEGRATION:
            raise ValueError("IntegrationPlugin must have plugin_type=INTEGRATION")
    
    @abstractmethod
    async def connect(self, config: Dict[str, Any]) -> bool:
        """Connect to external service"""
        pass
    
    @abstractmethod
    async def disconnect(self) -> None:
        """Disconnect from external service"""
        pass

class ProcessorPlugin(BasePlugin):
    """Specialized base class for processor plugins"""
    
    def __init__(self, metadata: PluginMetadata):
        super().__init__(metadata)
        if metadata.plugin_type != PluginType.PROCESSOR:
            raise ValueError("ProcessorPlugin must have plugin_type=PROCESSOR")
    
    @abstractmethod
    async def process(self, data: Any) -> Any:
        """Process data"""
        pass
