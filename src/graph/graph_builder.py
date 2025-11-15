"""Graph builder for constructing knowledge graphs from documents."""

from typing import List
from loguru import logger

from ..models import Document, Entity, Relationship
from .neo4j_client import Neo4jClient


class GraphBuilder:
    """Build knowledge graph from documents."""
    
    def __init__(self, neo4j_client: Neo4jClient):
        """Initialize graph builder.
        
        Args:
            neo4j_client: Neo4j client instance
        """
        self.client = neo4j_client
    
    def build_from_documents(self, documents: List[Document]) -> None:
        """Build graph from multiple documents.
        
        Args:
            documents: List of processed documents
        """
        logger.info(f"Building graph from {len(documents)} documents")
        
        # Collect all entities and relationships
        all_entities = []
        all_relationships = []
        
        for doc in documents:
            all_entities.extend(doc.entities)
            all_relationships.extend(doc.relationships)
        
        # Add to graph
        if all_entities:
            self.client.add_entities_batch(all_entities)
        
        if all_relationships:
            self.client.add_relationships_batch(all_relationships)
        
        logger.info(
            f"Added {len(all_entities)} entities and "
            f"{len(all_relationships)} relationships to graph"
        )
    
    def build_from_document(self, document: Document) -> None:
        """Build graph from single document.
        
        Args:
            document: Processed document
        """
        if document.entities:
            self.client.add_entities_batch(document.entities)
        
        if document.relationships:
            self.client.add_relationships_batch(document.relationships)
        
        logger.info(
            f"Added {len(document.entities)} entities and "
            f"{len(document.relationships)} relationships from {document.title}"
        )

