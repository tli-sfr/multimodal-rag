# Graph Filtering Tests - Quick Reference

## One-Line Commands

### Run All Tests

```bash
python scripts/run_graph_filtering_tests.py
```

### Run Specific Test Types

```bash
# Search tests only (no answer generation)
python scripts/run_graph_filtering_tests.py --type search

# Answer generation tests only
python scripts/run_graph_filtering_tests.py --type answer
```

### Using pytest Directly

```bash
# All tests
pytest tests/test_graph_filtering_integration.py -v -s

# Specific test class
pytest tests/test_graph_filtering_integration.py::TestGraphFilteringWithRealData -v -s

# Specific test
pytest tests/test_graph_filtering_integration.py::TestGraphFilteringWithRealData::test_andrew_ng_query_excludes_fei_fei -v -s
```

---

## Test Scenarios

| Test | Query | Expected Results |
|------|-------|------------------|
| **Andrew Ng** | "What is Andrew Ng's work in AI?" | ✅ Andrew Ng<br>❌ Fei-Fei Li<br>❌ Elon Musk |
| **Fei-Fei Li** | "What is Fei-Fei Li's work in AI?" | ✅ Fei-Fei Li<br>❌ Andrew Ng<br>❌ Elon Musk |
| **General AI** | "Who talked about AI?" | ✅ Andrew Ng<br>✅ Fei-Fei Li<br>✅ Elon Musk |
| **Elon Musk** | "What is Elon Musk's opinion about AI?" | ✅ Elon Musk<br>❌ Andrew Ng<br>❌ Fei-Fei Li |
| **Unknown** | "What is Geoffrey Hinton's work in AI?" | ❌ Empty results |

---

## Prerequisites

```bash
# Start services
docker-compose up -d

# Verify services
docker-compose ps
```

---

## Expected Output

```
✅ 8 passed in 45.23s

Test Results:
  ✅ Andrew Ng query excludes Fei-Fei Li
  ✅ Fei-Fei Li query excludes Andrew Ng
  ✅ General AI query includes all three
  ✅ Elon Musk query excludes others
  ✅ Unknown person returns empty
  ✅ Andrew Ng full query (with answer)
  ✅ Fei-Fei Li full query (with answer)
  ✅ General AI full query (with answer)
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Services not running | `docker-compose up -d` |
| Tests fail | Check `tests/GRAPH_FILTERING_TESTS.md` |
| No results returned | Verify data ingestion in test setup |
| Wrong results returned | Check graph filter is enabled |

---

## Test Data

| Person | Source | Type |
|--------|--------|------|
| Andrew Ng | `tests/data/txt/andrew_ng.txt` | Text |
| Andrew Ng | `tests/data/pdf/Andrew Ng - Wikipedia.pdf` | PDF |
| Fei-Fei Li | Generated in test | Text |
| Elon Musk | `tests/data/video/elon_ai_danger.mp4` | Video |

---

## Quick Debug

```bash
# Check Qdrant
curl http://localhost:6333/collections

# Check Neo4j (in browser)
open http://localhost:7474

# View test logs
pytest tests/test_graph_filtering_integration.py -v -s --log-cli-level=DEBUG
```

---

**Quick start:** `python scripts/run_graph_filtering_tests.py`

