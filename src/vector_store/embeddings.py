"""Embedding generation for multimodal content."""

from typing import List, Optional
import numpy as np

from langchain_openai import OpenAIEmbeddings
from loguru import logger

from ..models import Chunk, ModalityType
from ..config import get_settings


class EmbeddingGenerator:
    """Generate embeddings for multimodal content."""
    
    def __init__(
        self,
        model: str = "text-embedding-3-large",
        dimensions: int = 3072
    ):
        """Initialize embedding generator.
        
        Args:
            model: Embedding model name
            dimensions: Embedding dimensions
        """
        settings = get_settings()
        
        self.model = model
        self.dimensions = dimensions
        
        self.embeddings = OpenAIEmbeddings(
            model=model,
            api_key=settings.openai_api_key,
            dimensions=dimensions
        )
    
    def generate_for_chunk(self, chunk: Chunk) -> List[float]:
        """Generate embedding for a single chunk.
        
        Args:
            chunk: Content chunk
            
        Returns:
            Embedding vector
        """
        try:
            if not chunk.content or len(chunk.content.strip()) == 0:
                logger.warning(f"Empty content for chunk {chunk.id}")
                return self._get_zero_embedding()
            
            # Generate embedding
            embedding = self.embeddings.embed_query(chunk.content)
            
            return embedding
        
        except Exception as e:
            logger.error(f"Failed to generate embedding for chunk {chunk.id}: {e}")
            return self._get_zero_embedding()
    
    def generate_for_chunks(
        self,
        chunks: List[Chunk],
        batch_size: int = 100
    ) -> List[List[float]]:
        """Generate embeddings for multiple chunks.
        
        Args:
            chunks: List of chunks
            batch_size: Batch size for processing
            
        Returns:
            List of embedding vectors
        """
        if not chunks:
            return []
        
        all_embeddings = []
        
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i + batch_size]
            
            try:
                # Extract texts
                texts = [chunk.content for chunk in batch]
                
                # Generate embeddings in batch
                embeddings = self.embeddings.embed_documents(texts)
                all_embeddings.extend(embeddings)
            
            except Exception as e:
                logger.error(f"Batch embedding generation failed: {e}")
                # Add zero embeddings for failed batch
                all_embeddings.extend([
                    self._get_zero_embedding() for _ in batch
                ])
        
        logger.info(f"Generated {len(all_embeddings)} embeddings")
        return all_embeddings
    
    def generate_for_query(self, query: str) -> List[float]:
        """Generate embedding for a query.
        
        Args:
            query: Query text
            
        Returns:
            Embedding vector
        """
        try:
            return self.embeddings.embed_query(query)
        except Exception as e:
            logger.error(f"Failed to generate query embedding: {e}")
            return self._get_zero_embedding()
    
    def _get_zero_embedding(self) -> List[float]:
        """Get zero embedding vector.
        
        Returns:
            Zero vector of appropriate dimensions
        """
        return [0.0] * self.dimensions

