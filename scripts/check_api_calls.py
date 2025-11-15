#!/usr/bin/env python3
"""Check if OpenAI API is actually being called."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import os
from unittest.mock import patch
from src.vector_store.embeddings import EmbeddingGenerator

# Track API calls
api_calls = []

def mock_openai_call(*args, **kwargs):
    """Mock function to track OpenAI API calls."""
    api_calls.append({
        'args': args,
        'kwargs': kwargs
    })
    # Return a fake embedding
    return [[0.1] * 3072]

print("Testing if OpenAI API is being called...")
print("=" * 80)

# Create embedding generator
embedding_gen = EmbeddingGenerator()

# Patch the OpenAI client to track calls
with patch.object(embedding_gen.embeddings.client, 'create', side_effect=mock_openai_call):
    # Test 1: Generate embedding for query
    print("\n1. Testing query embedding...")
    try:
        result = embedding_gen.generate_for_query("test query")
        print(f"   Result length: {len(result)}")
        print(f"   API calls made: {len(api_calls)}")
    except Exception as e:
        print(f"   Error: {e}")

print("\n" + "=" * 80)
print(f"\nTotal API calls tracked: {len(api_calls)}")

if len(api_calls) > 0:
    print("\n✅ OpenAI API IS being called")
else:
    print("\n❌ OpenAI API is NOT being called")
    print("\nPossible reasons:")
    print("1. Caching is enabled somewhere")
    print("2. API key is not set correctly")
    print("3. LangChain is using a different method")

# Check if API key is set
print("\n" + "=" * 80)
print("Checking API key...")
api_key = os.getenv("OPENAI_API_KEY")
if api_key:
    print(f"✅ OPENAI_API_KEY is set (length: {len(api_key)})")
else:
    print("❌ OPENAI_API_KEY is NOT set")

