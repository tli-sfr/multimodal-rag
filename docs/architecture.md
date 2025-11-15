# Architecture Guide

## System Overview

The Multimodal Enterprise RAG system is built with a modular, evaluation-first architecture that supports text, image, audio, and video ingestion with hybrid search capabilities.

## Core Principles

### 1. Evaluation-First Design
- All features are driven by measurable success criteria
- Comprehensive test suites define expected behavior
- Metrics tracked: faithfulness, relevance, hallucination rate, latency
- Continuous evaluation during development and production

### 2. Modularity
- Each component is independently testable and replaceable
- Clear interfaces between modules
- Dependency injection for flexibility
- Easy to extend with new modalities or search strategies

### 3. Graceful Degradation
- Fallback mechanisms for all critical paths
- Error handling at every layer
- Partial results better than complete failure
- Comprehensive logging and monitoring

## Architecture Layers

### Layer 1: Ingestion Pipeline

```
Input Files → Validation → Modality Detection → Processing → Chunking → Output
```

**Components:**
- `BaseIngester`: Abstract interface for all ingesters
- `TextIngester`: PDF, TXT, DOCX processing
- `ImageIngester`: OCR + captioning
- `AudioIngester`: Whisper transcription
- `VideoIngester`: Frame extraction + scene detection
- `IngestionPipeline`: Orchestrates all ingesters

**Key Features:**
- Parallel processing for performance
- File validation and size limits
- Semantic chunking for optimal retrieval
- Metadata extraction and enrichment

### Layer 2: Extraction Pipeline

```
Chunks → Entity Extraction → Relationship Extraction → Cross-Modal Linking → Graph
```

**Components:**
- `EntityExtractor`: LLM-based entity recognition
- `RelationshipExtractor`: Relationship identification
- `CrossModalLinker`: Links entities across modalities

**Key Features:**
- Supports multiple entity types (Person, Organization, Location, etc.)
- Confidence scoring for all extractions
- Deduplication and entity resolution
- Cross-modal entity matching

### Layer 3: Storage Layer

```
                    ┌─────────────────┐
                    │   Documents     │
                    └────────┬────────┘
                             │
                    ┌────────┴────────┐
                    │                 │
            ┌───────▼──────┐  ┌──────▼───────┐
            │  Vector DB   │  │  Graph DB    │
            │  (Qdrant)    │  │  (Neo4j)     │
            └──────────────┘  └──────────────┘
```

**Vector Store (Qdrant):**
- Stores chunk embeddings
- Supports semantic similarity search
- Metadata filtering
- Scalable to millions of vectors

**Graph Database (Neo4j):**
- Stores entities and relationships
- Enables graph traversal queries
- Supports complex relationship patterns
- Optimized for connected data

### Layer 4: Search Layer

```
Query → Embedding → ┌─ Vector Search
                    ├─ Graph Search
                    └─ Keyword Search
                           │
                    Result Fusion → Reranking → Top-K Results
```

**Hybrid Search Strategy:**
1. **Vector Search** (50% weight): Semantic similarity using embeddings
2. **Graph Search** (30% weight): Relationship-based traversal
3. **Keyword Search** (20% weight): BM25-style term matching

**Result Fusion:**
- Weighted score combination
- Deduplication across sources
- Diversity promotion
- Configurable weights

### Layer 5: Generation Layer

```
Query + Context → Prompt Construction → LLM → Post-Processing → Answer
```

**Components:**
- Context assembly from search results
- Prompt engineering for quality
- LLM-based answer generation
- Citation and source tracking
- Hallucination detection

### Layer 6: Evaluation Layer

```
Test Cases → System → Answers → Metrics Calculation → Pass/Fail
```

**Metrics:**
- **Faithfulness**: Answer consistency with context
- **Relevance**: Answer relevance to query
- **Context Precision**: Quality of retrieved context
- **Hallucination Rate**: Factual accuracy
- **Latency**: Response time (P50, P95, P99)

## Data Flow

### Ingestion Flow

```
1. File Upload
   ↓
2. Validation (type, size, format)
   ↓
3. Content Extraction (modality-specific)
   ↓
4. Chunking (semantic or fixed)
   ↓
5. Entity Extraction (LLM-based)
   ↓
6. Relationship Extraction
   ↓
7. Embedding Generation
   ↓
8. Storage (Vector DB + Graph DB)
```

### Query Flow

```
1. Query Input
   ↓
2. Query Validation & Triage
   ↓
3. Query Rewriting (optional)
   ↓
4. Parallel Search:
   - Vector Search
   - Graph Search
   - Keyword Search
   ↓
5. Result Fusion
   ↓
6. Reranking
   ↓
7. Context Assembly
   ↓
8. Answer Generation (LLM)
   ↓
9. Post-Processing & Validation
   ↓
10. Response + Sources
```

## Technology Stack

### Core Framework
- **LangChain**: LLM orchestration
- **LlamaIndex**: Document processing (optional)
- **Pydantic**: Data validation

### LLMs
- **OpenAI GPT-4**: Entity extraction, answer generation
- **OpenAI Embeddings**: Text embeddings (3072-dim)

### Multimodal Processing
- **Whisper**: Audio transcription
- **BLIP**: Image captioning
- **Tesseract**: OCR
- **OpenCV**: Video processing
- **SceneDetect**: Scene detection

### Storage
- **Qdrant**: Vector database
- **Neo4j**: Graph database
- **Redis**: Caching (optional)

### Evaluation
- **DeepEval**: RAG evaluation framework
- **RAGAS**: Additional metrics

### UI
- **Streamlit**: Web interface

## Scalability Considerations

### Horizontal Scaling
- Stateless API design
- Load balancing across instances
- Distributed vector search
- Graph database clustering

### Performance Optimization
- Batch processing for embeddings
- Parallel ingestion
- Result caching
- Query optimization

### Resource Management
- Configurable batch sizes
- Memory-efficient chunking
- GPU utilization for models
- Connection pooling

## Security

### Input Validation
- File type verification
- Size limits
- Content sanitization
- PII detection

### Access Control
- API authentication (optional)
- Rate limiting
- Query filtering
- Audit logging

## Monitoring & Observability

### Metrics
- Request latency
- Error rates
- Cache hit rates
- Database performance

### Logging
- Structured logging with Loguru
- Request/response tracking
- Error tracking
- Performance profiling

### Alerting
- Prometheus metrics export
- Custom alert rules
- Health checks

