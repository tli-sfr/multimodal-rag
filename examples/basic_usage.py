"""Basic usage example for Multimodal RAG System."""

from pathlib import Path
from loguru import logger

from src.pipeline import MultimodalRAGPipeline
from src.evaluation import TestSuite


def main():
    """Run basic usage example."""
    
    # Configure logging
    logger.add("logs/example.log", rotation="10 MB")
    
    print("=" * 60)
    print("Multimodal Enterprise RAG System - Basic Usage Example")
    print("=" * 60)
    
    # Initialize pipeline
    print("\n1. Initializing pipeline...")
    pipeline = MultimodalRAGPipeline()
    print("✅ Pipeline initialized")
    
    # Ingest documents
    print("\n2. Ingesting documents...")
    data_path = Path("data/raw")
    
    if not data_path.exists():
        print(f"⚠️  Data directory not found: {data_path}")
        print("Creating sample text file...")
        data_path.mkdir(parents=True, exist_ok=True)
        
        # Create sample document
        sample_file = data_path / "sample.txt"
        sample_file.write_text("""
        Multimodal Enterprise RAG System
        
        This is a sample document for testing the RAG system.
        
        Key Features:
        - Text ingestion from PDF, TXT, DOCX
        - Image processing with OCR and captioning
        - Audio transcription using Whisper
        - Video frame extraction and scene detection
        - Entity and relationship extraction
        - Knowledge graph construction with Neo4j
        - Vector search with Qdrant
        - Hybrid search combining graph, keyword, and vector retrieval
        
        The system is built with an evaluation-first approach, ensuring
        high quality and reliability through comprehensive metrics and testing.
        
        Organizations mentioned: OpenAI, Anthropic, Neo4j, Qdrant
        People: John Smith (CEO), Jane Doe (CTO)
        Locations: San Francisco, New York
        """)
        print(f"✅ Created sample file: {sample_file}")
    
    # Ingest documents
    documents = pipeline.ingest_documents(data_path, recursive=True)
    print(f"✅ Ingested {len(documents)} documents")
    
    # Display document info
    for doc in documents:
        print(f"\n  Document: {doc.title}")
        print(f"  Modality: {doc.modality.value}")
        print(f"  Chunks: {len(doc.chunks)}")
        print(f"  Entities: {len(doc.entities)}")
        print(f"  Relationships: {len(doc.relationships)}")
    
    # Query the system
    print("\n3. Querying the system...")
    
    queries = [
        "What are the key features of the system?",
        "Which organizations are mentioned?",
        "Who are the people mentioned in the document?",
    ]
    
    for query_text in queries:
        print(f"\n  Query: {query_text}")
        answer = pipeline.query(query_text, top_k=5)
        
        print(f"  Answer: {answer.text}")
        print(f"  Confidence: {answer.confidence:.2%}")
        print(f"  Latency: {answer.latency_ms:.0f}ms")
        print(f"  Sources: {len(answer.sources)}")
    
    # Run evaluation
    print("\n4. Running evaluation...")
    
    test_suite_path = Path("data/eval/test_queries.json")
    if test_suite_path.exists():
        test_suite = TestSuite.from_json(str(test_suite_path))
        print(f"  Loaded {len(test_suite.test_cases)} test cases")
        
        # Run a few test cases
        for test_case in test_suite.test_cases[:2]:
            print(f"\n  Test: {test_case.query}")
            
            # Get answer
            answer = pipeline.query(test_case.query)
            
            # Evaluate
            contexts = [s.content for s in answer.sources]
            result = test_suite.evaluate_answer(test_case, answer, contexts)
            
            print(f"  Passed: {result.passed}")
            print(f"  Metrics: {result.metrics}")
        
        # Save results
        output_path = Path("data/eval/results/example_results.json")
        test_suite.save_results(str(output_path))
        print(f"\n✅ Evaluation results saved to: {output_path}")
    else:
        print(f"  ⚠️  Test suite not found: {test_suite_path}")
    
    # Close pipeline
    print("\n5. Closing pipeline...")
    pipeline.close()
    print("✅ Pipeline closed")
    
    print("\n" + "=" * 60)
    print("Example completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    main()

