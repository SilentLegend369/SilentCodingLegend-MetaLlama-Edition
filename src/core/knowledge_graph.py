"""
Knowledge Graph Manager for SilentCodingLegend AI Agent
Manages relationships between concepts, entities, and knowledge pieces
"""

import json
import asyncio
import logging
from typing import Dict, List, Any, Optional, Set, Tuple
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass, asdict
from enum import Enum
import networkx as nx
import pickle

logger = logging.getLogger(__name__)


class RelationType(Enum):
    """Types of relationships in the knowledge graph"""
    RELATED_TO = "related_to"
    DEPENDS_ON = "depends_on"
    IMPLEMENTS = "implements"
    USES = "uses"
    CONTAINS = "contains"
    SIMILAR_TO = "similar_to"
    FOLLOWS_FROM = "follows_from"
    RESOLVES = "resolves"
    CAUSES = "causes"
    MENTIONED_WITH = "mentioned_with"


class EntityType(Enum):
    """Types of entities in the knowledge graph"""
    CONCEPT = "concept"
    CODE_FILE = "code_file"
    FUNCTION = "function"
    CLASS = "class"
    VARIABLE = "variable"
    ERROR = "error"
    TECHNOLOGY = "technology"
    FRAMEWORK = "framework"
    LIBRARY = "library"
    PERSON = "person"
    PROJECT = "project"
    CONVERSATION = "conversation"


@dataclass
class Entity:
    """Knowledge graph entity"""
    id: str
    name: str
    entity_type: EntityType
    properties: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "entity_type": self.entity_type.value,
            "properties": self.properties,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Entity':
        return cls(
            id=data["id"],
            name=data["name"],
            entity_type=EntityType(data["entity_type"]),
            properties=data["properties"],
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"])
        )


@dataclass
class Relationship:
    """Knowledge graph relationship"""
    id: str
    source_id: str
    target_id: str
    relation_type: RelationType
    properties: Dict[str, Any]
    weight: float
    created_at: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "source_id": self.source_id,
            "target_id": self.target_id,
            "relation_type": self.relation_type.value,
            "properties": self.properties,
            "weight": self.weight,
            "created_at": self.created_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Relationship':
        return cls(
            id=data["id"],
            source_id=data["source_id"],
            target_id=data["target_id"],
            relation_type=RelationType(data["relation_type"]),
            properties=data["properties"],
            weight=data["weight"],
            created_at=datetime.fromisoformat(data["created_at"])
        )


