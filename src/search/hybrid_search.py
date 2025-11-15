"""Hybrid search combining multiple retrieval strategies."""

from typing import List, Dict, Any, Optional
from collections import defaultdict

from loguru import logger

from ..models import Query, SearchResult, ModalityType, Chunk, EntityType
from ..vector_store import QdrantVectorStore, EmbeddingGenerator
from ..graph import Neo4jClient
from ..extraction import EntityExtractor
from ..config import get_config


class HybridSearchEngine:
    """Hybrid search engine combining graph, keyword, and vector search."""

    def __init__(
        self,
        vector_store: QdrantVectorStore,
        graph_client: Neo4jClient,
        embedding_generator: EmbeddingGenerator,
        entity_extractor: Optional[EntityExtractor] = None,
        graph_weight: float = 0.3,
        keyword_weight: float = 0.2,
        vector_weight: float = 0.5,
        use_graph_filter: bool = True,
    ):
        """Initialize hybrid search engine.

        Args:
            vector_store: Vector store client
            graph_client: Graph database client
            embedding_generator: Embedding generator
            entity_extractor: Entity extractor for query analysis (optional)
            graph_weight: Weight for graph search results
            keyword_weight: Weight for keyword search results
            vector_weight: Weight for vector search results
            use_graph_filter: If True, filter out vector results not connected to query entities
        """
        self.vector_store = vector_store
        self.graph_client = graph_client
        self.embedding_generator = embedding_generator
        self.entity_extractor = entity_extractor
        self.use_graph_filter = use_graph_filter

        # Normalize weights
        total_weight = graph_weight + keyword_weight + vector_weight
        self.graph_weight = graph_weight / total_weight
        self.keyword_weight = keyword_weight / total_weight
        self.vector_weight = vector_weight / total_weight

        config = get_config()
        self.top_k = config.get('search.hybrid.vector_search.top_k', 20)
        self.score_threshold = config.get('search.hybrid.vector_search.score_threshold', 0.3)  # Lowered from 0.7 to 0.3
    
    def search(
        self,
        query: Query,
        top_k: Optional[int] = None,
        modality_filter: Optional[ModalityType] = None
    ) -> List[SearchResult]:
        """Perform hybrid search.
        
        Args:
            query: Search query
            top_k: Number of results to return
            modality_filter: Filter by modality
            
        Returns:
            Ranked list of search results
        """
        top_k = top_k or self.top_k
        
        logger.info(f"Performing hybrid search for: {query.text}")

        # 1. Vector search
        vector_results = self._vector_search(query, modality_filter)

        # 2. Graph search (if entities detected)
        graph_results = self._graph_search(query)

        # 3. Apply graph-based filtering if enabled
        if self.use_graph_filter and graph_results:
            vector_results = self._apply_graph_filter(vector_results, graph_results)
            logger.info(f"Graph filter applied: {len(vector_results)} vector results remain")

        # 4. Keyword search (simple BM25-like)
        keyword_results = self._keyword_search(query, modality_filter)

        # 5. Fuse results
        fused_results = self._fuse_results(
            vector_results,
            graph_results,
            keyword_results
        )

        # 6. Rerank and return top-k
        final_results = fused_results[:top_k]

        logger.info(f"Hybrid search returned {len(final_results)} results")
        return final_results
    
    def _vector_search(
        self,
        query: Query,
        modality_filter: Optional[ModalityType]
    ) -> List[SearchResult]:
        """Perform vector similarity search.
        
        Args:
            query: Search query
            modality_filter: Modality filter
            
        Returns:
            Search results
        """
        try:
            # Generate query embedding
            query_embedding = self.embedding_generator.generate_for_query(query.text)
            
            # Search vector store
            results = self.vector_store.search(
                query_embedding=query_embedding,
                top_k=self.top_k,
                score_threshold=self.score_threshold,
                modality_filter=modality_filter
            )
            
            return results
        
        except Exception as e:
            logger.error(f"Vector search failed: {e}")
            return []
    
    def _graph_search(self, query: Query) -> List[SearchResult]:
        """Perform graph-based search using knowledge graph.

        Strategy:
        1. Extract potential entity names from query text
        2. Find matching entities in Neo4j graph
        3. Traverse relationships to find related entities
        4. Retrieve source chunks from Qdrant
        5. Return as SearchResults with graph-based scores

        Args:
            query: Search query

        Returns:
            Search results from graph traversal
        """
        try:
            # Step 1: Extract potential entity names from query
            # Clean the query text: remove possessives, punctuation
            import re

            # Remove possessive 's
            cleaned_text = re.sub(r"'s\b", "", query.text)

            # Split into words
            query_words = cleaned_text.split()

            # Also try the full cleaned query as an entity name
            potential_entities = [cleaned_text] + query_words

            # Filter out very short words and common stop words
            stop_words = {'what', 'is', 'the', 'a', 'an', 'about', 'how', 'why', 'when', 'where',
                         'who', 'which', 'their', 'his', 'her', 'its', 'our', 'your', 'my',
                         'opinion', 'view', 'think', 'thought', 'idea', 'belief'}

            potential_entities = [
                e for e in potential_entities
                if len(e) > 2 and e.lower() not in stop_words
            ]

            if not potential_entities:
                logger.debug("No potential entities found in query")
                return []

            logger.debug(f"Searching for entities: {potential_entities}")

            # Step 2: Find matching entities in graph
            matched_entities = self.graph_client.find_entities_by_name(
                entity_names=potential_entities,
                fuzzy=True,
                limit=10
            )

            if not matched_entities:
                logger.debug("No matching entities found in graph")
                return []

            logger.info(f"Found {len(matched_entities)} matching entities in graph")

            # Step 3: Get entity IDs and traverse relationships
            entity_ids = [e['id'] for e in matched_entities]

            related_chunks = self.graph_client.find_related_chunks(
                entity_ids=entity_ids,
                max_depth=2,  # Traverse up to 2 relationships away
                limit=20
            )

            if not related_chunks:
                logger.debug("No related chunks found through graph traversal")
                return []

            logger.info(f"Found {len(related_chunks)} related chunks through graph")

            # Step 4: Retrieve chunks from Qdrant
            chunk_ids = [c['chunk_id'] for c in related_chunks]
            search_results = self.vector_store.retrieve_by_ids(chunk_ids)

            # Step 5: Update scores based on graph relevance
            # Create a mapping of chunk_id to relevance score
            relevance_map = {c['chunk_id']: c['relevance'] for c in related_chunks}

            for result in search_results:
                chunk_id = str(result.id)
                if chunk_id in relevance_map:
                    result.score = relevance_map[chunk_id]
                    result.source = 'graph'

            logger.info(f"Graph search returned {len(search_results)} results")
            return search_results

        except Exception as e:
            logger.error(f"Graph search failed: {e}")
            return []
    
    def _apply_graph_filter(
        self,
        vector_results: List[SearchResult],
        graph_results: List[SearchResult]
    ) -> List[SearchResult]:
        """Filter vector results to only include chunks connected to query entities.

        Args:
            vector_results: Results from vector search
            graph_results: Results from graph search (chunks connected to query entities)

        Returns:
            Filtered vector results containing only graph-connected chunks
        """
        # Build set of chunk IDs that are connected to query entities
        graph_chunk_ids = {str(result.id) for result in graph_results}

        # Filter vector results to only include chunks in the graph
        filtered_results = [
            result for result in vector_results
            if str(result.id) in graph_chunk_ids
        ]

        logger.info(
            f"Graph filter: {len(vector_results)} vector results -> "
            f"{len(filtered_results)} graph-connected results "
            f"({len(vector_results) - len(filtered_results)} excluded)"
        )

        return filtered_results

    def _keyword_search(
        self,
        query: Query,
        modality_filter: Optional[ModalityType]
    ) -> List[SearchResult]:
        """Perform keyword-based search.

        Args:
            query: Search query
            modality_filter: Modality filter

        Returns:
            Search results
        """
        # Simplified keyword search
        # In production, this would use BM25 or similar
        return []
    
    def _fuse_results(
        self,
        vector_results: List[SearchResult],
        graph_results: List[SearchResult],
        keyword_results: List[SearchResult]
    ) -> List[SearchResult]:
        """Fuse results from different search strategies.
        
        Args:
            vector_results: Results from vector search
            graph_results: Results from graph search
            keyword_results: Results from keyword search
            
        Returns:
            Fused and ranked results
        """
        # Combine results with weighted scores
        result_scores: Dict[str, tuple] = {}
        
        # Add vector results
        for result in vector_results:
            result_id = str(result.id)
            weighted_score = result.score * self.vector_weight
            result_scores[result_id] = (result, weighted_score)
        
        # Add graph results
        for result in graph_results:
            result_id = str(result.id)
            weighted_score = result.score * self.graph_weight

            if result_id in result_scores:
                # Combine scores and update source to show it came from both
                existing_result, existing_score = result_scores[result_id]
                # Update source to indicate hybrid
                if existing_result.source != result.source:
                    existing_result.source = f"{existing_result.source}+graph"
                result_scores[result_id] = (existing_result, existing_score + weighted_score)
            else:
                result_scores[result_id] = (result, weighted_score)
        
        # Add keyword results
        for result in keyword_results:
            result_id = str(result.id)
            weighted_score = result.score * self.keyword_weight
            
            if result_id in result_scores:
                existing_result, existing_score = result_scores[result_id]
                result_scores[result_id] = (existing_result, existing_score + weighted_score)
            else:
                result_scores[result_id] = (result, weighted_score)
        
        # Sort by combined score
        sorted_results = sorted(
            result_scores.values(),
            key=lambda x: x[1],
            reverse=True
        )
        
        # Update scores and return
        final_results = []
        for result, score in sorted_results:
            result.score = score
            final_results.append(result)
        
        return final_results

