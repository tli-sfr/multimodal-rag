# Debug Output Guide - Entity Matching

## Overview

The system now prints detailed debug information when entities are matched during graph search. This helps you understand:
1. What entities were extracted from your query
2. Which entities were found in the knowledge graph
3. How entities connect to chunks through graph traversal

## Debug Output Sections

### 1. Extracted Entities from Query

Shows what entities the system extracted from your query text.

```
======================================================================
EXTRACTED ENTITIES FROM QUERY: 'Who works in Stanford University'
  Potential entities: ['Who works in Stanford University', 'works', 'Stanford', 'University']
======================================================================
```

**What this means:**
- The system tries multiple entity extraction strategies
- It extracts both the full query and individual capitalized words
- These are potential entities that will be searched in the graph

### 2. Matched Entities

Shows which entities were actually found in the Neo4j knowledge graph.

```
======================================================================
MATCHED ENTITIES:
  1. Name: 'Deep Neural Networks' | Type: Concept | ID: 174cacd3-112b-4ca1-8e79-5dd0dbaaf51b
     Description: ML architecture
  2. Name: 'Stanford University' | Type: Organization | ID: c8b48b91-5314-4909-8a9e-c214d8519929
     Description: Research university
  3. Name: 'Stanford University' | Type: Organization | ID: 46909aa8-f326-4fcd-b963-65b2e2c37c8b
     Description: Research university
  4. Name: 'Stanford AI Lab' | Type: Organization | ID: e0695553-4090-463d-b181-0d5664dc3306
     Description: Research laboratory
  5. Name: 'Stanford HAI' | Type: Organization | ID: 2f6a2bb8-53d3-4189-9581-1e0c2f16fcce
     Description: Human-Centered AI Institute
  ... (up to 10 entities shown)
======================================================================
```

**What this means:**
- These are actual entities found in your knowledge graph
- Multiple entities can have the same name (different IDs) if they appear in different chunks
- The system uses fuzzy matching (case-insensitive, partial match)
- Entity types: Person, Organization, Location, Concept, Event, etc.

### 3. Related Chunks from Graph Traversal

Shows which chunks are connected to the matched entities through graph relationships.

```
======================================================================
RELATED CHUNKS FROM GRAPH TRAVERSAL:
  1. Entity: 'Andrew Ng' (Person) | Relevance: 0.80
     Chunk ID: 988ce544-3ddd-46d8-8d9c-66436edb0949
  2. Entity: 'Fei-Fei Li' (Person) | Relevance: 0.80
     Chunk ID: 67203046-6a75-4778-b1b8-9c49ccbfc9f6
  3. Entity: 'Andrew Ng' (Person) | Relevance: 0.80
     Chunk ID: 49c74b78-44bd-4cf6-b095-022e7b818494
  4. Entity: 'Computer Vision' (Concept) | Relevance: 0.80
     Chunk ID: 793973b5-c482-4480-8e0b-75128c904b08
  5. Entity: 'Google Brain' (Organization) | Relevance: 0.50
     Chunk ID: 49c74b78-44bd-4cf6-b095-022e7b818494
  ... (up to 10 chunks shown, total may be more)
======================================================================
```

**What this means:**
- These are chunks that contain entities related to your query
- **Relevance scores:**
  - `1.0` = Direct match (entity is in the chunk)
  - `0.8` = 1 relationship away (e.g., Andrew Ng WORKS_FOR Stanford University)
  - `0.5` = 2 relationships away (e.g., Google Brain FOUNDED_BY Andrew Ng WORKS_FOR Stanford)
  - `0.3` = 3+ relationships away
- The system traverses up to 2 relationships deep by default

## Example: "Who works in Stanford University"

### Full Debug Output

```
2025-11-16 09:49:42.695 | INFO | EXTRACTED ENTITIES FROM QUERY: 'Who works in Stanford University'
2025-11-16 09:49:42.696 | INFO |   Potential entities: ['Who works in Stanford University', 'works', 'Stanford', 'University']

2025-11-16 09:49:42.710 | INFO | Found 10 matching entities in graph

2025-11-16 09:49:42.710 | INFO | MATCHED ENTITIES:
2025-11-16 09:49:42.710 | INFO |   1. Name: 'Deep Neural Networks' | Type: Concept
2025-11-16 09:49:42.711 | INFO |   2. Name: 'Stanford University' | Type: Organization ✅
2025-11-16 09:49:42.711 | INFO |   3. Name: 'Stanford University' | Type: Organization ✅
2025-11-16 09:49:42.711 | INFO |   4. Name: 'Stanford University' | Type: Organization ✅
2025-11-16 09:49:42.711 | INFO |   5. Name: 'Stanford AI Lab' | Type: Organization
2025-11-16 09:49:42.711 | INFO |   6. Name: 'Stanford HAI' | Type: Organization

2025-11-16 09:49:42.734 | INFO | Found 20 related chunks through graph

2025-11-16 09:49:42.734 | INFO | RELATED CHUNKS FROM GRAPH TRAVERSAL:
2025-11-16 09:49:42.734 | INFO |   1. Entity: 'Andrew Ng' (Person) | Relevance: 0.80 ✅
2025-11-16 09:49:42.734 | INFO |   2. Entity: 'Fei-Fei Li' (Person) | Relevance: 0.80 ✅
2025-11-16 09:49:42.734 | INFO |   3. Entity: 'Andrew Ng' (Person) | Relevance: 0.80
2025-11-16 09:49:42.734 | INFO |   4. Entity: 'Computer Vision' (Concept) | Relevance: 0.80
```

### Interpretation

1. **Query**: "Who works in Stanford University"
2. **Extracted**: System found "Stanford University" as a multi-word entity ✅
3. **Matched**: Found 3 "Stanford University" entities in the graph ✅
4. **Related**: Found Andrew Ng and Fei-Fei Li connected via WORKS_FOR relationship ✅
5. **Result**: Returns chunks about Andrew Ng and Fei-Fei Li ✅

## How to View Debug Output

### In the Streamlit UI

The debug output appears in the terminal where you run `streamlit run src/ui/app.py`.

```bash
# Start the app
streamlit run src/ui/app.py

# The debug output will appear in this terminal when you perform a search
```

### In Tests

```bash
# Run the entity matching debug test
python3 scripts/test_entity_matching_debug.py

# This will show debug output for multiple test queries
```

### In Your Own Code

```python
from loguru import logger
import sys

# Configure logger to show INFO level
logger.remove()
logger.add(sys.stderr, level="INFO")

# Now run your search
results = search_engine.search(query, top_k=5)
```

## Troubleshooting

### No Entities Found

```
INFO | Entities extracted (['Stanford', 'University']) but not found in graph
```

**Possible causes:**
- The entity doesn't exist in your knowledge graph
- You need to load data first: `python3 scripts/prepare_mock_data.py`
- The entity name doesn't match (try fuzzy search)

### Entities Found but No Related Chunks

```
INFO | Found 5 matching entities in graph
INFO | No related chunks found through graph traversal
```

**Possible causes:**
- Entities exist but have no relationships to chunks
- The `source_id` field is not set on entities
- Relationships are missing in the graph

### Wrong Entities Matched

```
INFO | MATCHED ENTITIES:
INFO |   1. Name: 'University' | Type: Concept  ❌ (too generic)
```

**Solution:**
- The multi-word entity extraction should help with this
- Make sure you're using the latest version with the entity extraction fix
- Consider using more specific entity names in your data

## Files Modified

- `src/search/hybrid_search.py`: Added debug logging for entity matching
- `scripts/test_entity_matching_debug.py`: Test script to demonstrate debug output

