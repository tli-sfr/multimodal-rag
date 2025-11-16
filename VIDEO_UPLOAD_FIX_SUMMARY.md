# Video Upload Fix Summary

## Problem

Video upload works in local tests but fails in Streamlit UI with error:

```
2025-11-15 18:05:58.214 | WARNING  | src.ingestion.video_ingester:_extract_and_transcribe_audio:203 - Failed to extract/transcribe audio: got an unexpected keyword argument 'verbose'
```

Nothing is saved to Qdrant database.

---

## Root Cause

**Streamlit is running with cached/old code.**

Even though the MoviePy fix was applied to `src/ingestion/video_ingester.py` (removing the `verbose` parameter), Streamlit is still using the old cached version from:
- Python bytecode cache (`__pycache__/`)
- Streamlit's internal cache (`~/.streamlit/cache/`)
- The running Streamlit process hasn't been restarted

---

## Solution

### Quick Fix (Recommended)

Run the automated restart script:

```bash
# Option A: Bash script
./scripts/restart_streamlit.sh

# Option B: Python script
python scripts/restart_streamlit.py
```

This will:
1. ✅ Stop all running Streamlit processes
2. ✅ Clear Python bytecode cache
3. ✅ Clear Streamlit cache
4. ✅ Restart Streamlit on port 8501

### Manual Fix

If the automated script doesn't work:

```bash
# 1. Stop Streamlit
pkill -f "streamlit run"
lsof -ti:8501 | xargs kill -9

# 2. Clear caches
find . -type d -name "__pycache__" -exec rm -rf {} +
rm -rf ~/.streamlit/cache

# 3. Restart
streamlit run src/ui/app.py --server.port 8501
```

---

## Files Created

| File | Purpose |
|------|---------|
| `scripts/restart_streamlit.sh` | Bash script to restart Streamlit |
| `scripts/restart_streamlit.py` | Python script to restart Streamlit |
| `STREAMLIT_TROUBLESHOOTING.md` | Comprehensive troubleshooting guide |
| `VIDEO_UPLOAD_FIX_SUMMARY.md` | This summary document |

---

## Verification Steps

After restarting Streamlit:

### 1. Open the UI

```
http://localhost:8501
```

### 2. Upload a Test Video

Use the test video:
```
tests/data/video/elon_ai_danger.mp4
```

### 3. Check for Success

- ✅ No error messages in the UI
- ✅ Video appears in the ingested documents list
- ✅ Can query the video content

### 4. Verify in Qdrant

```bash
python -c "
from src.vector_store import QdrantVectorStore
vs = QdrantVectorStore()
info = vs.client.get_collection('multimodal_chunks')
print(f'Total chunks: {info.points_count}')
"
```

Should show increased chunk count after video upload.

---

## Why Local Tests Worked

When you run tests directly:

```bash
python scripts/extract_test_data.py --type video
```

Python loads the **current code** from disk, so it uses the fixed version.

But Streamlit:
- Loads code once when it starts
- Caches modules and components
- **Doesn't automatically reload when code changes**

**Solution:** Always restart Streamlit after code changes.

---

## Best Practices Going Forward

### 1. Always Restart After Code Changes

```bash
./scripts/restart_streamlit.sh
```

### 2. Test Locally First

```bash
# Test video ingestion
python -c "
from pathlib import Path
from src.ingestion.video_ingester import VideoIngester

ingester = VideoIngester()
doc = ingester.ingest(Path('tests/data/video/elon_ai_danger.mp4'))
print(f'✅ Success: {doc.title}')
"
```

### 3. Use the UI Cache Button

In the Streamlit sidebar, click:
- **"Clear Cache & Reload Pipeline"**

This helps but doesn't clear Python bytecode cache.

---

## Technical Details

### The Fix (Already Applied)

<augment_code_snippet path="src/ingestion/video_ingester.py" mode="EXCERPT">
````python
# MoviePy 2.x: removed 'verbose' and 'logger' parameters
# OLD (v1.x): video.audio.write_audiofile(str(tmp_path), verbose=False, logger=None)
# NEW (v2.x): video.audio.write_audiofile(str(tmp_path))
video.audio.write_audiofile(str(tmp_path))
````
</augment_code_snippet>

### Why Restart is Needed

1. **Python Module Cache:**
   - Python caches imported modules in `sys.modules`
   - Changes to `.py` files don't affect already-imported modules
   - Need to restart Python process to reload

2. **Python Bytecode Cache:**
   - Python compiles `.py` files to `.pyc` bytecode
   - Stored in `__pycache__/` directories
   - Can become stale if not cleared

3. **Streamlit Cache:**
   - Streamlit caches data and functions with `@st.cache_data`
   - Stored in `~/.streamlit/cache/`
   - Can persist old results

---

## Summary

- ✅ **Problem:** Streamlit using cached old code
- ✅ **Solution:** Restart Streamlit and clear caches
- ✅ **Scripts created:** `restart_streamlit.sh` and `restart_streamlit.py`
- ✅ **Documentation:** `STREAMLIT_TROUBLESHOOTING.md`
- ✅ **Next step:** Run `./scripts/restart_streamlit.sh`

---

**Quick fix:** `./scripts/restart_streamlit.sh`

