# Quick Fix Guide

## Fix "ModuleNotFoundError: No module named 'src'"

This error occurs when running tests because the package isn't installed in development mode.

### ✅ Quick Solution

Run this command from the project root:

```bash
pip install -e .
```

Then run tests again:

```bash
pytest tests/ -v
```

### Alternative: Use the test script

```bash
chmod +x scripts/run_tests.sh
./scripts/run_tests.sh
```

## Fix "No matching distribution found for qdrant-client"

### ✅ Quick Solution

```bash
pip install --upgrade pip
pip install -r requirements-minimal.txt
```

## Complete Setup from Scratch

If you want to start fresh:

```bash
# 1. Upgrade pip
pip install --upgrade pip setuptools wheel

# 2. Install minimal requirements
pip install -r requirements-minimal.txt

# 3. Install package in development mode
pip install -e .

# 4. Configure environment
cp .env.example .env
# Edit .env with your OPENAI_API_KEY

# 5. Start Docker services
docker-compose up -d

# 6. Run tests
pytest tests/ -v
```

## Running the System

### Option 1: Web UI

```bash
# Recommended way (uses launcher script)
python run_ui.py

# Or directly with streamlit
streamlit run src/ui/app.py
```

### Option 2: Command Line

```bash
# Ingest documents
python -m src.cli ingest data/raw --recursive

# Query
python -m src.cli query "What are the main topics?"

# Evaluate
python -m src.cli evaluate data/eval/test_queries.json
```

### Option 3: Python API

```python
from src.pipeline import MultimodalRAGPipeline

pipeline = MultimodalRAGPipeline()
documents = pipeline.ingest_documents("data/raw")
answer = pipeline.query("What are the key features?")
print(answer.answer)
```

## Common Issues

### Tests fail with "No module named 'src'"

**Fix**: `pip install -e .`

### Package installation fails

**Fix**: `pip install -r requirements-minimal.txt`

### Docker services not running

**Fix**: `docker-compose up -d`

### Import errors

**Fix**: Make sure you're in the project root and virtual environment is activated

```bash
# Check location
pwd  # Should be /path/to/multimodal

# Check virtual environment
which python  # Should be venv/bin/python

# Activate if needed
source venv/bin/activate
```

## Need More Help?

See detailed troubleshooting: [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
