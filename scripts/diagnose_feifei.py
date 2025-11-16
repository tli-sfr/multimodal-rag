"""Diagnose why Fei-Fei Li queries return Andrew Ng results."""

import sys
from pathlib import Path

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent))
from script_utils import setup_environment

# Set up environment
setup_environment()

from src.graph.neo4j_client import Neo4jClient
from src.vector_store.qdrant_client import QdrantVectorStore
from src.vector_store.embeddings import EmbeddingGenerator
from src.config import get_config

def main():
    config = get_config()
    
    # Initialize clients
    neo4j_client = Neo4jClient()
    vector_store = QdrantVectorStore()
    
    print("=" * 80)
    print("DIAGNOSING FEI-FEI LI QUERY ISSUE")
    print("=" * 80)
    
    # Step 1: Find Fei-Fei Li entities in Neo4j
    print("\n1. SEARCHING FOR FEI-FEI LI ENTITIES IN NEO4J")
    print("-" * 80)
    entities = neo4j_client.find_entities_by_name(['fei-fei'], fuzzy=True, limit=10)
    print(f"Found {len(entities)} entities:")
    for e in entities:
        print(f"  - {e['name']} ({e['type']}) - ID: {e['id']}")
    
    if not entities:
        print("❌ No Fei-Fei Li entities found!")
        neo4j_client.close()
        return
    
    # Step 2: Find related chunks in Neo4j
    print("\n2. FINDING RELATED CHUNKS IN NEO4J")
    print("-" * 80)
    entity_ids = [e['id'] for e in entities]
    related_chunks = neo4j_client.find_related_chunks(entity_ids, max_depth=2, limit=20)
    print(f"Found {len(related_chunks)} related chunks:")
    for chunk in related_chunks[:5]:
        print(f"  - Chunk ID: {chunk['chunk_id']}")
        print(f"    Relevance: {chunk['relevance']}")
    
    if not related_chunks:
        print("❌ No related chunks found!")
        neo4j_client.close()
        return
    
    # Step 3: Try to retrieve these chunks from Qdrant
    print("\n3. RETRIEVING CHUNKS FROM QDRANT")
    print("-" * 80)
    chunk_ids = [c['chunk_id'] for c in related_chunks]
    print(f"Attempting to retrieve {len(chunk_ids)} chunks...")
    print(f"Sample chunk IDs: {chunk_ids[:3]}")
    
    search_results = vector_store.retrieve_by_ids(chunk_ids)
    print(f"✅ Retrieved {len(search_results)} chunks from Qdrant")
    
    if len(search_results) == 0:
        print("\n❌ PROBLEM: Qdrant returned 0 chunks!")
        print("\nPossible causes:")
        print("1. Chunk IDs in Neo4j don't match chunk IDs in Qdrant")
        print("2. Chunks were deleted from Qdrant but not from Neo4j")
        print("3. ID format mismatch (UUID vs string)")
        
        # Check what's actually in Qdrant
        print("\n4. CHECKING QDRANT COLLECTION")
        print("-" * 80)
        
        # Get a sample of points from Qdrant
        from qdrant_client.models import Filter, FieldCondition, MatchValue
        
        sample_results = vector_store.client.scroll(
            collection_name=vector_store.collection_name,
            limit=5,
            with_payload=True,
            with_vectors=False
        )
        
        print(f"Sample Qdrant points:")
        for point in sample_results[0]:
            print(f"  - ID: {point.id} (type: {type(point.id)})")
            content = point.payload.get('content', '')[:80]
            print(f"    Content: {content}...")
        
        print(f"\nNeo4j chunk IDs (type: {type(chunk_ids[0])}):")
        for cid in chunk_ids[:3]:
            print(f"  - {cid}")
    else:
        print(f"\n✅ SUCCESS: Retrieved {len(search_results)} chunks")
        for result in search_results[:3]:
            print(f"  - {result.content[:80]}...")
    
    # Cleanup
    neo4j_client.close()
    print("\n" + "=" * 80)

if __name__ == "__main__":
    main()

