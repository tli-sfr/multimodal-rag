#!/usr/bin/env python3
"""Debug what's actually in the databases."""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.vector_store.qdrant_client import QdrantVectorStore
from src.graph.neo4j_client import Neo4jClient

print("=" * 80)
print("CHECKING QDRANT")
print("=" * 80)

qdrant = QdrantVectorStore()
try:
    info = qdrant.client.get_collection('multimodal_chunks')
    print(f"✅ Collection exists: multimodal_chunks")
    print(f"   Points count: {info.points_count}")
    print(f"   Vector size: {info.config.params.vectors.size}")
    
    # Get some sample points
    if info.points_count > 0:
        print("\n📄 Sample points:")
        result = qdrant.client.scroll(
            collection_name='multimodal_chunks',
            limit=5,
            with_payload=True,
            with_vectors=False
        )
        points, _ = result
        for i, point in enumerate(points, 1):
            print(f"\n  Point {i}:")
            print(f"    ID: {point.id}")
            if point.payload:
                print(f"    Content preview: {point.payload.get('content', '')[:100]}...")
                print(f"    Modality: {point.payload.get('modality', 'N/A')}")
                print(f"    Source: {point.payload.get('source', 'N/A')}")
    else:
        print("⚠️  No points in collection!")
        
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "=" * 80)
print("CHECKING NEO4J")
print("=" * 80)

neo4j = Neo4jClient()
try:
    with neo4j.driver.session() as session:
        # Count all entities
        result = session.run("MATCH (e:Entity) RETURN count(e) as count")
        total_entities = result.single()["count"]
        print(f"✅ Total entities: {total_entities}")
        
        # Count mock entities
        result = session.run("""
            MATCH (e:Entity)
            WHERE e.mock_data = true
            RETURN count(e) as count
        """)
        mock_entities = result.single()["count"]
        print(f"   Mock entities: {mock_entities}")
        
        # Count relationships
        result = session.run("MATCH ()-[r]->() RETURN count(r) as count")
        total_rels = result.single()["count"]
        print(f"✅ Total relationships: {total_rels}")
        
        # Count mock relationships
        result = session.run("""
            MATCH ()-[r]->()
            WHERE r.mock_data = true
            RETURN count(r) as count
        """)
        mock_rels = result.single()["count"]
        print(f"   Mock relationships: {mock_rels}")
        
        # Show sample entities
        if total_entities > 0:
            print("\n📊 Sample entities:")
            result = session.run("""
                MATCH (e:Entity)
                RETURN e.name as name, e.type as type, e.source_modality as modality
                LIMIT 10
            """)
            for record in result:
                print(f"   - {record['name']} ({record['type']}) - {record['modality']}")
        else:
            print("⚠️  No entities in Neo4j!")
            
except Exception as e:
    print(f"❌ Error: {e}")
finally:
    neo4j.close()

print("\n" + "=" * 80)

