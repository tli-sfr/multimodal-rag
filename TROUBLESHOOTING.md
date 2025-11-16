# Troubleshooting Guide

## Installation Issues

### Issue: "No matching distribution found for qdrant-client==1.7.0"

**Solution 1: Use flexible version constraints**

The requirements.txt has been updated to use `>=` instead of `==` for version constraints. Try:

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**Solution 2: Use minimal requirements**

If you still encounter issues, use the minimal requirements file:

```bash
pip install -r requirements-minimal.txt
```

**Solution 3: Install packages individually**

```bash
# Core packages
pip install langchain langchain-openai openai
pip install qdrant-client neo4j
pip install deepeval pytest

# Multimodal processing
pip install Pillow pytesseract transformers torch
pip install openai-whisper pydub opencv-python

# Document processing
pip install pypdf python-docx

# Utilities
pip install streamlit pandas plotly
pip install python-dotenv pydantic loguru tqdm
```

### Issue: "ERROR: Could not find a version that satisfies the requirement..."

**Cause**: Package version not available for your Python version or platform.

**Solution**:

1. Check your Python version:

   ```bash
   python --version
   ```

   Required: Python 3.10+

2. Upgrade pip:

   ```bash
   pip install --upgrade pip setuptools wheel
   ```

3. Install without version constraints:
   ```bash
   pip install -r requirements-minimal.txt
   ```

### Issue: PyTorch installation fails

**Solution**: Install PyTorch separately based on your system:

**For CPU only:**

```bash
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
```

**For CUDA (GPU):**

```bash
# CUDA 11.8
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118

# CUDA 12.1
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121
```

**For Mac (MPS):**

```bash
pip install torch torchvision
```

Then install other requirements:

```bash
pip install -r requirements-minimal.txt
```

### Issue: "No module named 'tesseract'"

**Solution**: Install Tesseract OCR system package:

**macOS:**

```bash
brew install tesseract
```

**Ubuntu/Debian:**

```bash
sudo apt-get update
sudo apt-get install tesseract-ocr
```

**Windows:**
Download from: https://github.com/UB-Mannheim/tesseract/wiki

### Issue: "ffmpeg not found" (for audio/video processing)

**Solution**: Install ffmpeg:

**macOS:**

```bash
brew install ffmpeg
```

**Ubuntu/Debian:**

```bash
sudo apt-get install ffmpeg
```

**Windows:**
Download from: https://ffmpeg.org/download.html

## Docker Issues

### Issue: Docker services not starting

**Solution 1: Check Docker is running**

```bash
docker --version
docker-compose --version
```

**Solution 2: Restart Docker services**

```bash
docker-compose down
docker-compose up -d
```

**Solution 3: Check for port conflicts**

```bash
# Check if ports are in use
lsof -i :7474  # Neo4j HTTP
lsof -i :7687  # Neo4j Bolt
lsof -i :6333  # Qdrant
lsof -i :6379  # Redis
```

**Solution 4: Remove volumes and restart**

```bash
docker-compose down -v
docker-compose up -d
```

### Issue: "Cannot connect to Neo4j"

**Solution**:

1. Check Neo4j is running:

   ```bash
   docker-compose ps
   ```

2. Check Neo4j logs:

   ```bash
   docker-compose logs neo4j
   ```

3. Wait for Neo4j to fully start (can take 30-60 seconds):

   ```bash
   docker-compose logs -f neo4j
   # Wait for "Started."
   ```

4. Verify connection:
   ```bash
   curl http://localhost:7474
   ```

### Issue: "Cannot connect to Qdrant"

**Solution**:

1. Check Qdrant is running:

   ```bash
   docker-compose ps
   ```

2. Check Qdrant logs:

   ```bash
   docker-compose logs qdrant
   ```

3. Verify connection:
   ```bash
   curl http://localhost:6333
   ```

## Runtime Issues

### Issue: "OpenAI API key not found"

**Solution**:

1. Create .env file:

   ```bash
   cp .env.example .env
   ```

2. Edit .env and add your key:

   ```
   OPENAI_API_KEY=sk-your-key-here
   ```

3. Verify it's loaded:
   ```python
   from dotenv import load_dotenv
   import os
   load_dotenv()
   print(os.getenv("OPENAI_API_KEY"))
   ```

### Issue: "Out of memory" errors

**Solution**:

1. Reduce batch sizes in `config/config.yaml`:

   ```yaml
   ingestion:
     batch_size: 5 # Reduce from 10

   vector_store:
     batch_size: 50 # Reduce from 100
   ```

2. Process files sequentially instead of in parallel:

   ```yaml
   ingestion:
     max_workers: 1 # Reduce from 4
   ```

3. Use smaller models:
   ```yaml
   audio:
     whisper_model: "tiny" # Instead of "base" or "medium"
   ```

### Issue: "Property values can only be of primitive types" (Neo4j Error)

**Cause**: Neo4j was receiving nested dictionaries/objects in entity properties, which it doesn't support.

**Solution**: This has been fixed! The code now automatically flattens nested properties:

