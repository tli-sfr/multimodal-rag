#!/bin/bash

# Script to run tests for Multimodal Enterprise RAG System

set -e

echo "🧪 Running Multimodal Enterprise RAG Tests..."
echo ""

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
fi

# Install package in development mode if not already installed
echo "Ensuring package is installed in development mode..."
pip install -e . > /dev/null 2>&1 || echo "Package already installed"

echo ""
echo "Running tests..."
echo ""

# Run tests with different options based on arguments
if [ "$1" == "unit" ]; then
    echo "Running unit tests only..."
    pytest tests/ -v -m unit
elif [ "$1" == "integration" ]; then
    echo "Running integration tests only..."
    pytest tests/ -v -m integration
elif [ "$1" == "coverage" ]; then
    echo "Running tests with coverage..."
    pytest tests/ -v --cov=src --cov-report=html --cov-report=term
    echo ""
    echo "Coverage report generated in htmlcov/index.html"
elif [ "$1" == "fast" ]; then
    echo "Running fast tests only (excluding slow tests)..."
    pytest tests/ -v -m "not slow"
else
    echo "Running all tests..."
    pytest tests/ -v
fi

echo ""
echo "✅ Tests complete!"

