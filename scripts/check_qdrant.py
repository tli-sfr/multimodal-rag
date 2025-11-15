#!/usr/bin/env python3
"""Check what's actually in Qdrant."""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from qdrant_client import QdrantClient

client = QdrantClient(host="localhost", port=6333)

# Get collection info
info = client.get_collection('multimodal_chunks')
print(f"Points count: {info.points_count}")
print(f"Vector size: {info.config.params.vectors.size}")

if info.points_count > 0:
    # Scroll through all points
    result = client.scroll(
        collection_name='multimodal_chunks',
        limit=100,
        with_payload=True,
        with_vectors=False
    )
    points, _ = result

    print(f"\nTotal points retrieved: {len(points)}")
    print("\nSample points:")

    for i, point in enumerate(points[:5], 1):
        content = point.payload.get('content', '')[:60]
        modality = point.payload.get('modality', 'N/A')
        print(f"[{i}] {modality}: {content}...")
else:
    print("NO DATA IN QDRANT!")