- Primitive types (strings, numbers, booleans) are stored as-is
- Nested objects are converted to JSON strings
- All data is preserved

See **[NEO4J_PROPERTIES_FIX.md](NEO4J_PROPERTIES_FIX.md)** for details.

### Issue: "Failed to create relationship: 'RELATIONSHIP_TYPE'"

**Cause**: The LLM extracted a relationship type that wasn't in the predefined enum.

**Solution**: This has been fixed! The system now:

1. Supports 20+ relationship types (family, work, education, achievements, etc.)
2. Gracefully handles unknown types by mapping them to `RELATED_TO`

If you still see warnings:

1. The relationships are still being created (just with a generic type)
2. You can add new types to `RelationshipType` in `src/models.py`
3. Update the prompt in `src/extraction/relationship_extractor.py`

See **[RELATIONSHIP_EXTRACTION_FIX.md](RELATIONSHIP_EXTRACTION_FIX.md)** for details.

### Issue: "Connection refused" or "[Errno 61] Connection refused"

**Cause**: The Docker services (Qdrant and Neo4j) are not running.

**Solution**:

1. **Make sure Docker Desktop is running**

2. **Start the services**:

   ```bash
   docker-compose up -d
   ```

3. **Verify services are running**:

   ```bash
   docker ps
   ```

   You should see containers for:

   - `qdrant/qdrant` (port 6333)
   - `neo4j` (ports 7474, 7687)
   - `redis` (port 6379)

4. **Wait 10-20 seconds** for services to fully start

5. **Refresh the Streamlit UI** in your browser

**Alternative: Check service health**:

```bash
# Check Qdrant
curl http://localhost:6333/healthz

# Check Neo4j (should show connection info)
curl http://localhost:7474
```

**If Docker Compose fails**:

```bash
# Stop any existing containers
docker-compose down

# Remove volumes and restart fresh
docker-compose down -v
docker-compose up -d
```

### Issue: "No module named 'langchain.prompts'"

**Cause**: LangChain has reorganized its modules. The `langchain.prompts` module has moved to `langchain_core.prompts`.

**Solution**: The imports have been updated in the codebase. If you encounter this error:

1. Make sure you have the latest code:

   ```bash
   git pull  # if using git
   ```

2. The following imports should be used:

   ```python
   # OLD (deprecated)
   from langchain.prompts import ChatPromptTemplate
   from langchain.text_splitter import RecursiveCharacterTextSplitter

   # NEW (correct)
   from langchain_core.prompts import ChatPromptTemplate
   from langchain_text_splitters import RecursiveCharacterTextSplitter
   ```

3. Reinstall the package:
   ```bash
   pip install -e .
   ```

### Issue: "ModuleNotFoundError: No module named 'src'"

**Cause**: The package is not installed in development mode, so Python can't find the `src` module.

**Solution 1: Install in development mode (Recommended)**

```bash
pip install -e .
```

This installs the package in "editable" mode, allowing you to make changes without reinstalling.

**Solution 2: Add to PYTHONPATH**

```bash
export PYTHONPATH="${PYTHONPATH}:${PWD}"
```

Or add to your shell profile (~/.bashrc or ~/.zshrc):

```bash
export PYTHONPATH="${PYTHONPATH}:/path/to/multimodal"
```

**Solution 3: Run tests with pytest from project root**

```bash
# From the project root directory
pytest tests/ -v
```

The `pytest.ini` file is configured to add the current directory to the Python path.

**Solution 4: Use the test script**

```bash
chmod +x scripts/run_tests.sh
./scripts/run_tests.sh
```

### Issue: Import errors in general

**Solution**:

1. Verify you're in the correct directory:

   ```bash
   pwd  # Should show /path/to/multimodal
   ls src/  # Should show Python files
   ```

2. Check virtual environment is activated:

   ```bash
   which python  # Should point to venv/bin/python
   ```

3. Reinstall in development mode:
   ```bash
   pip uninstall multimodal-rag
   pip install -e .
   ```

## Performance Issues

### Issue: Slow ingestion

**Solutions**:

1. Increase parallel workers (if you have enough memory):

   ```yaml
   ingestion:
     max_workers: 8
   ```

2. Use GPU for model inference:

   - Install CUDA-enabled PyTorch
   - Models will automatically use GPU if available

3. Use smaller chunk sizes:
   ```yaml
   ingestion:
     chunk_size: 256 # Reduce from 512
   ```

### Issue: Slow search

**Solutions**:

1. Reduce top_k:

   ```python
   answer = pipeline.query("question", top_k=5)  # Instead of 10
   ```

2. Adjust search weights to favor faster methods:
   ```yaml
   search:
     graph_weight: 0.1
     keyword_weight: 0.4
     vector_weight: 0.5
   ```

## Getting More Help

If you're still experiencing issues:

1. Check the logs in `logs/` directory
2. Run with verbose logging:
   ```bash
   python -m src.cli query "test" -v
   ```
3. Check Docker logs:
   ```bash
   docker-compose logs
   ```
4. Open an issue on GitHub with:
   - Error message
   - Python version
   - Operating system
   - Steps to reproduce
