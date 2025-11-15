#!/usr/bin/env python3
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from qdrant_client import QdrantClient

client = QdrantClient(host="localhost", port=6333)
info = client.get_collection('multimodal_chunks')

print(f"Total points: {info.points_count}")

if info.points_count > 0:
    result = client.scroll(
        collection_name='multimodal_chunks',
        limit=25,
        with_payload=True,
        with_vectors=False
    )
    points, _ = result
    
    print(f"\nAll {len(points)} points:")
    for i, point in enumerate(points, 1):
        content = point.payload.get('content', '')[:50]
        modality = point.payload.get('modality', 'N/A')
        print(f"{i}. [{modality}] {content}...")

