# Quick Test Reference

## One-Line Test Commands

### Fast Tests (< 5 seconds)

```bash
# Check all libraries are installed
python scripts/run_media_tests.py --type library

# Test text extraction (txt, pdf)
python scripts/run_media_tests.py --type text
```

### Slow Tests (may download models)

```bash
# Test image captioning (downloads BLIP model ~1GB on first run)
python scripts/run_media_tests.py --type image

# Test audio transcription (downloads Whisper model on first run)
python scripts/run_media_tests.py --type audio

# Test video processing
python scripts/run_media_tests.py --type video

# Test scene detection
python scripts/run_media_tests.py --type scene
```

### All Tests

```bash
# Run everything
python scripts/run_media_tests.py
```

## Using pytest Directly

```bash
# All media tests
pytest tests/test_media_extraction.py -v -s

# Only fast tests (skip slow model downloads)
pytest tests/test_media_extraction.py -v -s -m "unit and not slow"

# Specific test class
pytest tests/test_media_extraction.py::TestLibraryAvailability -v -s

# Specific test method
pytest tests/test_media_extraction.py::TestTextExtraction::test_txt_file_extraction -v -s
```

## Expected Results

### ✅ All Libraries Available

```
✅ pypdf available
✅ PIL/Pillow available
✅ transformers (BLIP) available
✅ whisper available
✅ moviepy available
✅ scenedetect available
✅ FFmpeg available
   Version: ffmpeg version 8.0
```

### ✅ Text Extraction Working

```
✅ TXT extraction successful: 1220 characters
✅ PDF extraction successful: 4760 characters from 2 pages
```

### ✅ Image Captioning Working

```
✅ Image captioning successful: 'a man in a suit and tie'
```

### ✅ Audio Transcription Working

```
✅ Audio transcription successful: 234 characters
   Transcript preview: This is a sample audio transcription...
```

### ✅ Video Processing Working

```
✅ Video loaded successfully:
   Duration: 15.23 seconds
   Size: (1920, 1080)
   FPS: 30.0
   Has audio: True
```

## Common Issues

| Error | Solution |
|-------|----------|
| `ModuleNotFoundError: No module named 'moviepy.editor'` | MoviePy 2.x uses `from moviepy import VideoFileClip` |
| `FileNotFoundError: FFmpeg not installed` | Install FFmpeg: `brew install ffmpeg` (macOS) |
| `Model download failed` | Set cache: `export HF_HOME=/path/to/cache` |
| `Test file not found` | Ensure test data exists in `tests/data/` |

## Test Coverage

| Media Type | Library | Test Status |
|------------|---------|-------------|
| Text (.txt) | Built-in | ✅ Tested |
| PDF (.pdf) | pypdf | ✅ Tested |
| Image (.jpg, .png) | Pillow + BLIP | ✅ Tested |
| Audio (.mp3, .wav) | Whisper | ✅ Tested |
| Video (.mp4) | MoviePy + Whisper | ✅ Tested |
| Scene Detection | scenedetect | ✅ Tested |

## Pre-Deployment Checklist

- [ ] Run `python scripts/run_media_tests.py --type library`
- [ ] Run `python scripts/run_media_tests.py --type text`
- [ ] Verify FFmpeg is installed
- [ ] Verify all test data files exist
- [ ] Run full test suite: `python scripts/run_media_tests.py`

---

**Quick test before using UI:** `python scripts/run_media_tests.py --type library`

