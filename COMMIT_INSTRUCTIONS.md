# Git Commit Instructions

## Summary of Changes

You have made several important fixes that need to be committed:

### 1. **Script Environment Loading Fixes** ✅
- Created `scripts/script_utils.py` - Helper to load .env properly
- Updated `scripts/cleanup_mock_data.py` - Now loads .env from project root
- Updated `scripts/prepare_mock_data.py` - Now loads .env from project root
- Updated `scripts/test_graph_search.py` - Now loads .env from project root
- **Fixes:** OpenAI API 401 error when running scripts

### 2. **FFmpeg Documentation** ✅
- Updated `DEPLOYMENT.md` - Added FFmpeg to prerequisites
- Updated `DEPLOYMENT.md` - Added FFmpeg installation instructions
- Updated `scripts/script_utils.py` - Added check_ffmpeg() function
- **Fixes:** Audio/video ingestion errors

---

## How to Commit All Changes

Run these commands in your terminal:

```bash
# Navigate to project directory
cd /Users/admin/ai/multimodal

# Check what files have changed
git status

# Stage all modified files
git add scripts/cleanup_mock_data.py
git add scripts/prepare_mock_data.py
git add scripts/test_graph_search.py
git add scripts/script_utils.py
git add DEPLOYMENT.md

# Commit with descriptive message
git commit -m "fix: environment loading and ffmpeg documentation

- Add scripts/script_utils.py with setup_environment() and check_ffmpeg()
- Update all scripts to load .env from project root
- Add FFmpeg to prerequisites in DEPLOYMENT.md
- Add FFmpeg installation instructions for macOS/Linux/Windows
- Fix 401 API key error when running scripts from different directories
- Fix audio/video ingestion by documenting FFmpeg requirement

Resolves:
- OpenAI API 401 authentication errors in scripts
- Audio/video ingestion failures due to missing FFmpeg"

# Push to GitHub
git push origin main
```

---

## Alternative: Commit All Changes at Once

If you want to commit ALL tracked changes (including any manual edits):

```bash
cd /Users/admin/ai/multimodal

# Stage all changes to tracked files
git commit -a -m "fix: environment loading and ffmpeg documentation

- Add scripts/script_utils.py with setup_environment() and check_ffmpeg()
- Update all scripts to load .env from project root
- Add FFmpeg to prerequisites in DEPLOYMENT.md
- Add FFmpeg installation instructions for macOS/Linux/Windows
- Fix 401 API key error when running scripts from different directories
- Fix audio/video ingestion by documenting FFmpeg requirement

Resolves:
- OpenAI API 401 authentication errors in scripts
- Audio/video ingestion failures due to missing FFmpeg"

# Push to GitHub
git push origin main
```

---

## Install FFmpeg (Required for Audio/Video)

Before testing audio/video ingestion, install FFmpeg:

### macOS:
```bash
brew install ffmpeg
```

### Ubuntu/Debian:
```bash
sudo apt update
sudo apt install ffmpeg
```

### Verify Installation:
```bash
ffmpeg -version
```

---

## Verify Everything Works

After committing and installing FFmpeg:

```bash
# Test that scripts load .env properly
python scripts/test_graph_search.py

# Test audio ingestion (after installing FFmpeg)
# Upload an audio file in the Streamlit UI
```

---

## Files Changed

- ✅ `scripts/script_utils.py` (NEW)
- ✅ `scripts/cleanup_mock_data.py` (MODIFIED)
- ✅ `scripts/prepare_mock_data.py` (MODIFIED)
- ✅ `scripts/test_graph_search.py` (MODIFIED)
- ✅ `DEPLOYMENT.md` (MODIFIED)

---

**Run the git commands above to commit and push your changes!** 🚀

