"""
Tool Registry for Plugin System
Manages tool registration, discovery, and execution with Llama tool calling support
"""

from typing import Dict, List, Any, Optional, Callable, Union
from dataclasses import dataclass, field
from enum import Enum
import json
import inspect
import asyncio
from datetime import datetime

class ParameterType(Enum):
    """Supported parameter types for tools"""
    STRING = "string"
    INTEGER = "integer" 
    NUMBER = "number"
    BOOLEAN = "boolean"
    ARRAY = "array"
    OBJECT = "object"

@dataclass
class ToolParameter:
    """Tool parameter definition"""
    name: str
    type: ParameterType
    description: str
    required: bool = False
    default: Any = None
    enum: Optional[List[Any]] = None
    items: Optional[Dict[str, Any]] = None  # For array types
    properties: Optional[Dict[str, Any]] = None  # For object types
    
    def to_llama_schema(self) -> Dict[str, Any]:
        """Convert to Llama tool calling parameter schema"""
        schema = {
            "type": self.type.value,
            "description": self.description
        }
        
        if self.enum:
            schema["enum"] = self.enum
            
        if self.items and self.type == ParameterType.ARRAY:
            schema["items"] = self.items
            
        if self.properties and self.type == ParameterType.OBJECT:
            schema["properties"] = self.properties
            
        return schema

@dataclass 
class Tool:
    """Tool definition with execution capability"""
    name: str
    description: str
    parameters: List[ToolParameter]
    function: Callable
    plugin_name: str
    category: str = "general"
    examples: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    
    def to_llama_schema(self) -> Dict[str, Any]:
        """Convert tool to Llama tool calling schema format"""
        required_params = [p.name for p in self.parameters if p.required]
        
        properties = {}
        for param in self.parameters:
            properties[param.name] = param.to_llama_schema()
        
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": properties,
                    "required": required_params
                }
            }
        }
    
    async def execute(self, **kwargs) -> Any:
        """Execute the tool with given parameters"""
        try:
            # Validate required parameters
            for param in self.parameters:
                if param.required and param.name not in kwargs:
                    raise ValueError(f"Required parameter '{param.name}' missing")
                    
                # Set default values
                if param.name not in kwargs and param.default is not None:
                    kwargs[param.name] = param.default
            
            # Execute function (handle both sync and async)
            if asyncio.iscoroutinefunction(self.function):
                return await self.function(**kwargs)
            else:
                return self.function(**kwargs)
                
        except Exception as e:
            raise RuntimeError(f"Tool execution failed: {str(e)}")

class ToolRegistry:
    """Central registry for all tools across plugins"""
    
    def __init__(self):
        self._tools: Dict[str, Tool] = {}
        self._categories: Dict[str, List[str]] = {}
        self._plugin_tools: Dict[str, List[str]] = {}
        
    def register_tool(self, tool: Tool) -> None:
        """Register a tool in the registry"""
        if tool.name in self._tools:
            raise ValueError(f"Tool '{tool.name}' already registered")
            
        self._tools[tool.name] = tool
        
        # Update category index
        if tool.category not in self._categories:
            self._categories[tool.category] = []
        self._categories[tool.category].append(tool.name)
        
        # Update plugin index
        if tool.plugin_name not in self._plugin_tools:
            self._plugin_tools[tool.plugin_name] = []
        self._plugin_tools[tool.plugin_name].append(tool.name)
        
        print(f"Registered tool '{tool.name}' from plugin '{tool.plugin_name}'")
    
    def unregister_tool(self, tool_name: str) -> None:
        """Unregister a tool from the registry"""
        if tool_name not in self._tools:
            return
            
        tool = self._tools[tool_name]
        
        # Remove from indices
        if tool.category in self._categories:
            self._categories[tool.category].remove(tool_name)
            if not self._categories[tool.category]:
                del self._categories[tool.category]
                
        if tool.plugin_name in self._plugin_tools:
            self._plugin_tools[tool.plugin_name].remove(tool_name)
            if not self._plugin_tools[tool.plugin_name]:
                del self._plugin_tools[tool.plugin_name]
        
        del self._tools[tool_name]
        print(f"Unregistered tool '{tool_name}'")
    
    def unregister_plugin_tools(self, plugin_name: str) -> None:
        """Unregister all tools from a specific plugin"""
        if plugin_name in self._plugin_tools:
            tools_to_remove = self._plugin_tools[plugin_name].copy()
            for tool_name in tools_to_remove:
                self.unregister_tool(tool_name)
    
    def get_tool(self, tool_name: str) -> Optional[Tool]:
        """Get a specific tool by name"""
        return self._tools.get(tool_name)
    
    def get_all_tools(self) -> Dict[str, Tool]:
        """Get all registered tools"""
        return self._tools.copy()
    
    def get_tools_by_category(self, category: str) -> List[Tool]:
        """Get all tools in a specific category"""
        tool_names = self._categories.get(category, [])
        return [self._tools[name] for name in tool_names]
    
    def get_tools_by_plugin(self, plugin_name: str) -> List[Tool]:
        """Get all tools from a specific plugin"""
        tool_names = self._plugin_tools.get(plugin_name, [])
        return [self._tools[name] for name in tool_names]
    
    def search_tools(self, query: str) -> List[Tool]:
        """Search tools by name or description"""
        query = query.lower()
        results = []
        
        for tool in self._tools.values():
            if (query in tool.name.lower() or 
                query in tool.description.lower() or
                query in tool.category.lower()):
                results.append(tool)
                
        return results
    
    def get_categories(self) -> List[str]:
        """Get all available tool categories"""
        return list(self._categories.keys())
    
    def get_llama_tools_schema(self, categories: Optional[List[str]] = None,
                              plugins: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """Get tools in Llama tool calling schema format"""
        tools_to_include = []
        
        if categories:
            for category in categories:
                tools_to_include.extend(self.get_tools_by_category(category))
        elif plugins:
            for plugin in plugins:
                tools_to_include.extend(self.get_tools_by_plugin(plugin))
        else:
            tools_to_include = list(self._tools.values())
        
        return [tool.to_llama_schema() for tool in tools_to_include]
    
    async def execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Any:
        """Execute a tool with given parameters"""
        tool = self.get_tool(tool_name)
        if not tool:
            raise ValueError(f"Tool '{tool_name}' not found")
        
        return await tool.execute(**parameters)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get registry statistics"""
        return {
            "total_tools": len(self._tools),
            "total_categories": len(self._categories),
            "total_plugins": len(self._plugin_tools),
            "categories": {cat: len(tools) for cat, tools in self._categories.items()},
            "plugins": {plugin: len(tools) for plugin, tools in self._plugin_tools.items()}
        }
    
    def export_tools_schema(self, filepath: str) -> None:
        """Export all tools schema to JSON file"""
        schema = {
            "tools": self.get_llama_tools_schema(),
            "metadata": {
                "total_tools": len(self._tools),
                "categories": list(self._categories.keys()),
                "plugins": list(self._plugin_tools.keys()),
                "exported_at": datetime.now().isoformat()
            }
        }
        
        with open(filepath, 'w') as f:
            json.dump(schema, f, indent=2)
        
        print(f"Exported {len(self._tools)} tools schema to {filepath}")

# Global tool registry instance
tool_registry = ToolRegistry()
