"""Command-line interface for Multimodal RAG System."""

import argparse
from pathlib import Path
import sys

from loguru import logger

from .pipeline import MultimodalRAGPipeline
from .evaluation import TestSuite


def setup_logging(verbose: bool = False):
    """Setup logging configuration."""
    logger.remove()
    
    level = "DEBUG" if verbose else "INFO"
    logger.add(sys.stderr, level=level)
    logger.add("logs/cli.log", rotation="10 MB", level="DEBUG")


def ingest_command(args):
    """Handle ingest command."""
    logger.info(f"Ingesting from: {args.input}")
    
    pipeline = MultimodalRAGPipeline()
    
    input_path = Path(args.input)
    documents = pipeline.ingest_documents(
        input_path,
        recursive=args.recursive
    )
    
    logger.info(f"Successfully ingested {len(documents)} documents")
    
    # Print summary
    for doc in documents:
        print(f"\n{doc.title}")
        print(f"  Modality: {doc.modality.value}")
        print(f"  Chunks: {len(doc.chunks)}")
        print(f"  Entities: {len(doc.entities)}")
        print(f"  Relationships: {len(doc.relationships)}")
    
    pipeline.close()


def query_command(args):
    """Handle query command."""
    logger.info(f"Querying: {args.query}")
    
    pipeline = MultimodalRAGPipeline()
    
    answer = pipeline.query(args.query, top_k=args.top_k)
    
    print("\n" + "=" * 60)
    print("ANSWER")
    print("=" * 60)
    print(answer.text)
    print("\n" + "=" * 60)
    print("METADATA")
    print("=" * 60)
    print(f"Confidence: {answer.confidence:.2%}")
    print(f"Latency: {answer.latency_ms:.0f}ms")
    print(f"Sources: {len(answer.sources)}")
    
    if args.show_sources:
        print("\n" + "=" * 60)
        print("SOURCES")
        print("=" * 60)
        for i, source in enumerate(answer.sources, 1):
            print(f"\n[{i}] {source.modality.value} (score: {source.score:.3f})")
            print(source.content[:200] + "..." if len(source.content) > 200 else source.content)
    
    pipeline.close()


def evaluate_command(args):
    """Handle evaluate command."""
    logger.info(f"Running evaluation from: {args.test_suite}")
    
    # Load test suite
    test_suite = TestSuite.from_json(args.test_suite)
    logger.info(f"Loaded {len(test_suite.test_cases)} test cases")
    
    # Initialize pipeline
    pipeline = MultimodalRAGPipeline()
    
    # Run evaluation
    print("\n" + "=" * 60)
    print("RUNNING EVALUATION")
    print("=" * 60)
    
    for i, test_case in enumerate(test_suite.test_cases, 1):
        print(f"\n[{i}/{len(test_suite.test_cases)}] {test_case.query}")
        
        # Get answer
        answer = pipeline.query(test_case.query)
        
        # Evaluate
        contexts = [s.content for s in answer.sources]
        result = test_suite.evaluate_answer(test_case, answer, contexts)
        
        # Display result
        status = "✅ PASS" if result.passed else "❌ FAIL"
        print(f"  {status}")
        print(f"  Metrics: {result.metrics}")
        
        if result.errors:
            print(f"  Errors: {result.errors}")
    
    # Summary
    pass_rate = test_suite.get_pass_rate()
    print("\n" + "=" * 60)
    print("EVALUATION SUMMARY")
    print("=" * 60)
    print(f"Total tests: {len(test_suite.results)}")
    print(f"Passed: {sum(1 for r in test_suite.results if r.passed)}")
    print(f"Failed: {sum(1 for r in test_suite.results if not r.passed)}")
    print(f"Pass rate: {pass_rate:.1%}")
    
    # Save results
    if args.output:
        test_suite.save_results(args.output)
        print(f"\nResults saved to: {args.output}")
    
    pipeline.close()


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Multimodal Enterprise RAG System CLI"
    )
    
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Ingest command
    ingest_parser = subparsers.add_parser("ingest", help="Ingest documents")
    ingest_parser.add_argument("input", help="Input file or directory")
    ingest_parser.add_argument(
        "-r", "--recursive",
        action="store_true",
        help="Process directories recursively"
    )
    
    # Query command
    query_parser = subparsers.add_parser("query", help="Query the system")
    query_parser.add_argument("query", help="Query text")
    query_parser.add_argument(
        "-k", "--top-k",
        type=int,
        default=10,
        help="Number of results to retrieve"
    )
    query_parser.add_argument(
        "-s", "--show-sources",
        action="store_true",
        help="Show source documents"
    )
    
    # Evaluate command
    eval_parser = subparsers.add_parser("evaluate", help="Run evaluation")
    eval_parser.add_argument(
        "test_suite",
        help="Path to test suite JSON file"
    )
    eval_parser.add_argument(
        "-o", "--output",
        help="Output path for results"
    )
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.verbose)
    
    # Execute command
    if args.command == "ingest":
        ingest_command(args)
    elif args.command == "query":
        query_command(args)
    elif args.command == "evaluate":
        evaluate_command(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

