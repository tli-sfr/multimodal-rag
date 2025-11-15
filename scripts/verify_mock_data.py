#!/usr/bin/env python3
"""Verify mock data exists in Qdrant and Neo4j."""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.vector_store.qdrant_client import QdrantVectorStore
from src.graph.neo4j_client import Neo4jClient
from loguru import logger


def verify_qdrant():
    """Verify Qdrant has mock data."""
    logger.info("Checking Qdrant...")
    client = QdrantVectorStore()
    
    try:
        info = client.client.get_collection('multimodal_chunks')
        points_count = info.points_count
        vector_size = info.config.params.vectors.size
        
        logger.info(f"✅ Qdrant collection exists")
        logger.info(f"   Total points: {points_count}")
        logger.info(f"   Vector size: {vector_size}")
        
        if points_count == 0:
            logger.warning("⚠️  No data in Qdrant!")
            return False
        
        return True
    except Exception as e:
        logger.error(f"❌ Qdrant error: {e}")
        return False


def verify_neo4j():
    """Verify Neo4j has mock data."""
    logger.info("Checking Neo4j...")
    client = Neo4jClient()
    
    try:
        with client.driver.session() as session:
            # Count mock entities
            result = session.run("""
                MATCH (e:Entity)
                WHERE e.mock_data = true
                RETURN count(e) as count
            """)
            entity_count = result.single()["count"]
            
            # Count mock relationships
            result = session.run("""
                MATCH ()-[r]->()
                WHERE r.mock_data = true
                RETURN count(r) as count
            """)
            rel_count = result.single()["count"]
            
            logger.info(f"✅ Neo4j connected")
            logger.info(f"   Mock entities: {entity_count}")
            logger.info(f"   Mock relationships: {rel_count}")
            
            if entity_count == 0:
                logger.warning("⚠️  No mock entities in Neo4j!")
                return False
            
            return True
    except Exception as e:
        logger.error(f"❌ Neo4j error: {e}")
        return False
    finally:
        client.close()


def main():
    """Main verification."""
    logger.info("=" * 60)
    logger.info("Verifying Mock Data")
    logger.info("=" * 60)
    
    qdrant_ok = verify_qdrant()
    print()
    neo4j_ok = verify_neo4j()
    
    print()
    logger.info("=" * 60)
    if qdrant_ok and neo4j_ok:
        logger.success("✅ Mock data verified successfully!")
        logger.info("=" * 60)
        logger.info("")
        logger.info("To use the data:")
        logger.info("1. Open Streamlit: http://localhost:8502")
        logger.info("2. Go to 'Query' tab")
        logger.info("3. Search for: 'Andrew Ng' or 'Fei-Fei Li'")
        logger.info("")
        logger.info("To view graph:")
        logger.info("1. Open Neo4j: http://localhost:7474")
        logger.info("2. Run: MATCH (e:Entity {name: 'Andrew Ng'})-[r*1..2]-(c) RETURN e,r,c")
    else:
        logger.error("❌ Mock data verification failed!")
        logger.info("=" * 60)
        logger.info("")
        logger.info("To populate mock data:")
        logger.info("  python scripts/prepare_mock_data.py")


if __name__ == "__main__":
    main()

