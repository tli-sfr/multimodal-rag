"""Integration tests for graph filtering with real test data.

This test suite verifies that:
1. Query for Andrew Ng's AI info won't bring in Fei-Fei Li
2. Query for Fei-Fei Li's AI info won't bring in Andrew Ng
3. Query for "who talked about AI" brings in Andrew, Fei-Fei, and Elon
4. Graph filtering properly excludes unrelated entities
"""

import pytest
from pathlib import Path
import sys
import tempfile
import shutil

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.pipeline import MultimodalRAGPipeline
from src.models.query import Query
from src.config import settings


@pytest.fixture(scope="module")
def pipeline():
    """Create a pipeline instance for testing."""
    return MultimodalRAGPipeline()


@pytest.fixture(scope="module")
def ingested_data(pipeline):
    """Ingest test data once for all tests."""
    
    # Clean up existing data first
    print("\n🧹 Cleaning up existing test data...")
    pipeline.vector_store.client.delete_collection(collection_name=settings.qdrant_collection_name)
    pipeline.vector_store.client.create_collection(
        collection_name=settings.qdrant_collection_name,
        vectors_config=pipeline.vector_store._get_vector_config()
    )
    
    # Clear Neo4j
    with pipeline.graph_client.driver.session() as session:
        session.run("MATCH (n) DETACH DELETE n")
    
    print("✅ Cleanup complete")
    
    # Ingest Andrew Ng data
    print("\n📄 Ingesting Andrew Ng text data...")
    andrew_txt = project_root / "tests/data/txt/andrew_ng.txt"
    if andrew_txt.exists():
        pipeline.ingest_documents(str(andrew_txt))
        print(f"✅ Ingested: {andrew_txt.name}")
    
    # Ingest Andrew Ng PDF
    print("\n📄 Ingesting Andrew Ng PDF data...")
    andrew_pdf = project_root / "tests/data/pdf/Andrew Ng - Wikipedia.pdf"
    if andrew_pdf.exists():
        pipeline.ingest_documents(str(andrew_pdf))
        print(f"✅ Ingested: {andrew_pdf.name}")
    
    # Ingest Elon Musk video
    print("\n🎥 Ingesting Elon Musk video data...")
    elon_video = project_root / "tests/data/video/elon_ai_danger.mp4"
    if elon_video.exists():
        pipeline.ingest_documents(str(elon_video))
        print(f"✅ Ingested: {elon_video.name}")
    
    # Create and ingest Fei-Fei Li data
    print("\n📄 Creating and ingesting Fei-Fei Li data...")
    fei_fei_content = """About Fei-Fei Li

Dr. Fei-Fei Li is a renowned computer scientist and AI researcher. She is the Sequoia Professor of Computer Science at Stanford University and Co-Director of Stanford's Human-Centered AI Institute.

Dr. Li is best known for her work on ImageNet, a large-scale image database that has been instrumental in advancing computer vision and deep learning research. Her work on ImageNet and the ImageNet Large Scale Visual Recognition Challenge (ILSVRC) has been pivotal in the development of modern AI systems.

She has been a strong advocate for diversity in AI and has worked to make AI more inclusive and human-centered. Dr. Li emphasizes the importance of developing AI that benefits all of humanity and addresses societal challenges.

Her research focuses on computer vision, machine learning, cognitive neuroscience, and AI ethics. She has published over 200 scientific papers and has received numerous awards for her contributions to AI research.

Dr. Li is also known for her efforts in AI education and has been instrumental in democratizing AI knowledge through various educational initiatives."""
    
    # Create temporary file for Fei-Fei Li
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write(fei_fei_content)
        fei_fei_file = Path(f.name)
    
    try:
        pipeline.ingest_documents(str(fei_fei_file))
        print(f"✅ Ingested: Fei-Fei Li content")
    finally:
        fei_fei_file.unlink()
    
    print("\n✅ All test data ingested")
    
    # Wait a bit for indexing
    import time
    time.sleep(2)
    
    return {
        "andrew_ng": True,
        "fei_fei_li": True,
        "elon_musk": True
    }


