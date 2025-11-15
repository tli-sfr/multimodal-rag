# Deployment Guide - Multimodal RAG System

This guide helps you deploy the system on a new machine after cloning from GitHub.

## Prerequisites

- Python 3.13+
- Docker and Docker Compose
- Git
- OpenAI API key

## Quick Setup on New Machine

### 1. Clone Repository

```bash
git clone <your-github-repo-url>
cd multimodal
```

### 2. Set Up Python Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On macOS/Linux
# or
venv\Scripts\activate  # On Windows

# Upgrade pip
pip install --upgrade pip

# Option A: Use automated installation script (recommended)
bash scripts/install_dependencies.sh

# Option B: Install manually
pip install numpy  # Install numpy first to avoid errors
pip install -r requirements.txt

# Option C: Use stable pinned versions (if Option A/B fails)
pip install -r requirements-stable.txt
```

### 3. Configure Environment Variables

```bash
# Copy example env file
cp .env.example .env

# Edit .env and add your OpenAI API key
# OPENAI_API_KEY=sk-...
```

### 4. Start Infrastructure Services

```bash
# Start Neo4j, Qdrant, and Redis
docker-compose up -d

# Verify services are running
docker-compose ps
```

Expected services:

- Neo4j: http://localhost:7474 (bolt://localhost:7687)
- Qdrant: http://localhost:6333
- Redis: localhost:6379

### 5. Prepare Mock Data (Optional)

```bash
# Load sample data for testing
python scripts/prepare_mock_data.py
```

This creates:

- 20 chunks in Qdrant
- 44 entities in Neo4j
- 37 relationships in Neo4j

### 6. Start Application

**Option A: Streamlit UI**

```bash
streamlit run src/ui/app.py
```

Then open http://localhost:8501

**Option B: Python API**

```bash
python
>>> from src.pipeline import MultimodalRAGPipeline
>>> pipeline = MultimodalRAGPipeline()
>>> answer = pipeline.query("What did Andrew Ng teach?")
>>> print(answer.text)
```

## Verification

### Test Graph Filtering

```bash
python scripts/test_graph_search.py
```

Expected output:

- Query "Andrew Ng" returns 10 results
- NO Fei-Fei Li content (graph filtering working)
- All results marked as "vector+graph"

### Test in Streamlit

1. Open http://localhost:8501
2. Click "Clear Cache & Reload Pipeline" if needed
3. Query: "What did Andrew Ng teach?"
4. Verify: No Fei-Fei Li in results

## Troubleshooting

### Installation Issues

#### Error: "RuntimeError: Numpy is not available"

This happens when packages try to use numpy during installation before it's installed.

**Solution:**

```bash
# Install numpy first
pip install numpy

# Then install other requirements
pip install -r requirements.txt
```

Or use the automated script:

```bash
bash scripts/install_dependencies.sh
```

#### Error: "ModuleNotFoundError: No module named 'loguru'"

You forgot to activate the virtual environment or install dependencies.

**Solution:**

```bash
source venv/bin/activate
pip install -r requirements.txt
```

#### Installation takes too long or fails

Use the stable pinned versions:

```bash
pip install -r requirements-stable.txt
```

You can also skip evaluation packages (deepeval, ragas) if you don't need them:

```bash
# Edit requirements.txt and comment out these lines:
# deepeval>=0.20.0
# ragas>=0.1.0

# Then install
pip install -r requirements.txt
```

### Services Not Running

```bash
# Check Docker containers
docker-compose ps

# Restart services
docker-compose restart

# View logs
docker-compose logs neo4j
docker-compose logs qdrant
```

### Qdrant Version Mismatch Warning

If you see version mismatch warnings, you can either:

1. Ignore them (usually safe)
2. Update Qdrant: `docker-compose pull qdrant && docker-compose up -d qdrant`

### Streamlit Shows Old Results

Click "🔄 Clear Cache & Reload Pipeline" button in the sidebar.

### No Search Results

1. Check if mock data is loaded: `python scripts/prepare_mock_data.py`
2. Verify Qdrant has data: http://localhost:6333/dashboard
3. Verify Neo4j has data: http://localhost:7474 (run `MATCH (n) RETURN count(n)`)

## Architecture

```
┌─────────────────┐
│  Streamlit UI   │
└────────┬────────┘
         │
┌────────▼────────┐
│  RAG Pipeline   │
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
┌───▼──┐  ┌──▼───┐
│Qdrant│  │Neo4j │
│Vector│  │Graph │
└──────┘  └──────┘
```

## Key Features Implemented

✅ **Graph-Based Filtering**

- Excludes semantically similar but unconnected content
- Uses Neo4j knowledge graph for relationship-aware search

✅ **Hybrid Search**

- Vector search (50% weight)
- Graph search (30% weight)
- Keyword search (20% weight - stub)

✅ **Multimodal Support**

- Text, Image, Audio, Video ingestion
- Entity extraction and relationship mapping

## Next Steps

1. Upload your own documents via Streamlit UI
2. Customize entity extraction in `src/extraction/entity_extractor.py`
3. Adjust search weights in `src/search/hybrid_search.py`
4. Add evaluation metrics in `src/evaluation/`

## Support

For issues, check:

- Logs: `docker-compose logs`
- Streamlit terminal output
- Neo4j browser: http://localhost:7474
- Qdrant dashboard: http://localhost:6333/dashboard
