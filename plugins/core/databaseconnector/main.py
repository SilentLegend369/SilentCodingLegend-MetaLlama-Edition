"""
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