@pytest.mark.integration
@pytest.mark.slow
class TestGraphFilteringWithRealData:
    """Test graph filtering with real ingested data."""
    
    def test_andrew_ng_query_excludes_fei_fei(self, pipeline, ingested_data):
        """Test that querying Andrew Ng's AI info doesn't bring in Fei-Fei Li."""
        
        query_text = "What is Andrew Ng's work in AI?"
        query = Query(text=query_text)
        
        # Perform search
        results = pipeline.search_engine.search(query, top_k=10)
        
        print(f"\n🔍 Query: {query_text}")
        print(f"📊 Results: {len(results)} chunks found")
        
        # Check results
        andrew_mentioned = False
        fei_fei_mentioned = False
        
        for i, result in enumerate(results, 1):
            content_lower = result.content.lower()
            print(f"\n  Result {i}:")
            print(f"    Score: {result.score:.4f}")
            print(f"    Preview: {result.content[:100]}...")
            
            if "andrew" in content_lower or "ng" in content_lower:
                andrew_mentioned = True
            if "fei-fei" in content_lower or "fei fei" in content_lower:
                fei_fei_mentioned = True
        
        # Assertions
        assert len(results) > 0, "Should return results for Andrew Ng"
        assert andrew_mentioned, "Results should mention Andrew Ng"
        assert not fei_fei_mentioned, "Results should NOT mention Fei-Fei Li (graph filter should exclude)"
        
        print(f"\n✅ PASS: Andrew Ng query correctly excludes Fei-Fei Li")
    
    def test_fei_fei_query_excludes_andrew(self, pipeline, ingested_data):
        """Test that querying Fei-Fei Li's AI info doesn't bring in Andrew Ng."""
        
        query_text = "What is Fei-Fei Li's work in AI?"
        query = Query(text=query_text)
        
        # Perform search
        results = pipeline.search_engine.search(query, top_k=10)
        
        print(f"\n🔍 Query: {query_text}")
        print(f"📊 Results: {len(results)} chunks found")
        
        # Check results
        andrew_mentioned = False
        fei_fei_mentioned = False
        
        for i, result in enumerate(results, 1):
            content_lower = result.content.lower()
            print(f"\n  Result {i}:")
            print(f"    Score: {result.score:.4f}")
            print(f"    Preview: {result.content[:100]}...")
            
            if "andrew" in content_lower:
                andrew_mentioned = True
            if "fei-fei" in content_lower or "fei fei" in content_lower:
                fei_fei_mentioned = True

        # Assertions
        assert len(results) > 0, "Should return results for Fei-Fei Li"
        assert fei_fei_mentioned, "Results should mention Fei-Fei Li"
        assert not andrew_mentioned, "Results should NOT mention Andrew Ng (graph filter should exclude)"

        print(f"\n✅ PASS: Fei-Fei Li query correctly excludes Andrew Ng")

    def test_general_ai_query_includes_all(self, pipeline, ingested_data):
        """Test that asking 'who talked about AI' brings in Andrew, Fei-Fei, and Elon."""

        query_text = "Who talked about AI?"
        query = Query(text=query_text)

        # Perform search
        results = pipeline.search_engine.search(query, top_k=20)

        print(f"\n🔍 Query: {query_text}")
        print(f"📊 Results: {len(results)} chunks found")

        # Check results
        andrew_mentioned = False
        fei_fei_mentioned = False
        elon_mentioned = False

        for i, result in enumerate(results, 1):
            content_lower = result.content.lower()
            print(f"\n  Result {i}:")
            print(f"    Score: {result.score:.4f}")
            print(f"    Preview: {result.content[:100]}...")

            if "andrew" in content_lower or "ng" in content_lower:
                andrew_mentioned = True
                print(f"    ✅ Contains: Andrew Ng")
            if "fei-fei" in content_lower or "fei fei" in content_lower:
                fei_fei_mentioned = True
                print(f"    ✅ Contains: Fei-Fei Li")
            if "elon" in content_lower or "musk" in content_lower:
                elon_mentioned = True
                print(f"    ✅ Contains: Elon Musk")

        # Assertions
        assert len(results) > 0, "Should return results for general AI query"
        assert andrew_mentioned, "Results should include Andrew Ng"
        assert fei_fei_mentioned, "Results should include Fei-Fei Li"
        assert elon_mentioned, "Results should include Elon Musk"

        print(f"\n✅ PASS: General AI query includes all three people")
        print(f"   - Andrew Ng: {'✅' if andrew_mentioned else '❌'}")
        print(f"   - Fei-Fei Li: {'✅' if fei_fei_mentioned else '❌'}")
        print(f"   - Elon Musk: {'✅' if elon_mentioned else '❌'}")

    def test_elon_query_excludes_andrew_and_fei_fei(self, pipeline, ingested_data):
        """Test that querying Elon Musk's AI opinions doesn't bring in Andrew or Fei-Fei."""

        query_text = "What is Elon Musk's opinion about AI?"
        query = Query(text=query_text)

        # Perform search
        results = pipeline.search_engine.search(query, top_k=10)

        print(f"\n🔍 Query: {query_text}")
        print(f"📊 Results: {len(results)} chunks found")

        # Check results
        andrew_mentioned = False
        fei_fei_mentioned = False
        elon_mentioned = False

        for i, result in enumerate(results, 1):
            content_lower = result.content.lower()
            print(f"\n  Result {i}:")
            print(f"    Score: {result.score:.4f}")
            print(f"    Preview: {result.content[:100]}...")

            if "andrew" in content_lower:
                andrew_mentioned = True
            if "fei-fei" in content_lower or "fei fei" in content_lower:
                fei_fei_mentioned = True
            if "elon" in content_lower or "musk" in content_lower:
                elon_mentioned = True

        # Assertions
        assert len(results) > 0, "Should return results for Elon Musk"
        assert elon_mentioned, "Results should mention Elon Musk"
        assert not andrew_mentioned, "Results should NOT mention Andrew Ng (graph filter should exclude)"
        assert not fei_fei_mentioned, "Results should NOT mention Fei-Fei Li (graph filter should exclude)"

        print(f"\n✅ PASS: Elon Musk query correctly excludes Andrew Ng and Fei-Fei Li")

    def test_unknown_person_returns_empty(self, pipeline, ingested_data):
        """Test that querying an unknown person returns empty results."""

        query_text = "What is Geoffrey Hinton's work in AI?"
        query = Query(text=query_text)

        # Perform search
        results = pipeline.search_engine.search(query, top_k=10)

        print(f"\n🔍 Query: {query_text}")
        print(f"📊 Results: {len(results)} chunks found")

        # Should return empty because Geoffrey Hinton is not in our knowledge base
        assert len(results) == 0, "Should return empty results for unknown person (graph filter should exclude all)"

        print(f"\n✅ PASS: Unknown person query correctly returns empty results")


