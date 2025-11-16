# Test Suite Documentation

## Overview
Comprehensive test suite for the Multimodal Enterprise RAG System with 56 fast tests covering all core functionality.

## Quick Start

```bash
# Run all tests (recommended - fast, ~40 seconds)
pytest

# Run specific test file
pytest tests/test_graph_filtering_mock.py

# Run specific test class
pytest tests/test_graph_filtering_mock.py::TestGraphFilteringWithMockData

# Run specific test
pytest tests/test_graph_filtering_mock.py::TestGraphFilteringWithMockData::test_andrew_ng_query_excludes_fei_fei

# Run with more verbose output
pytest -vv

# Run with output capture disabled (see print statements)
pytest -s
```

## Test Organization

### Fast Tests (Default - 56 tests, ~40 seconds)

#### Graph Filtering Tests (`test_graph_filtering_mock.py`)
**Purpose**: Test graph filtering logic with mock data
- ✅ 8 tests covering entity-based filtering and answer generation
- ✅ Uses mock data (no file I/O, no video processing)
- ✅ Fast execution (~22 seconds)

**Test Cases**:
- `test_andrew_ng_query_excludes_fei_fei` - Verify graph filter excludes unrelated entities
- `test_fei_fei_query_excludes_andrew` - Verify graph filter works bidirectionally
- `test_elon_musk_query_excludes_others` - Verify multi-entity exclusion
- `test_unknown_person_returns_empty` - Verify vector search fallback
- `test_general_ai_query_includes_multiple_people` - Verify general queries work
- `test_andrew_ng_full_query` - Full pipeline with answer generation
- `test_fei_fei_full_query` - Full pipeline with answer generation
- `test_general_ai_full_query` - Full pipeline with answer generation

#### Ingestion Tests (`test_ingestion.py`)
**Purpose**: Test document ingestion pipeline
- ✅ 5 tests covering ingester initialization and configuration

#### Media Extraction Tests (`test_media_extraction.py`)
**Purpose**: Test text, image, audio, and video extraction
- ✅ 18 tests covering all media types
- ✅ Includes video processing tests (audio extraction, frame extraction, transcription, scene detection)

#### Media Extraction Reference Tests (`test_media_extraction_with_reference.py`)
**Purpose**: Verify extraction consistency with reference data
- ✅ 5 tests comparing extraction results with known references

#### Model Tests (`test_models.py`)
**Purpose**: Test Pydantic model validation
- ✅ 7 tests covering Chunk, Entity, and Query models

#### Neo4j Client Tests (`test_neo4j_client.py`)
**Purpose**: Test graph database operations
- ✅ 13 tests covering entity/relationship storage and edge cases

### Slow Tests (Optional - Not Run by Default)

#### E2E Integration Tests (`test_e2e_integration_slow.py`)
**Purpose**: End-to-end testing with real file ingestion
- ⚠️ Slow execution (minutes due to video processing)
- ⚠️ Not recommended - use mock tests instead
- ⚠️ Excluded by default in `pytest.ini`

**To run slow tests**:
```bash
pytest tests/test_e2e_integration_slow.py -v
```

## Test Data

### Mock Data
Located in test fixtures within `test_graph_filtering_mock.py`:
- Andrew Ng (AI education, Coursera, deeplearning.ai)
- Fei-Fei Li (ImageNet, computer vision, AI ethics)
- Elon Musk (AI safety, Tesla, AGI)
- Jane Smith (unknown person for testing fallback)

### Real Test Files
Located in `tests/data/`:
- `txt/` - Text files (Andrew Ng, Fei-Fei Li)
- `pdf/` - PDF files (Andrew Ng Wikipedia)
- `image/` - Image files (test images)
- `audio/` - Audio files (test audio)
- `video/` - Video files (`elon_musk_ai_danger.mp4`)

## Configuration

### pytest.ini
```ini
[pytest]
addopts = -v --tb=short --ignore=tests/test_e2e_integration_slow.py
testpaths = tests
```

### Markers
- `@pytest.mark.slow` - Marks slow tests (can skip with `-m "not slow"`)

## CI/CD Integration

### Recommended GitHub Actions Workflow
```yaml
- name: Run tests
  run: |
    pytest  # Runs fast tests only (56 tests, ~40 seconds)
```

### Optional: Run All Tests Including Slow
```yaml
- name: Run all tests
  run: |
    pytest tests/  # Includes slow E2E tests
```

## Troubleshooting

### Docker Services Not Running
```bash
docker-compose up -d
```

### Tests Fail with Connection Errors
Ensure services are running:
- Neo4j: `localhost:7687`
- Qdrant: `localhost:6333`
- Redis: `localhost:6379`

### Video Tests Fail
Ensure video file exists:
```bash
ls tests/data/video/elon_musk_ai_danger.mp4
```

## Test Coverage

Run with coverage:
```bash
pytest --cov=src --cov-report=html
open htmlcov/index.html
```

