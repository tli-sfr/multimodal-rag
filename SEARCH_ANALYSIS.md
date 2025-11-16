# Why Fei-Fei Li Appears in "Andrew Ng" Search Results

## The Issue

When searching for "Andrew Ng", result #7 is about Fei-Fei Li:

```
7. Score: 0.4407 | FEI-FEI LI | [video] I'm Fei-Fei Li, and I direct the Stanford Artificial Intelli...
   Doc: mock_data_feifei_li_video
```

## Root Cause Analysis

### 1. **Semantic Similarity in AI Research Context**

The search uses **semantic embeddings** (OpenAI text-embedding-3-large), which finds content that is **semantically similar**, not just keyword matches.

Looking at the scores with threshold 0.3:

| Rank | Score  | Person      | Content Preview |
|------|--------|-------------|-----------------|
| 1    | 0.7388 | Andrew Ng   | Andrew Ng is a British-American computer scientist... |
| 2    | 0.6559 | Andrew Ng   | Welcome to Machine Learning! I'm Andrew Ng... |
| 3    | 0.5780 | Andrew Ng   | Hello everyone, I'm Andrew Ng... |
| 6    | 0.4942 | Andrew Ng   | At Stanford, we've been working on making AI education... |
| **7**| **0.4407** | **Fei-Fei Li** | **I'm Fei-Fei Li, and I direct the Stanford Artificial Intelli...** |
| 8    | 0.4240 | Andrew Ng   | I've been teaching this course at Stanford... |
| 9    | 0.4151 | Fei-Fei Li  | Fei-Fei Li is a Chinese-American computer scientist... |

### 2. **Why Score 0.4407 for Fei-Fei Li?**

The Fei-Fei Li content has semantic similarity to "Andrew Ng" because:

✅ **Both are AI researchers at Stanford**
- Andrew Ng: "At Stanford, we've been working on making AI education..."
- Fei-Fei Li: "I direct the Stanford Artificial Intelligence Lab..."

✅ **Similar professional context**
- Both are computer scientists
- Both work on AI/machine learning
- Both are professors at Stanford
- Both have similar biographical structures

✅ **Similar sentence structures**
- "I'm Andrew Ng..." vs "I'm Fei-Fei Li..."
- Both introduce themselves in similar ways
- Both describe their work at Stanford

### 3. **The Mock Data Problem**

Looking at the mock data content, there's significant overlap in:
- **Institutional affiliation**: Both at Stanford
- **Field**: Both in AI/ML
- **Content structure**: Similar biographical formats
- **Vocabulary**: "Stanford", "AI", "machine learning", "research", "professor"

This creates **high semantic similarity** even though they are different people.

## Is This a Bug or Expected Behavior?

### ✅ **This is EXPECTED behavior for semantic search**

Semantic search is designed to find **contextually related** content, not just exact matches. 

**Example**: If you search for "Einstein", you might also get results about "Niels Bohr" or "Richard Feynman" because they're semantically related (all physicists, similar era, similar context).

Similarly, searching for "Andrew Ng" returns Fei-Fei Li content because they share:
- Same institution (Stanford)
- Same field (AI/ML)
- Similar roles (professors, researchers)
- Similar content structure

## Solutions

### Option 1: Increase Score Threshold (Trade-off: Fewer Results)

```yaml
# config/config.yaml
score_threshold: 0.5  # Instead of 0.3
```

**Result with threshold 0.5:**
- Only 5 results (all Andrew Ng)
- No Fei-Fei Li content
- But you lose some valid Andrew Ng content too

### Option 2: Add Keyword Filtering (Recommended)

Modify the search to **require** the query terms to appear in the content:

```python
# In hybrid_search.py
# After vector search, filter results to require "andrew" or "ng" in content
filtered_results = [
    r for r in results 
    if any(term in r.content.lower() for term in query.text.lower().split())
]
```

### Option 3: Use Entity-Based Filtering

Since you have entity extraction, you could:
1. Extract entities from the query ("Andrew Ng" → PERSON entity)
2. Only return results that mention that specific entity
3. Use the knowledge graph to filter

### Option 4: Improve Mock Data Diversity

The current mock data has too much overlap. Make the content more distinct:
- Andrew Ng: Focus on **online education, Coursera, deep learning courses**
- Fei-Fei Li: Focus on **computer vision, ImageNet, visual recognition**

This would reduce semantic overlap.

## Current Behavior Summary

With `score_threshold: 0.3`:
- **17 results** total
- **10 results** shown (top_k=10 in reranking)
- **~6 Fei-Fei Li results** mixed in (scores 0.30-0.44)
- **~11 Andrew Ng results** (scores 0.31-0.74)

The system is working as designed - it's finding semantically similar content about AI researchers at Stanford.

## Recommendation

For your use case (testing multimodal RAG), I recommend:

1. **Keep threshold at 0.3** - Shows the system is working
2. **Add keyword boosting** - Give higher scores to results that contain query terms
3. **Use this as a demo** - Show that semantic search finds related content
4. **Add entity filtering option** - Let users toggle "strict matching" vs "semantic matching"

This way you can demonstrate both:
- ✅ Semantic search (finds related AI researchers)
- ✅ Precise search (finds only Andrew Ng when filtered)

---

## Technical Details

**Embedding Model**: OpenAI text-embedding-3-large (3072 dimensions)
**Similarity Metric**: Cosine similarity (0.0 = unrelated, 1.0 = identical)
**Score 0.44**: Moderately similar (same domain, different person)
**Score 0.74**: Highly similar (exact person match)

The 0.44 score for Fei-Fei Li is actually **correct** - she IS semantically related to Andrew Ng in the AI research context!

