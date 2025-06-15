"""
Backup Manager for SilentCodingLegend AI Agent
Handles automatic backups of configurations, data, and system state
"""

import os
import json
import shutil
import zipfile
import asyncio
import aiofiles
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging
import hashlib
import schedule
import threading
import time

logger = logging.getLogger(__name__)


class BackupManager:
    """Manages automatic backups for the AI agent system"""
    
    def __init__(self, base_dir: str = None):
        self.base_dir = Path(base_dir) if base_dir else Path.cwd()
        self.backup_dir = self.base_dir / "backups"
        self.config_file = self.backup_dir / "backup_config.json"
        
        # Default backup configuration
        self.config = {
            "enabled": True,
            "auto_backup_interval": "daily",  # daily, hourly, weekly
            "max_backups": 30,
            "compress": True,
            "include_patterns": [
                "*.json",
                "*.py",
                "*.md",
                "*.txt",
                "*.log",
                "data/**",
                "plugins/**",
                "src/**",
                "pages/**"
            ],
            "exclude_patterns": [
                "__pycache__/**",
                "*.pyc",
                "*.pyo",
                "node_modules/**",
                ".git/**",
                "backups/**",
                "*.tmp",
                "logs/debug.log"
            ],
            "backup_types": {
                "full": True,
                "incremental": True,
                "configuration": True,
                "data": True,
                "plugins": True
            }
        }
        
        self.backup_thread = None
        self.running = False
        
    async def initialize(self):
        """Initialize the backup manager"""
        try:
            # Create backup directory
            self.backup_dir.mkdir(exist_ok=True)
            
            # Load existing configuration
            await self._load_config()
            
            # Start automatic backup scheduler if enabled
            if self.config.get("enabled", True):
                await self.start_auto_backup()
            
            logger.info(f"Backup manager initialized at {self.backup_dir}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize backup manager: {e}")
            return False
    
    async def _load_config(self):
        """Load backup configuration from file"""
        if self.config_file.exists():
            try:
                async with aiofiles.open(self.config_file, 'r') as f:
                    content = await f.read()
                    saved_config = json.loads(content)
                    self.config.update(saved_config)
            except Exception as e:
                logger.warning(f"Failed to load backup config: {e}")
    
    async def _save_config(self):
        """Save backup configuration to file"""
        try:
            async with aiofiles.open(self.config_file, 'w') as f:
                await f.write(json.dumps(self.config, indent=2))
        except Exception as e:
            logger.error(f"Failed to save backup config: {e}")
    
    async def create_backup(self, backup_type: str = "full", custom_name: str = None) -> Dict[str, Any]:
        """Create a backup with specified type"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = custom_name or f"backup_{backup_type}_{timestamp}"
        backup_path = self.backup_dir / backup_name
        
        try:
            logger.info(f"Creating {backup_type} backup: {backup_name}")
            
            if backup_type == "full":
                result = await self._create_full_backup(backup_path)
            elif backup_type == "incremental":
                result = await self._create_incremental_backup(backup_path)
            elif backup_type == "configuration":
                result = await self._create_config_backup(backup_path)
            elif backup_type == "data":
                result = await self._create_data_backup(backup_path)
            elif backup_type == "plugins":
                result = await self._create_plugins_backup(backup_path)
            else:
                raise ValueError(f"Unknown backup type: {backup_type}")
            
            # Compress if enabled
            if self.config.get("compress", True) and result.get("success"):
                compressed_path = await self._compress_backup(backup_path)
                if compressed_path:
                    # Remove uncompressed directory
                    if backup_path.is_dir():
                        shutil.rmtree(backup_path)
                    result["backup_path"] = str(compressed_path)
                    result["compressed"] = True
            
            # Clean old backups
            await self._cleanup_old_backups()
            
            logger.info(f"Backup created successfully: {result.get('backup_path')}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to create backup: {e}")
            return {
                "success": False,
                "error": str(e),
                "backup_type": backup_type,
                "timestamp": timestamp
            }
    
    async def _create_full_backup(self, backup_path: Path) -> Dict[str, Any]:
        """Create a full system backup"""
        backup_path.mkdir(exist_ok=True)
        
        files_copied = 0
        total_size = 0
        
        # Copy files based on include/exclude patterns
        for pattern in self.config["include_patterns"]:
            for file_path in self.base_dir.glob(pattern):
                if self._should_include_file(file_path):
                    rel_path = file_path.relative_to(self.base_dir)
                    dest_path = backup_path / rel_path
                    
                    dest_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    if file_path.is_file():
                        shutil.copy2(file_path, dest_path)
                        files_copied += 1
                        total_size += file_path.stat().st_size
        
        # Create backup manifest
        manifest = {
            "backup_type": "full",
            "timestamp": datetime.now().isoformat(),
            "files_count": files_copied,
            "total_size_bytes": total_size,
            "base_directory": str(self.base_dir),
            "include_patterns": self.config["include_patterns"],
            "exclude_patterns": self.config["exclude_patterns"]
        }
        
        manifest_path = backup_path / "backup_manifest.json"
        async with aiofiles.open(manifest_path, 'w') as f:
            await f.write(json.dumps(manifest, indent=2))
        
        return {
            "success": True,
            "backup_type": "full",
            "backup_path": str(backup_path),
            "files_count": files_copied,
            "total_size_bytes": total_size,
            "timestamp": manifest["timestamp"]
        }
    
    async def _create_incremental_backup(self, backup_path: Path) -> Dict[str, Any]:
        """Create an incremental backup (only changed files)"""
        # Find the last full backup for comparison
        last_backup = await self._find_last_backup("full")
        if not last_backup:
            logger.info("No previous full backup found, creating full backup instead")
            return await self._create_full_backup(backup_path)
        
        backup_path.mkdir(exist_ok=True)
        
        # Load last backup manifest
        last_manifest_path = Path(last_backup["path"]) / "backup_manifest.json"
        last_files = {}
        
        if last_manifest_path.exists():
            async with aiofiles.open(last_manifest_path, 'r') as f:
                content = await f.read()
                last_manifest = json.loads(content)
                # Would need to store file hashes in manifest for proper comparison
        
        # For now, backup files modified since last backup
        last_backup_time = datetime.fromisoformat(last_backup["timestamp"])
        
        files_copied = 0
        total_size = 0
        
        for pattern in self.config["include_patterns"]:
            for file_path in self.base_dir.glob(pattern):
                if (self._should_include_file(file_path) and 
                    file_path.is_file() and
                    datetime.fromtimestamp(file_path.stat().st_mtime) > last_backup_time):
                    
                    rel_path = file_path.relative_to(self.base_dir)
                    dest_path = backup_path / rel_path
                    
                    dest_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(file_path, dest_path)
                    files_copied += 1
                    total_size += file_path.stat().st_size
        
        # Create manifest
        manifest = {
            "backup_type": "incremental", 
            "timestamp": datetime.now().isoformat(),
            "files_count": files_copied,
            "total_size_bytes": total_size,
            "base_backup": last_backup["path"],
            "base_timestamp": last_backup["timestamp"]
        }
        
        manifest_path = backup_path / "backup_manifest.json"
        async with aiofiles.open(manifest_path, 'w') as f:
            await f.write(json.dumps(manifest, indent=2))
        
        return {
            "success": True,
            "backup_type": "incremental",
            "backup_path": str(backup_path),
            "files_count": files_copied,
            "total_size_bytes": total_size,
            "timestamp": manifest["timestamp"]
        }
    
    async def _create_config_backup(self, backup_path: Path) -> Dict[str, Any]:
        """Create a backup of just configuration files"""
        backup_path.mkdir(exist_ok=True)
        
        config_patterns = [
            "*.json",
            "*.env*",
            "*.yml",
            "*.yaml",
            "*.toml",
            "*.ini",
            "plugins/config.json",
            "src/core/config.py"
        ]
        
        files_copied = 0
        for pattern in config_patterns:
            for file_path in self.base_dir.glob(pattern):
                if self._should_include_file(file_path) and file_path.is_file():
                    rel_path = file_path.relative_to(self.base_dir)
                    dest_path = backup_path / rel_path
                    dest_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(file_path, dest_path)
                    files_copied += 1
        
        manifest = {
            "backup_type": "configuration",
            "timestamp": datetime.now().isoformat(),
            "files_count": files_copied
        }
        
        manifest_path = backup_path / "backup_manifest.json"
        async with aiofiles.open(manifest_path, 'w') as f:
            await f.write(json.dumps(manifest, indent=2))
        
        return {
            "success": True,
            "backup_type": "configuration",
            "backup_path": str(backup_path),
            "files_count": files_copied,
            "timestamp": manifest["timestamp"]
        }
    
    async def _create_data_backup(self, backup_path: Path) -> Dict[str, Any]:
        """Create a backup of just data files"""
        backup_path.mkdir(exist_ok=True)
        
        data_dirs = ["data", "logs", "summaries"]
        files_copied = 0
        total_size = 0
        
        for data_dir in data_dirs:
            data_path = self.base_dir / data_dir
            if data_path.exists():
                dest_dir = backup_path / data_dir
                shutil.copytree(data_path, dest_dir, dirs_exist_ok=True)
                
                # Count files
                for file_path in data_path.rglob("*"):
                    if file_path.is_file():
                        files_copied += 1
                        total_size += file_path.stat().st_size
        
        manifest = {
            "backup_type": "data",
            "timestamp": datetime.now().isoformat(),
            "files_count": files_copied,
            "total_size_bytes": total_size,
            "data_directories": data_dirs
        }
        
        manifest_path = backup_path / "backup_manifest.json"
        async with aiofiles.open(manifest_path, 'w') as f:
            await f.write(json.dumps(manifest, indent=2))
        
        return {
            "success": True,
            "backup_type": "data",
            "backup_path": str(backup_path),
            "files_count": files_copied,
            "total_size_bytes": total_size,
            "timestamp": manifest["timestamp"]
        }
    
    async def _create_plugins_backup(self, backup_path: Path) -> Dict[str, Any]:
        """Create a backup of just plugins"""
        backup_path.mkdir(exist_ok=True)
        
        plugins_dir = self.base_dir / "plugins"
        if plugins_dir.exists():
            dest_dir = backup_path / "plugins"
            shutil.copytree(plugins_dir, dest_dir, dirs_exist_ok=True)
            
            files_copied = sum(1 for _ in plugins_dir.rglob("*") if _.is_file())
            total_size = sum(f.stat().st_size for f in plugins_dir.rglob("*") if f.is_file())
        else:
            files_copied = 0
            total_size = 0
        
        manifest = {
            "backup_type": "plugins",
            "timestamp": datetime.now().isoformat(),
            "files_count": files_copied,
            "total_size_bytes": total_size
        }
        
        manifest_path = backup_path / "backup_manifest.json"
        async with aiofiles.open(manifest_path, 'w') as f:
            await f.write(json.dumps(manifest, indent=2))
        
        return {
            "success": True,
            "backup_type": "plugins",
            "backup_path": str(backup_path),
            "files_count": files_copied,
            "total_size_bytes": total_size,
            "timestamp": manifest["timestamp"]
        }
    
    def _should_include_file(self, file_path: Path) -> bool:
        """Check if file should be included in backup"""
        rel_path = file_path.relative_to(self.base_dir)
        path_str = str(rel_path)
        
        # Check exclude patterns first
        for pattern in self.config["exclude_patterns"]:
            if rel_path.match(pattern):
                return False
        
        return True
    
    async def _compress_backup(self, backup_path: Path) -> Optional[Path]:
        """Compress backup directory to zip file"""
        try:
            zip_path = backup_path.with_suffix('.zip')
            
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for file_path in backup_path.rglob('*'):
                    if file_path.is_file():
                        arcname = file_path.relative_to(backup_path)
                        zipf.write(file_path, arcname)
            
            return zip_path
            
        except Exception as e:
            logger.error(f"Failed to compress backup: {e}")
            return None
    
    async def _cleanup_old_backups(self):
        """Remove old backups based on retention policy"""
        try:
            max_backups = self.config.get("max_backups", 30)
            
            # Get all backup files/directories
            backups = []
            for item in self.backup_dir.iterdir():
                if item.name.startswith("backup_") and item.name != "backup_config.json":
                    backups.append({
                        "path": item,
                        "timestamp": item.stat().st_mtime
                    })
            
            # Sort by timestamp (newest first)
            backups.sort(key=lambda x: x["timestamp"], reverse=True)
            
            # Remove excess backups
            for backup in backups[max_backups:]:
                path = backup["path"]
                if path.is_file():
                    path.unlink()
                elif path.is_dir():
                    shutil.rmtree(path)
                logger.info(f"Removed old backup: {path.name}")
                
        except Exception as e:
            logger.error(f"Failed to cleanup old backups: {e}")
    
    async def _find_last_backup(self, backup_type: str = None) -> Optional[Dict[str, Any]]:
        """Find the most recent backup of specified type"""
        try:
            backups = []
            
            for item in self.backup_dir.iterdir():
                if item.name.startswith("backup_"):
                    manifest_path = item / "backup_manifest.json" if item.is_dir() else None
                    
                    # For zip files, would need to extract manifest
                    if item.suffix == '.zip':
                        continue  # Skip for now
                    
                    if manifest_path and manifest_path.exists():
                        async with aiofiles.open(manifest_path, 'r') as f:
                            content = await f.read()
                            manifest = json.loads(content)
                            
                            if not backup_type or manifest.get("backup_type") == backup_type:
                                backups.append({
                                    "path": str(item),
                                    "type": manifest.get("backup_type"),
                                    "timestamp": manifest.get("timestamp"),
                                    "manifest": manifest
                                })
            
            if backups:
                # Return most recent
                backups.sort(key=lambda x: x["timestamp"], reverse=True)
                return backups[0]
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to find last backup: {e}")
            return None
    
    async def start_auto_backup(self):
        """Start automatic backup scheduler"""
        if self.running:
            return
        
        self.running = True
        interval = self.config.get("auto_backup_interval", "daily")
        
        def schedule_backups():
            if interval == "hourly":
                schedule.every().hour.do(self._run_scheduled_backup)
            elif interval == "daily":
                schedule.every().day.at("02:00").do(self._run_scheduled_backup)  # 2 AM
            elif interval == "weekly":
                schedule.every().sunday.at("02:00").do(self._run_scheduled_backup)
            
            while self.running:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        
        self.backup_thread = threading.Thread(target=schedule_backups, daemon=True)
        self.backup_thread.start()
        
        logger.info(f"Auto-backup started with {interval} schedule")
    
    def _run_scheduled_backup(self):
        """Run scheduled backup in async context"""
        asyncio.create_task(self.create_backup("incremental"))
    
    async def stop_auto_backup(self):
        """Stop automatic backup scheduler"""
        self.running = False
        if self.backup_thread:
            self.backup_thread.join(timeout=5)
        logger.info("Auto-backup stopped")
    
    async def list_backups(self) -> List[Dict[str, Any]]:
        """List all available backups"""
        backups = []
        
        try:
            for item in self.backup_dir.iterdir():
                if item.name.startswith("backup_"):
                    backup_info = {
                        "name": item.name,
                        "path": str(item),
                        "size_bytes": 0,
                        "is_compressed": item.suffix == '.zip',
                        "created": datetime.fromtimestamp(item.stat().st_ctime).isoformat()
                    }
                    
                    # Get size
                    if item.is_file():
                        backup_info["size_bytes"] = item.stat().st_size
                    elif item.is_dir():
                        backup_info["size_bytes"] = sum(
                            f.stat().st_size for f in item.rglob('*') if f.is_file()
                        )
                    
                    # Try to load manifest
                    manifest_path = item / "backup_manifest.json" if item.is_dir() else None
                    if manifest_path and manifest_path.exists():
                        try:
                            async with aiofiles.open(manifest_path, 'r') as f:
                                content = await f.read()
                                manifest = json.loads(content)
                                backup_info.update({
                                    "type": manifest.get("backup_type"),
                                    "files_count": manifest.get("files_count"),
                                    "timestamp": manifest.get("timestamp")
                                })
                        except:
                            pass
                    
                    backups.append(backup_info)
            
            # Sort by creation time (newest first)
            backups.sort(key=lambda x: x["created"], reverse=True)
            return backups
            
        except Exception as e:
            logger.error(f"Failed to list backups: {e}")
            return []
    
    async def restore_backup(self, backup_name: str, target_dir: str = None) -> Dict[str, Any]:
        """Restore from a backup"""
        try:
            backup_path = self.backup_dir / backup_name
            target_path = Path(target_dir) if target_dir else self.base_dir
            
            if not backup_path.exists():
                raise FileNotFoundError(f"Backup not found: {backup_name}")
            
            # Handle compressed backups
            if backup_path.suffix == '.zip':
                with zipfile.ZipFile(backup_path, 'r') as zipf:
                    zipf.extractall(target_path)
            else:
                # Copy directory contents
                for item in backup_path.iterdir():
                    if item.name != "backup_manifest.json":
                        dest = target_path / item.name
                        if item.is_file():
                            shutil.copy2(item, dest)
                        elif item.is_dir():
                            shutil.copytree(item, dest, dirs_exist_ok=True)
            
            return {
                "success": True,
                "backup_name": backup_name,
                "target_directory": str(target_path),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to restore backup: {e}")
            return {
                "success": False,
                "error": str(e),
                "backup_name": backup_name
            }
    
    async def get_backup_config(self) -> Dict[str, Any]:
        """Get current backup configuration"""
        return self.config.copy()
    
    async def update_backup_config(self, new_config: Dict[str, Any]) -> bool:
        """Update backup configuration"""
        try:
            self.config.update(new_config)
            await self._save_config()
            
            # Restart auto-backup if settings changed
            if self.running:
                await self.stop_auto_backup()
                if self.config.get("enabled", True):
                    await self.start_auto_backup()
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to update backup config: {e}")
            return False
