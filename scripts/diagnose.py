#!/usr/bin/env python3
"""Diagnose data and search issues."""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.vector_store.qdrant_client import QdrantVectorStore
from src.vector_store.embeddings import EmbeddingGenerator
from src.graph.neo4j_client import Neo4jClient

output_file = Path(__file__).parent / "diagnosis_output.txt"

with open(output_file, 'w') as f:
    f.write("=" * 80 + "\n")
    f.write("DIAGNOSIS REPORT\n")
    f.write("=" * 80 + "\n\n")
    
    # Check Qdrant
    f.write("1. QDRANT STATUS\n")
    f.write("-" * 80 + "\n")
    try:
        qdrant = QdrantVectorStore()
        info = qdrant.client.get_collection('multimodal_chunks')
        f.write(f"✅ Collection exists: multimodal_chunks\n")
        f.write(f"   Points count: {info.points_count}\n")
        f.write(f"   Vector size: {info.config.params.vectors.size}\n\n")
        
        if info.points_count > 0:
            f.write("   Sample points:\n")
            result = qdrant.client.scroll(
                collection_name='multimodal_chunks',
                limit=10,
                with_payload=True,
                with_vectors=False
            )
            points, _ = result
            for i, point in enumerate(points, 1):
                content = point.payload.get('content', '')[:100]
                modality = point.payload.get('modality', 'N/A')
                f.write(f"   [{i}] {modality}: {content}...\n")
        else:
            f.write("   ⚠️  NO POINTS IN COLLECTION!\n")
    except Exception as e:
        f.write(f"❌ Error: {e}\n")
    
    f.write("\n")
    
    # Check Neo4j
    f.write("2. NEO4J STATUS\n")
    f.write("-" * 80 + "\n")
    try:
        neo4j = Neo4jClient()
        with neo4j.driver.session() as session:
            # Count entities
            result = session.run("MATCH (e:Entity) RETURN count(e) as count")
            total = result.single()["count"]
            f.write(f"✅ Total entities: {total}\n")
            
            # Count mock entities
            result = session.run("""
                MATCH (e:Entity)
                WHERE e.mock_data = true
                RETURN count(e) as count
            """)
            mock = result.single()["count"]
            f.write(f"   Mock entities: {mock}\n\n")
            
            if total > 0:
                f.write("   Sample entities:\n")
                result = session.run("""
                    MATCH (e:Entity)
                    RETURN e.name as name, e.type as type, e.source_modality as modality
                    LIMIT 10
                """)
                for record in result:
                    f.write(f"   - {record['name']} ({record['type']}) - {record['modality']}\n")
            else:
                f.write("   ⚠️  NO ENTITIES IN NEO4J!\n")
        neo4j.close()
    except Exception as e:
        f.write(f"❌ Error: {e}\n")
    
    f.write("\n")
    
    # Test search
    f.write("3. SEARCH TEST: 'Andrew Ng'\n")
    f.write("-" * 80 + "\n")
    try:
        embedding_gen = EmbeddingGenerator()
        query_embedding = embedding_gen.generate_for_query("Andrew Ng")
        f.write(f"✅ Generated embedding ({len(query_embedding)} dims)\n\n")
        
        for threshold in [0.0, 0.5, 0.7]:
            results = qdrant.search(
                query_embedding=query_embedding,
                top_k=10,
                score_threshold=threshold
            )
            f.write(f"   Threshold {threshold}: {len(results)} results\n")
            for i, result in enumerate(results[:3], 1):
                f.write(f"      [{i}] Score: {result.score:.4f} | {result.content[:60]}...\n")
            f.write("\n")
    except Exception as e:
        f.write(f"❌ Error: {e}\n")
    
    f.write("=" * 80 + "\n")
    f.write("END OF REPORT\n")
    f.write("=" * 80 + "\n")

print(f"Diagnosis complete! Check: {output_file}")

