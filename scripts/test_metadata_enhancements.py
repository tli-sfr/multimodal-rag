#!/usr/bin/env python3
"""Test script for metadata enhancements (speaker name, original filename, upload source)."""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Setup environment
from scripts.script_utils import setup_environment
setup_environment()

from src.pipeline import MultimodalRAGPipeline
from loguru import logger

def test_video_metadata():
    """Test video ingestion with speaker name extraction."""
    print("\n" + "=" * 80)
    print("Testing Video Metadata Enhancements")
    print("=" * 80)
    
    # Initialize pipeline
    pipeline = MultimodalRAGPipeline()
    
    # Test video file
    video_path = project_root / "tests/data/video/elon_musk_ai_danger.mp4"

    if not video_path.exists():
        print(f"\n❌ Test video not found: {video_path}")
        return False

    print(f"\n📹 Testing video: {video_path.name}")
    print(f"   Expected speaker name: Elon Musk (from filename 'elon_musk_ai_danger.mp4')")
    
    # Ingest with upload_source='script'
    documents = pipeline.ingest_documents(
        video_path,
        upload_source="script"
    )
    
    if not documents:
        print("\n❌ No documents created!")
        return False
    
    doc = documents[0]
    print(f"\n✅ Document created with {len(doc.chunks)} chunks")
    
    # Check metadata
    for i, chunk in enumerate(doc.chunks, 1):
        print(f"\n📦 Chunk {i} Metadata:")
        print(f"   - Original Filename: {chunk.metadata.original_filename}")
        print(f"   - Upload Source: {chunk.metadata.upload_source}")
        print(f"   - Speaker Name: {chunk.metadata.speaker_name}")
        print(f"   - Modality: {chunk.metadata.modality}")
        
        # Verify values
        if chunk.metadata.original_filename != "elon_musk_ai_danger.mp4":
            print(f"   ⚠️  Expected original_filename='elon_musk_ai_danger.mp4', got '{chunk.metadata.original_filename}'")

        if chunk.metadata.upload_source != "script":
            print(f"   ⚠️  Expected upload_source='script', got '{chunk.metadata.upload_source}'")

        if chunk.metadata.speaker_name != "Elon Musk":
            print(f"   ⚠️  Expected speaker_name='Elon Musk', got '{chunk.metadata.speaker_name}'")
    
    # Check entities
    print(f"\n🔍 Checking entities in Neo4j...")
    entities = pipeline.graph_client.find_entities_by_name("Elon")
    
    if entities:
        print(f"✅ Found {len(entities)} entities matching 'Elon':")
        for entity in entities:
            print(f"   - {entity['name']} ({entity['type']})")
            # Check if entity has properties and from_filename flag
            props = entity.get('properties')
            if props and isinstance(props, dict) and props.get('from_filename'):
                print(f"     ✅ Entity created from filename!")
    else:
        print("⚠️  No entities found for 'Elon'")
    
    pipeline.close()
    return True


def test_ui_upload_simulation():
    """Simulate UI upload with original filename."""
    print("\n" + "=" * 80)
    print("Testing UI Upload Simulation")
    print("=" * 80)
    
    # Initialize pipeline
    pipeline = MultimodalRAGPipeline()
    
    # Simulate UI upload: temp file with original filename passed
    import tempfile
    import shutil
    
    video_path = project_root / "tests/data/video/elon_musk_ai_danger.mp4"

    if not video_path.exists():
        print(f"\n❌ Test video not found: {video_path}")
        return False

    # Create temp file (simulating Streamlit upload)
    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tmp:
        shutil.copy(video_path, tmp.name)
        tmp_path = Path(tmp.name)

    print(f"\n📤 Simulating UI upload:")
    print(f"   - Original filename: elon_musk_ai_danger.mp4")
    print(f"   - Temp file: {tmp_path.name}")

    # Ingest with original_filename and upload_source (like UI does)
    documents = pipeline.ingest_documents(
        tmp_path,
        original_filename="elon_musk_ai_danger.mp4",
        upload_source="ui"
    )
    
    # Clean up temp file
    tmp_path.unlink()
    
    if not documents:
        print("\n❌ No documents created!")
        return False
    
    doc = documents[0]
    print(f"\n✅ Document created with {len(doc.chunks)} chunks")
    
    # Check metadata
    for i, chunk in enumerate(doc.chunks, 1):
        print(f"\n📦 Chunk {i} Metadata:")
        print(f"   - Original Filename: {chunk.metadata.original_filename}")
        print(f"   - Upload Source: {chunk.metadata.upload_source}")
        print(f"   - Speaker Name: {chunk.metadata.speaker_name}")
        
        # Verify values
        assert chunk.metadata.original_filename == "elon_musk_ai_danger.mp4", \
            f"Expected original_filename='elon_musk_ai_danger.mp4', got '{chunk.metadata.original_filename}'"

        assert chunk.metadata.upload_source == "ui", \
            f"Expected upload_source='ui', got '{chunk.metadata.upload_source}'"

        assert chunk.metadata.speaker_name == "Elon Musk", \
            f"Expected speaker_name='Elon Musk', got '{chunk.metadata.speaker_name}'"
        
        print("   ✅ All metadata fields correct!")
    
    pipeline.close()
    return True


if __name__ == "__main__":
    try:
        success = True
        
        # Test 1: Video metadata
        if not test_video_metadata():
            success = False
        
        # Test 2: UI upload simulation
        if not test_ui_upload_simulation():
            success = False
        
        if success:
            print("\n" + "=" * 80)
            print("✅ ALL TESTS PASSED!")
            print("=" * 80)
        else:
            print("\n" + "=" * 80)
            print("❌ SOME TESTS FAILED")
            print("=" * 80)
            sys.exit(1)
    
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

