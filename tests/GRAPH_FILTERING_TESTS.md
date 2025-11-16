# Graph Filtering Integration Tests

## Overview

This test suite verifies that the graph filtering functionality works correctly with real test data. It ensures that queries for specific people only return relevant information and don't leak information about unrelated people.

## Test Scenarios

### 1. Andrew Ng Query Excludes Fei-Fei Li

**Query:** "What is Andrew Ng's work in AI?"

**Expected Behavior:**
- ✅ Returns results about Andrew Ng
- ❌ Does NOT return results about Fei-Fei Li
- ❌ Does NOT return results about Elon Musk

**Why:** Graph filtering should identify "Andrew Ng" as the entity and only return chunks connected to Andrew Ng in the knowledge graph.

---

### 2. Fei-Fei Li Query Excludes Andrew Ng

**Query:** "What is Fei-Fei Li's work in AI?"

**Expected Behavior:**
- ✅ Returns results about Fei-Fei Li
- ❌ Does NOT return results about Andrew Ng
- ❌ Does NOT return results about Elon Musk

**Why:** Graph filtering should identify "Fei-Fei Li" as the entity and only return chunks connected to Fei-Fei Li in the knowledge graph.

---

### 3. General AI Query Includes All

**Query:** "Who talked about AI?"

**Expected Behavior:**
- ✅ Returns results about Andrew Ng
- ✅ Returns results about Fei-Fei Li
- ✅ Returns results about Elon Musk

**Why:** This is a general query with no specific entity mentioned, so graph filtering should NOT be applied. All relevant chunks should be returned based on vector similarity.

---

### 4. Elon Musk Query Excludes Others

**Query:** "What is Elon Musk's opinion about AI?"

**Expected Behavior:**
- ✅ Returns results about Elon Musk
- ❌ Does NOT return results about Andrew Ng
- ❌ Does NOT return results about Fei-Fei Li

**Why:** Graph filtering should identify "Elon Musk" as the entity and only return chunks connected to Elon Musk in the knowledge graph.

---

### 5. Unknown Person Returns Empty

**Query:** "What is Geoffrey Hinton's work in AI?"

**Expected Behavior:**
- ❌ Returns empty results

**Why:** Geoffrey Hinton is not in our knowledge base. Graph filtering should identify "Geoffrey Hinton" as the entity, find no matches in the graph, and return empty results with a polite message.

---

## Test Data

The tests use real test data from `tests/data/`:

| Person | Data Source | Content |
|--------|-------------|---------|
| **Andrew Ng** | `tests/data/txt/andrew_ng.txt` | Biography and AI work |
| **Andrew Ng** | `tests/data/pdf/Andrew Ng - Wikipedia.pdf` | Wikipedia article |
| **Fei-Fei Li** | Generated in test | Biography and ImageNet work |
| **Elon Musk** | `tests/data/video/elon_ai_danger.mp4` | Video about AI concerns |

---

## Running the Tests

### Prerequisites

1. **Start all services:**
   ```bash
   docker-compose up -d
   ```

2. **Verify services are running:**
   ```bash
   docker-compose ps
   ```

### Run All Tests

```bash
python scripts/run_graph_filtering_tests.py
```

### Run Specific Test Types

```bash
# Run only search tests (no answer generation)
python scripts/run_graph_filtering_tests.py --type search

# Run only answer generation tests
python scripts/run_graph_filtering_tests.py --type answer
```

### Run with pytest Directly

```bash
# All tests
pytest tests/test_graph_filtering_integration.py -v -s

# Only search tests
pytest tests/test_graph_filtering_integration.py::TestGraphFilteringWithRealData -v -s

# Only answer generation tests
pytest tests/test_graph_filtering_integration.py::TestFullQueryAnswerGeneration -v -s

# Specific test
pytest tests/test_graph_filtering_integration.py::TestGraphFilteringWithRealData::test_andrew_ng_query_excludes_fei_fei -v -s
```

---

## Expected Output

### Successful Test Run

