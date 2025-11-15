#!/bin/bash

# Installation script for multimodal-rag dependencies
# This script installs dependencies in the correct order to avoid conflicts

set -e  # Exit on error

echo "=========================================="
echo "Installing Multimodal RAG Dependencies"
echo "=========================================="
echo ""

# Check if virtual environment is activated
if [[ -z "$VIRTUAL_ENV" ]]; then
    echo "❌ Virtual environment is not activated!"
    echo ""
    echo "Please run:"
    echo "  python3 -m venv venv"
    echo "  source venv/bin/activate"
    echo "  bash scripts/install_dependencies.sh"
    echo ""
    exit 1
fi

echo "✅ Virtual environment detected: $VIRTUAL_ENV"
echo ""

# Upgrade pip, setuptools, and wheel
echo "📦 Upgrading pip, setuptools, and wheel..."
pip install --upgrade pip setuptools wheel
echo ""

# Install numpy first (required by many packages)
echo "📦 Installing numpy (required by many packages)..."
pip install "numpy>=1.24.0,<2.0.0"
echo ""

# Install core dependencies that other packages depend on
echo "📦 Installing core dependencies..."
pip install \
    "pydantic>=2.6.0" \
    "pydantic-settings>=2.1.0" \
    "python-dotenv>=1.0.0" \
    "loguru>=0.7.0" \
    "tenacity>=8.2.0" \
    "httpx>=0.26.0" \
    "aiofiles>=23.2.0" \
    "tqdm>=4.66.0"
echo ""

# Install PyTorch (large package, install separately)
echo "📦 Installing PyTorch (this may take a while)..."
pip install torch>=2.0.0 torchvision>=0.15.0
echo ""

# Install transformers and related ML packages
echo "📦 Installing ML packages..."
pip install \
    "transformers>=4.30.0" \
    "sentence-transformers>=2.3.0" \
    "scikit-learn>=1.3.0"
echo ""

# Install the rest from requirements.txt
echo "📦 Installing remaining dependencies from requirements.txt..."
pip install -r requirements.txt --no-deps || true
pip install -r requirements.txt
echo ""

# Verify critical imports
echo "🔍 Verifying critical imports..."
python -c "
import sys
errors = []

try:
    import numpy
    print('✅ numpy')
except ImportError as e:
    errors.append(f'❌ numpy: {e}')

try:
    from loguru import logger
    print('✅ loguru')
except ImportError as e:
    errors.append(f'❌ loguru: {e}')

try:
    import torch
    print('✅ torch')
except ImportError as e:
    errors.append(f'❌ torch: {e}')

try:
    import streamlit
    print('✅ streamlit')
except ImportError as e:
    errors.append(f'❌ streamlit: {e}')

try:
    from langchain import LLMChain
    print('✅ langchain')
except ImportError as e:
    errors.append(f'❌ langchain: {e}')

try:
    from qdrant_client import QdrantClient
    print('✅ qdrant-client')
except ImportError as e:
    errors.append(f'❌ qdrant-client: {e}')

try:
    from neo4j import GraphDatabase
    print('✅ neo4j')
except ImportError as e:
    errors.append(f'❌ neo4j: {e}')

try:
    import openai
    print('✅ openai')
except ImportError as e:
    errors.append(f'❌ openai: {e}')

if errors:
    print()
    print('Some imports failed:')
    for error in errors:
        print(error)
    sys.exit(1)
else:
    print()
    print('✅ All critical imports successful!')
"

echo ""
echo "=========================================="
echo "✅ Installation Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Configure environment: cp .env.example .env"
echo "2. Edit .env and add your OPENAI_API_KEY"
echo "3. Start services: docker-compose up -d"
echo "4. Load mock data: python scripts/prepare_mock_data.py"
echo "5. Run app: streamlit run src/ui/app.py"
echo ""

