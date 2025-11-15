#!/bin/bash

# Setup script for Multimodal Enterprise RAG System

set -e

echo "🚀 Setting up Multimodal Enterprise RAG System..."

# Check Python version
echo "📋 Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
required_version="3.10"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Python 3.10+ is required. Found: $python_version"
    exit 1
fi

echo "✅ Python version: $python_version"

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📥 Installing dependencies..."
echo "Attempting to install from requirements.txt..."

if pip install -r requirements.txt; then
    echo "✅ Dependencies installed successfully"
else
    echo "⚠️  Some packages failed to install from requirements.txt"
    echo "Trying minimal requirements..."

    if pip install -r requirements-minimal.txt; then
        echo "✅ Minimal dependencies installed successfully"
    else
        echo "❌ Installation failed. Please install packages manually."
        echo "Try: pip install --upgrade pip"
        echo "Then: pip install -r requirements-minimal.txt"
    fi
fi

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p data/raw
mkdir -p data/processed
mkdir -p data/eval/results
mkdir -p logs

# Copy environment file
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cp .env.example .env
    echo "⚠️  Please edit .env file with your API keys"
fi

# Check Docker
echo "🐳 Checking Docker..."
if ! command -v docker &> /dev/null; then
    echo "⚠️  Docker not found. Please install Docker to run Neo4j and Qdrant"
else
    echo "✅ Docker found"
    
    # Start infrastructure
    echo "🚀 Starting infrastructure (Neo4j, Qdrant, Redis)..."
    docker-compose up -d
    
    echo "⏳ Waiting for services to be ready..."
    sleep 10
    
    echo "✅ Infrastructure started"
fi

# Install package in development mode
echo "📦 Installing package in development mode..."
pip install -e .

# Download spaCy model (optional, skip if fails)
echo "📥 Downloading spaCy model..."
python -m spacy download en_core_web_sm || echo "⚠️  spaCy model download failed (optional)"

# Run tests
echo "🧪 Running tests..."
pytest tests/ -v || echo "⚠️  Some tests failed (this is expected if services aren't running)"

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your API keys"
echo "2. Start the UI: streamlit run src/ui/app.py"
echo "3. Or use the Python API directly"
echo ""
echo "For more information, see README.md"