```
================================================================ test session starts ================================================================

tests/test_graph_filtering_integration.py::TestGraphFilteringWithRealData::test_andrew_ng_query_excludes_fei_fei 
🔍 Query: What is Andrew Ng's work in AI?
📊 Results: 3 chunks found

  Result 1:
    Score: 0.8234
    Preview: Dr. Andrew Ng is a globally recognized leader in AI (Artificial Intelligence). He is Founder of DeepLearning.AI...
    
✅ PASS: Andrew Ng query correctly excludes Fei-Fei Li
PASSED

tests/test_graph_filtering_integration.py::TestGraphFilteringWithRealData::test_fei_fei_query_excludes_andrew 
🔍 Query: What is Fei-Fei Li's work in AI?
📊 Results: 2 chunks found

  Result 1:
    Score: 0.7891
    Preview: Dr. Fei-Fei Li is a renowned computer scientist and AI researcher. She is the Sequoia Professor...
    
✅ PASS: Fei-Fei Li query correctly excludes Andrew Ng
PASSED

tests/test_graph_filtering_integration.py::TestGraphFilteringWithRealData::test_general_ai_query_includes_all 
🔍 Query: Who talked about AI?
📊 Results: 8 chunks found

  Result 1:
    Score: 0.8123
    Preview: Dr. Andrew Ng is a globally recognized leader in AI...
    ✅ Contains: Andrew Ng
    
  Result 3:
    Score: 0.7654
    Preview: Dr. Fei-Fei Li is a renowned computer scientist...
    ✅ Contains: Fei-Fei Li
    
  Result 5:
    Score: 0.7234
    Preview: I'm a little worried about the AI stuff...
    ✅ Contains: Elon Musk
    
✅ PASS: General AI query includes all three people
   - Andrew Ng: ✅
   - Fei-Fei Li: ✅
   - Elon Musk: ✅
PASSED

=========================================================== 5 passed in 45.23s ============================================================
```

---

## Troubleshooting

### Test Fails: "Should NOT mention Fei-Fei Li"

**Problem:** Graph filtering is not working correctly.

**Solutions:**
1. Check that `use_graph_filter=True` in `src/search/hybrid_search.py`
2. Verify entities are being extracted from queries
3. Check Neo4j has entities and relationships
4. Verify Qdrant chunks have correct IDs matching Neo4j

### Test Fails: "Should return results for Andrew Ng"

**Problem:** No results returned when they should be.

**Solutions:**
1. Check that test data was ingested correctly
2. Verify Qdrant has chunks
3. Verify Neo4j has entities
4. Check embedding generation is working

### Services Not Running

**Error:** "Qdrant is not accessible" or "Neo4j is not accessible"

**Solution:**
```bash
# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs qdrant
docker-compose logs neo4j
```

---

## Test Architecture

### Test Flow

```
1. Setup (once per test module)
   ├── Clean Qdrant collection
   ├── Clean Neo4j database
   ├── Ingest Andrew Ng text
   ├── Ingest Andrew Ng PDF
   ├── Ingest Elon Musk video
   └── Ingest Fei-Fei Li text (generated)

2. Run Tests
   ├── Query with specific entity
   ├── Extract entities from query
   ├── Search Neo4j for entities
   ├── Get related chunk IDs
   ├── Retrieve chunks from Qdrant
   ├── Apply graph filter to vector results
   └── Verify results contain/exclude expected people

3. Teardown
   └── (Data remains for inspection)
```

### Key Components Tested

- **Entity Extraction** - Extracting person names from queries
- **Graph Search** - Finding entities in Neo4j
- **Graph Traversal** - Finding related chunks
- **Graph Filtering** - Excluding unrelated chunks
- **Vector Search** - Semantic similarity
- **Hybrid Search** - Combining vector + graph
- **Answer Generation** - LLM-based answers from filtered results

---

## Integration with CI/CD

Add to `.github/workflows/test.yml`:

```yaml
- name: Run graph filtering tests
  run: |
    docker-compose up -d
    sleep 10  # Wait for services to start
    python scripts/run_graph_filtering_tests.py
  env:
    OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
```

---

## Next Steps

After tests pass:

1. ✅ Graph filtering is working correctly
2. ✅ Entity-based queries return focused results
3. ✅ General queries return broad results
4. ✅ Unknown entities return empty results
5. ✅ Ready for production use!

---

**Run the tests:** `python scripts/run_graph_filtering_tests.py`

