"""Test script for graph search functionality."""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.pipeline import MultimodalRAGPipeline
from src.models import Query
from loguru import logger

def main():
    """Test graph search with mock data."""
    
    logger.info("=" * 80)
    logger.info("Testing Graph Search Functionality")
    logger.info("=" * 80)
    
    # Initialize pipeline
    logger.info("\n1. Initializing pipeline...")
    pipeline = MultimodalRAGPipeline()
    
    # Test queries
    test_queries = [
        "Andrew Ng",
        "Stanford",
        "machine learning",
        "Coursera",
        "Fei-Fei Li"
    ]
    
    for query_text in test_queries:
        logger.info(f"\n{'=' * 80}")
        logger.info(f"Query: '{query_text}'")
        logger.info(f"{'=' * 80}")
        
        # Perform search
        answer = pipeline.query(query_text, top_k=10)
        
        # Display results
        logger.info(f"\nAnswer: {answer.text[:200]}...")
        logger.info(f"Confidence: {answer.confidence}")
        logger.info(f"Latency: {answer.latency_ms}ms")
        logger.info(f"\nSources ({len(answer.sources)} total):")
        
        # Group sources by type
        vector_sources = [s for s in answer.sources if s.source == 'vector']
        graph_sources = [s for s in answer.sources if s.source == 'graph']
        
        logger.info(f"  - Vector search: {len(vector_sources)} results")
        logger.info(f"  - Graph search: {len(graph_sources)} results")
        
        # Show top 5 sources
        for i, source in enumerate(answer.sources[:5], 1):
            logger.info(f"\n  [{i}] Source: {source.source}, Score: {source.score:.4f}")
            logger.info(f"      Modality: {source.modality.value}")
            logger.info(f"      Content: {source.content[:100]}...")
        
        logger.info("\n")

if __name__ == "__main__":
    main()

