# Mock Data Scripts

This directory contains scripts to populate and clean up mock data for testing the multimodal RAG system.

## Overview

The mock data includes realistic content about two AI researchers:

### Andrew Ng (Related Content)
- **Video**: "The Future of AI" - Discusses AI's impact on industries
- **Audio**: "AI Course Introduction" - Introduction to machine learning course
- **PDF**: Biography - Career, education, and achievements

### Fei-Fei Li (Unrelated Content)
- **Video**: "AI Research at Stanford" - Computer vision and ImageNet
- **Audio**: "ImageNet Talk" - Story of creating ImageNet dataset
- **PDF**: Biography - Career, education, and achievements

## Mock Data Structure

Each document includes:
- **Chunks**: 3-4 text chunks with realistic content and metadata
- **Entities**: 6-10 entities (people, organizations, concepts, events)
- **Relationships**: 4-9 relationships between entities
- **Embeddings**: Generated using OpenAI embeddings API

All mock data is tagged with `mock_data: true` property for easy cleanup.

## Usage

### 1. Prepare Mock Data

Populate Qdrant and Neo4j with mock data:

```bash
python scripts/prepare_mock_data.py
```

**Expected output:**
```
INFO     | Processing andrew_ng_video...
INFO     |   Generating embeddings for 3 chunks...
INFO     |   Adding 3 chunks to Qdrant...
INFO     |   Adding 7 entities to Neo4j...
INFO     |   Adding 6 relationships to Neo4j...
SUCCESS  | ✅ andrew_ng_video completed!
...
SUCCESS  | ✅ Mock data population completed!
============================================================
SUCCESS  | Total chunks added to Qdrant: 21
SUCCESS  | Total entities added to Neo4j: 45
SUCCESS  | Total relationships added to Neo4j: 35
============================================================
```

### 2. Use the Mock Data

**Start Streamlit UI:**
```bash
streamlit run src/ui/app.py
```

**Test Hybrid Search:**

1. **Search for "Andrew Ng"**
   - Should return 3 documents (video, audio, PDF)
   - All content is related to Andrew Ng
   - Knowledge graph shows connections to Coursera, Stanford, deeplearning.ai

2. **Search for "Fei-Fei Li"**
   - Should return 3 documents (video, audio, PDF)
   - All content is related to Fei-Fei Li
   - Knowledge graph shows connections to ImageNet, Stanford AI Lab

3. **Search for "machine learning"**
   - Should return Andrew Ng content (he's an ML expert)
   - May also return some Fei-Fei Li content (related to deep learning)

4. **Search for "ImageNet"**
   - Should return Fei-Fei Li content
   - Should NOT return Andrew Ng content (unrelated)

### 3. Verify in Neo4j Browser

Open http://localhost:7474 and run:

```cypher
// View all mock entities
MATCH (e:Entity)
WHERE e.mock_data = true
RETURN e.name, e.type, e.source_modality
LIMIT 20

// View mock relationships
MATCH (source:Entity)-[r]->(target:Entity)
WHERE r.mock_data = true
RETURN source.name, type(r), target.name
LIMIT 20

// View Andrew Ng's knowledge graph
MATCH (e:Entity {name: "Andrew Ng"})-[r*1..2]-(connected)
RETURN e, r, connected

// View Fei-Fei Li's knowledge graph
MATCH (e:Entity {name: "Fei-Fei Li"})-[r*1..2]-(connected)
RETURN e, r, connected

// Count entities by type
MATCH (e:Entity)
WHERE e.mock_data = true
RETURN e.type as entity_type, count(e) as count
ORDER BY count DESC

// Count relationships by type
MATCH ()-[r]->()
WHERE r.mock_data = true
RETURN type(r) as relationship_type, count(r) as count
ORDER BY count DESC
```

### 4. Clean Up Mock Data

Remove all mock data from Qdrant and Neo4j:

```bash
python scripts/cleanup_mock_data.py
```

**You will be prompted for confirmation:**
```
⚠️  WARNING: This will delete all mock data from Neo4j and Qdrant!
Are you sure you want to continue? (yes/no):
```

Type `yes` to proceed.

**Expected output:**
```
INFO     | Cleaning up Neo4j...
INFO     |   Found 45 mock entities
INFO     |   Found 35 mock relationships
SUCCESS  |   ✅ Deleted 35 mock relationships
SUCCESS  |   ✅ Deleted 45 mock entities
INFO     | Cleaning up Qdrant...
SUCCESS  |   ✅ Deleted 21 mock chunks from Qdrant
SUCCESS  | ✅ Mock data cleanup completed!
```

## Testing Scenarios

### Scenario 1: Related Content Search
**Query**: "Tell me about Andrew Ng's work in AI education"

**Expected Results**:
- Video chunk: "At Stanford, we've been working on making AI education accessible..."
- Audio chunk: "Welcome to Machine Learning! I'm Andrew Ng..."
- PDF chunk: "He is the founder of DeepLearning.AI and co-founder of Coursera..."
- Knowledge graph shows: Andrew Ng → FOUNDER_OF → Coursera, deeplearning.ai

### Scenario 2: Unrelated Content Separation
**Query**: "What is ImageNet?"

**Expected Results**:
- Fei-Fei Li content ONLY
- No Andrew Ng content
- Knowledge graph shows: Fei-Fei Li → CREATED_BY → ImageNet

### Scenario 3: Multimodal Search
**Query**: "machine learning courses"

**Expected Results**:
- Andrew Ng audio (course introduction)
- Andrew Ng video (mentions education)
- Mixed modalities (VIDEO, AUDIO, TEXT)

## Troubleshooting

### Issue: "No module named 'src'"
**Solution**: Run from the project root directory:
```bash
cd /Users/admin/ai/multimodal
python scripts/prepare_mock_data.py
```

### Issue: "Connection refused" errors
**Solution**: Make sure Docker services are running:
```bash
docker-compose up -d
```

### Issue: OpenAI API errors
**Solution**: Check your `.env` file has valid `OPENAI_API_KEY`

### Issue: Mock data still appears after cleanup
**Solution**: Manually verify in Neo4j:
```cypher
MATCH (e:Entity) WHERE e.mock_data = true DELETE e
MATCH ()-[r]->() WHERE r.mock_data = true DELETE r
```

## Files

- `prepare_mock_data.py` - Populates mock data
- `cleanup_mock_data.py` - Removes mock data
- `MOCK_DATA_README.md` - This file

