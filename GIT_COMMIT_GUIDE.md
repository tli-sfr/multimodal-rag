# Git Commit Guide - Graph Filtering Implementation

## Quick Start (Automated)

```bash
# Run the automated commit script
bash scripts/commit_changes.sh
```

This script will:

1. Initialize git if needed
2. Stage all necessary files
3. Create a detailed commit
4. Optionally push to GitHub

---

## Manual Steps (If You Prefer)

### Step 1: Initialize Git (if needed)

```bash
# Check if git is initialized
git status

# If not, initialize
git init
```

### Step 2: Add Remote Repository

```bash
# Add your GitHub repository
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git

# Verify
git remote -v
```

### Step 3: Stage Essential Files

```bash
# Configuration files
git add .gitignore
git add .env.example
git add requirements.txt
git add docker-compose.yml
git add DEPLOYMENT.md
git add GIT_COMMIT_GUIDE.md
git add README.md
git add QUICKSTART.md

# All source code
git add src/

# All scripts
git add scripts/*.py
git add scripts/*.sh
git add scripts/*.md

# All tests
git add tests/*.py
git add tests/__init__.py
git add tests/conftest.py

# Config and docs (if they exist)
git add config/ 2>/dev/null || true
git add docs/ 2>/dev/null || true
git add examples/ 2>/dev/null || true
```

### Step 4: Check What Will Be Committed

```bash
# See staged files
git status

# See actual changes
git diff --cached

# See summary
git diff --cached --stat
```

### Step 5: Commit

```bash
git commit -m "feat: implement graph-based filtering for hybrid search

- Add graph filtering to exclude unconnected content
- Implement _apply_graph_filter() in HybridSearchEngine
- Add cache clear button to Streamlit UI
- Fix entity-chunk mapping in mock data
- Add graph traversal methods to Neo4jClient
- Add ID-based retrieval to QdrantVectorStore

Impact: Excludes semantically similar but graph-unconnected content
(e.g., Fei-Fei Li when searching for Andrew Ng)"
```

### Step 6: Push to GitHub

```bash
# Push to main branch
git push -u origin main

# Or if your default branch is master
git push -u origin master
```

---

## Files Included in Commit

### ✅ Essential Files

**Configuration:**

- `.gitignore` - Excludes unnecessary files
- `.env.example` - Environment template
- `requirements.txt` - Python dependencies
- `docker-compose.yml` - Infrastructure setup
- `DEPLOYMENT.md` - Setup guide for new machines
- `GIT_COMMIT_GUIDE.md` - This guide
- `README.md` - Main documentation
- `QUICKSTART.md` - Quick start guide

**All Source Code (`src/`):**

- `src/search/` - Hybrid search with graph filtering
- `src/pipeline.py` - Main pipeline orchestration
- `src/ui/app.py` - Streamlit UI with cache management
- `src/graph/` - Neo4j client and graph operations
- `src/vector_store/` - Qdrant client and embeddings
- `src/extraction/` - Entity/relationship extraction
- `src/ingestion/` - Multimodal file ingesters
- `src/evaluation/` - Evaluation framework
- `src/models.py` - Pydantic data models
- `src/config.py` - Configuration management
- `src/cli.py` - Command-line interface

**All Scripts (`scripts/`):**

- ALL `.py` files: prepare_mock_data.py, test_graph_search.py, test_search.py, cleanup_mock_data.py, etc.
- ALL `.sh` files: setup.sh, commit_changes.sh, run_tests.sh, etc.
- ALL `.md` files in scripts/

**All Tests (`tests/`):**

- `tests/test_ingestion.py` - Ingestion tests
- `tests/test_models.py` - Model tests
- `tests/test_neo4j_client.py` - Neo4j tests
- `tests/conftest.py` - Pytest configuration
- `tests/__init__.py` - Test package init

**Documentation (if exists):**

- `docs/` - Additional documentation
- `config/` - Configuration files
- `examples/` - Usage examples

### ❌ Excluded Files (via .gitignore)

- `venv/` - Virtual environment
- `__pycache__/` - Python cache
- `.env` - Your API keys (sensitive!)
- `data/raw/*` - Your actual data
- `*.log` - Log files
- `.DS_Store` - OS files

---

## Cloning on New Machine

After pushing to GitHub, on your new machine:

```bash
# 1. Clone repository
git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git
cd YOUR_REPO

# 2. Follow DEPLOYMENT.md
# - Set up Python environment
# - Install dependencies
# - Configure .env
# - Start Docker services
# - Load mock data
# - Run application
```

---

## Troubleshooting

### "fatal: not a git repository"

```bash
git init
```

### "fatal: remote origin already exists"

```bash
git remote remove origin
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
```

### "Permission denied (publickey)"

```bash
# Use HTTPS instead of SSH
git remote set-url origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
```

### Want to see what changed?

```bash
# See all changes
git diff

# See staged changes
git diff --cached

# See commit history
git log --oneline
```

### Made a mistake?

```bash
# Unstage a file
git reset HEAD <file>

# Undo last commit (keep changes)
git reset --soft HEAD~1

# Discard all uncommitted changes
git checkout -- .
```

---

## Next Steps

After committing and pushing:

1. ✅ Verify on GitHub that all files are there
2. ✅ Check that `.env` is NOT in the repository (security!)
3. ✅ Test cloning on another machine
4. ✅ Follow DEPLOYMENT.md to set up on new machine
5. ✅ Run `python scripts/test_graph_search.py` to verify

---

## Summary

**What you're committing:**

- Graph filtering implementation
- Neo4j integration for knowledge graph
- Improved search relevance
- Deployment documentation

**What you're NOT committing:**

- Virtual environment
- API keys
- Your actual data
- Log files
- Cache files

This ensures your repository is clean, secure, and ready to deploy anywhere! 🚀
