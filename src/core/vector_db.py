"""
Vector Database Manager for SilentCodingLegend AI Agent
Handles vector embeddings, semantic search, and knowledge retrieval
"""

import os
import json
import asyncio
import logging
from typing import List, Dict, Any, Optional, Tuple, Union
from datetime import datetime, timedelta
from pathlib import Path
import hashlib
import uuid

import chromadb
from chromadb.config import Settings
import numpy as np
from sentence_transformers import SentenceTransformer
import tiktoken
from dataclasses import dataclass, asdict
from enum import Enum

logger = logging.getLogger(__name__)


class DocumentType(Enum):
    """Types of documents that can be stored"""
    CONVERSATION = "conversation"
    CODE_SNIPPET = "code_snippet"
    ERROR_LOG = "error_log"
    DOCUMENTATION = "documentation"
    KNOWLEDGE_NOTE = "knowledge_note"
    PLUGIN_INFO = "plugin_info"
    USER_PREFERENCE = "user_preference"


@dataclass
class Document:
    """Document structure for vector storage"""
    id: str
    content: str
    metadata: Dict[str, Any]
    doc_type: DocumentType
    timestamp: datetime
    embedding: Optional[List[float]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage"""
        return {
            "id": self.id,
            "content": self.content,
            "metadata": self.metadata,
            "doc_type": self.doc_type.value,
            "timestamp": self.timestamp.isoformat(),
            "embedding": self.embedding
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Document':
        """Create from dictionary"""
        return cls(
            id=data["id"],
            content=data["content"],
            metadata=data["metadata"],
            doc_type=DocumentType(data["doc_type"]),
            timestamp=datetime.fromisoformat(data["timestamp"]),
            embedding=data.get("embedding")
        )


class VectorDatabaseManager:
    """Manages vector embeddings and semantic search"""
    
    def __init__(self, db_path: str = None, model_name: str = "all-MiniLM-L6-v2"):
        self.db_path = Path(db_path) if db_path else Path.cwd() / "data" / "vector_db"
        self.db_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize embedding model
        self.model_name = model_name
        self.embedding_model = None
        self.embedding_dimension = None
        
        # Initialize ChromaDB
        self.client = None
        self.collection = None
        
        # Token counter for chunking
        self.encoding = tiktoken.get_encoding("cl100k_base")
        
        # Configuration
        self.max_chunk_tokens = 512
        self.chunk_overlap = 50
        self.similarity_threshold = 0.7
        
        self.initialized = False
    
    async def initialize(self) -> bool:
        """Initialize the vector database"""
        try:
            logger.info("Initializing Vector Database Manager...")
            
            # Initialize embedding model
            await self._initialize_embedding_model()
            
            # Initialize ChromaDB
            await self._initialize_chromadb()
            
            self.initialized = True
            logger.info("Vector Database Manager initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Vector Database Manager: {e}")
            return False
    
    async def _initialize_embedding_model(self):
        """Initialize the sentence transformer model"""
        try:
            logger.info(f"Loading embedding model: {self.model_name}")
            self.embedding_model = SentenceTransformer(self.model_name)
            
            # Get embedding dimension
            test_embedding = self.embedding_model.encode(["test"])
            self.embedding_dimension = len(test_embedding[0])
            
            logger.info(f"Embedding model loaded. Dimension: {self.embedding_dimension}")
            
        except Exception as e:
            logger.error(f"Failed to initialize embedding model: {e}")
            raise
    
    async def _initialize_chromadb(self):
        """Initialize ChromaDB client and collection"""
        try:
            # Create client with new API
            self.client = chromadb.PersistentClient(path=str(self.db_path))
            
            # Get or create collection
            collection_name = "silentcodinglegend_knowledge"
            try:
                self.collection = self.client.get_collection(
                    name=collection_name
                )
                logger.info(f"Loaded existing collection: {collection_name}")
            except Exception:
                self.collection = self.client.create_collection(
                    name=collection_name
                )
                logger.info(f"Created new collection: {collection_name}")
            
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB: {e}")
            raise
    
    def _chunk_text(self, text: str, metadata: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Split text into chunks for embedding"""
        if not text.strip():
            return []
        
        tokens = self.encoding.encode(text)
        chunks = []
        
        # Split into chunks with overlap
        start = 0
        chunk_id = 0
        
        while start < len(tokens):
            end = min(start + self.max_chunk_tokens, len(tokens))
            chunk_tokens = tokens[start:end]
            chunk_text = self.encoding.decode(chunk_tokens)
            
            chunk_metadata = (metadata or {}).copy()
            chunk_metadata.update({
                "chunk_id": chunk_id,
                "chunk_start": start,
                "chunk_end": end,
                "total_chunks": None,  # Will be set after all chunks are created
                "token_count": len(chunk_tokens)
            })
            
            chunks.append({
                "text": chunk_text,
                "metadata": chunk_metadata
            })
            
            chunk_id += 1
            start = max(start + self.max_chunk_tokens - self.chunk_overlap, end)
        
        # Update total chunks count
        for chunk in chunks:
            chunk["metadata"]["total_chunks"] = len(chunks)
        
        return chunks
    
    async def add_document(self, content: str, doc_type: DocumentType, 
                          metadata: Dict[str, Any] = None) -> str:
        """Add a document to the vector database"""
        if not self.initialized:
            raise RuntimeError("Vector database not initialized")
        
        try:
            # Generate document ID
            doc_id = str(uuid.uuid4())
            timestamp = datetime.now()
            
            # Prepare metadata
            doc_metadata = (metadata or {}).copy()
            doc_metadata.update({
                "doc_id": doc_id,
                "doc_type": doc_type.value,
                "timestamp": timestamp.isoformat(),
                "content_hash": hashlib.md5(content.encode()).hexdigest()
            })
            
            # Chunk the content
            chunks = self._chunk_text(content, doc_metadata)
            
            if not chunks:
                logger.warning("No chunks created from content")
                return doc_id
            
            # Generate embeddings for chunks
            chunk_texts = [chunk["text"] for chunk in chunks]
            embeddings = self.embedding_model.encode(chunk_texts).tolist()
            
            # Prepare data for ChromaDB
            chunk_ids = [f"{doc_id}_chunk_{i}" for i in range(len(chunks))]
            metadatas = [chunk["metadata"] for chunk in chunks]
            
            # Add to ChromaDB
            self.collection.add(
                ids=chunk_ids,
                embeddings=embeddings,
                documents=chunk_texts,
                metadatas=metadatas
            )
            
            logger.info(f"Added document {doc_id} with {len(chunks)} chunks")
            return doc_id
            
        except Exception as e:
            logger.error(f"Failed to add document: {e}")
            raise
    
    async def semantic_search(self, query: str, n_results: int = 10, 
                            doc_types: List[DocumentType] = None,
                            metadata_filter: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Perform semantic search"""
        if not self.initialized:
            raise RuntimeError("Vector database not initialized")
        
        try:
            # Generate query embedding
            query_embedding = self.embedding_model.encode([query])[0].tolist()
            
            # Prepare filters
            where_clause = {}
            if doc_types:
                where_clause["doc_type"] = {"$in": [dt.value for dt in doc_types]}
            
            if metadata_filter:
                where_clause.update(metadata_filter)
            
            # Perform search
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                where=where_clause if where_clause else None,
                include=["documents", "metadatas", "distances"]
            )
            
            # Format results
            search_results = []
            for i in range(len(results["ids"][0])):
                result = {
                    "id": results["ids"][0][i],
                    "content": results["documents"][0][i],
                    "metadata": results["metadatas"][0][i],
                    "similarity": 1 - results["distances"][0][i],  # Convert distance to similarity
                    "doc_type": DocumentType(results["metadatas"][0][i]["doc_type"])
                }
                search_results.append(result)
            
            logger.info(f"Semantic search returned {len(search_results)} results")
            return search_results
            
        except Exception as e:
            logger.error(f"Semantic search failed: {e}")
            raise
    
    async def get_similar_conversations(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """Find similar conversations"""
        return await self.semantic_search(
            query=query,
            n_results=n_results,
            doc_types=[DocumentType.CONVERSATION]
        )
    
    async def get_relevant_code(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """Find relevant code snippets"""
        return await self.semantic_search(
            query=query,
            n_results=n_results,
            doc_types=[DocumentType.CODE_SNIPPET]
        )
    
    async def get_documentation(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """Find relevant documentation"""
        return await self.semantic_search(
            query=query,
            n_results=n_results,
            doc_types=[DocumentType.DOCUMENTATION]
        )
    
    async def add_conversation(self, conversation_data: Dict[str, Any]) -> str:
        """Add a conversation to the knowledge base"""
        # Extract meaningful content from conversation
        messages = conversation_data.get("messages", [])
        content_parts = []
        
        for msg in messages:
            role = msg.get("role", "")
            content = msg.get("content", "")
            if content:
                content_parts.append(f"{role}: {content}")
        
        full_content = "\n\n".join(content_parts)
        
        metadata = {
            "conversation_id": conversation_data.get("id", "unknown"),
            "message_count": len(messages),
            "created_at": conversation_data.get("created_at", datetime.now().isoformat()),
            "topics": conversation_data.get("topics", []),
            "programming_languages": conversation_data.get("programming_languages", [])
        }
        
        return await self.add_document(
            content=full_content,
            doc_type=DocumentType.CONVERSATION,
            metadata=metadata
        )
    
    async def add_code_snippet(self, code: str, language: str, description: str = "", 
                             tags: List[str] = None) -> str:
        """Add a code snippet to the knowledge base"""
        content = f"Language: {language}\n\n"
        if description:
            content += f"Description: {description}\n\n"
        content += f"Code:\n{code}"
        
        metadata = {
            "language": language,
            "description": description,
            "tags": tags or [],
            "code_length": len(code),
            "lines": len(code.split('\n'))
        }
        
        return await self.add_document(
            content=content,
            doc_type=DocumentType.CODE_SNIPPET,
            metadata=metadata
        )
    
    async def get_conversation_context(self, current_message: str, n_results: int = 3) -> List[Dict[str, Any]]:
        """Get relevant context from previous conversations"""
        try:
            results = await self.get_similar_conversations(current_message, n_results)
            
            # Filter by similarity threshold
            relevant_results = [
                r for r in results 
                if r["similarity"] >= self.similarity_threshold
            ]
            
            return relevant_results
            
        except Exception as e:
            logger.error(f"Failed to get conversation context: {e}")
            return []
    
    async def delete_document(self, doc_id: str) -> bool:
        """Delete a document and all its chunks"""
        if not self.initialized:
            raise RuntimeError("Vector database not initialized")
        
        try:
            # Find all chunks for this document
            results = self.collection.get(
                where={"doc_id": doc_id},
                include=["documents", "metadatas"]
            )
            
            chunk_ids = results["ids"]
            
            if chunk_ids:
                self.collection.delete(ids=chunk_ids)
                logger.info(f"Deleted document {doc_id} with {len(chunk_ids)} chunks")
                return True
            else:
                logger.warning(f"No chunks found for document {doc_id}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to delete document {doc_id}: {e}")
            return False
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        if not self.initialized:
            return {"error": "Database not initialized"}
        
        try:
            # Get collection info
            count = self.collection.count()
            
            # Get document type distribution
            all_results = self.collection.get(include=["metadatas"])
            doc_types = {}
            for metadata in all_results["metadatas"]:
                doc_type = metadata.get("doc_type", "unknown")
                doc_types[doc_type] = doc_types.get(doc_type, 0) + 1
            
            return {
                "total_chunks": count,
                "document_types": doc_types,
                "embedding_dimension": self.embedding_dimension,
                "model_name": self.model_name,
                "database_path": str(self.db_path),
                "initialized": self.initialized
            }
            
        except Exception as e:
            logger.error(f"Failed to get stats: {e}")
            return {"error": str(e)}
    
    async def cleanup(self):
        """Cleanup resources"""
        if self.client:
            # ChromaDB client doesn't need explicit cleanup
            pass
        logger.info("Vector database cleanup completed")


# Global instance
vector_db_manager = VectorDatabaseManager()
