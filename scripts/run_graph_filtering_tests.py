#!/usr/bin/env python3
"""Run graph filtering integration tests.

This script runs integration tests that verify:
1. Query for Andrew Ng's AI info won't bring in Fei-Fei Li
2. Query for Fei-Fei Li's AI info won't bring in Andrew Ng
3. Query for "who talked about AI" brings in Andrew, Fei-Fei, and Elon
4. Graph filtering properly excludes unrelated entities
"""

import sys
import subprocess
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def check_services():
    """Check if required services are running."""
    print("=" * 80)
    print("Checking Required Services")
    print("=" * 80)
    
    try:
        from src.config import settings
        
        # Check Qdrant
        print("\n🔍 Checking Qdrant...")
        import requests
        try:
            response = requests.get(f"http://{settings.qdrant_host}:{settings.qdrant_port}/collections")
            if response.status_code == 200:
                print(f"✅ Qdrant is running at {settings.qdrant_host}:{settings.qdrant_port}")
            else:
                print(f"❌ Qdrant returned status code: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Qdrant is not accessible: {e}")
            print(f"   Please start Qdrant: docker-compose up -d qdrant")
            return False
        
        # Check Neo4j
        print("\n🔍 Checking Neo4j...")
        from neo4j import GraphDatabase
        try:
            driver = GraphDatabase.driver(
                settings.neo4j_uri,
                auth=(settings.neo4j_user, settings.neo4j_password)
            )
            with driver.session() as session:
                result = session.run("RETURN 1")
                result.single()
            driver.close()
            print(f"✅ Neo4j is running at {settings.neo4j_uri}")
        except Exception as e:
            print(f"❌ Neo4j is not accessible: {e}")
            print(f"   Please start Neo4j: docker-compose up -d neo4j")
            return False
        
        # Check Redis
        print("\n🔍 Checking Redis...")
        import redis
        try:
            r = redis.Redis(host=settings.redis_host, port=settings.redis_port, db=0)
            r.ping()
            print(f"✅ Redis is running at {settings.redis_host}:{settings.redis_port}")
        except Exception as e:
            print(f"❌ Redis is not accessible: {e}")
            print(f"   Please start Redis: docker-compose up -d redis")
            return False
        
        print("\n✅ All services are running!")
        return True
        
    except Exception as e:
        print(f"❌ Error checking services: {e}")
        return False


def run_tests(test_type=None):
    """Run integration tests."""
    
    print("\n" + "=" * 80)
    print("Running Graph Filtering Integration Tests")
    print("=" * 80)
    
    cmd = ["pytest", "tests/test_graph_filtering_integration.py", "-v", "-s"]
    
    if test_type:
        if test_type == "search":
            cmd.extend(["-k", "TestGraphFilteringWithRealData"])
        elif test_type == "answer":
            cmd.extend(["-k", "TestFullQueryAnswerGeneration"])
    
    print(f"\nCommand: {' '.join(cmd)}\n")
    
    result = subprocess.run(cmd, cwd=project_root)
    return result.returncode


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Run graph filtering integration tests",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Check services and run all tests
  python scripts/run_graph_filtering_tests.py
  
  # Run only search tests
  python scripts/run_graph_filtering_tests.py --type search
  
  # Run only answer generation tests
  python scripts/run_graph_filtering_tests.py --type answer
  
  # Skip service check
  python scripts/run_graph_filtering_tests.py --skip-check

Test Scenarios:
  1. Andrew Ng query excludes Fei-Fei Li
  2. Fei-Fei Li query excludes Andrew Ng
  3. General "who talked about AI" includes all three
  4. Elon Musk query excludes Andrew and Fei-Fei
  5. Unknown person returns empty results
        """
    )
    
    parser.add_argument(
        "--type",
        choices=["search", "answer"],
        help="Type of tests to run (default: all)"
    )
    
    parser.add_argument(
        "--skip-check",
        action="store_true",
        help="Skip service availability check"
    )
    
    args = parser.parse_args()
    
    # Check services
    if not args.skip_check:
        if not check_services():
            print("\n❌ Service check failed. Please start required services:")
            print("   docker-compose up -d")
            return 1
    
    # Run tests
    exit_code = run_tests(args.type)
    
    if exit_code == 0:
        print("\n" + "=" * 80)
        print("✅ All tests passed!")
        print("=" * 80)
    else:
        print("\n" + "=" * 80)
        print("❌ Some tests failed")
        print("=" * 80)
    
    return exit_code


if __name__ == "__main__":
    sys.exit(main())

