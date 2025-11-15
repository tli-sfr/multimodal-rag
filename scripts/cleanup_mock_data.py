#!/usr/bin/env python3
"""
Mock Data Cleanup Script

Removes all mock data from Qdrant and Neo4j.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from loguru import logger
from src.graph.neo4j_client import Neo4jClient
from src.vector_store.qdrant_client import QdrantVectorStore


def cleanup_mock_data():
    """Remove all mock data from Qdrant and Neo4j."""
    logger.info("Starting mock data cleanup...")
    
    # Initialize clients
    neo4j_client = Neo4jClient()
    qdrant_client = QdrantVectorStore()
    
    try:
        # Clean up Neo4j - remove all entities and relationships with mock_data property
        logger.info("Cleaning up Neo4j...")
        
        with neo4j_client.driver.session() as session:
            # Count entities before deletion
            result = session.run("""
                MATCH (e:Entity)
                WHERE e.mock_data = true
                RETURN count(e) as count
            """)
            entity_count = result.single()["count"]
            
            # Count relationships before deletion
            result = session.run("""
                MATCH ()-[r]->()
                WHERE r.mock_data = true
                RETURN count(r) as count
            """)
            rel_count = result.single()["count"]
            
            logger.info(f"  Found {entity_count} mock entities")
            logger.info(f"  Found {rel_count} mock relationships")
            
            # Delete relationships first (to avoid orphaned relationships)
            session.run("""
                MATCH ()-[r]->()
                WHERE r.mock_data = true
                DELETE r
            """)
            logger.success(f"  ✅ Deleted {rel_count} mock relationships")
            
            # Delete entities
            session.run("""
                MATCH (e:Entity)
                WHERE e.mock_data = true
                DELETE e
            """)
            logger.success(f"  ✅ Deleted {entity_count} mock entities")
        
        # Clean up Qdrant - delete points with mock_data metadata
        logger.info("Cleaning up Qdrant...")
        
        # Get all points with mock_data filter
        try:
            # Qdrant doesn't have a direct "delete by filter" for all points
            # We need to scroll through and delete by IDs
            from qdrant_client.models import Filter, FieldCondition, MatchValue
            
            # Search for mock data points
            scroll_result = qdrant_client.client.scroll(
                collection_name=qdrant_client.collection_name,
                scroll_filter=Filter(
                    must=[
                        FieldCondition(
                            key="metadata.source",
                            match=MatchValue(value="mock_data")
                        )
                    ]
                ),
                limit=1000,
                with_payload=False,
                with_vectors=False
            )
            
            points_to_delete = [point.id for point in scroll_result[0]]
            
            if points_to_delete:
                qdrant_client.client.delete(
                    collection_name=qdrant_client.collection_name,
                    points_selector=points_to_delete
                )
                logger.success(f"  ✅ Deleted {len(points_to_delete)} mock chunks from Qdrant")
            else:
                logger.info("  No mock chunks found in Qdrant")
                
        except Exception as e:
            logger.warning(f"  Could not clean Qdrant by filter: {e}")
            logger.info("  Attempting alternative cleanup method...")
            
            # Alternative: delete by source pattern
            # This requires knowing the source IDs, which we don't have
            # So we'll just log a warning
            logger.warning("  Please manually clean Qdrant if needed, or recreate the collection")
        
        logger.success(f"\n{'='*60}")
        logger.success(f"✅ Mock data cleanup completed!")
        logger.success(f"{'='*60}\n")
        
        logger.info("Verification queries:")
        logger.info("  Neo4j: MATCH (e:Entity) WHERE e.mock_data = true RETURN count(e)")
        logger.info("  Neo4j: MATCH ()-[r]->() WHERE r.mock_data = true RETURN count(r)")
        
    except Exception as e:
        logger.error(f"Error cleaning up mock data: {e}")
        raise
    finally:
        neo4j_client.close()


if __name__ == "__main__":
    import sys
    
    # Ask for confirmation
    print("\n⚠️  WARNING: This will delete all mock data from Neo4j and Qdrant!")
    print("This includes:")
    print("  - All entities with mock_data=true")
    print("  - All relationships with mock_data=true")
    print("  - All chunks from mock data sources")
    print()
    
    response = input("Are you sure you want to continue? (yes/no): ")
    
    if response.lower() in ['yes', 'y']:
        cleanup_mock_data()
    else:
        print("Cleanup cancelled.")
        sys.exit(0)

