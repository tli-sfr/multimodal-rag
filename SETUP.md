# Setup Guide - Multimodal RAG System

This guide provides multiple setup options with automatic environment compatibility detection and fixes.

## 🚀 Quick Setup (Recommended)

### Option 1: Automated Setup Script (Bash - Mac/Linux)

The automated setup script detects and fixes common environment issues automatically:

```bash
# Run the automated setup script
bash scripts/setup_auto.sh
```

**What it does:**
- ✅ Detects and resolves Python environment conflicts (Conda/Homebrew/venv)
- ✅ Automatically cleans up corrupted virtual environments
- ✅ Creates venv with fallback methods if standard creation fails
- ✅ Installs dependencies with individual package fallback
- ✅ Verifies critical package installation
- ✅ Sets up Docker services (Neo4j, Qdrant, Redis)
- ✅ Creates .env file from template

### Option 2: Automated Setup Script (Python - Cross-platform)

For Windows or if you prefer Python:

```bash
# Run the Python setup script
python3 scripts/setup_auto.py
```

**Same features as bash script, works on:**
- ✅ macOS
- ✅ Linux
- ✅ Windows

### Option 3: Manual Setup

If you prefer manual control:

```bash
# Run the standard setup script
bash scripts/setup.sh
```

## 🔧 What Gets Fixed Automatically

### 1. **Conda/Anaconda Conflicts**
**Problem**: Mixing Conda and venv causes `ModuleNotFoundError` even after installing packages.

**Auto-fix**: 
- Detects Conda environment variables
- Deactivates Conda before creating venv
- Uses system Python instead of Conda Python

### 2. **Corrupted Virtual Environment**
**Problem**: venv directory exists but pip doesn't work.

**Auto-fix**:
- Checks if existing venv is healthy
- Removes corrupted venv automatically
- Creates fresh venv

### 3. **venv Creation Failures**
**Problem**: `python3 -m venv venv` fails due to Python installation issues.

**Auto-fix**:
- Tries standard venv creation first
- Falls back to `--without-pip` method
- Manually installs pip using get-pip.py

### 4. **Dependency Installation Failures**
**Problem**: Some packages fail to install from requirements.txt.

**Auto-fix**:
- Tries full requirements.txt first
- Falls back to installing critical packages individually
- Verifies installation by importing packages

### 5. **Docker Container Conflicts**
**Problem**: Old containers with same names prevent new containers from starting.

**Auto-fix**:
- Detects existing containers
- Removes old containers with `docker-compose down`
- Starts fresh containers

## 📋 Prerequisites

### Required
- **Python 3.10+** (3.11 or 3.12 recommended)
- **Docker Desktop** (for Neo4j, Qdrant, Redis)
- **OpenAI API Key**

### Optional
- Git (for cloning repository)
- Make (for using Makefile commands)

## 🎯 Step-by-Step Manual Setup

If automated scripts don't work, follow these steps:

### 1. Clone Repository

```bash
git clone <repository-url>
cd multimodal-rag
```

### 2. Fix Environment Conflicts

```bash
# If you're in a Conda environment, deactivate it
conda deactivate

# Unset Conda variables
unset CONDA_DEFAULT_ENV
unset CONDA_PREFIX
unset CONDA_PYTHON_EXE
```

### 3. Create Virtual Environment

```bash
# Try standard method first
python3 -m venv venv

# If that fails, try without pip
python3 -m venv venv --without-pip

# Then manually install pip
source venv/bin/activate  # On Windows: venv\Scripts\activate
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
python get-pip.py
rm get-pip.py
```

### 4. Install Dependencies

```bash
# Activate venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt
```

### 5. Configure Environment

```bash
# Copy example env file
cp .env.example .env

# Edit .env and add your OpenAI API key
nano .env  # or use your preferred editor
```

### 6. Start Docker Services

```bash
# Remove old containers if they exist
docker-compose down --remove-orphans

# Start services
docker-compose up -d

# Wait for services to be ready (30 seconds)
sleep 30

# Verify services are running
docker ps
```

### 7. Run the Application

```bash
# Make sure venv is activated
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Start Streamlit app
streamlit run src/ui/app.py
```

The app will be available at: http://localhost:8501

## 🧪 Verify Installation

```bash
# Activate venv
source venv/bin/activate

# Run tests
pytest

# Expected: 56 tests passed in ~40 seconds
```

## 🐛 Troubleshooting

### Issue: `ModuleNotFoundError: No module named 'loguru'`

**Cause**: Not using virtual environment

**Solution**:
```bash
source venv/bin/activate  # Always activate venv first!
streamlit run src/ui/app.py
```

### Issue: `Error: The container name is already in use`

**Cause**: Old Docker containers exist

**Solution**:
```bash
docker-compose down --remove-orphans
docker-compose up -d
```

### Issue: `pip: command not found` in venv

**Cause**: venv created without pip

**Solution**:
```bash
source venv/bin/activate
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
python get-pip.py
rm get-pip.py
```

### Issue: Streamlit uses wrong port

**Cause**: Port 8501 already in use

**Solution**: Streamlit automatically uses next available port (8502, 8503, etc.)

## 📚 Additional Resources

- **Quick Start**: See `QUICKSTART.md` for usage instructions
- **Testing**: See `tests/README.md` for testing documentation  
- **Deployment**: See `DEPLOYMENT.md` for production deployment
- **API Documentation**: See `docs/` directory

## 🆘 Getting Help

If you encounter issues not covered here:

1. Check the automated setup script output for specific error messages
2. Review the troubleshooting section above
3. Check Docker logs: `docker-compose logs -f`
4. Verify Python version: `python3 --version` (should be 3.10+)
5. Verify Docker is running: `docker info`

