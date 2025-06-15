"""
Plugin Marketplace for SilentCodingLegend AI Agent
Handles plugin discovery, sharing, and community features
"""

import json
import asyncio
import aiohttp
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime
import hashlib
import tempfile
import logging

from .base_plugin import PluginMetadata, PluginType
from .plugin_manager import PluginManager

# Use standard logging to avoid circular imports
logger = logging.getLogger(__name__)

class PluginMarketplace:
    """Plugin marketplace for discovering and sharing plugins"""
    
    def __init__(self, plugin_manager: PluginManager):
        self.plugin_manager = plugin_manager
        self.marketplace_url = "https://api.silentcodinglegend.com/plugins"  # Future API
        self.local_cache = plugin_manager.marketplace_dir / "cache"
        self.local_registry = plugin_manager.marketplace_dir / "registry.json"
        
        # Local plugin registry
        self._local_plugins: Dict[str, Dict[str, Any]] = {}
        self._featured_plugins: List[str] = []
        
    async def initialize(self) -> None:
        """Initialize marketplace"""
        await self._load_local_registry()
        await self._setup_featured_plugins()
        logger.info("Plugin marketplace initialized")
    
    async def _load_local_registry(self) -> None:
        """Load local plugin registry"""
        if self.local_registry.exists():
            try:
                with open(self.local_registry, 'r') as f:
                    data = json.load(f)
                    self._local_plugins = data.get("plugins", {})
                    self._featured_plugins = data.get("featured", [])
            except Exception as e:
                logger.error(f"Failed to load local registry: {e}")
                self._local_plugins = {}
                self._featured_plugins = []
    
    async def _save_local_registry(self) -> None:
        """Save local plugin registry"""
        try:
            data = {
                "plugins": self._local_plugins,
                "featured": self._featured_plugins,
                "updated_at": datetime.now().isoformat()
            }
            with open(self.local_registry, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save local registry: {e}")
    
    async def _setup_featured_plugins(self) -> None:
        """Setup featured plugins with sample plugins"""
        featured_plugins = [
            {
                "name": "FileSystemTools",
                "version": "1.0.0",
                "description": "File system operations - read, write, list files",
                "author": "SilentCodingLegend",
                "plugin_type": "tool",
                "category": "utility",
                "tags": ["filesystem", "files", "utility"],
                "download_url": "local://core/filesystem_tools",
                "featured": True
            },
            {
                "name": "WebScraper",
                "version": "1.0.0", 
                "description": "Web scraping and content extraction tools",
                "author": "SilentCodingLegend",
                "plugin_type": "tool",
                "category": "web",
                "tags": ["web", "scraping", "extraction"],
                "download_url": "local://core/web_scraper",
                "featured": True
            },
            {
                "name": "CodeAnalyzer",
                "version": "1.0.0",
                "description": "Advanced code analysis and quality metrics",
                "author": "SilentCodingLegend", 
                "plugin_type": "analyzer",
                "category": "development",
                "tags": ["code", "analysis", "quality"],
                "download_url": "local://core/code_analyzer",
                "featured": True
            },
            {
                "name": "DatabaseConnector",
                "version": "1.0.0",
                "description": "Connect and query various databases",
                "author": "SilentCodingLegend",
                "plugin_type": "integration", 
                "category": "database",
                "tags": ["database", "sql", "integration"],
                "download_url": "local://core/database_connector",
                "featured": True
            }
        ]
        
        for plugin_info in featured_plugins:
            self._local_plugins[plugin_info["name"]] = plugin_info
            if plugin_info["name"] not in self._featured_plugins:
                self._featured_plugins.append(plugin_info["name"])
        
        await self._save_local_registry()
    
    async def search_plugins(self, query: str = "", 
                           category: Optional[str] = None,
                           plugin_type: Optional[str] = None,
                           tags: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """Search for plugins in the marketplace"""
        results = []
        
        for plugin_name, plugin_info in self._local_plugins.items():
            # Apply filters
            if category and plugin_info.get("category") != category:
                continue
                
            if plugin_type and plugin_info.get("plugin_type") != plugin_type:
                continue
                
            if tags:
                plugin_tags = plugin_info.get("tags", [])
                if not any(tag in plugin_tags for tag in tags):
                    continue
            
            # Apply text search
            if query:
                searchable_text = (
                    plugin_info.get("name", "").lower() +
                    plugin_info.get("description", "").lower() +
                    " ".join(plugin_info.get("tags", [])).lower()
                )
                if query.lower() not in searchable_text:
                    continue
            
            results.append(plugin_info.copy())
        
        # Sort by relevance (featured first, then alphabetical)
        results.sort(key=lambda x: (not x.get("featured", False), x.get("name", "")))
        
        return results
    
    async def get_featured_plugins(self) -> List[Dict[str, Any]]:
        """Get featured plugins"""
        featured = []
        for plugin_name in self._featured_plugins:
            if plugin_name in self._local_plugins:
                featured.append(self._local_plugins[plugin_name].copy())
        return featured
    
    async def get_plugin_details(self, plugin_name: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a plugin"""
        return self._local_plugins.get(plugin_name)
    
    async def download_plugin(self, plugin_name: str) -> bool:
        """Download and install a plugin from marketplace"""
        plugin_info = self._local_plugins.get(plugin_name)
        if not plugin_info:
            logger.error(f"Plugin {plugin_name} not found in marketplace")
            return False
        
        download_url = plugin_info.get("download_url", "")
        
        if download_url.startswith("local://"):
            # Handle local plugin installation
            return await self._install_local_plugin(plugin_name, download_url)
        else:
            # Handle remote plugin download
            return await self._download_remote_plugin(plugin_name, download_url)
    
    async def _install_local_plugin(self, plugin_name: str, local_path: str) -> bool:
        """Install a local plugin"""
        try:
            # For demo purposes, create the plugin files
            await self._create_sample_plugin(plugin_name)
            return True
        except Exception as e:
            logger.error(f"Failed to install local plugin {plugin_name}: {e}")
            return False
    
    async def _download_remote_plugin(self, plugin_name: str, url: str) -> bool:
        """Download a plugin from remote URL"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        plugin_data = await response.read()
                        
                        # Save to temporary file
                        with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as temp_file:
                            temp_file.write(plugin_data)
                            temp_path = temp_file.name
                        
                        # Install plugin
                        return await self.plugin_manager.install_plugin(temp_path)
                    else:
                        logger.error(f"Failed to download plugin: HTTP {response.status}")
                        return False
                        
        except Exception as e:
            logger.error(f"Failed to download plugin {plugin_name}: {e}")
            return False
    
    async def _create_sample_plugin(self, plugin_name: str) -> None:
        """Create a sample plugin for demonstration"""
        plugin_dir = self.plugin_manager.plugins_dir / "core" / plugin_name.lower()
        plugin_dir.mkdir(parents=True, exist_ok=True)
        
        # Create plugin metadata
        metadata = {
            "name": plugin_name,
            "version": "1.0.0",
            "description": f"Sample {plugin_name} plugin",
            "author": "SilentCodingLegend",
            "plugin_type": "tool",
            "dependencies": [],
            "created_at": datetime.now().isoformat()
        }
        
        with open(plugin_dir / "plugin.json", 'w') as f:
            json.dump(metadata, f, indent=2)
        
        # Create basic plugin implementation
        if plugin_name == "FileSystemTools":
            await self._create_filesystem_plugin(plugin_dir)
        elif plugin_name == "WebScraper":
            await self._create_webscraper_plugin(plugin_dir)
        elif plugin_name == "CodeAnalyzer":
            # DISABLED: CodeAnalyzer functionality now provided by Coding.py page
            # await self._create_codeanalyzer_plugin(plugin_dir)
            logger.warning("CodeAnalyzer plugin creation disabled. Use the dedicated Coding page instead.")
            return
        elif plugin_name == "DatabaseConnector":
            await self._create_database_plugin(plugin_dir)
    
    async def _create_filesystem_plugin(self, plugin_dir: Path) -> None:
        """Create filesystem tools plugin"""
        plugin_code = '''"""
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
'''
        
        with open(plugin_dir / "main.py", 'w') as f:
            f.write(plugin_code)
    
    async def _create_webscraper_plugin(self, plugin_dir: Path) -> None:
        """Create web scraper plugin"""
        plugin_code = '''"""
Web Scraper Plugin for SilentCodingLegend AI Agent  
"""

import aiohttp
from bs4 import BeautifulSoup
from typing import Dict, List, Any
from src.plugins.base_plugin import ToolPlugin, PluginMetadata, PluginType

class WebScraperPlugin(ToolPlugin):
    """Plugin providing web scraping capabilities"""
    
    async def initialize(self) -> bool:
        """Initialize the web scraper plugin"""
        
        self.register_tool(
            "fetch_webpage",
            self.fetch_webpage,
            "Fetch and parse a webpage",
            {
                "url": {"type": "string", "description": "URL to fetch", "required": True},
                "extract_text": {"type": "boolean", "description": "Extract text only", "default": True}
            }
        )
        
        self.register_tool(
            "extract_links",
            self.extract_links,
            "Extract all links from a webpage", 
            {
                "url": {"type": "string", "description": "URL to analyze", "required": True}
            }
        )
        
        return True
    
    async def cleanup(self) -> None:
        """Cleanup plugin resources"""
        pass
    
    async def get_available_tools(self) -> List[Dict[str, Any]]:
        """Get available tools in Llama format"""
        return [tool.to_llama_schema() for tool in self._tools.values()]
    
    async def fetch_webpage(self, url: str, extract_text: bool = True) -> str:
        """Fetch a webpage and optionally extract text"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    html = await response.text()
                    
                    if extract_text:
                        soup = BeautifulSoup(html, 'html.parser')
                        return soup.get_text(strip=True)
                    else:
                        return html
                        
        except Exception as e:
            raise RuntimeError(f"Failed to fetch webpage {url}: {e}")
    
    async def extract_links(self, url: str) -> List[str]:
        """Extract all links from a webpage"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    html = await response.text()
                    
                    soup = BeautifulSoup(html, 'html.parser')
                    links = []
                    
                    for link in soup.find_all('a', href=True):
                        links.append(link['href'])
                    
                    return links
                    
        except Exception as e:
            raise RuntimeError(f"Failed to extract links from {url}: {e}")
'''
        
        with open(plugin_dir / "main.py", 'w') as f:
            f.write(plugin_code)
    
    async def _create_codeanalyzer_plugin(self, plugin_dir: Path) -> None:
        """Create code analyzer plugin - DISABLED to avoid conflicts with Coding.py page"""
        # NOTE: CodeAnalyzer functionality is now provided by the Coding.py page
        # This template is disabled to prevent tool registration conflicts
        plugin_code = '''"""
Code Analyzer Plugin for SilentCodingLegend AI Agent - DISABLED
This functionality is now handled by the dedicated Coding.py page.
"""

# DISABLED - Functionality moved to dedicated Coding.py Streamlit page
# import ast
# import os
# from typing import Dict, List, Any
# from src.plugins.base_plugin import ToolPlugin, PluginMetadata, PluginType

# class CodeAnalyzerPlugin(ToolPlugin):
    """Plugin providing code analysis capabilities"""
    
    async def initialize(self) -> bool:
        """Initialize the code analyzer plugin"""
        
        self.register_tool(
            "analyze_python_code",
            self.analyze_python_code,
            "Analyze Python code for metrics and issues",
            {
                "code": {"type": "string", "description": "Python code to analyze", "required": True}
            }
        )
        
        self.register_tool(
            "count_lines_of_code",
            self.count_lines_of_code,
            "Count lines of code in a file or directory",
            {
                "path": {"type": "string", "description": "File or directory path", "required": True}
            }
        )
        
        return True
    
    async def cleanup(self) -> None:
        """Cleanup plugin resources"""
        pass
    
    async def get_available_tools(self) -> List[Dict[str, Any]]:
        """Get available tools in Llama format"""
        return [tool.to_llama_schema() for tool in self._tools.values()]
    
    async def analyze_python_code(self, code: str) -> Dict[str, Any]:
        """Analyze Python code and return metrics"""
        try:
            tree = ast.parse(code)
            
            analysis = {
                "functions": 0,
                "classes": 0,
                "imports": 0,
                "lines": len(code.split('\\n')),
                "complexity_score": 0
            }
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    analysis["functions"] += 1
                elif isinstance(node, ast.ClassDef):
                    analysis["classes"] += 1
                elif isinstance(node, (ast.Import, ast.ImportFrom)):
                    analysis["imports"] += 1
                elif isinstance(node, (ast.If, ast.For, ast.While, ast.Try)):
                    analysis["complexity_score"] += 1
            
            return analysis
            
        except Exception as e:
            raise RuntimeError(f"Failed to analyze code: {e}")
    
    async def count_lines_of_code(self, path: str) -> Dict[str, int]:
        """Count lines of code in files"""
        try:
            total_lines = 0
            total_files = 0
            
            if os.path.isfile(path):
                with open(path, 'r') as f:
                    total_lines = len(f.readlines())
                    total_files = 1
            elif os.path.isdir(path):
                for root, dirs, files in os.walk(path):
                    for file in files:
                        if file.endswith(('.py', '.js', '.ts', '.java', '.cpp', '.c')):
                            file_path = os.path.join(root, file)
                            try:
                                with open(file_path, 'r') as f:
                                    total_lines += len(f.readlines())
                                    total_files += 1
                            except:
                                continue
            
            return {
                "total_lines": total_lines,
                "total_files": total_files,
                "average_lines_per_file": total_lines // max(total_files, 1)
            }
            
        except Exception as e:
            raise RuntimeError(f"Failed to count lines of code: {e}")
'''
        
        with open(plugin_dir / "main.py", 'w') as f:
            f.write(plugin_code)
    
    async def _create_database_plugin(self, plugin_dir: Path) -> None:
        """Create database connector plugin"""
        plugin_code = '''"""
Database Connector Plugin for SilentCodingLegend AI Agent
"""

import sqlite3
from typing import Dict, List, Any, Optional
from src.plugins.base_plugin import ToolPlugin, PluginMetadata, PluginType

class DatabaseConnectorPlugin(ToolPlugin):
    """Plugin providing database connectivity"""
    
    def __init__(self, metadata):
        super().__init__(metadata)
        self.connections = {}
    
    async def initialize(self) -> bool:
        """Initialize the database connector plugin"""
        
        self.register_tool(
            "connect_sqlite",
            self.connect_sqlite,
            "Connect to SQLite database",
            {
                "database_path": {"type": "string", "description": "Path to SQLite database", "required": True},
                "connection_name": {"type": "string", "description": "Name for this connection", "default": "default"}
            }
        )
        
        self.register_tool(
            "execute_query",
            self.execute_query,
            "Execute SQL query",
            {
                "query": {"type": "string", "description": "SQL query to execute", "required": True},
                "connection_name": {"type": "string", "description": "Connection to use", "default": "default"}
            }
        )
        
        return True
    
    async def cleanup(self) -> None:
        """Cleanup plugin resources"""
        for conn in self.connections.values():
            conn.close()
    
    async def get_available_tools(self) -> List[Dict[str, Any]]:
        """Get available tools in Llama format"""
        return [tool.to_llama_schema() for tool in self._tools.values()]
    
    async def connect_sqlite(self, database_path: str, connection_name: str = "default") -> str:
        """Connect to SQLite database"""
        try:
            if connection_name in self.connections:
                self.connections[connection_name].close()
            
            self.connections[connection_name] = sqlite3.connect(database_path)
            return f"Connected to SQLite database at {database_path}"
            
        except Exception as e:
            raise RuntimeError(f"Failed to connect to database: {e}")
    
    async def execute_query(self, query: str, connection_name: str = "default") -> List[Dict[str, Any]]:
        """Execute SQL query"""
        try:
            if connection_name not in self.connections:
                raise RuntimeError(f"No connection named '{connection_name}'")
            
            conn = self.connections[connection_name]
            cursor = conn.cursor()
            cursor.execute(query)
            
            # Get column names
            columns = [description[0] for description in cursor.description] if cursor.description else []
            
            # Fetch results
            rows = cursor.fetchall()
            
            # Convert to list of dicts
            results = []
            for row in rows:
                results.append(dict(zip(columns, row)))
            
            conn.commit()
            return results
            
        except Exception as e:
            raise RuntimeError(f"Failed to execute query: {e}")
'''
        
        with open(plugin_dir / "main.py", 'w') as f:
            f.write(plugin_code)
    
    async def publish_plugin(self, plugin_path: str, metadata: Dict[str, Any]) -> bool:
        """Publish a plugin to the marketplace"""
        try:
            # For now, just add to local registry
            plugin_name = metadata["name"]
            self._local_plugins[plugin_name] = metadata
            await self._save_local_registry()
            
            logger.info(f"Published plugin {plugin_name} to local marketplace")
            return True
            
        except Exception as e:
            logger.error(f"Failed to publish plugin: {e}")
            return False
    
    def get_marketplace_stats(self) -> Dict[str, Any]:
        """Get marketplace statistics"""
        total_plugins = len(self._local_plugins)
        categories = {}
        types = {}
        
        for plugin_info in self._local_plugins.values():
            # Count by category
            category = plugin_info.get("category", "other")
            categories[category] = categories.get(category, 0) + 1
            
            # Count by type
            plugin_type = plugin_info.get("plugin_type", "other")
            types[plugin_type] = types.get(plugin_type, 0) + 1
        
        return {
            "total_plugins": total_plugins,
            "featured_plugins": len(self._featured_plugins),
            "categories": categories,
            "types": types
        }
    
    async def get_available_categories(self) -> List[str]:
        """Returns a list of unique plugin categories."""
        if not self._local_plugins:
            await self.initialize()
        return list(set(p.get("category", "Other") for p in self._local_plugins.values()))

    async def get_available_plugin_types(self) -> List[str]:
        """Returns a list of unique plugin types."""
        if not self._local_plugins:
            await self.initialize()
        return list(set(p.get("plugin_type", "Generic") for p in self._local_plugins.values()))

    async def get_all_plugins(self) -> Dict[str, Dict[str, Any]]:
        """Returns all available plugins."""
        if not self._local_plugins:
            await self.initialize()
        return self._local_plugins.copy()  # Return a copy to prevent external modification