class KnowledgeGraphManager:
    """Manages the knowledge graph for long-term memory"""
    
    def __init__(self, db_path: str = None):
        self.db_path = Path(db_path) if db_path else Path.cwd() / "data" / "knowledge_graph"
        self.db_path.mkdir(parents=True, exist_ok=True)
        
        # NetworkX graph for in-memory operations
        self.graph = nx.MultiDiGraph()
        
        # Storage files
        self.entities_file = self.db_path / "entities.json"
        self.relationships_file = self.db_path / "relationships.json"
        self.graph_file = self.db_path / "graph.pickle"
        
        # In-memory storage
        self.entities: Dict[str, Entity] = {}
        self.relationships: Dict[str, Relationship] = {}
        
        self.initialized = False
    
    async def initialize(self) -> bool:
        """Initialize the knowledge graph"""
        try:
            logger.info("Initializing Knowledge Graph Manager...")
            
            # Load existing data
            await self._load_entities()
            await self._load_relationships()
            await self._rebuild_graph()
            
            self.initialized = True
            logger.info("Knowledge Graph Manager initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Knowledge Graph Manager: {e}")
            return False
    
    async def _load_entities(self):
        """Load entities from storage"""
        if self.entities_file.exists():
            try:
                with open(self.entities_file, 'r') as f:
                    entities_data = json.load(f)
                
                for entity_data in entities_data:
                    entity = Entity.from_dict(entity_data)
                    self.entities[entity.id] = entity
                
                logger.info(f"Loaded {len(self.entities)} entities")
            except Exception as e:
                logger.error(f"Failed to load entities: {e}")
    
    async def _load_relationships(self):
        """Load relationships from storage"""
        if self.relationships_file.exists():
            try:
                with open(self.relationships_file, 'r') as f:
                    relationships_data = json.load(f)
                
                for rel_data in relationships_data:
                    relationship = Relationship.from_dict(rel_data)
                    self.relationships[relationship.id] = relationship
                
                logger.info(f"Loaded {len(self.relationships)} relationships")
            except Exception as e:
                logger.error(f"Failed to load relationships: {e}")
    
    async def _rebuild_graph(self):
        """Rebuild the NetworkX graph from entities and relationships"""
        self.graph.clear()
        
        # Add entities as nodes
        for entity in self.entities.values():
            self.graph.add_node(
                entity.id,
                name=entity.name,
                entity_type=entity.entity_type.value,
                properties=entity.properties,
                created_at=entity.created_at,
                updated_at=entity.updated_at
            )
        
        # Add relationships as edges
        for relationship in self.relationships.values():
            if (relationship.source_id in self.entities and 
                relationship.target_id in self.entities):
                self.graph.add_edge(
                    relationship.source_id,
                    relationship.target_id,
                    key=relationship.id,
                    relation_type=relationship.relation_type.value,
                    weight=relationship.weight,
                    properties=relationship.properties,
                    created_at=relationship.created_at
                )
        
        logger.info(f"Rebuilt graph with {len(self.graph.nodes)} nodes and {len(self.graph.edges)} edges")
    
    async def save_to_disk(self):
        """Save entities and relationships to disk"""
        try:
            # Save entities
            entities_data = [entity.to_dict() for entity in self.entities.values()]
            with open(self.entities_file, 'w') as f:
                json.dump(entities_data, f, indent=2)
            
            # Save relationships
            relationships_data = [rel.to_dict() for rel in self.relationships.values()]
            with open(self.relationships_file, 'w') as f:
                json.dump(relationships_data, f, indent=2)
            
            # Save NetworkX graph
            with open(self.graph_file, 'wb') as f:
                pickle.dump(self.graph, f)
            
            logger.info("Knowledge graph saved to disk")
            
        except Exception as e:
            logger.error(f"Failed to save knowledge graph: {e}")
    
    async def add_entity(self, name: str, entity_type: EntityType, 
                        properties: Dict[str, Any] = None) -> str:
        """Add an entity to the knowledge graph"""
        if not self.initialized:
            raise RuntimeError("Knowledge graph not initialized")
        
        entity_id = f"{entity_type.value}_{name}_{datetime.now().timestamp()}"
        
        entity = Entity(
            id=entity_id,
            name=name,
            entity_type=entity_type,
            properties=properties or {},
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        self.entities[entity_id] = entity
        
        # Add to NetworkX graph
        self.graph.add_node(
            entity_id,
            name=name,
            entity_type=entity_type.value,
            properties=properties or {},
            created_at=entity.created_at,
            updated_at=entity.updated_at
        )
        
        logger.info(f"Added entity: {name} ({entity_type.value})")
        return entity_id
    
    async def add_relationship(self, source_id: str, target_id: str, 
                             relation_type: RelationType, weight: float = 1.0,
                             properties: Dict[str, Any] = None) -> str:
        """Add a relationship between entities"""
        if not self.initialized:
            raise RuntimeError("Knowledge graph not initialized")
        
        if source_id not in self.entities or target_id not in self.entities:
            raise ValueError("Source or target entity not found")
        
        relationship_id = f"rel_{source_id}_{target_id}_{relation_type.value}_{datetime.now().timestamp()}"
        
        relationship = Relationship(
            id=relationship_id,
            source_id=source_id,
            target_id=target_id,
            relation_type=relation_type,
            properties=properties or {},
            weight=weight,
            created_at=datetime.now()
        )
        
        self.relationships[relationship_id] = relationship
        
        # Add to NetworkX graph
        self.graph.add_edge(
            source_id,
            target_id,
            key=relationship_id,
            relation_type=relation_type.value,
            weight=weight,
            properties=properties or {},
            created_at=relationship.created_at
        )
        
        logger.info(f"Added relationship: {relation_type.value} between {source_id} and {target_id}")
        return relationship_id
    
    async def find_entity_by_name(self, name: str, entity_type: EntityType = None) -> List[Entity]:
        """Find entities by name"""
        results = []
        for entity in self.entities.values():
            if entity.name.lower() == name.lower():
                if entity_type is None or entity.entity_type == entity_type:
                    results.append(entity)
        return results
    
    async def get_related_entities(self, entity_id: str, max_depth: int = 2) -> List[Dict[str, Any]]:
        """Get entities related to a given entity"""
        if entity_id not in self.graph:
            return []
        
        related = []
        visited = set()
        
        def traverse(current_id: str, depth: int):
            if depth > max_depth or current_id in visited:
                return
            
            visited.add(current_id)
            
            # Get neighbors
            for neighbor in self.graph.neighbors(current_id):
                if neighbor not in visited:
                    # Get edge data
                    edge_data = self.graph.get_edge_data(current_id, neighbor)
                    
                    for edge_key, edge_attrs in edge_data.items():
                        related.append({
                            "entity": self.entities[neighbor],
                            "relationship_type": edge_attrs["relation_type"],
                            "weight": edge_attrs["weight"],
                            "depth": depth + 1,
                            "path_length": depth + 1
                        })
                    
                    if depth < max_depth:
                        traverse(neighbor, depth + 1)
        
        traverse(entity_id, 0)
        
        # Sort by weight and depth
        related.sort(key=lambda x: (-x["weight"], x["depth"]))
        return related
    
    async def find_shortest_path(self, source_id: str, target_id: str) -> List[str]:
        """Find shortest path between two entities"""
        try:
            path = nx.shortest_path(self.graph, source_id, target_id)
            return path
        except nx.NetworkXNoPath:
            return []
    
    async def get_central_entities(self, n: int = 10) -> List[Tuple[str, float]]:
        """Get most central entities in the graph"""
        try:
            centrality = nx.degree_centrality(self.graph)
            sorted_centrality = sorted(centrality.items(), key=lambda x: x[1], reverse=True)
            return sorted_centrality[:n]
        except Exception as e:
            logger.error(f"Failed to calculate centrality: {e}")
            return []
    
    async def get_communities(self) -> List[List[str]]:
        """Detect communities in the knowledge graph"""
        try:
            # Convert to undirected graph for community detection
            undirected_graph = self.graph.to_undirected()
            
            # Use Louvain algorithm for community detection
            import networkx.algorithms.community as nx_comm
            communities = list(nx_comm.louvain_communities(undirected_graph))
            
            return [list(community) for community in communities]
        except Exception as e:
            logger.error(f"Failed to detect communities: {e}")
            return []
    
    async def extract_entities_from_text(self, text: str, context: Dict[str, Any] = None) -> List[str]:
        """Extract entities from text and add to knowledge graph"""
        entities_added = []
        
        # Simple entity extraction (can be enhanced with NLP libraries)
        # For now, we'll extract programming-related terms
        
        programming_keywords = {
            'python', 'javascript', 'java', 'c++', 'react', 'vue', 'angular',
            'django', 'flask', 'fastapi', 'streamlit', 'numpy', 'pandas',
            'tensorflow', 'pytorch', 'git', 'docker', 'kubernetes'
        }
        
        words = text.lower().split()
        
        for word in words:
            word_clean = word.strip('.,!?()[]{}";:')
            if word_clean in programming_keywords:
                # Check if entity already exists
                existing = await self.find_entity_by_name(word_clean, EntityType.TECHNOLOGY)
                if not existing:
                    entity_id = await self.add_entity(
                        name=word_clean,
                        entity_type=EntityType.TECHNOLOGY,
                        properties={
                            "extracted_from": context.get("source", "text"),
                            "extraction_timestamp": datetime.now().isoformat()
                        }
                    )
                    entities_added.append(entity_id)
        
        return entities_added
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get knowledge graph statistics"""
        if not self.initialized:
            return {"error": "Knowledge graph not initialized"}
        
        try:
            entity_types = {}
            for entity in self.entities.values():
                entity_type = entity.entity_type.value
                entity_types[entity_type] = entity_types.get(entity_type, 0) + 1
            
            relation_types = {}
            for relationship in self.relationships.values():
                rel_type = relationship.relation_type.value
                relation_types[rel_type] = relation_types.get(rel_type, 0) + 1
            
            # Graph metrics
            num_nodes = len(self.graph.nodes)
            num_edges = len(self.graph.edges)
            density = nx.density(self.graph) if num_nodes > 1 else 0
            
            # Connected components
            num_components = nx.number_weakly_connected_components(self.graph)
            
            return {
                "total_entities": len(self.entities),
                "total_relationships": len(self.relationships),
                "entity_types": entity_types,
                "relationship_types": relation_types,
                "graph_nodes": num_nodes,
                "graph_edges": num_edges,
                "graph_density": density,
                "connected_components": num_components,
                "database_path": str(self.db_path),
                "initialized": self.initialized
            }
            
        except Exception as e:
            logger.error(f"Failed to get stats: {e}")
            return {"error": str(e)}
    
    async def cleanup(self):
        """Cleanup and save"""
        await self.save_to_disk()
        logger.info("Knowledge graph cleanup completed")
    
    async def search_entities(self, query: str, limit: int = 10) -> List[Entity]:
        """Search entities by name or properties containing the query text"""
        results = []
        query_lower = query.lower()
        
        for entity in self.entities.values():
            # Search in entity name
            if query_lower in entity.name.lower():
                results.append(entity)
                continue
                
            # Search in entity properties
            for prop_value in entity.properties.values():
                if isinstance(prop_value, str) and query_lower in prop_value.lower():
                    results.append(entity)
                    break
        
        # Sort by relevance (exact matches first, then partial matches)
        results.sort(key=lambda e: (
            0 if e.name.lower() == query_lower else 1,
            e.name.lower()
        ))
        
        return results[:limit]
    
    async def get_relationships_between(self, entity_ids: List[str]) -> List[Relationship]:
        """Get relationships between specific entities"""
        try:
            relationships = []
            for relationship in self.relationships.values():
                if relationship.source_id in entity_ids and relationship.target_id in entity_ids:
                    relationships.append(relationship)
            return relationships
        except Exception as e:
            logger.error(f"Error getting relationships between entities: {e}")
            return []

    async def get_entity_relationships(self, entity_id: str) -> List[Relationship]:
        """Get all relationships for a specific entity"""
        try:
            relationships = []
            for relationship in self.relationships.values():
                if relationship.source_id == entity_id or relationship.target_id == entity_id:
                    relationships.append(relationship)
            return relationships
        except Exception as e:
            logger.error(f"Error getting entity relationships: {e}")
            return []


# Global instance
knowledge_graph_manager = KnowledgeGraphManager()
