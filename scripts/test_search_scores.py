#!/usr/bin/env python3
"""Test search to see actual scores and why Fei-Fei Li appears in Andrew Ng results."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.vector_store.qdrant_client import QdrantVectorStore
from src.vector_store.embeddings import EmbeddingGenerator

# Initialize
vector_store = QdrantVectorStore()
embedding_gen = EmbeddingGenerator()

# Generate embedding for "andrew ng"
query_text = "andrew ng"
print(f"Searching for: '{query_text}'")
print("=" * 80)

query_embedding = embedding_gen.generate_for_query(query_text)

# Search with different thresholds
for threshold in [0.0, 0.3, 0.5, 0.7]:
    print(f"\n{'='*80}")
    print(f"THRESHOLD: {threshold}")
    print(f"{'='*80}")
    
    results = vector_store.search(
        query_embedding=query_embedding,
        top_k=20,
        score_threshold=threshold
    )
    
    print(f"Found {len(results)} results\n")
    
    for i, result in enumerate(results, 1):
        content = result.content[:60]
        modality = result.modality.value
        source_type = result.source
        score = result.score
        doc_source = result.metadata.get('source', 'unknown')

        # Determine if it's Andrew Ng or Fei-Fei Li content
        is_andrew = "andrew" in content.lower() or "ng" in content.lower() or "andrew_ng" in doc_source.lower()
        is_feifei = "fei-fei" in content.lower() or "li" in content.lower() or "feifei" in doc_source.lower()

        if is_andrew:
            person = "ANDREW NG"
        elif is_feifei:
            person = "FEI-FEI LI"
        else:
            person = "UNKNOWN"

        print(f"{i:2d}. Score: {score:.4f} | {person:12s} | [{modality:5s}] {content}...")
        print(f"    Doc: {doc_source}")

