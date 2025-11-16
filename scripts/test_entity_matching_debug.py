#!/usr/bin/env python3
"""
Test entity matching with debug output
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.models import Query
from src.search.hybrid_search import HybridSearchEngine
from src.vector_store import QdrantVectorStore, EmbeddingGenerator
from src.graph.neo4j_client import Neo4jClient
from src.extraction import EntityExtractor
from loguru import logger

# Configure logger to show INFO level
logger.remove()
logger.add(sys.stderr, level="INFO")


def test_entity_matching():
    """Test entity matching with debug output"""
    
    print("\n" + "=" * 70)
    print("Testing Entity Matching with Debug Output")
    print("=" * 70 + "\n")
    
    # Initialize components
    print("Initializing components...")
    neo4j_client = Neo4jClient()
    vector_store = QdrantVectorStore()
    embedding_gen = EmbeddingGenerator()
    entity_extractor = EntityExtractor()
    
    # Create hybrid search engine
    search_engine = HybridSearchEngine(
        vector_store=vector_store,
        graph_client=neo4j_client,
        embedding_generator=embedding_gen,
        entity_extractor=entity_extractor,
        use_graph_filter=True
    )
    
    # Test queries
    test_queries = [
        "Who works in Stanford University",
        "What did Andrew Ng say about AI",
        "Tell me about Fei-Fei Li",
        "What is Machine Learning",
    ]
    
    for query_text in test_queries:
        print("\n" + "=" * 70)
        print(f"QUERY: {query_text}")
        print("=" * 70 + "\n")
        
        query = Query(text=query_text)
        
        # Perform search
        results = search_engine.search(query, top_k=5)
        
        print(f"\nReturned {len(results)} results\n")
        
        if results:
            print("Top Results:")
            for i, result in enumerate(results[:3], 1):
                print(f"  {i}. Score: {result.score:.3f} | Modality: {result.modality}")
                # SearchResult has content, not text
                content_preview = result.content[:100] if len(result.content) > 100 else result.content
                print(f"     Content: {content_preview}...")
        else:
            print("  No results found")
        
        print("\n" + "-" * 70 + "\n")
    
    # Close connections
    neo4j_client.close()
    
    print("\n" + "=" * 70)
    print("Test Complete!")
    print("=" * 70 + "\n")


if __name__ == '__main__':
    test_entity_matching()

