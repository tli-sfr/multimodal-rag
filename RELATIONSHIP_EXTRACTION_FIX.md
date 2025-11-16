# Relationship Extraction Fix

## Issue
When ingesting PDF files, the relationship extraction was failing with warnings like:
```
WARNING | Failed to create relationship: 'SPOUSE_OF'
WARNING | Failed to create relationship: 'CHILD_OF'
WARNING | Failed to create relationship: 'AWARDED'
```

## Root Cause
The LLM (GPT-4) was extracting relationships with types that weren't defined in the `RelationshipType` enum. When the code tried to create these relationships, it failed because the relationship types didn't exist.

The original enum only had these types:
- MENTIONS
- RELATED_TO
- PART_OF
- LOCATED_IN
- WORKS_FOR
- APPEARS_IN
- TRANSCRIBED_FROM
- EXTRACTED_FROM

But the LLM was naturally extracting more specific relationships like:
- SPOUSE_OF (family relationships)
- CHILD_OF (family relationships)
- AWARDED (achievement relationships)
- And many others

## Solution Implemented

### 1. Expanded RelationshipType Enum

Added comprehensive relationship types to `src/models.py`:

**Family Relationships:**
- SPOUSE_OF
- CHILD_OF
- PARENT_OF
- SIBLING_OF

**Achievement Relationships:**
- AWARDED
- RECEIVED
- WON

**Work/Organization Relationships:**
- EMPLOYED_BY
- MEMBER_OF

**Educational Relationships:**
- STUDIED_AT
- GRADUATED_FROM

**Creation Relationships:**
- CREATED_BY
- AUTHORED_BY
- FOUNDED_BY

### 2. Graceful Fallback Handling

Updated `src/extraction/relationship_extractor.py` to:
- Try to match the LLM's relationship type to the enum
- If the type doesn't exist, log a debug message and use `RELATED_TO` as fallback
- Continue processing instead of failing

### 3. Updated LLM Prompt

Enhanced the prompt to:
- List all available relationship types
- Instruct the LLM to use exact types from the list
- Provide clear examples of each relationship type

## Benefits

1. **More Accurate Knowledge Graph**: The system can now capture specific relationship types like family connections, awards, and educational history

2. **Robust Error Handling**: Unknown relationship types won't break the extraction process

3. **Better Semantic Search**: More specific relationships enable better graph traversal and context retrieval

4. **Extensible**: Easy to add new relationship types in the future

## Testing

After this fix, you should see:
- ✅ No more "Failed to create relationship" warnings
- ✅ Relationships successfully extracted and stored in Neo4j
- ✅ More detailed knowledge graph with specific relationship types

## Verification

To verify relationships are being extracted:

1. **Check the logs** - You should see:
   ```
   INFO | Extracted X relationships from Y chunks
   ```

2. **Query Neo4j** - Open http://localhost:7474 and run:
   ```cypher
   MATCH (a)-[r]->(b)
   RETURN type(r) as relationship_type, count(*) as count
   ORDER BY count DESC
   ```

3. **Use the Streamlit UI** - Upload a document and check the Query tab to see if relationships are being used in search results

## Example Relationships Extracted

From a typical document, you might now see:
- `(Marie Curie)-[AWARDED]->(Nobel Prize)`
- `(Marie Curie)-[SPOUSE_OF]->(Pierre Curie)`
- `(Marie Curie)-[STUDIED_AT]->(University of Paris)`
- `(Marie Curie)-[DISCOVERED]->(Radium)`

## Next Steps

If you want to add more relationship types:

1. Add them to `RelationshipType` enum in `src/models.py`
2. Update the prompt in `src/extraction/relationship_extractor.py`
3. Restart the application

The fallback mechanism ensures the system keeps working even if you forget to update the prompt!

