"""
Backup Manager Plugin for SilentCodingLegend AI Agent
Provides automatic backup and restore functionality
"""

import asyncio
from typing import Dict, List, Any, Optional
from pathlib import Path
import logging

from src.plugins import BasePlugin, PluginMetadata, PluginType
from src.plugins.tool_registry import Tool, ToolParameter, ParameterType
from src.utils.backup_manager import BackupManager

logger = logging.getLogger(__name__)


class BackupManagerPlugin(BasePlugin):
    """Plugin for automatic backup and restore functionality"""
    
    def __init__(self):
        metadata = PluginMetadata(
            name="BackupManager",
            version="1.0.0",
            description="Automatic backup and restore tools for the AI agent system",
            author="SilentCodingLegend",
            plugin_type=PluginType.TOOL,
            dependencies=["schedule"]
        )
        super().__init__(metadata)
        self.backup_manager = None
        
    async def initialize(self):
        """Initialize the backup manager plugin"""
        try:
            # Use the data/backups directory for backup storage
            backup_dir = Path.cwd() / "data" / "backups"
            self.backup_manager = BackupManager(base_dir=str(backup_dir.parent))
            success = await self.backup_manager.initialize()
            
            if success:
                logger.info("Backup Manager Plugin initialized successfully")
            else:
                logger.error("Failed to initialize backup manager")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to initialize Backup Manager Plugin: {e}")
            return False
        
    async def cleanup(self):
        """Cleanup plugin resources"""
        if self.backup_manager:
            await self.backup_manager.stop_auto_backup()
            
    def get_tools(self) -> List[Tool]:
        """Get available backup tools"""
        return [
            Tool(
                name="create_backup",
                description="Create a backup of the system with specified type",
                category="backup",
                parameters=[
                    ToolParameter(
                        name="backup_type",
                        type=ParameterType.STRING,
                        description="Type of backup (full, incremental, configuration, data, plugins)",
                        required=False,
                        default="full"
                    ),
                    ToolParameter(
                        name="custom_name",
                        type=ParameterType.STRING,
                        description="Custom name for the backup",
                        required=False
                    )
                ],
                function=self.create_backup,
                plugin_name=self.metadata.name
            ),
            Tool(
                name="list_backups",
                description="List all available backups",
                category="backup",
                parameters=[],
                function=self.list_backups,
                plugin_name=self.metadata.name
            ),
            Tool(
                name="restore_backup",
                description="Restore from a specific backup",
                category="backup",
                parameters=[
                    ToolParameter(
                        name="backup_name",
                        type=ParameterType.STRING,
                        description="Name of the backup to restore",
                        required=True
                    ),
                    ToolParameter(
                        name="target_directory",
                        type=ParameterType.STRING,
                        description="Target directory for restoration (optional)",
                        required=False
                    )
                ],
                function=self.restore_backup,
                plugin_name=self.metadata.name
            ),
            Tool(
                name="get_backup_config",
                description="Get current backup configuration",
                category="backup",
                parameters=[],
                function=self.get_backup_config,
                plugin_name=self.metadata.name
            ),
            Tool(
                name="update_backup_config",
                description="Update backup configuration settings",
                category="backup",
                parameters=[
                    ToolParameter(
                        name="config",
                        type=ParameterType.STRING,
                        description="JSON string with new configuration settings",
                        required=True
                    )
                ],
                function=self.update_backup_config,
                plugin_name=self.metadata.name
            ),
            Tool(
                name="start_auto_backup",
                description="Start automatic backup scheduler",
                category="backup",
                parameters=[],
                function=self.start_auto_backup,
                plugin_name=self.metadata.name
            ),
            Tool(
                name="stop_auto_backup",
                description="Stop automatic backup scheduler",
                category="backup",
                parameters=[],
                function=self.stop_auto_backup,
                plugin_name=self.metadata.name
            ),
            Tool(
                name="backup_status",
                description="Get backup system status and statistics",
                category="backup",
                parameters=[],
                function=self.backup_status,
                plugin_name=self.metadata.name
            )
        ]
    
    async def create_backup(self, backup_type: str = "full", custom_name: str = None) -> Dict[str, Any]:
        """Create a backup"""
        try:
            if not self.backup_manager:
                return {
                    "success": False,
                    "error": "Backup manager not initialized"
                }
            
            result = await self.backup_manager.create_backup(backup_type, custom_name)
            return result
            
        except Exception as e:
            logger.error(f"Failed to create backup: {e}")
            return {
                "success": False,
                "error": str(e),
                "backup_type": backup_type
            }
    
    async def list_backups(self) -> Dict[str, Any]:
        """List all available backups"""
        try:
            if not self.backup_manager:
                return {
                    "success": False,
                    "error": "Backup manager not initialized"
                }
            
            backups = await self.backup_manager.list_backups()
            return {
                "success": True,
                "backups": backups,
                "total_count": len(backups)
            }
            
        except Exception as e:
            logger.error(f"Failed to list backups: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def restore_backup(self, backup_name: str, target_directory: str = None) -> Dict[str, Any]:
        """Restore from a backup"""
        try:
            if not self.backup_manager:
                return {
                    "success": False,
                    "error": "Backup manager not initialized"
                }
            
            result = await self.backup_manager.restore_backup(backup_name, target_directory)
            return result
            
        except Exception as e:
            logger.error(f"Failed to restore backup: {e}")
            return {
                "success": False,
                "error": str(e),
                "backup_name": backup_name
            }
    
    async def get_backup_config(self) -> Dict[str, Any]:
        """Get current backup configuration"""
        try:
            if not self.backup_manager:
                return {
                    "success": False,
                    "error": "Backup manager not initialized"
                }
            
            config = await self.backup_manager.get_backup_config()
            return {
                "success": True,
                "config": config
            }
            
        except Exception as e:
            logger.error(f"Failed to get backup config: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def update_backup_config(self, config: str) -> Dict[str, Any]:
        """Update backup configuration"""
        try:
            if not self.backup_manager:
                return {
                    "success": False,
                    "error": "Backup manager not initialized"
                }
            
            import json
            new_config = json.loads(config)
            
            success = await self.backup_manager.update_backup_config(new_config)
            return {
                "success": success,
                "message": "Configuration updated successfully" if success else "Failed to update configuration"
            }
            
        except json.JSONDecodeError as e:
            return {
                "success": False,
                "error": f"Invalid JSON configuration: {e}"
            }
        except Exception as e:
            logger.error(f"Failed to update backup config: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def start_auto_backup(self) -> Dict[str, Any]:
        """Start automatic backup scheduler"""
        try:
            if not self.backup_manager:
                return {
                    "success": False,
                    "error": "Backup manager not initialized"
                }
            
            await self.backup_manager.start_auto_backup()
            return {
                "success": True,
                "message": "Automatic backup started",
                "status": "running"
            }
            
        except Exception as e:
            logger.error(f"Failed to start auto backup: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def stop_auto_backup(self) -> Dict[str, Any]:
        """Stop automatic backup scheduler"""
        try:
            if not self.backup_manager:
                return {
                    "success": False,
                    "error": "Backup manager not initialized"
                }
            
            await self.backup_manager.stop_auto_backup()
            return {
                "success": True,
                "message": "Automatic backup stopped",
                "status": "stopped"
            }
            
        except Exception as e:
            logger.error(f"Failed to stop auto backup: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def backup_status(self) -> Dict[str, Any]:
        """Get backup system status and statistics"""
        try:
            if not self.backup_manager:
                return {
                    "success": False,
                    "error": "Backup manager not initialized"
                }
            
            # Get basic status info
            config = await self.backup_manager.get_backup_config()
            backups = await self.backup_manager.list_backups()
            
            # Calculate statistics
            total_backups = len(backups)
            total_size = sum(backup.get("size_bytes", 0) for backup in backups)
            
            # Get backup types count
            backup_types = {}
            for backup in backups:
                backup_type = backup.get("type", "unknown")
                backup_types[backup_type] = backup_types.get(backup_type, 0) + 1
            
            # Get recent backup info
            recent_backup = backups[0] if backups else None
            
            return {
                "success": True,
                "status": {
                    "auto_backup_enabled": config.get("enabled", False),
                    "auto_backup_running": self.backup_manager.running,
                    "backup_interval": config.get("auto_backup_interval", "daily"),
                    "max_backups": config.get("max_backups", 30)
                },
                "statistics": {
                    "total_backups": total_backups,
                    "total_size_bytes": total_size,
                    "total_size_mb": round(total_size / (1024 * 1024), 2),
                    "backup_types": backup_types,
                    "recent_backup": recent_backup
                },
                "configuration": config
            }
            
        except Exception as e:
            logger.error(f"Failed to get backup status: {e}")
            return {
                "success": False,
                "error": str(e)
            }


# Plugin entry point
def create_plugin():
    """Create and return the plugin instance"""
    return BackupManagerPlugin()
