# Issues and Solutions

## Issue 1: Mock Data Not Showing on UI

### Problem
After running `python scripts/prepare_mock_data.py`, the data didn't appear on http://localhost:8502

### Root Causes

1. **No "Browse Data" Feature**: The original UI only had:
   - Upload tab (for uploading NEW files)
   - Query tab (shows results only when you SEARCH)
   - Evaluation tab
   
   There was no way to VIEW existing data without searching.

2. **Wrong Port**: Streamlit was running on port 8502, not 8501

### Solution ✅

**Added a new "Browse Data" tab** that shows:
- Total chunks in Qdrant vector store
- Total entities and relationships in Neo4j
- Sample chunks with content preview
- Sample entities in a table
- Link to Neo4j browser for graph visualization

**How to use:**
1. Open http://localhost:8502
2. Click on "📊 Browse Data" tab
3. You'll see all the mock data statistics and samples

---

## Issue 2: Query "Andrew Ng" Returns Only 1 Result

### Problem
Searching for "Andrew Ng" only returned 1 result instead of the expected 3 documents (video, audio, PDF)

### Root Causes

1. **High Score Threshold**: The hybrid search had `score_threshold=0.7` which is very strict
   - This filtered out results with similarity scores below 0.7
   - Mock data embeddings might not have perfect similarity scores

2. **Possible Data Issue**: Need to verify all 20 chunks were actually ingested

### Solution ✅

**Lowered score threshold from 0.7 to 0.3** in `src/search/hybrid_search.py`

This allows more results to pass through while still filtering out completely irrelevant content.

**To test:**
1. Restart Streamlit (already done)
2. Go to "🔍 Query" tab
3. Search for "Andrew Ng"
4. Should now see more results

---

## How to Verify Mock Data

### Option 1: Use the New "Browse Data" Tab
1. Open http://localhost:8502
2. Click "📊 Browse Data"
3. Check:
   - Total Chunks: Should be 20
   - Total Entities: Should be 44
   - Total Relationships: Should be 37

### Option 2: Use Neo4j Browser
1. Open http://localhost:7474
2. Run this query:
```cypher
MATCH (e:Entity {name: "Andrew Ng"})-[r*1..2]-(connected)
RETURN e, r, connected
```

### Option 3: Run Verification Script
```bash
python scripts/verify_mock_data.py
```

---

## Expected Mock Data

### Andrew Ng (3 documents)
- **Video**: "The Future of AI" - 3 chunks
- **Audio**: "AI Course Introduction" - 3 chunks  
- **PDF**: "Biography" - 4 chunks
- **Total**: 10 chunks, 23 entities, 20 relationships

### Fei-Fei Li (3 documents)
- **Video**: "AI Research at Stanford" - 3 chunks
- **Audio**: "ImageNet Talk" - 3 chunks
- **PDF**: "Biography" - 4 chunks
- **Total**: 10 chunks, 21 entities, 17 relationships

### Grand Total
- **20 chunks** in Qdrant
- **44 entities** in Neo4j
- **37 relationships** in Neo4j

---

## Test Queries

Try these in the Query tab:

1. **"Andrew Ng"** - Should return Andrew Ng content
2. **"Fei-Fei Li"** - Should return Fei-Fei Li content
3. **"machine learning course"** - Should return Andrew Ng's course content
4. **"ImageNet dataset"** - Should return Fei-Fei Li's ImageNet content
5. **"AI education"** - Should return Andrew Ng's Coursera content
6. **"computer vision"** - Should return Fei-Fei Li's research content

---

## Files Modified

1. **src/ui/app.py** - Added "Browse Data" tab
2. **src/search/hybrid_search.py** - Lowered score threshold from 0.7 to 0.3

---

## Next Steps

1. ✅ Streamlit is running at http://localhost:8502
2. ✅ Browse Data tab added
3. ✅ Score threshold lowered
4. ⏭️ Test queries in the UI
5. ⏭️ Verify all mock data is visible
6. ⏭️ If still only 1 result, investigate Qdrant data integrity

---

## Cleanup

When done testing:
```bash
python scripts/cleanup_mock_data.py
```

This will remove all mock data from both Qdrant and Neo4j.

