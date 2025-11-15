#!/bin/bash

# Script to commit graph filtering implementation to GitHub
# This ensures only necessary files are committed

set -e  # Exit on error

echo "=========================================="
echo "Git Commit Helper - Graph Filtering"
echo "=========================================="
echo ""

# Check if git is initialized
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo "❌ Not a git repository. Initializing..."
    git init
    echo "✅ Git initialized"
    echo ""
fi

# Check if there's a remote
if ! git remote get-url origin > /dev/null 2>&1; then
    echo "⚠️  No remote repository configured."
    echo "Please add your GitHub repository:"
    echo ""
    echo "  git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git"
    echo ""
    read -p "Enter your GitHub repository URL (or press Enter to skip): " REPO_URL
    
    if [ -n "$REPO_URL" ]; then
        git remote add origin "$REPO_URL"
        echo "✅ Remote added: $REPO_URL"
    else
        echo "⚠️  Skipping remote configuration. You can add it later."
    fi
    echo ""
fi

# Stage essential files
echo "📦 Staging essential files..."
echo ""

# Core configuration files
git add .gitignore
git add DEPLOYMENT.md
git add GIT_COMMIT_GUIDE.md
git add requirements.txt
git add docker-compose.yml
git add .env.example
git add README.md 2>/dev/null || true
git add QUICKSTART.md 2>/dev/null || true

# All source code directories
git add src/

# All scripts (including all .py files)
git add scripts/*.py
git add scripts/*.sh
git add scripts/*.md 2>/dev/null || true

# All tests
git add tests/*.py
git add tests/__init__.py 2>/dev/null || true
git add tests/conftest.py 2>/dev/null || true

# Config directory if it exists
git add config/ 2>/dev/null || true

# Documentation if it exists
git add docs/ 2>/dev/null || true

# Examples if they exist
git add examples/ 2>/dev/null || true

echo "✅ Files staged"
echo ""

# Show what will be committed
echo "📋 Files to be committed:"
git status --short
echo ""

# Show diff summary
echo "📊 Changes summary:"
git diff --cached --stat
echo ""

# Confirm before committing
read -p "Proceed with commit? (y/n): " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Commit cancelled"
    exit 1
fi

# Commit with detailed message
echo "💾 Creating commit..."
git commit -m "feat: implement graph-based filtering for hybrid search

## Features Added

- Graph-based filtering to exclude unconnected content from search results
- Integration with Neo4j knowledge graph for relationship-aware search
- Cache management UI for Streamlit (clear cache button)
- Proper entity-chunk mapping in mock data

## Implementation Details

### Core Changes
- Added \`use_graph_filter\` parameter to HybridSearchEngine (default: True)
- Implemented \`_apply_graph_filter()\` method to filter vector results
- Modified search flow: Vector → Graph → Filter → Fusion → Top-k
- Added graph traversal methods to Neo4jClient:
  - \`find_entities_by_name()\` - Fuzzy entity matching
  - \`find_related_chunks()\` - Graph traversal up to depth 2
- Added \`retrieve_by_ids()\` to QdrantVectorStore for ID-based retrieval

### Files Modified
- src/search/hybrid_search.py - Graph filtering logic
- src/pipeline.py - Pipeline integration
- src/ui/app.py - Cache clear button
- src/graph/neo4j_client.py - Graph query methods
- src/vector_store/qdrant_client.py - ID-based retrieval
- scripts/prepare_mock_data.py - Fixed entity-chunk mapping

## Impact

**Before (Vector Search Only):**
- Query: \"Andrew Ng\" → 18 results
- Includes 2 Fei-Fei Li results (semantic similarity)

**After (Hybrid Search with Graph Filtering):**
- Query: \"Andrew Ng\" → 10 results
- 0 Fei-Fei Li results ✅
- All results connected to Andrew Ng in knowledge graph

## Testing

Run \`python scripts/test_graph_search.py\` to verify graph filtering.

## Deployment

See DEPLOYMENT.md for setup instructions on new machines."

echo "✅ Commit created"
echo ""

# Show commit details
echo "📝 Commit details:"
git log -1 --stat
echo ""

# Ask about pushing
if git remote get-url origin > /dev/null 2>&1; then
    read -p "Push to GitHub? (y/n): " -n 1 -r
    echo ""
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        # Get current branch
        BRANCH=$(git rev-parse --abbrev-ref HEAD)
        
        echo "🚀 Pushing to origin/$BRANCH..."
        git push -u origin "$BRANCH"
        echo "✅ Pushed to GitHub"
        echo ""
        echo "🎉 Done! Your changes are now on GitHub."
        echo ""
        echo "To clone on another machine:"
        echo "  git clone $(git remote get-url origin)"
        echo "  cd $(basename $(git rev-parse --show-toplevel))"
        echo "  See DEPLOYMENT.md for setup instructions"
    else
        echo "⏭️  Skipping push. You can push later with:"
        echo "  git push -u origin $(git rev-parse --abbrev-ref HEAD)"
    fi
else
    echo "⚠️  No remote configured. Add remote and push with:"
    echo "  git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git"
    echo "  git push -u origin $(git rev-parse --abbrev-ref HEAD)"
fi

echo ""
echo "=========================================="
echo "✅ Commit process complete!"
echo "=========================================="

