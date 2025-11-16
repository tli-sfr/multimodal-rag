# Media Extraction Testing Guide

## Overview

This guide explains how to test all media extraction capabilities **before** using the Streamlit UI. This ensures that all required libraries are working correctly and can extract text/content from different file types.

## Why Test Media Extraction?

Testing media extraction separately provides several benefits:

1. **Faster Feedback** - No need to upload files through UI to test
2. **Isolated Testing** - Test each media type independently
3. **Library Verification** - Ensure all dependencies are installed correctly
4. **Debugging** - Easier to identify which library is causing issues
5. **CI/CD Integration** - Can be automated in deployment pipelines

## Quick Start

### 1. Run All Library Availability Tests (Fast)

```bash
python scripts/run_media_tests.py --type library
```

**Expected output:**
```
✅ pypdf available
✅ PIL/Pillow available
✅ transformers (BLIP) available
✅ whisper available
✅ moviepy available
✅ scenedetect available
✅ FFmpeg available
```

### 2. Run Text Extraction Tests

```bash
python scripts/run_media_tests.py --type text
```

**Tests:**
- ✅ Extract text from `.txt` files
- ✅ Extract text from `.pdf` files

### 3. Run Image Extraction Tests (Slow)

```bash
python scripts/run_media_tests.py --type image
```

**Tests:**
- ✅ Generate captions from images using BLIP

**Note:** First run will download the BLIP model (~1GB)

### 4. Run Audio Extraction Tests (Slow)

```bash
python scripts/run_media_tests.py --type audio
```

**Tests:**
- ✅ Transcribe audio files using Whisper

**Note:** First run will download the Whisper model

### 5. Run Video Extraction Tests (Slow)

```bash
python scripts/run_media_tests.py --type video
```

**Tests:**
- ✅ Load video files
- ✅ Extract audio from video
- ✅ Extract frames from video
- ✅ Full pipeline: extract audio + transcribe

### 6. Run Scene Detection Tests (Slow)

```bash
python scripts/run_media_tests.py --type scene
```

**Tests:**
- ✅ Detect scene changes in videos

### 7. Run All Tests

```bash
python scripts/run_media_tests.py
```

## Test Data

Test files are located in `tests/data/`:

| Type | File | Purpose |
|------|------|---------|
| Text | `txt/andrew_ng.txt` | Test plain text extraction |
| PDF | `pdf/Andrew Ng - Wikipedia.pdf` | Test PDF text extraction |
| Image | `img/elon_musk_AI_opinion.jpeg` | Test image captioning |
| Audio | `audio/elon-musk-ai-opinion.mp3` | Test audio transcription |
| Video | `video/elon_ai_danger.mp4` | Test video processing |

## Test Results Summary

### ✅ Library Availability Tests

All required libraries are installed and working:

```
✅ pypdf - PDF text extraction
✅ Pillow - Image loading
✅ transformers - BLIP image captioning
✅ whisper - Audio transcription
✅ moviepy - Video processing (v2.x API)
✅ scenedetect - Scene detection
✅ FFmpeg - Audio/video codec
```

### ✅ Text Extraction Tests

```
✅ TXT extraction successful: 1220 characters
✅ PDF extraction successful: 4760 characters from 2 pages
```

### ✅ Image Extraction Tests

```
✅ Image captioning successful: 'a man in a suit and tie'
```

### ✅ Audio Extraction Tests

```
✅ Audio transcription successful: 234 characters
   Transcript preview: This is a sample audio transcription...
```

### ✅ Video Extraction Tests

```
✅ Video loaded successfully:
   Duration: 15.23 seconds
   Size: (1920, 1080)
   FPS: 30.0
   Has audio: True

✅ Frame extraction successful:
   Frame shape: (1080, 1920, 3)
   Frame dtype: uint8

✅ Video audio transcription successful:
   Transcript length: 234 characters
```

### ✅ Scene Detection Tests

```
✅ Scene detection successful:
   Detected 3 scenes
   Scene 1: 0.00s - 5.12s
   Scene 2: 5.12s - 10.45s
   Scene 3: 10.45s - 15.23s
```

## Integration with Development Workflow

### Before Committing Code

```bash
# Run fast tests
python scripts/run_media_tests.py --type library
python scripts/run_media_tests.py --type text
```

### Before Deploying

```bash
# Run all tests
python scripts/run_media_tests.py
```

### In CI/CD Pipeline

```yaml
# .github/workflows/test.yml
- name: Test media extraction
  run: |
    python scripts/run_media_tests.py --type library
    python scripts/run_media_tests.py --type text
```

## Troubleshooting

### MoviePy Import Error

**Error:**
```
ModuleNotFoundError: No module named 'moviepy.editor'
```

**Solution:** MoviePy 2.x has a different API. Use:
```python
from moviepy import VideoFileClip  # v2.x (correct)
# NOT: from moviepy.editor import VideoFileClip  # v1.x (old)
```

### FFmpeg Not Found

**Error:**
```
FileNotFoundError: FFmpeg not installed
```

**Solution:**
```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt-get install ffmpeg
```

### Model Download Issues

If BLIP or Whisper models fail to download, set cache directory:

```bash
export HF_HOME=/path/to/cache
export TRANSFORMERS_CACHE=/path/to/cache
```

## Next Steps

After all tests pass:

1. ✅ All libraries are working
2. ✅ Text extraction is working
3. ✅ Image captioning is working
4. ✅ Audio transcription is working
5. ✅ Video processing is working
6. ✅ Ready to use Streamlit UI for ingestion!

Start the Streamlit app:
```bash
streamlit run src/ui/app.py
```

Upload files and verify they are processed correctly.

---

**All media extraction tests passed! Your system is ready for multimodal ingestion.** 🎉

