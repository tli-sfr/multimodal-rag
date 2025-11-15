"""Graph-based search using Neo4j."""

from typing import List, Optional
from uuid import UUID

from loguru import logger

from ..models import Query, SearchResult, ModalityType
from ..graph import Neo4jClient


class GraphSearcher:
    """Search using knowledge graph traversal."""
    
    def __init__(
        self,
        neo4j_client: Neo4jClient,
        max_depth: int = 3,
        max_results: int = 20
    ):
        """Initialize graph searcher.
        
        Args:
            neo4j_client: Neo4j client
            max_depth: Maximum traversal depth
            max_results: Maximum results to return
        """
        self.client = neo4j_client
        self.max_depth = max_depth
        self.max_results = max_results
    
    def search(
        self,
        query: Query,
        entity_names: Optional[List[str]] = None
    ) -> List[SearchResult]:
        """Search graph for relevant entities and relationships.
        
        Args:
            query: Search query
            entity_names: Optional list of entity names to start from
            
        Returns:
            List of search results
        """
        if not entity_names:
            # Extract potential entity names from query
            entity_names = self._extract_entity_names(query.text)
        
        if not entity_names:
            logger.debug("No entities found in query for graph search")
            return []
        
        # Find matching entities in graph
        results = []
        
        for entity_name in entity_names:
            entity_results = self._search_from_entity(entity_name)
            results.extend(entity_results)
        
        # Deduplicate and limit results
        unique_results = self._deduplicate_results(results)
        
        return unique_results[:self.max_results]
    
    def _extract_entity_names(self, text: str) -> List[str]:
        """Extract potential entity names from text.
        
        Args:
            text: Query text
            
        Returns:
            List of potential entity names
        """
        # Simple extraction - in production, use NER
        # For now, just return capitalized words
        words = text.split()
        entities = []
        
        for word in words:
            if word[0].isupper() and len(word) > 2:
                entities.append(word)
        
        return entities
    
    def _search_from_entity(self, entity_name: str) -> List[SearchResult]:
        """Search graph starting from an entity.
        
        Args:
            entity_name: Entity name to start from
            
        Returns:
            List of search results
        """
        # Simplified graph search
        # In production, this would:
        # 1. Find entity in graph
        # 2. Traverse relationships up to max_depth
        # 3. Collect connected documents/chunks
        # 4. Return as SearchResults
        
        # For now, return empty list
        # This is a placeholder for the full implementation
        return []
    
    def _deduplicate_results(
        self,
        results: List[SearchResult]
    ) -> List[SearchResult]:
        """Deduplicate search results.
        
        Args:
            results: List of results
            
        Returns:
            Deduplicated results
        """
        seen_ids = set()
        unique_results = []
        
        for result in results:
            if result.id not in seen_ids:
                seen_ids.add(result.id)
                unique_results.append(result)
        
        return unique_results

