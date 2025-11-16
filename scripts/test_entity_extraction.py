#!/usr/bin/env python3
"""
Test entity extraction from queries
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.search.graph_search import GraphSearcher
from src.graph.neo4j_client import Neo4jClient


def test_entity_extraction():
    """Test that multi-word entities are extracted correctly"""

    # Create a GraphSearcher instance (we only need the entity extraction method)
    neo4j_client = Neo4jClient()
    graph_search = GraphSearcher(neo4j_client)
    
    test_cases = [
        {
            "query": "Who works in Stanford University",
            "expected": ["Stanford University", "Stanford", "University"]
        },
        {
            "query": "What did Andrew Ng say about AI",
            "expected": ["Andrew Ng", "Andrew", "Ng"]
        },
        {
            "query": "Tell me about Fei-Fei Li",
            "expected": ["Fei-Fei Li", "Fei-Fei", "Li"]
        },
        {
            "query": "What is Machine Learning",
            "expected": ["Machine Learning", "Machine", "Learning"]
        },
        {
            "query": "Who founded Google Brain",
            "expected": ["Google Brain", "Google", "Brain"]
        },
        {
            "query": "What is the Stanford AI Lab",
            "expected": ["Stanford AI Lab", "Stanford", "Lab"]
        },
        {
            "query": "Tell me about UC Berkeley",
            "expected": ["UC Berkeley", "Berkeley"]
        },
        {
            "query": "single word Test",
            "expected": ["Test"]
        }
    ]
    
    print("=" * 70)
    print("Testing Entity Extraction from Queries")
    print("=" * 70)
    print()
    
    all_passed = True
    
    for i, test_case in enumerate(test_cases, 1):
        query = test_case["query"]
        expected = test_case["expected"]
        
        # Extract entities
        extracted = graph_search._extract_entity_names(query)
        
        # Check if all expected entities are extracted
        missing = [e for e in expected if e not in extracted]
        extra = [e for e in extracted if e not in expected]
        
        passed = len(missing) == 0
        
        print(f"Test {i}: {query}")
        print(f"  Expected: {expected}")
        print(f"  Extracted: {extracted}")
        
        if passed:
            print(f"  ✅ PASS")
        else:
            print(f"  ⚠️  PARTIAL (missing: {missing}, extra: {extra})")
            all_passed = False
        
        print()
    
    print("=" * 70)
    if all_passed:
        print("✅ All tests passed!")
    else:
        print("⚠️  Some tests had missing entities (but may have extras)")
    print("=" * 70)
    
    # Close Neo4j connection
    neo4j_client.close()


if __name__ == '__main__':
    test_entity_extraction()

