"""
RAG (Retrieval Augmented Generation) Module for SilentCodingLegend AI Agent
Combines knowledge retrieval with generation for enhanced responses
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Tuple, Union
from datetime import datetime
from dataclasses import dataclass

from .enhanced_memory import EnhancedMemoryManager
from .knowledge_graph import Entity, Relationship
from .vector_db import Document
from ..utils.logging import get_logger

logger = get_logger(__name__)


@dataclass
class RAGContext:
    """Context retrieved for RAG"""
    query: str
    semantic_matches: List[Tuple[Document, float]]
    knowledge_entities: List[Entity]
    knowledge_relationships: List[Relationship]
    conversation_history: List[Dict[str, Any]]
    context_summary: str
    relevance_score: float
    retrieval_time: float


class RAGProcessor:
    """
    RAG (Retrieval Augmented Generation) processor that enhances responses
    with relevant context from knowledge base and conversation history
    """
    
    def __init__(self, memory_manager: EnhancedMemoryManager):
        self.memory_manager = memory_manager
        
        # Configuration
        self.max_semantic_results = 5
        self.max_knowledge_entities = 10
        self.min_relevance_threshold = 0.3
        self.context_window_tokens = 4000
        
        # Weights for different context sources
        self.semantic_weight = 0.4
        self.knowledge_weight = 0.3
        self.conversation_weight = 0.3
        
        logger.info("RAG Processor initialized")
    
    async def retrieve_context(
        self,
        query: str,
        session_id: Optional[str] = None,
        include_conversation: bool = True,
        include_semantic: bool = True,
        include_knowledge: bool = True
    ) -> RAGContext:
        """
        Retrieve comprehensive context for a query
        
        Args:
            query: User query to retrieve context for
            session_id: Optional session identifier
            include_conversation: Include conversation history
            include_semantic: Include semantic search results
            include_knowledge: Include knowledge graph results
            
        Returns:
            RAGContext with all retrieved information
        """
        start_time = datetime.now()
        
        try:
            # Initialize containers
            semantic_matches = []
            knowledge_entities = []
            knowledge_relationships = []
            conversation_history = []
            
            # Retrieve semantic matches
            if include_semantic and self.memory_manager.semantic_search_enabled:
                semantic_matches = await self.memory_manager.vector_db.semantic_search(
                    query=query,
                    top_k=self.max_semantic_results,
                    filter_metadata={"session_id": session_id} if session_id else None
                )
                # Filter by relevance threshold
                semantic_matches = [
                    (doc, score) for doc, score in semantic_matches 
                    if score >= self.min_relevance_threshold
                ]
            
            # Retrieve knowledge graph entities and relationships
            if include_knowledge:
                knowledge_entities = await self.memory_manager.knowledge_graph.search_entities(
                    query=query,
                    limit=self.max_knowledge_entities
                )
                
                # Get relationships between found entities
                if knowledge_entities:
                    entity_ids = [entity.id for entity in knowledge_entities]
                    knowledge_relationships = await self.memory_manager.knowledge_graph.get_relationships_between(
                        entity_ids
                    )
            
            # Retrieve conversation history
            if include_conversation and session_id:
                conversation_history = self.memory_manager.conversation_memory.get_conversation(session_id)
                # Keep recent messages
                conversation_history = conversation_history[-10:] if len(conversation_history) > 10 else conversation_history
            
            # Calculate relevance score
            relevance_score = self._calculate_relevance_score(
                semantic_matches, knowledge_entities, conversation_history
            )
            
            # Generate context summary
            context_summary = self._generate_context_summary(
                query, semantic_matches, knowledge_entities, knowledge_relationships, conversation_history
            )
            
            # Calculate retrieval time
            retrieval_time = (datetime.now() - start_time).total_seconds()
            
            return RAGContext(
                query=query,
                semantic_matches=semantic_matches,
                knowledge_entities=knowledge_entities,
                knowledge_relationships=knowledge_relationships,
                conversation_history=conversation_history,
                context_summary=context_summary,
                relevance_score=relevance_score,
                retrieval_time=retrieval_time
            )
            
        except Exception as e:
            logger.error(f"Error retrieving RAG context: {e}")
            # Return empty context in case of error
            return RAGContext(
                query=query,
                semantic_matches=[],
                knowledge_entities=[],
                knowledge_relationships=[],
                conversation_history=[],
                context_summary=f"Error retrieving context: {e}",
                relevance_score=0.0,
                retrieval_time=(datetime.now() - start_time).total_seconds()
            )
    
    def _calculate_relevance_score(
        self,
        semantic_matches: List[Tuple[Document, float]],
        knowledge_entities: List[Entity],
        conversation_history: List[Dict[str, Any]]
    ) -> float:
        """Calculate overall relevance score for retrieved context"""
        
        # Semantic relevance
        semantic_score = 0.0
        if semantic_matches:
            semantic_score = sum(score for _, score in semantic_matches) / len(semantic_matches)
        
        # Knowledge relevance (based on number of entities found)
        knowledge_score = min(len(knowledge_entities) / self.max_knowledge_entities, 1.0)
        
        # Conversation relevance (based on recent activity)
        conversation_score = min(len(conversation_history) / 10, 1.0)
        
        # Weighted average
        total_score = (
            semantic_score * self.semantic_weight +
            knowledge_score * self.knowledge_weight +
            conversation_score * self.conversation_weight
        )
        
        return total_score
    
    def _generate_context_summary(
        self,
        query: str,
        semantic_matches: List[Tuple[Document, float]],
        knowledge_entities: List[Entity],
        knowledge_relationships: List[Relationship],
        conversation_history: List[Dict[str, Any]]
    ) -> str:
        """Generate a human-readable summary of the retrieved context"""
        
        summary_parts = []
        
        if semantic_matches:
            avg_score = sum(score for _, score in semantic_matches) / len(semantic_matches)
            summary_parts.append(
                f"Found {len(semantic_matches)} semantically similar conversations "
                f"(avg relevance: {avg_score:.2f})"
            )
        
        if knowledge_entities:
            entity_types = {}
            for entity in knowledge_entities:
                entity_type = entity.entity_type.value
                entity_types[entity_type] = entity_types.get(entity_type, 0) + 1
            
            type_summary = ", ".join([f"{count} {type_}" for type_, count in entity_types.items()])
            summary_parts.append(f"Found {len(knowledge_entities)} related entities: {type_summary}")
        
        if knowledge_relationships:
            rel_types = {}
            for rel in knowledge_relationships:
                rel_type = rel.relation_type.value
                rel_types[rel_type] = rel_types.get(rel_type, 0) + 1
            
            rel_summary = ", ".join([f"{count} {type_}" for type_, count in rel_types.items()])
            summary_parts.append(f"Found {len(knowledge_relationships)} relationships: {rel_summary}")
        
        if conversation_history:
            summary_parts.append(f"Available conversation history: {len(conversation_history)} messages")
        
        if not summary_parts:
            return "No relevant context found in knowledge base"
        
        return "; ".join(summary_parts)
    
    def format_context_for_prompt(
        self,
        rag_context: RAGContext,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        Format retrieved context for inclusion in the prompt
        
        Args:
            rag_context: Retrieved context
            max_tokens: Maximum tokens to include (approximate)
            
        Returns:
            Formatted context string
        """
        if max_tokens is None:
            max_tokens = self.context_window_tokens
        
        context_parts = []
        estimated_tokens = 0
        
        # Add semantic matches
        if rag_context.semantic_matches:
            context_parts.append("RELEVANT CONVERSATIONS:")
            for i, (doc, score) in enumerate(rag_context.semantic_matches[:3]):  # Top 3
                content = doc.content[:300] + "..." if len(doc.content) > 300 else doc.content
                context_parts.append(f"{i+1}. [Score: {score:.2f}] {content}")
                estimated_tokens += len(content.split()) + 10  # Rough token estimate
                
                if estimated_tokens > max_tokens * 0.4:  # Use max 40% for semantic matches
                    break
        
        # Add knowledge entities
        if rag_context.knowledge_entities and estimated_tokens < max_tokens * 0.8:
            context_parts.append("\nRELATED CONCEPTS:")
            entity_names = []
            for entity in rag_context.knowledge_entities[:10]:
                entity_info = f"{entity.name} ({entity.entity_type.value})"
                entity_names.append(entity_info)
                estimated_tokens += len(entity_info.split()) + 2
                
                if estimated_tokens > max_tokens * 0.6:  # Use max 20% for entities
                    break
            
            context_parts.append(", ".join(entity_names))
        
        # Add knowledge relationships
        if rag_context.knowledge_relationships and estimated_tokens < max_tokens * 0.9:
            context_parts.append("\nKNOWLEDGE RELATIONSHIPS:")
            for i, rel in enumerate(rag_context.knowledge_relationships[:5]):
                rel_info = f"{rel.source_id} --{rel.relation_type.value}--> {rel.target_id}"
                context_parts.append(f"- {rel_info}")
                estimated_tokens += len(rel_info.split()) + 3
                
                if estimated_tokens > max_tokens * 0.9 or i >= 4:  # Use max 10% for relationships
                    break
        
        # Add conversation context if there's still room
        if rag_context.conversation_history and estimated_tokens < max_tokens * 0.95:
            context_parts.append("\nRECENT CONVERSATION:")
            for msg in rag_context.conversation_history[-3:]:  # Last 3 messages
                msg_content = f"{msg['role']}: {msg['content'][:150]}..."
                context_parts.append(msg_content)
                estimated_tokens += len(msg_content.split()) + 5
                
                if estimated_tokens > max_tokens:
                    break
        
        formatted_context = "\n".join(context_parts)
        
        # Add metadata
        metadata = [
            f"Context retrieved in {rag_context.retrieval_time:.2f}s",
            f"Relevance score: {rag_context.relevance_score:.2f}",
            f"Estimated tokens: {estimated_tokens}"
        ]
        
        formatted_context += f"\n\n[{' | '.join(metadata)}]"
        
        return formatted_context
    
    async def augmented_response(
        self,
        query: str,
        session_id: Optional[str] = None,
        base_response: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate an augmented response using RAG
        
        Args:
            query: User query
            session_id: Session identifier
            base_response: Optional base response to augment
            
        Returns:
            Dictionary with augmented response and metadata
        """
        try:
            # Retrieve context
            rag_context = await self.retrieve_context(
                query=query,
                session_id=session_id
            )
            
            # Format context for prompt
            formatted_context = self.format_context_for_prompt(rag_context)
            
            # Create augmented prompt
            augmented_prompt = f"""
Context from knowledge base:
{formatted_context}

User query: {query}

Please provide a response that takes into account the relevant context above.
If the context provides useful information, incorporate it naturally into your response.
If the context is not relevant, you can ignore it and respond normally.
"""
            
            return {
                "success": True,
                "augmented_prompt": augmented_prompt,
                "context": rag_context,
                "formatted_context": formatted_context,
                "base_response": base_response,
                "metadata": {
                    "retrieval_time": rag_context.retrieval_time,
                    "relevance_score": rag_context.relevance_score,
                    "context_summary": rag_context.context_summary,
                    "semantic_matches": len(rag_context.semantic_matches),
                    "knowledge_entities": len(rag_context.knowledge_entities),
                    "knowledge_relationships": len(rag_context.knowledge_relationships)
                }
            }
            
        except Exception as e:
            logger.error(f"Error in augmented response generation: {e}")
            return {
                "success": False,
                "error": str(e),
                "augmented_prompt": query,  # Fallback to original query
                "context": None,
                "metadata": {}
            }
    
    async def evaluate_context_quality(
        self,
        rag_context: RAGContext,
        user_feedback: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Evaluate the quality of retrieved context
        
        Args:
            rag_context: Context to evaluate
            user_feedback: Optional user feedback
            
        Returns:
            Dictionary with quality metrics
        """
        try:
            quality_metrics = {
                "relevance_score": rag_context.relevance_score,
                "context_coverage": {
                    "semantic_matches": len(rag_context.semantic_matches),
                    "knowledge_entities": len(rag_context.knowledge_entities),
                    "knowledge_relationships": len(rag_context.knowledge_relationships),
                    "conversation_history": len(rag_context.conversation_history)
                },
                "retrieval_performance": {
                    "retrieval_time": rag_context.retrieval_time,
                    "context_summary": rag_context.context_summary
                }
            }
            
            # Calculate quality score
            coverage_score = min(
                (len(rag_context.semantic_matches) / self.max_semantic_results +
                 len(rag_context.knowledge_entities) / self.max_knowledge_entities) / 2,
                1.0
            )
            
            performance_score = max(0, 1.0 - (rag_context.retrieval_time / 10.0))  # Penalize slow retrieval
            
            overall_quality = (
                rag_context.relevance_score * 0.5 +
                coverage_score * 0.3 +
                performance_score * 0.2
            )
            
            quality_metrics["overall_quality"] = overall_quality
            quality_metrics["user_feedback"] = user_feedback
            
            return {
                "success": True,
                "quality_metrics": quality_metrics,
                "evaluation_time": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error evaluating context quality: {e}")
            return {
                "success": False,
                "error": str(e)
            }
