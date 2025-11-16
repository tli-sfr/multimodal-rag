#!/usr/bin/env python3
"""Test script to verify Elon Musk query returns empty results when not in knowledge base."""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Load environment
from scripts.script_utils import setup_environment
setup_environment()

from src.pipeline import MultimodalRAGPipeline
from src.models import Query

def test_elon_query():
    """Test that Elon query returns empty results when not in knowledge base."""
    
    print("=" * 80)
    print("Testing: 'What did Elon Musk say about AI?'")
    print("=" * 80)
    
    pipeline = MultimodalRAGPipeline()
    
    # Test query
    query_text = "What did Elon Musk say about AI?"
    print(f"\n📝 Query: {query_text}\n")
    
    # Perform search
    query = Query(text=query_text)
    results = pipeline.search_engine.search(query, top_k=10)
    
    print(f"🔍 Search Results: {len(results)} found\n")
    
    if len(results) == 0:
        print("✅ CORRECT: No results returned (Elon not in knowledge base)")
        print("\nNow testing full query with answer generation...\n")
        
        # Test full query
        answer = pipeline.query(query_text, top_k=10)
        print(f"💬 Answer:\n{answer.text}\n")
        print(f"📊 Confidence: {answer.confidence}")
        print(f"⏱️  Latency: {answer.latency_ms:.0f}ms")
        
    else:
        print("❌ INCORRECT: Results returned when Elon is not in knowledge base!")
        print("\nResults:")
        for i, result in enumerate(results, 1):
            has_andrew = 'Andrew' in result.content or 'Ng' in result.content
            has_feifei = 'Fei-Fei' in result.content or 'Li' in result.content
            has_elon = 'Elon' in result.content or 'Musk' in result.content
            
            marker = ""
            if has_elon:
                marker = "✅ ELON"
            elif has_andrew:
                marker = "❌ ANDREW NG"
            elif has_feifei:
                marker = "❌ FEI-FEI LI"
            else:
                marker = "❓ OTHER"
            
            print(f"{i}. {marker} | Score: {result.score:.4f} | Source: {result.source}")
            print(f"   Content: {result.content[:100]}...")
            print()
    
    pipeline.close()
    print("\n" + "=" * 80)

def test_andrew_query():
    """Test that Andrew Ng query still works correctly."""
    
    print("\n" + "=" * 80)
    print("Testing: 'What is Andrew Ng's focus on AI?'")
    print("=" * 80)
    
    pipeline = MultimodalRAGPipeline()
    
    # Test query
    query_text = "What is Andrew Ng's focus on AI?"
    print(f"\n📝 Query: {query_text}\n")
    
    # Perform search
    query = Query(text=query_text)
    results = pipeline.search_engine.search(query, top_k=10)
    
    print(f"🔍 Search Results: {len(results)} found\n")
    
    if len(results) > 0:
        print("✅ CORRECT: Results found for Andrew Ng")
        print("\nTop 3 results:")
        for i, result in enumerate(results[:3], 1):
            print(f"{i}. Score: {result.score:.4f} | Source: {result.source}")
            print(f"   Content: {result.content[:100]}...")
            print()
    else:
        print("❌ INCORRECT: No results found for Andrew Ng (should have results!)")
    
    pipeline.close()
    print("\n" + "=" * 80)

if __name__ == "__main__":
    # Test Elon query (should return empty)
    test_elon_query()
    
    # Test Andrew query (should return results)
    test_andrew_query()
    
    print("\n✅ Testing complete!")

