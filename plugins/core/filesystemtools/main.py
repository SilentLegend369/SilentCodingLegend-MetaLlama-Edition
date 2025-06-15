"""
FileSystem Tools Plugin for SilentCodingLegend AI Agent
"""

import os
import aiofiles
from pathlib import Path
from typing import Dict, List, Any
from src.plugins.base_plugin import ToolPlugin, PluginMetadata, PluginType

class FileSystemToolsPlugin(ToolPlugin):
    """Plugin providing file system operations"""
    
    async def initialize(self) -> bool:
        """Initialize the file system tools plugin"""
        
        # Register tools
        self.register_tool(
            "read_file",
            self.read_file,
            "Read contents of a file",
            {
                "file_path": {"type": "string", "description": "Path to the file", "required": True},
                "encoding": {"type": "string", "description": "File encoding", "default": "utf-8"}
            }
        )
        
        self.register_tool(
            "write_file", 
            self.write_file,
            "Write content to a file",
            {
                "file_path": {"type": "string", "description": "Path to the file", "required": True},
                "content": {"type": "string", "description": "Content to write", "required": True},
                "encoding": {"type": "string", "description": "File encoding", "default": "utf-8"}
            }
        )
        
        self.register_tool(
            "list_directory",
            self.list_directory, 
            "List contents of a directory",
            {
                "directory_path": {"type": "string", "description": "Path to directory", "required": True},
                "recursive": {"type": "boolean", "description": "List recursively", "default": False}
            }
        )
        
        return True
    
    async def cleanup(self) -> None:
        """Cleanup plugin resources"""
        pass
    
    async def get_available_tools(self) -> List[Dict[str, Any]]:
        """Get available tools in Llama format"""
        return [tool.to_llama_schema() for tool in self._tools.values()]
    
    async def read_file(self, file_path: str, encoding: str = "utf-8") -> str:
        """Read a file and return its contents"""
        try:
            async with aiofiles.open(file_path, 'r', encoding=encoding) as f:
                return await f.read()
        except Exception as e:
            raise RuntimeError(f"Failed to read file {file_path}: {e}")
    
    async def write_file(self, file_path: str, content: str, encoding: str = "utf-8") -> str:
        """Write content to a file"""
        try:
            # Ensure directory exists
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)
            
            async with aiofiles.open(file_path, 'w', encoding=encoding) as f:
                await f.write(content)
            
            return f"Successfully wrote {len(content)} characters to {file_path}"
        except Exception as e:
            raise RuntimeError(f"Failed to write file {file_path}: {e}")
    
    async def list_directory(self, directory_path: str, recursive: bool = False) -> List[str]:
        """List directory contents"""
        try:
            path = Path(directory_path)
            if not path.exists():
                raise FileNotFoundError(f"Directory {directory_path} does not exist")
            
            if recursive:
                return [str(p) for p in path.rglob("*") if p.is_file()]
            else:
                return [str(p) for p in path.iterdir()]
                
        except Exception as e:
            raise RuntimeError(f"Failed to list directory {directory_path}: {e}")