@pytest.mark.integration
@pytest.mark.slow
class TestFullQueryAnswerGeneration:
    """Test full query with answer generation."""

    def test_andrew_ng_full_query(self, pipeline, ingested_data):
        """Test full query for Andrew Ng with answer generation."""

        query_text = "What is Andrew Ng's work in AI?"

        print(f"\n🔍 Full Query: {query_text}")

        # Perform full query with answer generation
        answer = pipeline.query(query_text, top_k=5)

        print(f"\n💬 Answer:")
        print(f"{answer.text}")
        print(f"\n📊 Sources: {len(answer.sources)} chunks")

        # Check answer
        answer_lower = answer.text.lower()

        assert len(answer.text) > 0, "Should generate an answer"
        assert "andrew" in answer_lower or "ng" in answer_lower, "Answer should mention Andrew Ng"
        assert "fei-fei" not in answer_lower and "fei fei" not in answer_lower, "Answer should NOT mention Fei-Fei Li"

        print(f"\n✅ PASS: Full query answer correctly focuses on Andrew Ng")

    def test_fei_fei_full_query(self, pipeline, ingested_data):
        """Test full query for Fei-Fei Li with answer generation."""

        query_text = "What is Fei-Fei Li's work in AI?"

        print(f"\n🔍 Full Query: {query_text}")

        # Perform full query with answer generation
        answer = pipeline.query(query_text, top_k=5)

        print(f"\n💬 Answer:")
        print(f"{answer.text}")
        print(f"\n📊 Sources: {len(answer.sources)} chunks")

        # Check answer
        answer_lower = answer.text.lower()

        assert len(answer.text) > 0, "Should generate an answer"
        assert "fei-fei" in answer_lower or "fei fei" in answer_lower, "Answer should mention Fei-Fei Li"
        assert "andrew" not in answer_lower, "Answer should NOT mention Andrew Ng"

        print(f"\n✅ PASS: Full query answer correctly focuses on Fei-Fei Li")

    def test_general_ai_full_query(self, pipeline, ingested_data):
        """Test full query asking who talked about AI."""

        query_text = "Who talked about AI and what did they say?"

        print(f"\n🔍 Full Query: {query_text}")

        # Perform full query with answer generation
        answer = pipeline.query(query_text, top_k=15)

        print(f"\n💬 Answer:")
        print(f"{answer.text}")
        print(f"\n📊 Sources: {len(answer.sources)} chunks")

        # Check answer
        answer_lower = answer.text.lower()

        assert len(answer.text) > 0, "Should generate an answer"

        # Should mention at least 2 of the 3 people
        mentions = 0
        if "andrew" in answer_lower or "ng" in answer_lower:
            mentions += 1
            print("  ✅ Mentions: Andrew Ng")
        if "fei-fei" in answer_lower or "fei fei" in answer_lower:
            mentions += 1
            print("  ✅ Mentions: Fei-Fei Li")
        if "elon" in answer_lower or "musk" in answer_lower:
            mentions += 1
            print("  ✅ Mentions: Elon Musk")

        assert mentions >= 2, f"Answer should mention at least 2 people, but only mentioned {mentions}"

        print(f"\n✅ PASS: General query answer mentions multiple people ({mentions}/3)")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])


