"""
Enhanced Memory Manager for SilentCodingLegend AI Agent
Integrates traditional conversation memory with knowledge             # Extract relationships if multiple entities
            if len(entities) > 1:
                relationships = await self._extract_relationships(entities, user_message, assistant_response)
                for rel_data in relationships:
                    try:
                        await self.knowledge_graph.add_relationship(
                            source_id=rel_data["source_id"],
                            target_id=rel_data["target_id"],
                            relation_type=rel_data["type"],
                            weight=rel_data.get("confidence", 0.8),
                            properties=rel_data.get("properties", {})
                        )
                    except ValueError as e:
                        logger.error(f"Error processing conversation turn: {e}")
                        # Skip this relationship if entities don't exist
                        continueector database
"""

import asyncio
import logging
import json
from typing import Dict, List, Optional, Any, Tuple, Union
from datetime import datetime, timedelta
from pathlib import Path
import hashlib

from .memory import ConversationMemory
from .knowledge_graph import KnowledgeGraphManager, Entity, Relationship, EntityType, RelationType
from .vector_db import VectorDatabaseManager, Document, DocumentType
from ..utils.logging import get_logger

logger = get_logger(__name__)


class EnhancedMemoryManager:
    """
    Enhanced memory manager that combines:
    1. Traditional conversation memory
    2. Knowledge graph for relationships
    3. Vector database for semantic search
    """
    
    def __init__(self, storage_dir: str = "data"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(exist_ok=True)
        
        # Initialize components
        self.conversation_memory = ConversationMemory(
            storage_dir=str(self.storage_dir / "conversations")
        )
        self.knowledge_graph = KnowledgeGraphManager(
            db_path=str(self.storage_dir / "knowledge")
        )
        self.vector_db = VectorDatabaseManager(
            db_path=str(self.storage_dir / "vectors")
        )
        
        # Configuration
        self.auto_extract_entities = True
        self.auto_build_relationships = True
        self.semantic_search_enabled = True
        self.context_window_size = 4000  # For RAG context
        
        logger.info("Enhanced Memory Manager initialized")
    
    async def initialize(self) -> bool:
        """Initialize all memory components"""
        try:
            # Initialize vector database
            await self.vector_db.initialize()
            
            # Initialize knowledge graph
            await self.knowledge_graph.initialize()
            
            logger.info("Enhanced Memory Manager fully initialized")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Enhanced Memory Manager: {e}")
            return False
    
    async def add_conversation_turn(
        self,
        session_id: Optional[str],
        user_message: str,
        assistant_response: str,
        metadata: Optional[Dict] = None
    ) -> None:
        """
        Add a complete conversation turn with enhanced processing
        """
        try:
            # Add to traditional memory
            self.conversation_memory.add_message(session_id, "user", user_message, metadata)
            self.conversation_memory.add_message(session_id, "assistant", assistant_response, metadata)
            
            # Process for knowledge extraction
            if self.auto_extract_entities or self.auto_build_relationships:
                await self._process_conversation_turn(
                    session_id, user_message, assistant_response, metadata
                )
            
            # Add to vector database for semantic search
            if self.semantic_search_enabled:
                await self._add_to_vector_store(
                    session_id, user_message, assistant_response, metadata
                )
            
        except Exception as e:
            logger.error(f"Error adding conversation turn: {e}")
    
    async def _process_conversation_turn(
        self,
        session_id: str,
        user_message: str,
        assistant_response: str,
        metadata: Optional[Dict]
    ) -> None:
        """Process conversation for knowledge extraction"""
        try:
            # Extract entities from both messages
            entities = await self._extract_entities(user_message + " " + assistant_response)
            
            # Add all entities first and collect their IDs
            entity_ids = []
            for entity_data in entities:
                entity_id = await self.knowledge_graph.add_entity(
                    name=entity_data["name"],
                    entity_type=entity_data["type"],
                    properties=entity_data.get("properties", {})
                )
                entity_ids.append(entity_id)
                entity_data["id"] = entity_id  # Update with actual ID
            
            # Build relationships between entities after all are added
            if len(entities) > 1:
                relationships = await self._extract_relationships(entities, user_message, assistant_response)
                for rel_data in relationships:
                    try:
                        await self.knowledge_graph.add_relationship(
                            source_id=rel_data["source_id"],
                            target_id=rel_data["target_id"],
                            relation_type=rel_data["type"],
                            weight=rel_data.get("confidence", 0.8),
                            properties=rel_data.get("properties", {})
                        )
                    except ValueError as e:
                        logger.error(f"Error processing conversation turn: {e}")
                        # Skip this relationship if entities don't exist
                        continue
            
            # Add conversation as an entity
            await self.knowledge_graph.add_entity(
                name=f"Conversation {session_id}",
                entity_type=EntityType.CONVERSATION,
                properties={
                    "session_id": session_id,
                    "user_message": user_message[:200],  # Truncated
                    "assistant_response": assistant_response[:200],  # Truncated
                    "full_content": user_message + " " + assistant_response,
                    "metadata": metadata or {}
                }
            )
            
        except Exception as e:
            logger.error(f"Error processing conversation turn: {e}")
    
    async def _add_to_vector_store(
        self,
        session_id: str,
        user_message: str,
        assistant_response: str,
        metadata: Optional[Dict]
    ) -> None:
        """Add conversation to vector database"""
        try:
            # Create document for the conversation turn
            conversation_text = f"User: {user_message}\nAssistant: {assistant_response}"
            
            await self.vector_db.add_document(
                content=conversation_text,
                doc_type=DocumentType.CONVERSATION,
                metadata={
                    "session_id": session_id,
                    "user_message": user_message,
                    "assistant_response": assistant_response,
                    "timestamp": datetime.now().isoformat(),
                    **(metadata or {})
                }
            )
            
        except Exception as e:
            logger.error(f"Error adding to vector store: {e}")
    
    async def get_relevant_context(
        self,
        query: str,
        session_id: Optional[str] = None,
        max_results: int = 5,
        include_knowledge_graph: bool = True,
        include_semantic_search: bool = True
    ) -> Dict[str, Any]:
        """
        Get relevant context for a query using all available sources
        """
        context = {
            "conversation_history": [],
            "semantic_matches": [],
            "knowledge_entities": [],
            "knowledge_relationships": [],
            "summary": ""
        }
        
        try:
            # Get recent conversation history
            if session_id:
                history = self.conversation_memory.get_conversation(session_id)
                context["conversation_history"] = history[-10:]  # Last 10 messages
            
            # Semantic search in vector database
            if include_semantic_search and self.semantic_search_enabled:
                semantic_results = await self.vector_db.semantic_search(
                    query=query,
                    n_results=max_results,
                    metadata_filter={"session_id": session_id} if session_id else None
                )
                context["semantic_matches"] = [
                    {
                        "content": doc["content"],
                        "metadata": doc["metadata"],
                        "score": doc["similarity"]
                    }
                    for doc in semantic_results
                ]
            
            # Knowledge graph search
            if include_knowledge_graph:
                # Find relevant entities
                entities = await self.knowledge_graph.search_entities(query, limit=max_results)
                context["knowledge_entities"] = [
                    {
                        "id": entity.id,
                        "name": entity.name,
                        "type": entity.entity_type.value,
                        "properties": entity.properties
                    }
                    for entity in entities
                ]
                
                # Find relationships between relevant entities
                if entities:
                    entity_ids = [entity.id for entity in entities]
                    relationships = await self.knowledge_graph.get_relationships_between(entity_ids)
                    context["knowledge_relationships"] = [
                        {
                            "source": rel.source_id,
                            "target": rel.target_id,
                            "type": rel.relation_type.value,
                            "properties": rel.properties,
                            "confidence": rel.weight
                        }
                        for rel in relationships
                    ]
            
            # Generate summary
            context["summary"] = await self._generate_context_summary(context)
            
            return context
            
        except Exception as e:
            logger.error(f"Error getting relevant context: {e}")
            return context
    
    async def _extract_entities(self, text: str) -> List[Dict[str, Any]]:
        """Extract entities from text (simplified implementation)"""
        # This is a simplified implementation
        # In a real system, you'd use NLP models like spaCy, NLTK, or transformers
        entities = []
        
        # Basic keyword extraction (you can enhance this)
        keywords = [
            "python", "javascript", "react", "django", "flask", "api", "database",
            "error", "bug", "function", "class", "variable", "library", "framework"
        ]
        
        text_lower = text.lower()
        for i, keyword in enumerate(keywords):
            if keyword in text_lower:
                entities.append({
                    "id": f"entity_{keyword}_{hashlib.md5(text.encode()).hexdigest()[:8]}",
                    "name": keyword,
                    "type": self._classify_entity_type(keyword),
                    "properties": {
                        "source_text": text[:100],
                        "extraction_method": "keyword_matching"
                    }
                })
        
        return entities
    
    def _classify_entity_type(self, keyword: str) -> EntityType:
        """Classify entity type based on keyword"""
        technology_keywords = ["python", "javascript", "react", "django", "flask"]
        error_keywords = ["error", "bug"]
        code_keywords = ["function", "class", "variable"]
        
        if keyword in technology_keywords:
            return EntityType.TECHNOLOGY
        elif keyword in error_keywords:
            return EntityType.ERROR
        elif keyword in code_keywords:
            return EntityType.CONCEPT
        else:
            return EntityType.CONCEPT
    
    async def _extract_relationships(
        self,
        entities: List[Dict[str, Any]],
        user_message: str,
        assistant_response: str
    ) -> List[Dict[str, Any]]:
        """Extract relationships between entities"""
        relationships = []
        
        # Create relationships between entities that appeared together
        for i, entity1 in enumerate(entities):
            for j, entity2 in enumerate(entities):
                if i != j and "id" in entity1 and "id" in entity2:
                    # If both entities appear in the same context, create a relationship
                    rel_id = f"rel_{entity1['id']}_{entity2['id']}"
                    relationships.append({
                        "id": rel_id,
                        "source_id": entity1["id"],
                        "target_id": entity2["id"],
                        "type": RelationType.RELATED_TO,
                        "properties": {
                            "context": user_message + " " + assistant_response,
                            "extraction_method": "co_occurrence"
                        },
                        "confidence": 0.7
                    })
        
        return relationships
    
    async def _generate_context_summary(self, context: Dict[str, Any]) -> str:
        """Generate a summary of the retrieved context"""
        summary_parts = []
        
        if context["conversation_history"]:
            summary_parts.append(f"Found {len(context['conversation_history'])} recent messages in conversation.")
        
        if context["semantic_matches"]:
            summary_parts.append(f"Found {len(context['semantic_matches'])} semantically similar conversations.")
        
        if context["knowledge_entities"]:
            entity_types = set(entity["type"] for entity in context["knowledge_entities"])
            summary_parts.append(f"Found {len(context['knowledge_entities'])} related entities: {', '.join(entity_types)}")
        
        if context["knowledge_relationships"]:
            summary_parts.append(f"Found {len(context['knowledge_relationships'])} knowledge relationships.")
        
        return " ".join(summary_parts) if summary_parts else "No relevant context found."
    
    async def search_conversations(
        self,
        query: str,
        max_results: int = 10,
        session_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Search through all conversations using semantic search"""
        try:
            results = await self.vector_db.semantic_search(
                query=query,
                n_results=max_results,
                metadata_filter={"session_id": session_id} if session_id else None
            )
            
            return [
                {
                    "content": doc["content"],
                    "metadata": doc["metadata"],
                    "relevance_score": doc["similarity"],
                    "session_id": doc["metadata"].get("session_id"),
                    "timestamp": doc["metadata"].get("timestamp")
                }
                for doc in results
            ]
            
        except Exception as e:
            logger.error(f"Error searching conversations: {e}")
            return []
    
    async def get_knowledge_summary(self, topic: str) -> Dict[str, Any]:
        """Get a comprehensive knowledge summary for a topic"""
        try:
            # Search for entities related to the topic
            entities = await self.knowledge_graph.search_entities(topic, limit=20)
            
            # Get relationships between these entities
            entity_ids = [entity.id for entity in entities]
            relationships = await self.knowledge_graph.get_relationships_between(entity_ids)
            
            # Get semantic matches from conversations
            semantic_matches = await self.vector_db.semantic_search(query=topic, n_results=10)
            
            # Organize by entity types
            entities_by_type = {}
            for entity in entities:
                entity_type = entity.entity_type.value
                if entity_type not in entities_by_type:
                    entities_by_type[entity_type] = []
                entities_by_type[entity_type].append({
                    "name": entity.name,
                    "properties": entity.properties,
                    "created_at": entity.created_at.isoformat()
                })
            
            return {
                "topic": topic,
                "entities_by_type": entities_by_type,
                "total_entities": len(entities),
                "total_relationships": len(relationships),
                "relationship_types": list(set(rel.relation_type.value for rel in relationships)),
                "conversation_matches": len(semantic_matches),
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating knowledge summary: {e}")
            return {"topic": topic, "error": str(e)}
    
    async def cleanup_old_data(self, days_to_keep: int = 30) -> Dict[str, int]:
        """Clean up old data from all storage systems"""
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        cleanup_stats = {
            "conversations_cleaned": 0,
            "vectors_cleaned": 0,
            "entities_cleaned": 0,
            "relationships_cleaned": 0
        }
        
        try:
            # Clean up old conversations
            # (ConversationMemory should implement this)
            
            # Clean up old vectors
            vectors_cleaned = await self.vector_db.cleanup_old_documents(cutoff_date)
            cleanup_stats["vectors_cleaned"] = vectors_cleaned
            
            # Clean up old knowledge graph data
            kg_stats = await self.knowledge_graph.cleanup_old_data(cutoff_date)
            cleanup_stats.update(kg_stats)
            
            logger.info(f"Cleanup completed: {cleanup_stats}")
            return cleanup_stats
            
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
            return cleanup_stats
