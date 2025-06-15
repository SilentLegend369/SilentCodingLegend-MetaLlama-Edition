"""
Knowledge Management Plugin for SilentCodingLegend AI Agent
Provides knowledge graph, semantic search, and memory management tools
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path

from src.plugins import BasePlugin, PluginMetadata, PluginType
from src.plugins.tool_registry import Tool, ToolParameter, ParameterType
from src.core.enhanced_memory import EnhancedMemoryManager

logger = logging.getLogger(__name__)


class KnowledgeManagerPlugin(BasePlugin):
    """Plugin for advanced knowledge and memory management"""
    
    # Configuration schema for the plugin
    CONFIG_SCHEMA = {
        "enabled": {"type": "boolean", "default": True},
        "auto_extract_entities": {"type": "boolean", "default": True},
        "auto_build_relationships": {"type": "boolean", "default": True},
        "semantic_search_enabled": {"type": "boolean", "default": True},
        "context_window_size": {"type": "integer", "default": 4000}
    }
    
    def __init__(self):
        metadata = PluginMetadata(
            name="KnowledgeManager",
            version="1.0.0",
            description="Advanced knowledge graph, semantic search, and memory management",
            author="SilentCodingLegend",
            plugin_type=PluginType.TOOL,
            dependencies=["chromadb", "sentence-transformers", "networkx"]
        )
        
        super().__init__(metadata)
        self.memory_manager: Optional[EnhancedMemoryManager] = None
        self.initialized = False
    
    async def initialize(self, agent=None, config: Dict[str, Any] = None) -> bool:
        """Initialize the knowledge management system"""
        try:
            self.config = config or {}
            self.agent = agent
            
            # Initialize enhanced memory manager
            self.memory_manager = EnhancedMemoryManager()
            
            # Configure based on plugin config
            if self.config.get("auto_extract_entities") is not None:
                self.memory_manager.auto_extract_entities = self.config["auto_extract_entities"]
            
            if self.config.get("auto_build_relationships") is not None:
                self.memory_manager.auto_build_relationships = self.config["auto_build_relationships"]
            
            if self.config.get("semantic_search_enabled") is not None:
                self.memory_manager.semantic_search_enabled = self.config["semantic_search_enabled"]
            
            if self.config.get("context_window_size") is not None:
                self.memory_manager.context_window_size = self.config["context_window_size"]
            
            # Initialize the memory manager
            success = await self.memory_manager.initialize()
            
            if success:
                self.initialized = True
                logger.info("Knowledge Manager Plugin initialized successfully")
                return True
            else:
                logger.error("Failed to initialize memory manager")
                return False
            
        except Exception as e:
            logger.error(f"Error initializing Knowledge Manager Plugin: {e}")
            return False
    
    async def semantic_search(
        self,
        query: str,
        max_results: int = 10,
        session_id: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Perform semantic search across all conversations and knowledge
        
        Args:
            query: Search query
            max_results: Maximum number of results to return
            session_id: Optional session to filter by
            
        Returns:
            Dictionary with search results and metadata
        """
        if not self.initialized:
            return {"success": False, "error": "Plugin not initialized"}
        
        try:
            results = await self.memory_manager.search_conversations(
                query=query,
                max_results=max_results,
                session_id=session_id
            )
            
            return {
                "success": True,
                "query": query,
                "results": results,
                "total_results": len(results),
                "session_id": session_id
            }
            
        except Exception as e:
            logger.error(f"Error in semantic search: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_relevant_context(
        self,
        query: str,
        session_id: Optional[str] = None,
        max_results: int = 5,
        include_knowledge_graph: bool = True,
        include_semantic_search: bool = True,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Get comprehensive relevant context for a query
        
        Args:
            query: Query to find context for
            session_id: Optional session identifier
            max_results: Maximum results per category
            include_knowledge_graph: Include knowledge graph results
            include_semantic_search: Include semantic search results
            
        Returns:
            Dictionary with context from all sources
        """
        if not self.initialized:
            return {"success": False, "error": "Plugin not initialized"}
        
        try:
            context = await self.memory_manager.get_relevant_context(
                query=query,
                session_id=session_id,
                max_results=max_results,
                include_knowledge_graph=include_knowledge_graph,
                include_semantic_search=include_semantic_search
            )
            
            return {
                "success": True,
                "query": query,
                "context": context,
                "session_id": session_id
            }
            
        except Exception as e:
            logger.error(f"Error getting relevant context: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_knowledge_summary(
        self,
        topic: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Get a comprehensive knowledge summary for a topic
        
        Args:
            topic: Topic to summarize knowledge about
            
        Returns:
            Dictionary with knowledge summary
        """
        if not self.initialized:
            return {"success": False, "error": "Plugin not initialized"}
        
        try:
            summary = await self.memory_manager.get_knowledge_summary(topic)
            
            return {
                "success": True,
                "topic": topic,
                "summary": summary
            }
            
        except Exception as e:
            logger.error(f"Error getting knowledge summary: {e}")
            return {"success": False, "error": str(e)}
    
    async def search_knowledge_graph(
        self,
        query: str,
        entity_types: Optional[List[str]] = None,
        relation_types: Optional[List[str]] = None,
        max_results: int = 20,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Search the knowledge graph for entities and relationships
        
        Args:
            query: Search query
            entity_types: Filter by entity types
            relation_types: Filter by relationship types
            max_results: Maximum number of results
            
        Returns:
            Dictionary with knowledge graph search results
        """
        if not self.initialized:
            return {"success": False, "error": "Plugin not initialized"}
        
        try:
            # Search entities
            entities = await self.memory_manager.knowledge_graph.search_entities(
                query, limit=max_results
            )
            
            # Filter by entity types if specified
            if entity_types:
                entities = [e for e in entities if e.entity_type.value in entity_types]
            
            # Get relationships for found entities
            entity_ids = [entity.id for entity in entities]
            relationships = await self.memory_manager.knowledge_graph.get_relationships_between(entity_ids)
            
            # Filter by relationship types if specified
            if relation_types:
                relationships = [r for r in relationships if r.relation_type.value in relation_types]
            
            return {
                "success": True,
                "query": query,
                "entities": [
                    {
                        "id": e.id,
                        "name": e.name,
                        "type": e.entity_type.value,
                        "properties": e.properties,
                        "created_at": e.created_at.isoformat(),
                        "updated_at": e.updated_at.isoformat()
                    }
                    for e in entities
                ],
                "relationships": [
                    {
                        "id": r.id,
                        "source_id": r.source_id,
                        "target_id": r.target_id,
                        "type": r.relation_type.value,
                        "properties": r.properties,
                        "confidence": r.confidence,
                        "created_at": r.created_at.isoformat()
                    }
                    for r in relationships
                ],
                "filters": {
                    "entity_types": entity_types,
                    "relation_types": relation_types,
                    "max_results": max_results
                }
            }
            
        except Exception as e:
            logger.error(f"Error searching knowledge graph: {e}")
            return {"success": False, "error": str(e)}
    
    async def add_knowledge_note(
        self,
        title: str,
        content: str,
        tags: Optional[List[str]] = None,
        category: str = "general",
        **kwargs
    ) -> Dict[str, Any]:
        """
        Add a knowledge note to the system
        
        Args:
            title: Note title
            content: Note content
            tags: Optional tags
            category: Note category
            
        Returns:
            Dictionary with operation result
        """
        if not self.initialized:
            return {"success": False, "error": "Plugin not initialized"}
        
        try:
            from src.core.vector_db import Document, DocumentType
            import hashlib
            
            # Create document for the note
            doc_id = hashlib.md5(f"{title}_{content}".encode()).hexdigest()
            
            document = Document(
                id=doc_id,
                content=f"Title: {title}\nContent: {content}",
                metadata={
                    "title": title,
                    "category": category,
                    "tags": tags or [],
                    "created_by": "user",
                    "timestamp": datetime.now().isoformat()
                },
                doc_type=DocumentType.KNOWLEDGE_NOTE,
                timestamp=datetime.now()
            )
            
            # Add to vector database
            await self.memory_manager.vector_db.add_document(document)
            
            # Extract entities and add to knowledge graph
            entities = await self.memory_manager._extract_entities(content)
            for entity_data in entities:
                from src.core.knowledge_graph import Entity, EntityType
                entity = Entity(
                    id=entity_data["id"],
                    name=entity_data["name"],
                    entity_type=entity_data["type"],
                    properties={
                        **entity_data.get("properties", {}),
                        "source_note": title,
                        "source_category": category
                    },
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )
                await self.memory_manager.knowledge_graph.add_entity(entity)
            
            return {
                "success": True,
                "note_id": doc_id,
                "title": title,
                "entities_extracted": len(entities),
                "message": "Knowledge note added successfully"
            }
            
        except Exception as e:
            logger.error(f"Error adding knowledge note: {e}")
            return {"success": False, "error": str(e)}
    
    async def cleanup_old_knowledge(
        self,
        days_to_keep: int = 30,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Clean up old knowledge data
        
        Args:
            days_to_keep: Number of days of data to keep
            
        Returns:
            Dictionary with cleanup statistics
        """
        if not self.initialized:
            return {"success": False, "error": "Plugin not initialized"}
        
        try:
            stats = await self.memory_manager.cleanup_old_data(days_to_keep)
            
            return {
                "success": True,
                "days_to_keep": days_to_keep,
                "cleanup_stats": stats,
                "message": "Knowledge cleanup completed successfully"
            }
            
        except Exception as e:
            logger.error(f"Error cleaning up knowledge: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_knowledge_stats(self, **kwargs) -> Dict[str, Any]:
        """
        Get statistics about the knowledge base
        
        Returns:
            Dictionary with knowledge base statistics
        """
        if not self.initialized:
            return {"success": False, "error": "Plugin not initialized"}
        
        try:
            # Get knowledge graph stats
            kg_stats = await self.memory_manager.knowledge_graph.get_statistics()
            
            # Get vector database stats
            vector_stats = await self.memory_manager.vector_db.get_statistics()
            
            return {
                "success": True,
                "knowledge_graph": kg_stats,
                "vector_database": vector_stats,
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting knowledge stats: {e}")
            return {"success": False, "error": str(e)}
    
    async def export_knowledge(
        self,
        format: str = "json",
        include_vectors: bool = False,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Export knowledge data
        
        Args:
            format: Export format (json, csv)
            include_vectors: Whether to include vector embeddings
            
        Returns:
            Dictionary with exported data or file path
        """
        if not self.initialized:
            return {"success": False, "error": "Plugin not initialized"}
        
        try:
            export_data = {}
            
            # Export knowledge graph
            kg_export = await self.memory_manager.knowledge_graph.export_data()
            export_data["knowledge_graph"] = kg_export
            
            # Export vector database metadata
            vector_export = await self.memory_manager.vector_db.export_metadata(include_vectors)
            export_data["vector_database"] = vector_export
            
            export_data["export_info"] = {
                "format": format,
                "include_vectors": include_vectors,
                "exported_at": datetime.now().isoformat(),
                "exporter": "KnowledgeManagerPlugin"
            }
            
            return {
                "success": True,
                "export_data": export_data,
                "message": "Knowledge export completed successfully"
            }
            
        except Exception as e:
            logger.error(f"Error exporting knowledge: {e}")
            return {"success": False, "error": str(e)}
    
    async def cleanup(self) -> bool:
        """Clean up resources and save state"""
        return await self.shutdown()
    
    async def shutdown(self) -> bool:
        """Shutdown the plugin and save state"""
        try:
            if self.memory_manager:
                # Save any pending data
                await self.memory_manager.knowledge_graph.save()
                await self.memory_manager.vector_db.save()
                
            logger.info("Knowledge Manager Plugin shutdown successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error shutting down Knowledge Manager Plugin: {e}")
            return False


# Plugin registration
def get_plugin():
    """Return plugin instance for registration"""
    return KnowledgeManagerPlugin()
