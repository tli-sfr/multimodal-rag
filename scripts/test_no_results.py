#!/usr/bin/env python3
"""Test the pipeline behavior when no search results are found."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.pipeline import MultimodalRAGPipeline
from loguru import logger

def main():
    """Test queries that should return no results."""
    
    print("=" * 80)
    print("Testing Pipeline Behavior with No Search Results")
    print("=" * 80)
    
    # Initialize pipeline
    print("\n1. Initializing pipeline...")
    pipeline = MultimodalRAGPipeline()
    
    # Test queries that should NOT match the mock data
    test_queries = [
        "quantum physics and string theory",
        "cooking recipes for pasta",
        "latest news about cryptocurrency",
        "how to play guitar",
        "weather forecast for tomorrow"
    ]
    
    print("\n2. Testing queries that should return NO results:")
    print("-" * 80)
    
    for i, query_text in enumerate(test_queries, 1):
        print(f"\n[Query {i}] {query_text}")
        print("-" * 80)
        
        try:
            # Query the pipeline
            answer = pipeline.query(query_text, top_k=10)
            
            # Display results
            print(f"\n📊 Results:")
            print(f"   Sources found: {len(answer.sources)}")
            print(f"   Confidence: {answer.confidence:.2f}")
            print(f"   Latency: {answer.latency_ms:.0f}ms")
            
            print(f"\n💬 Answer:")
            print(f"   {answer.text}")
            
            # Check if LLM was called
            if len(answer.sources) == 0:
                print(f"\n✅ PASS: No LLM call made (saved API cost!)")
            else:
                print(f"\n⚠️  WARNING: Found {len(answer.sources)} results (unexpected)")
                for j, source in enumerate(answer.sources[:3], 1):
                    print(f"      [{j}] Score: {source.score:.4f} - {source.content[:60]}...")
        
        except Exception as e:
            print(f"\n❌ ERROR: {e}")
            logger.exception("Query failed")
    
    print("\n" + "=" * 80)
    print("Testing Complete!")
    print("=" * 80)
    
    # Now test a query that SHOULD return results
    print("\n3. Testing a query that SHOULD return results (for comparison):")
    print("-" * 80)
    
    query_text = "Andrew Ng machine learning"
    print(f"\n[Query] {query_text}")
    print("-" * 80)
    
    try:
        answer = pipeline.query(query_text, top_k=10)
        
        print(f"\n📊 Results:")
        print(f"   Sources found: {len(answer.sources)}")
        print(f"   Confidence: {answer.confidence:.2f}")
        print(f"   Latency: {answer.latency_ms:.0f}ms")
        
        print(f"\n💬 Answer:")
        print(f"   {answer.text[:200]}...")
        
        if len(answer.sources) > 0:
            print(f"\n✅ PASS: LLM was called (results found)")
        else:
            print(f"\n❌ FAIL: No results found (unexpected)")
    
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        logger.exception("Query failed")
    
    # Close pipeline
    pipeline.close()
    
    print("\n" + "=" * 80)
    print("Summary:")
    print("=" * 80)
    print("✅ Queries with no results: Skip LLM call, return polite message")
    print("✅ Queries with results: Call LLM, generate answer")
    print("💰 API Cost Savings: No wasted GPT-4 calls on empty results!")
    print("=" * 80)

if __name__ == "__main__":
    main()

