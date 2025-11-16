"""Qdrant vector store client."""

from typing import List, Dict, Any, Optional
from uuid import UUID

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue,
)
from loguru import logger

from ..models import Chunk, SearchResult, ModalityType
from ..config import get_settings


class QdrantVectorStore:
    """Qdrant vector store for semantic search."""
    
    def __init__(
        self,
        host: Optional[str] = None,
        port: Optional[int] = None,
        collection_name: str = "multimodal_chunks"
    ):
        """Initialize Qdrant client.
        
        Args:
            host: Qdrant host
            port: Qdrant port
            collection_name: Collection name
        """
        settings = get_settings()
        
        self.host = host or settings.qdrant_host
        self.port = port or settings.qdrant_port
        self.collection_name = collection_name
        
        self.client = QdrantClient(host=self.host, port=self.port)
        
        logger.info(f"Connected to Qdrant at {self.host}:{self.port}")

    def _get_vector_config(
        self,
        vector_size: int = 3072,
        distance: Distance = Distance.COSINE
    ) -> VectorParams:
        """Get vector configuration for collection.

        Args:
            vector_size: Size of embedding vectors
            distance: Distance metric

        Returns:
            VectorParams configuration
        """
        return VectorParams(
            size=vector_size,
            distance=distance
        )

    def create_collection(
        self,
        vector_size: int = 3072,
        distance: Distance = Distance.COSINE
    ) -> None:
        """Create collection if it doesn't exist.
        
        Args:
            vector_size: Size of embedding vectors
            distance: Distance metric
        """
        try:
            # Check if collection exists
            collections = self.client.get_collections().collections
            exists = any(c.name == self.collection_name for c in collections)
            
            if not exists:
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=self._get_vector_config(vector_size, distance)
                )
                logger.info(f"Created collection: {self.collection_name}")
            else:
                logger.info(f"Collection already exists: {self.collection_name}")
        
        except Exception as e:
            logger.error(f"Failed to create collection: {e}")
            raise
    
    def add_chunk(
        self,
        chunk: Chunk,
        embedding: List[float]
    ) -> None:
        """Add chunk with embedding to vector store.
        
        Args:
            chunk: Content chunk
            embedding: Embedding vector
        """
        point = PointStruct(
            id=str(chunk.id),
            vector=embedding,
            payload={
                'content': chunk.content,
                'modality': chunk.modality.value,
                'chunk_index': chunk.chunk_index,
                'parent_id': str(chunk.parent_id) if chunk.parent_id else None,
                'metadata': chunk.metadata.model_dump()
            }
        )
        
        self.client.upsert(
            collection_name=self.collection_name,
            points=[point]
        )
    
    def add_chunks_batch(
        self,
        chunks: List[Chunk],
        embeddings: List[List[float]],
        batch_size: int = 100
    ) -> None:
        """Add multiple chunks in batch.
        
        Args:
            chunks: List of chunks
            embeddings: List of embeddings
            batch_size: Batch size for upload
        """
        if len(chunks) != len(embeddings):
            raise ValueError("Number of chunks and embeddings must match")
        
        for i in range(0, len(chunks), batch_size):
            batch_chunks = chunks[i:i + batch_size]
            batch_embeddings = embeddings[i:i + batch_size]
            
            points = [
                PointStruct(
                    id=str(chunk.id),
                    vector=embedding,
                    payload={
                        'content': chunk.content,
                        'modality': chunk.modality.value,
                        'chunk_index': chunk.chunk_index,
                        'parent_id': str(chunk.parent_id) if chunk.parent_id else None,
                        'metadata': chunk.metadata.model_dump()
                    }
                )
                for chunk, embedding in zip(batch_chunks, batch_embeddings)
            ]
            
            self.client.upsert(
                collection_name=self.collection_name,
                points=points
            )
        
        logger.info(f"Added {len(chunks)} chunks to vector store")
    
    def search(
        self,
        query_embedding: List[float],
        top_k: int = 10,
        score_threshold: float = 0.7,
        modality_filter: Optional[ModalityType] = None
    ) -> List[SearchResult]:
        """Search for similar chunks.
        
        Args:
            query_embedding: Query embedding vector
            top_k: Number of results to return
            score_threshold: Minimum similarity score
            modality_filter: Filter by modality type
            
        Returns:
            List of search results
        """
        # Build filter
        query_filter = None
        if modality_filter:
            query_filter = Filter(
                must=[
                    FieldCondition(
                        key="modality",
                        match=MatchValue(value=modality_filter.value)
                    )
                ]
            )
        
        # Search
        results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_embedding,
            limit=top_k,
            score_threshold=score_threshold,
            query_filter=query_filter
        )
        
        # Convert to SearchResult objects
        search_results = []
        for result in results:
            search_result = SearchResult(
                id=UUID(result.id),
                content=result.payload['content'],
                score=result.score,
                modality=ModalityType(result.payload['modality']),
                metadata=result.payload.get('metadata', {}),
                source='vector'
            )
            search_results.append(search_result)
        
        logger.info(f"Found {len(search_results)} results from vector search")
        return search_results

    def retrieve_by_ids(
        self,
        chunk_ids: List[str]
    ) -> List[SearchResult]:
        """Retrieve chunks by their IDs.

        Args:
            chunk_ids: List of chunk IDs to retrieve

        Returns:
            List of search results (score will be 0.0 for direct retrieval)
        """
        if not chunk_ids:
            return []

        try:
            logger.debug(f"Attempting to retrieve {len(chunk_ids)} chunks by ID: {chunk_ids[:3]}...")

            # Retrieve points by IDs
            results = self.client.retrieve(
                collection_name=self.collection_name,
                ids=chunk_ids,
                with_payload=True,
                with_vectors=False
            )

            logger.debug(f"Qdrant returned {len(results)} results")

            # Convert to SearchResult objects
            search_results = []
            for result in results:
                try:
                    search_result = SearchResult(
                        id=UUID(result.id) if isinstance(result.id, str) else result.id,
                        content=result.payload['content'],
                        score=0.0,  # No similarity score for direct retrieval
                        modality=ModalityType(result.payload['modality']),
                        metadata=result.payload.get('metadata', {}),
                        source='graph'
                    )
                    search_results.append(search_result)
                except Exception as e:
                    logger.warning(f"Failed to convert result {result.id}: {e}")
                    continue

            logger.debug(f"Retrieved {len(search_results)} chunks by ID")
            return search_results

        except Exception as e:
            logger.error(f"Failed to retrieve chunks by IDs: {e}")
            return []

    def delete_collection(self) -> None:
        """Delete the collection."""
        self.client.delete_collection(collection_name=self.collection_name)
        logger.info(f"Deleted collection: {self.collection_name}")

