"""
File System Tools Plugin for SilentCodingLegend AI Agent
Provides file and directory management capabilities
"""

import os
import shutil
import asyncio
from pathlib import Path
from typing import Dict, List, Any, Optional
import mimetypes
from datetime import datetime

from src.plugins import BasePlugin, PluginMetadata, PluginType
from src.plugins.tool_registry import Tool, ToolParameter, ParameterType


class FileSystemToolsPlugin(BasePlugin):
    """File system management and operations plugin"""
    
    def __init__(self):
        metadata = PluginMetadata(
            name="FileSystemTools",
            version="1.0.0",
            description="File system operations and management tools",
            author="SilentCodingLegend",
            plugin_type=PluginType.TOOL,
            dependencies=[]
        )
        super().__init__(metadata)
        
    async def initialize(self):
        """Initialize the filesystem plugin"""
        return True
        
    async def cleanup(self):
        """Cleanup filesystem plugin resources"""
        pass
        
    def get_tools(self) -> List[Tool]:
        """Get available tools"""
        return [
            Tool(
                name="list_directory",
                description="List contents of a directory",
                parameters=[
                    ToolParameter(
                        name="path",
                        type=ParameterType.STRING,
                        description="Directory path to list",
                        required=True
                    ),
                    ToolParameter(
                        name="show_hidden",
                        type=ParameterType.BOOLEAN, 
                        description="Include hidden files",
                        required=False
                    )
                ],
                function=self.list_directory,
                plugin_name=self.metadata.name
            ),
            Tool(
                name="read_file",
                description="Read contents of a text file",
                parameters=[
                    ToolParameter(
                        name="path",
                        type=ParameterType.STRING,
                        description="File path to read",
                        required=True
                    ),
                    ToolParameter(
                        name="encoding",
                        type=ParameterType.STRING,
                        description="File encoding (default: utf-8)",
                        required=False
                    )
                ],
                function=self.read_file,
                plugin_name=self.metadata.name
            ),
            Tool(
                name="write_file",
                description="Write content to a file",
                parameters=[
                    ToolParameter(
                        name="path",
                        type=ParameterType.STRING,
                        description="File path to write to",
                        required=True
                    ),
                    ToolParameter(
                        name="content",
                        type=ParameterType.STRING,
                        description="Content to write",
                        required=True
                    ),
                    ToolParameter(
                        name="append",
                        type=ParameterType.BOOLEAN,
                        description="Append to file instead of overwriting",
                        required=False
                    )
                ],
                function=self.write_file,
                plugin_name=self.metadata.name
            ),
            Tool(
                name="get_file_info",
                description="Get detailed information about a file or directory",
                parameters=[
                    ToolParameter(
                        name="path",
                        type=ParameterType.STRING,
                        description="Path to analyze",
                        required=True
                    )
                ],
                function=self.get_file_info,
                plugin_name=self.metadata.name
            ),
            Tool(
                name="search_files",
                description="Search for files matching a pattern",
                parameters=[
                    ToolParameter(
                        name="directory",
                        type=ParameterType.STRING,
                        description="Directory to search in",
                        required=True
                    ),
                    ToolParameter(
                        name="pattern",
                        type=ParameterType.STRING,
                        description="File name pattern (supports wildcards)",
                        required=True
                    ),
                    ToolParameter(
                        name="recursive",
                        type=ParameterType.BOOLEAN,
                        description="Search subdirectories recursively",
                        required=False
                    )
                ],
                function=self.search_files,
                plugin_name=self.metadata.name
            )
        ]
        
    async def list_directory(self, path: str, show_hidden: bool = False) -> Dict[str, Any]:
        """List directory contents"""
        try:
            path_obj = Path(path)
            
            if not path_obj.exists():
                return {
                    "success": False,
                    "error": f"Path does not exist: {path}"
                }
                
            if not path_obj.is_dir():
                return {
                    "success": False,
                    "error": f"Path is not a directory: {path}"
                }
            
            items = []
            for item in path_obj.iterdir():
                if not show_hidden and item.name.startswith('.'):
                    continue
                    
                stat = item.stat()
                items.append({
                    "name": item.name,
                    "path": str(item),
                    "type": "directory" if item.is_dir() else "file",
                    "size": stat.st_size if item.is_file() else None,
                    "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    "permissions": oct(stat.st_mode)[-3:]
                })
            
            # Sort items: directories first, then files
            items.sort(key=lambda x: (x["type"] == "file", x["name"].lower()))
            
            return {
                "success": True,
                "path": str(path_obj.absolute()),
                "items": items,
                "total_items": len(items)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
            
    async def read_file(self, path: str, encoding: str = "utf-8") -> Dict[str, Any]:
        """Read file contents"""
        try:
            path_obj = Path(path)
            
            if not path_obj.exists():
                return {
                    "success": False,
                    "error": f"File does not exist: {path}"
                }
                
            if not path_obj.is_file():
                return {
                    "success": False,
                    "error": f"Path is not a file: {path}"
                }
            
            # Check if file is likely to be text
            mime_type, _ = mimetypes.guess_type(str(path_obj))
            if mime_type and not mime_type.startswith('text/'):
                return {
                    "success": False,
                    "error": f"File appears to be binary (MIME type: {mime_type})"
                }
            
            with open(path_obj, 'r', encoding=encoding) as f:
                content = f.read()
            
            stat = path_obj.stat()
            return {
                "success": True,
                "path": str(path_obj.absolute()),
                "content": content,
                "size": stat.st_size,
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "encoding": encoding
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
            
    async def write_file(self, path: str, content: str, append: bool = False) -> Dict[str, Any]:
        """Write content to file"""
        try:
            path_obj = Path(path)
            
            # Create parent directories if they don't exist
            path_obj.parent.mkdir(parents=True, exist_ok=True)
            
            mode = 'a' if append else 'w'
            with open(path_obj, mode, encoding='utf-8') as f:
                f.write(content)
            
            stat = path_obj.stat()
            return {
                "success": True,
                "path": str(path_obj.absolute()),
                "bytes_written": len(content.encode('utf-8')),
                "file_size": stat.st_size,
                "mode": "append" if append else "write"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
            
    async def get_file_info(self, path: str) -> Dict[str, Any]:
        """Get detailed file/directory information"""
        try:
            path_obj = Path(path)
            
            if not path_obj.exists():
                return {
                    "success": False,
                    "error": f"Path does not exist: {path}"
                }
            
            stat = path_obj.stat()
            mime_type, encoding = mimetypes.guess_type(str(path_obj))
            
            info = {
                "success": True,
                "path": str(path_obj.absolute()),
                "name": path_obj.name,
                "type": "directory" if path_obj.is_dir() else "file",
                "size": stat.st_size,
                "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "accessed": datetime.fromtimestamp(stat.st_atime).isoformat(),
                "permissions": oct(stat.st_mode)[-3:],
                "mime_type": mime_type,
                "encoding": encoding
            }
            
            if path_obj.is_dir():
                # Count directory contents
                try:
                    items = list(path_obj.iterdir())
                    info["contents_count"] = len(items)
                    info["subdirectories"] = len([item for item in items if item.is_dir()])
                    info["files"] = len([item for item in items if item.is_file()])
                except PermissionError:
                    info["contents_count"] = "Permission denied"
            
            return info
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
            
    async def search_files(self, directory: str, pattern: str, recursive: bool = True) -> Dict[str, Any]:
        """Search for files matching a pattern"""
        try:
            path_obj = Path(directory)
            
            if not path_obj.exists():
                return {
                    "success": False,
                    "error": f"Directory does not exist: {directory}"
                }
                
            if not path_obj.is_dir():
                return {
                    "success": False,
                    "error": f"Path is not a directory: {directory}"
                }
            
            matches = []
            search_pattern = f"**/{pattern}" if recursive else pattern
            
            for match in path_obj.glob(search_pattern):
                stat = match.stat()
                matches.append({
                    "path": str(match.absolute()),
                    "name": match.name,
                    "type": "directory" if match.is_dir() else "file",
                    "size": stat.st_size if match.is_file() else None,
                    "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    "relative_path": str(match.relative_to(path_obj))
                })
            
            # Sort by type then name
            matches.sort(key=lambda x: (x["type"] == "file", x["name"].lower()))
            
            return {
                "success": True,
                "directory": str(path_obj.absolute()),
                "pattern": pattern,
                "recursive": recursive,
                "matches": matches,
                "total_matches": len(matches)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }


# Plugin entry point
def create_plugin():
    """Create and return the plugin instance"""
    return FileSystemToolsPlugin()
