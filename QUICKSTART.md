# Quickstart Guide

Get up and running with the Multimodal Enterprise RAG system in 5 minutes.

## Prerequisites

- Python 3.10+
- Docker and Docker Compose
- OpenAI API key

## Installation

### 1. Clone and Setup

```bash
# Navigate to project directory
cd multimodal-rag

# Run automated setup
chmod +x scripts/setup.sh
./scripts/setup.sh
```

This will:

- Create virtual environment
- Install dependencies
- Start Docker services (Neo4j, Qdrant, Redis)
- Download required models
- Run initial tests

### 2. Configure API Keys

```bash
# Edit .env file
nano .env

# Add your OpenAI API key
OPENAI_API_KEY=sk-your-key-here
```

## Quick Usage

### Option 1: Web UI (Recommended)

```bash
# Activate virtual environment
source venv/bin/activate

# Start Streamlit UI
streamlit run src/ui/app.py
```

Then:

1. Open browser to http://localhost:8501
2. Upload documents in the "Upload" tab
3. Query in the "Query" tab
4. View evaluation metrics in the "Evaluation" tab

### Option 2: Command Line

```bash
# Activate virtual environment
source venv/bin/activate

# Ingest documents
python -m src.cli ingest data/raw --recursive

# Query the system
python -m src.cli query "What are the key features?"

# Run evaluation
python -m src.cli evaluate data/eval/test_queries.json -o results.json
```

### Option 3: Python API

```python
from pathlib import Path
from src.pipeline import MultimodalRAGPipeline

# Initialize pipeline
pipeline = MultimodalRAGPipeline()

# Ingest documents
documents = pipeline.ingest_documents(Path("data/raw"))

# Query
answer = pipeline.query("What are the main topics?", top_k=10)

print(f"Answer: {answer.text}")
print(f"Confidence: {answer.confidence:.2%}")
print(f"Sources: {len(answer.sources)}")

# Close
pipeline.close()
```

## Example Workflow

### 1. Prepare Sample Data

```bash
# Create sample directory
mkdir -p data/raw

# Add sample text file
cat > data/raw/sample.txt << EOF
Multimodal RAG System

This system supports text, image, audio, and video processing.
It uses Neo4j for knowledge graphs and Qdrant for vector search.

Key features:
- Entity extraction
- Relationship mapping
- Hybrid search
- Evaluation-first design

Organizations: OpenAI, Neo4j, Qdrant
People: John Smith (CEO), Jane Doe (CTO)
EOF
```

### 2. Ingest and Query

```bash
# Ingest
python -m src.cli ingest data/raw

# Query
python -m src.cli query "What organizations are mentioned?" --show-sources
```

### 3. Run Evaluation

```bash
# Run test suite
python -m src.cli evaluate data/eval/test_queries.json -o data/eval/results/run_1.json

# View results
cat data/eval/results/run_1.json
```

## Supported File Types

### Text

- PDF (.pdf)
- Text (.txt)
- Word (.docx)
- Markdown (.md)

### Images

- JPEG (.jpg, .jpeg)
- PNG (.png)
- BMP (.bmp)
- TIFF (.tiff)

### Audio

- MP3 (.mp3)
- WAV (.wav)
- M4A (.m4a)
- FLAC (.flac)

### Video

- MP4 (.mp4)
- AVI (.avi)
- MOV (.mov)
- MKV (.mkv)

## Configuration

Edit `config/config.yaml` to customize:

```yaml
# LLM settings
llm:
  model: "gpt-4"
  temperature: 0.0

# Search weights
search:
  graph_weight: 0.3
  keyword_weight: 0.2
  vector_weight: 0.5

# Evaluation thresholds
evaluation:
  min_faithfulness: 0.7
  min_relevance: 0.7
  max_hallucination_rate: 0.3
```

## Troubleshooting

### Installation Issues

If you encounter package installation errors:

```bash
# Option 1: Use minimal requirements
pip install -r requirements-minimal.txt

# Option 2: Upgrade pip first
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

### Common Issues

**"No matching distribution found for qdrant-client"**

- Solution: Use `requirements-minimal.txt` or see [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

**Services not starting**

```bash
docker-compose down
docker-compose up -d
docker-compose ps
```

**Import errors**

```bash
pip install -e .
```

**Memory issues**

- Reduce batch sizes in `config/config.yaml`
- See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for details

For detailed troubleshooting, see **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)**

## Next Steps

- Read [IMPLEMENTATION_GUIDE.md](IMPLEMENTATION_GUIDE.md) for detailed documentation
- Check [docs/architecture.md](docs/architecture.md) for system architecture
- Run tests: `pytest tests/ -v`
- Explore examples in `examples/`

## Getting Help

- Check logs in `logs/` directory
- Review error messages in terminal
- Consult documentation in `docs/`
- Check Docker logs: `docker-compose logs`

## Clean Up

```bash
# Stop services
docker-compose down

# Remove volumes (WARNING: deletes all data)
docker-compose down -v

# Deactivate virtual environment
deactivate
```
