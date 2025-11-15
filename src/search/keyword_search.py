"""Keyword-based search using BM25."""

from typing import List, Optional
from rank_bm25 import BM25Okapi
from loguru import logger

from ..models import Query, SearchResult, ModalityType, Chunk


class KeywordSearcher:
    """Keyword-based search using BM25 algorithm."""
    
    def __init__(self, k1: float = 1.5, b: float = 0.75):
        """Initialize keyword searcher.
        
        Args:
            k1: BM25 k1 parameter
            b: BM25 b parameter
        """
        self.k1 = k1
        self.b = b
        self.bm25 = None
        self.chunks = []
    
    def index_chunks(self, chunks: List[Chunk]) -> None:
        """Index chunks for keyword search.
        
        Args:
            chunks: List of chunks to index
        """
        self.chunks = chunks
        
        # Tokenize chunks
        tokenized_corpus = [
            chunk.content.lower().split()
            for chunk in chunks
        ]
        
        # Create BM25 index
        self.bm25 = BM25Okapi(tokenized_corpus)
        
        logger.info(f"Indexed {len(chunks)} chunks for keyword search")
    
    def search(
        self,
        query: Query,
        top_k: int = 20,
        modality_filter: Optional[ModalityType] = None
    ) -> List[SearchResult]:
        """Search using BM25 keyword matching.
        
        Args:
            query: Search query
            top_k: Number of results to return
            modality_filter: Filter by modality
            
        Returns:
            List of search results
        """
        if not self.bm25 or not self.chunks:
            logger.warning("No chunks indexed for keyword search")
            return []
        
        # Tokenize query
        tokenized_query = query.text.lower().split()
        
        # Get BM25 scores
        scores = self.bm25.get_scores(tokenized_query)
        
        # Create results with scores
        results = []
        for idx, score in enumerate(scores):
            chunk = self.chunks[idx]
            
            # Apply modality filter
            if modality_filter and chunk.modality != modality_filter:
                continue
            
            # Only include results with positive scores
            if score > 0:
                result = SearchResult(
                    id=chunk.id,
                    content=chunk.content,
                    score=float(score),
                    modality=chunk.modality,
                    metadata=chunk.metadata.model_dump(),
                    source='keyword'
                )
                results.append(result)
        
        # Sort by score and return top-k
        results.sort(key=lambda x: x.score, reverse=True)
        
        logger.info(f"Keyword search found {len(results[:top_k])} results")
        return results[:top_k]

