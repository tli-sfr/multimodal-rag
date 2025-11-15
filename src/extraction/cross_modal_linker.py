"""Cross-modal entity linking."""

from typing import List, Dict, Set, Tuple
from collections import defaultdict

from loguru import logger
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

from ..models import Entity, Relationship, RelationshipType, ModalityType


class CrossModalLinker:
    """Link entities across different modalities."""
    
    def __init__(self, similarity_threshold: float = 0.85):
        """Initialize cross-modal linker.
        
        Args:
            similarity_threshold: Threshold for entity matching
        """
        self.similarity_threshold = similarity_threshold
    
    def link_entities(
        self,
        entities: List[Entity]
    ) -> Tuple[List[Entity], List[Relationship]]:
        """Link entities across modalities.
        
        Args:
            entities: List of all entities
            
        Returns:
            Tuple of (merged entities, cross-modal relationships)
        """
        # Group entities by modality
        entities_by_modality = defaultdict(list)
        for entity in entities:
            entities_by_modality[entity.source_modality].append(entity)
        
        # Find cross-modal matches
        matches = self._find_cross_modal_matches(entities_by_modality)
        
        # Create relationships for matches
        relationships = []
        for entity1, entity2 in matches:
            rel = Relationship(
                source_entity_id=entity1.id,
                target_entity_id=entity2.id,
                relationship_type=RelationshipType.RELATED_TO,
                confidence=0.9,
                source_modality=entity1.source_modality,
                source_id=entity1.source_id,
                properties={'cross_modal_link': True}
            )
            relationships.append(rel)
        
        logger.info(f"Created {len(relationships)} cross-modal links")
        
        return entities, relationships
    
    def _find_cross_modal_matches(
        self,
        entities_by_modality: Dict[ModalityType, List[Entity]]
    ) -> List[Tuple[Entity, Entity]]:
        """Find matching entities across modalities.
        
        Args:
            entities_by_modality: Entities grouped by modality
            
        Returns:
            List of entity pairs that match
        """
        matches = []
        modalities = list(entities_by_modality.keys())
        
        # Compare entities across different modalities
        for i, mod1 in enumerate(modalities):
            for mod2 in modalities[i+1:]:
                entities1 = entities_by_modality[mod1]
                entities2 = entities_by_modality[mod2]
                
                # Find matches between these two modalities
                modal_matches = self._match_entity_lists(entities1, entities2)
                matches.extend(modal_matches)
        
        return matches
    
    def _match_entity_lists(
        self,
        entities1: List[Entity],
        entities2: List[Entity]
    ) -> List[Tuple[Entity, Entity]]:
        """Match entities from two lists.
        
        Args:
            entities1: First list of entities
            entities2: Second list of entities
            
        Returns:
            List of matching pairs
        """
        matches = []
        
        for e1 in entities1:
            for e2 in entities2:
                # Check if entities match
                if self._entities_match(e1, e2):
                    matches.append((e1, e2))
        
        return matches
    
    def _entities_match(self, entity1: Entity, entity2: Entity) -> bool:
        """Check if two entities match.
        
        Args:
            entity1: First entity
            entity2: Second entity
            
        Returns:
            True if entities match
        """
        # Must be same type
        if entity1.entity_type != entity2.entity_type:
            return False
        
        # Check name similarity
        name_sim = self._string_similarity(entity1.name, entity2.name)
        
        if name_sim >= self.similarity_threshold:
            return True
        
        # Check embedding similarity if available
        if entity1.embedding and entity2.embedding:
            emb_sim = self._embedding_similarity(
                entity1.embedding,
                entity2.embedding
            )
            if emb_sim >= self.similarity_threshold:
                return True
        
        return False
    
    def _string_similarity(self, str1: str, str2: str) -> float:
        """Calculate string similarity.
        
        Args:
            str1: First string
            str2: Second string
            
        Returns:
            Similarity score (0-1)
        """
        # Simple normalized edit distance
        str1 = str1.lower().strip()
        str2 = str2.lower().strip()
        
        if str1 == str2:
            return 1.0
        
        # Jaccard similarity on words
        words1 = set(str1.split())
        words2 = set(str2.split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union)
    
    def _embedding_similarity(
        self,
        emb1: List[float],
        emb2: List[float]
    ) -> float:
        """Calculate embedding similarity.
        
        Args:
            emb1: First embedding
            emb2: Second embedding
            
        Returns:
            Cosine similarity (0-1)
        """
        emb1_arr = np.array(emb1).reshape(1, -1)
        emb2_arr = np.array(emb2).reshape(1, -1)
        
        similarity = cosine_similarity(emb1_arr, emb2_arr)[0][0]
        
        # Convert from [-1, 1] to [0, 1]
        return (similarity + 1) / 2

