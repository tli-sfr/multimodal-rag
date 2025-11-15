# Multimodal Enterprise RAG System

A production-grade Retrieval-Augmented Generation (RAG) system supporting text, image, audio, and video ingestion with hybrid search capabilities combining knowledge graphs and vector databases.

## 🏗️ Architecture Overview

This system follows an **evaluation-first, modular design** with the following key components:

### Core Components

1. **Evaluation Framework** (`src/evaluation/`)
   - DeepEval-based test suites
   - Metrics: hallucination rate, latency, accuracy, retrieval quality
   - Query type classification (factual, lookup, reasoning)

2. **Ingestion Pipeline** (`src/ingestion/`)
   - Text: PDF, TXT parsing with chunking
   - Image: OCR, captioning, visual embeddings
   - Audio: Transcription with Whisper
   - Video: Frame extraction, scene detection, audio transcription

3. **Entity & Relationship Extraction** (`src/extraction/`)
   - LLM-based entity recognition
   - Cross-modal entity linking
   - Relationship extraction and schema inference

4. **Knowledge Graph** (`src/graph/`)
   - Neo4j integration
   - Graph construction and traversal
   - Entity resolution and merging

5. **Vector Database** (`src/vector_store/`)
   - Qdrant integration
   - Multimodal embeddings
   - Semantic search

6. **Hybrid Search** (`src/search/`)
   - Graph traversal for structured queries
   - Keyword filtering with BM25
   - Vector similarity search
   - Result fusion and reranking

7. **Query Processing** (`src/query/`)
   - Query triage and classification
   - Query rewriting and expansion
   - Agent-based orchestration

8. **Answer Generation** (`src/generation/`)
   - RAG with context assembly
   - Post-processing and validation
   - Hallucination detection

9. **User Interface** (`src/ui/`)
   - Streamlit web application
   - File upload and management
   - Query interface with graph visualization

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Docker (for Neo4j and Qdrant)
- OpenAI API key (or local LLM)

### Installation

```bash
# Clone and setup
cd multimodal
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start infrastructure
docker-compose up -d

# Configure environment
cp .env.example .env
# Edit .env with your API keys
```

### Running the System

```bash
# Run evaluations
python -m pytest tests/ -v

# Start the UI
streamlit run src/ui/app.py

# Run ingestion pipeline
python -m src.ingestion.pipeline --input data/raw --output data/processed
```

## 📊 Evaluation Metrics

- **Retrieval Quality**: Precision@K, Recall@K, MRR
- **Answer Quality**: Faithfulness, Answer Relevance, Contextual Precision
- **Hallucination Rate**: Factual consistency score
- **Latency**: P50, P95, P99 response times
- **Cross-modal Accuracy**: Entity linking precision

## 🏛️ System Design Principles

1. **Evaluation-First**: All features driven by measurable success criteria
2. **Modularity**: Each component is independently testable and replaceable
3. **Graceful Degradation**: Fallback mechanisms for all critical paths
4. **Observability**: Comprehensive logging and metrics
5. **Security**: Query validation, access control, PII detection

## 📁 Project Structure

```
multimodal/
├── src/
│   ├── evaluation/       # Evaluation framework and metrics
│   ├── ingestion/        # Multimodal data ingestion
│   ├── extraction/       # Entity and relationship extraction
│   ├── graph/           # Knowledge graph operations
│   ├── vector_store/    # Vector database integration
│   ├── search/          # Hybrid search pipeline
│   ├── query/           # Query processing and orchestration
│   ├── generation/      # Answer generation
│   ├── ui/              # User interface
│   └── utils/           # Shared utilities
├── tests/               # Test suites
├── data/                # Data storage
├── config/              # Configuration files
├── docker-compose.yml   # Infrastructure setup
└── requirements.txt     # Python dependencies
```

## 🔧 Configuration

See `config/config.yaml` for detailed configuration options.

## 📚 Documentation

- [Architecture Guide](docs/architecture.md)
- [Evaluation Framework](docs/evaluation.md)
- [API Reference](docs/api.md)
- [Deployment Guide](docs/deployment.md)

## 🧪 Testing

```bash
# Run all tests
pytest tests/ -v

# Run evaluation suite
python -m src.evaluation.run_evals

# Run specific test category
pytest tests/test_ingestion.py -v
```

## 📄 License

MIT License

