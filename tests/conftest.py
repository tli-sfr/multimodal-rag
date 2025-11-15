"""Pytest configuration and fixtures for tests."""

import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import pytest
from unittest.mock import MagicMock


@pytest.fixture
def sample_text_file(tmp_path):
    """Create a sample text file for testing."""
    file_path = tmp_path / "sample.txt"
    file_path.write_text("This is a sample text for testing.")
    return file_path


@pytest.fixture
def sample_pdf_file(tmp_path):
    """Create a sample PDF file path (mock)."""
    file_path = tmp_path / "sample.pdf"
    # Note: This is just a path, actual PDF creation would require pypdf
    return file_path


@pytest.fixture
def sample_metadata():
    """Sample metadata for testing."""
    return {
        "source": "test_document.txt",
        "page": 1,
        "total_pages": 1,
        "file_type": "text/plain",
        "created_at": "2024-01-01T00:00:00Z"
    }


@pytest.fixture
def mock_openai_client():
    """Mock OpenAI client for testing."""
    mock_client = MagicMock()
    mock_client.embeddings.create.return_value = MagicMock(
        data=[MagicMock(embedding=[0.1] * 3072)]
    )
    mock_client.chat.completions.create.return_value = MagicMock(
        choices=[MagicMock(message=MagicMock(content="Test response"))]
    )
    return mock_client


@pytest.fixture
def mock_neo4j_client():
    """Mock Neo4j client for testing."""
    mock_client = MagicMock()
    mock_client.verify_connection.return_value = True
    return mock_client


@pytest.fixture
def mock_qdrant_client():
    """Mock Qdrant client for testing."""
    mock_client = MagicMock()
    mock_client.collection_exists.return_value = True
    return mock_client


@pytest.fixture(autouse=True)
def reset_environment(monkeypatch):
    """Reset environment variables for each test."""
    # Set test environment variables
    monkeypatch.setenv("OPENAI_API_KEY", "test-key-123")
    monkeypatch.setenv("NEO4J_URI", "bolt://localhost:7687")
    monkeypatch.setenv("NEO4J_USER", "neo4j")
    monkeypatch.setenv("NEO4J_PASSWORD", "test-password")
    monkeypatch.setenv("QDRANT_HOST", "localhost")
    monkeypatch.setenv("QDRANT_PORT", "6333")


def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers", "requires_docker: mark test as requiring Docker services"
    )
    config.addinivalue_line(
        "markers", "requires_api_key: mark test as requiring API keys"
    )

