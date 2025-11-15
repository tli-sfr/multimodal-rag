#!/usr/bin/env python3
"""Test search functionality."""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.vector_store.qdrant_client import QdrantVectorStore
from src.vector_store.embeddings import EmbeddingGenerator
from src.graph.neo4j_client import Neo4jClient

print("=" * 80)
print("TESTING SEARCH FOR 'Andrew Ng'")
print("=" * 80)

# Initialize clients
qdrant = QdrantVectorStore()
embedding_gen = EmbeddingGenerator()
neo4j = Neo4jClient()

# Generate embedding for query
query_text = "Andrew Ng"
print(f"\n1. Generating embedding for query: '{query_text}'")
query_embedding = embedding_gen.generate_for_query(query_text)
print(f"   ✅ Generated embedding with {len(query_embedding)} dimensions")

# Search with different thresholds
print(f"\n2. Searching Qdrant with different score thresholds:")

for threshold in [0.0, 0.5, 0.7, 0.9]:
    print(f"\n   Threshold: {threshold}")
    results = qdrant.search(
        query_embedding=query_embedding,
        top_k=10,
        score_threshold=threshold
    )
    print(f"   Results: {len(results)}")
    
    if results:
        for i, result in enumerate(results[:3], 1):
            print(f"      [{i}] Score: {result.score:.4f} | {result.content[:80]}...")

# Check Neo4j for Andrew Ng
print(f"\n3. Checking Neo4j for 'Andrew Ng' entity:")
try:
    with neo4j.driver.session() as session:
        result = session.run("""
            MATCH (e:Entity)
            WHERE e.name CONTAINS 'Andrew' OR e.name CONTAINS 'Ng'
            RETURN e.name as name, e.type as type, e.source_modality as modality
            LIMIT 10
        """)
        
        entities = list(result)
        print(f"   Found {len(entities)} entities")
        for record in entities:
            print(f"      - {record['name']} ({record['type']}) - {record['modality']}")
            
except Exception as e:
    print(f"   ❌ Error: {e}")
finally:
    neo4j.close()

print("\n" + "=" * 80)
print("CHECKING QDRANT COLLECTION")
print("=" * 80)

try:
    info = qdrant.client.get_collection('multimodal_chunks')
    print(f"Total points: {info.points_count}")
    print(f"Vector size: {info.config.params.vectors.size}")
    
    # Get all points
    if info.points_count > 0:
        print(f"\nSample points:")
        result = qdrant.client.scroll(
            collection_name='multimodal_chunks',
            limit=5,
            with_payload=True,
            with_vectors=False
        )
        points, _ = result
        for i, point in enumerate(points, 1):
            print(f"\n  Point {i}:")
            print(f"    Content: {point.payload.get('content', '')[:100]}...")
            print(f"    Modality: {point.payload.get('modality', 'N/A')}")
            
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "=" * 80)

