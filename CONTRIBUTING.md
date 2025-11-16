# Contributing to Multimodal Enterprise RAG

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

## Development Setup

### 1. Fork and Clone

```bash
git clone https://github.com/yourusername/multimodal-rag.git
cd multimodal-rag
```

### 2. Setup Environment

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install -e ".[dev]"
```

### 3. Start Infrastructure

```bash
docker-compose up -d
```

## Development Workflow

### 1. Create a Branch

```bash
git checkout -b feature/your-feature-name
```

### 2. Make Changes

Follow these guidelines:

- **Code Style**: Follow PEP 8
- **Type Hints**: Use type hints for all functions
- **Docstrings**: Use Google-style docstrings
- **Testing**: Write tests for new features
- **Logging**: Use loguru for logging

### 3. Run Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# Run specific test
pytest tests/test_ingestion.py -v
```

### 4. Format Code

```bash
# Format with black
black src/ tests/

# Check with flake8
flake8 src/ tests/

# Type check with mypy
mypy src/
```

### 5. Commit Changes

```bash
git add .
git commit -m "feat: add new feature"
```

Use conventional commit messages:
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `test:` - Test changes
- `refactor:` - Code refactoring
- `chore:` - Maintenance tasks

### 6. Push and Create PR

```bash
git push origin feature/your-feature-name
```

Then create a Pull Request on GitHub.

## Code Guidelines

### Python Style

```python
from typing import List, Optional
from loguru import logger

def process_documents(
    documents: List[Document],
    batch_size: int = 10
) -> List[ProcessedDocument]:
    """Process a list of documents.
    
    Args:
        documents: List of documents to process
        batch_size: Number of documents to process at once
        
    Returns:
        List of processed documents
        
    Raises:
        ValueError: If documents list is empty
    """
    if not documents:
        raise ValueError("Documents list cannot be empty")
    
    logger.info(f"Processing {len(documents)} documents")
    
    # Implementation here
    pass
```

### Testing

```python
import pytest
from src.ingestion import TextIngester

class TestTextIngester:
    """Test text ingestion."""
    
    def test_ingester_initialization(self):
        """Test ingester can be initialized."""
        ingester = TextIngester()
        assert ingester.modality == ModalityType.TEXT
    
    def test_ingester_with_invalid_file(self):
        """Test ingester handles invalid files."""
        ingester = TextIngester()
        
        with pytest.raises(ValueError):
            ingester.ingest(Path("nonexistent.txt"))
```

### Documentation

- Add docstrings to all public functions and classes
- Update README.md for major changes
- Add examples for new features
- Update architecture docs if needed

## Project Structure

When adding new features:

```
src/
├── your_module/
│   ├── __init__.py
│   ├── your_feature.py
│   └── utils.py
tests/
├── test_your_module.py
examples/
├── your_feature_example.py
docs/
├── your_feature.md
```

## Areas for Contribution

### High Priority

1. **Improve Graph Search**: Enhance graph traversal algorithms
2. **Add More Modalities**: Support for additional file types
3. **Optimize Performance**: Profile and optimize bottlenecks
4. **Enhance Evaluation**: Add more metrics and test cases

### Medium Priority

1. **Add Caching**: Implement Redis caching layer
2. **Improve UI**: Enhance Streamlit interface
3. **Add Authentication**: User authentication and authorization
4. **Better Error Handling**: More robust error handling

### Low Priority

1. **Add More Examples**: Additional usage examples
2. **Improve Documentation**: Expand documentation
3. **Add Tutorials**: Step-by-step tutorials
4. **Performance Benchmarks**: Benchmark suite

## Testing Requirements

All PRs must:

- Include tests for new features
- Maintain or improve code coverage (target: 80%+)
- Pass all existing tests
- Pass linting checks

## Documentation Requirements

All PRs must:

- Include docstrings for new functions/classes
- Update relevant documentation
- Add examples if applicable
- Update CHANGELOG.md

## Review Process

1. **Automated Checks**: CI/CD runs tests and linting
2. **Code Review**: Maintainer reviews code
3. **Feedback**: Address review comments
4. **Merge**: PR is merged after approval

## Questions?

- Open an issue for bugs or feature requests
- Start a discussion for questions
- Check existing issues before creating new ones

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

Thank you for contributing! 🎉

