# Streamlit UI Troubleshooting Guide

## Problem: Video Upload Fails with "verbose" Error

### Symptoms

When uploading a video through the Streamlit UI, you see this error:

```
2025-11-15 18:05:58.214 | WARNING  | src.ingestion.video_ingester:_extract_and_transcribe_audio:203 - Failed to extract/transcribe audio: got an unexpected keyword argument 'verbose'
```

And nothing is saved to the Qdrant database.

### Root Cause

Streamlit is running with **cached/old code**. Even though the code has been fixed in `src/ingestion/video_ingester.py`, Streamlit is still using the old version from:
- Python bytecode cache (`__pycache__`)
- Streamlit's internal cache
- The running process hasn't been restarted

### Solution 1: Quick Restart (Recommended)

Use the automated restart script:

```bash
# Option A: Bash script
./scripts/restart_streamlit.sh

# Option B: Python script
python scripts/restart_streamlit.py
```

This will:
1. ✅ Stop all running Streamlit processes
2. ✅ Clear Python bytecode cache (`__pycache__`)
3. ✅ Clear Streamlit cache (`~/.streamlit/cache`)
4. ✅ Restart Streamlit on port 8501

### Solution 2: Manual Restart

If the automated script doesn't work, do it manually:

```bash
# 1. Stop Streamlit
pkill -f "streamlit run"
lsof -ti:8501 | xargs kill -9

# 2. Clear Python cache
find . -type d -name "__pycache__" -exec rm -rf {} +
find . -type f -name "*.pyc" -delete

# 3. Clear Streamlit cache
rm -rf ~/.streamlit/cache

# 4. Wait a moment
sleep 2

# 5. Restart Streamlit
streamlit run src/ui/app.py --server.port 8501
```

### Solution 3: Use the UI Button

If Streamlit is already running:

1. Open http://localhost:8501
2. Look for the **"Clear Cache & Reload Pipeline"** button in the sidebar
3. Click it
4. Wait for the page to reload
5. Try uploading the video again

**Note:** This only clears Streamlit's cache, not Python bytecode cache. If it doesn't work, use Solution 1 or 2.

---

## Problem: Local Tests Work But UI Doesn't

### Why This Happens

When you run tests directly with Python:
```bash
python scripts/extract_test_data.py --type video
```

Python loads the **current code** from disk.

But when Streamlit is running, it:
- Loads code once when it starts
- Caches Python modules
- Caches Streamlit components
- **Doesn't automatically reload when code changes**

### Solution

**Always restart Streamlit after code changes:**

```bash
./scripts/restart_streamlit.sh
```

Or use Streamlit's auto-reload feature (if enabled):
- Press `R` in the terminal where Streamlit is running
- Or click "Rerun" in the UI

---

## Problem: Changes Not Reflected After Restart

### Possible Causes

1. **Wrong Python environment**
   ```bash
   # Check which Python Streamlit is using
   which streamlit
   which python
   
   # Should both be in your venv
   # /Users/admin/ai/multimodal/venv/bin/streamlit
   # /Users/admin/ai/multimodal/venv/bin/python
   ```

2. **Multiple Streamlit processes running**
   ```bash
   # Check for multiple processes
   ps aux | grep streamlit
   
   # Kill all of them
   pkill -f streamlit
   ```

3. **Code not saved**
   - Make sure you saved the file in your editor
   - Check the file modification time:
     ```bash
     ls -la src/ingestion/video_ingester.py
     ```

4. **Wrong file being edited**
   - Make sure you're editing the file in the correct directory
   - Check the file path:
     ```bash
     pwd
     # Should be: /Users/admin/ai/multimodal
     ```

---

## Problem: Streamlit Won't Start

### Error: "Address already in use"

```bash
# Kill the process using port 8501
lsof -ti:8501 | xargs kill -9

# Wait a moment
sleep 2

# Try again
streamlit run src/ui/app.py --server.port 8501
```

### Error: "streamlit: command not found"

```bash
# Activate virtual environment
source venv/bin/activate

# Install Streamlit
pip install streamlit

# Try again
streamlit run src/ui/app.py
```

### Error: "No module named 'src'"

```bash
# Make sure you're in the project root
cd /Users/admin/ai/multimodal

# Check that src/ exists
ls -la src/

# Try again
streamlit run src/ui/app.py
```

---

## Best Practices

### 1. Always Restart After Code Changes

```bash
# After editing any Python file
./scripts/restart_streamlit.sh
```

### 2. Check Logs for Errors

```bash
# Run Streamlit in foreground to see logs
streamlit run src/ui/app.py --server.port 8501

# Or check the terminal where Streamlit is running
```

### 3. Test Changes Locally First

```bash
# Test video ingestion directly
python -c "
from pathlib import Path
from src.ingestion.video_ingester import VideoIngester

ingester = VideoIngester()
doc = ingester.ingest(Path('tests/data/video/elon_ai_danger.mp4'))
print(f'✅ Ingested: {doc.title}')
print(f'   Content length: {len(doc.content)} chars')
print(f'   Chunks: {len(doc.chunks)}')
"
```

### 4. Use Version Control

```bash
# Check what changed
git diff src/ingestion/video_ingester.py

# Commit working changes
git add src/ingestion/video_ingester.py
git commit -m "fix: remove verbose parameter from MoviePy 2.x"
```

---

## Quick Reference

| Problem | Solution |
|---------|----------|
| Video upload fails | `./scripts/restart_streamlit.sh` |
| Changes not reflected | Clear cache + restart |
| Port already in use | `lsof -ti:8501 \| xargs kill -9` |
| Streamlit not found | `source venv/bin/activate` |
| Import errors | Check you're in project root |

---

## Verification

After restarting, verify the fix worked:

1. **Open Streamlit UI:** http://localhost:8501
2. **Upload a video:** Use `tests/data/video/elon_ai_danger.mp4`
3. **Check for success:**
   - No error messages
   - Video appears in the ingested documents list
   - Can query the video content

4. **Verify in Qdrant:**
   ```bash
   python -c "
   from src.vector_store import QdrantVectorStore
   vs = QdrantVectorStore()
   info = vs.client.get_collection('multimodal_chunks')
   print(f'Total chunks: {info.points_count}')
   "
   ```

---

**Quick fix:** `./scripts/restart_streamlit.sh`

