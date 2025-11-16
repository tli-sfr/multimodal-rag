# Media Extraction Tests

This directory contains unit tests to verify that all required libraries can successfully extract text/content from different media types **before** sending them to the ingestion pipeline.

## Purpose

These tests ensure that:
1. All required libraries are installed and working
2. Text can be extracted from text files (.txt, .pdf)
3. Captions can be generated from images (.jpg, .png)
4. Audio can be transcribed from audio files (.mp3, .wav)
5. Video can be processed (audio extraction, frame extraction)
6. Scene detection works for videos

## Test Data

Test files are located in `tests/data/`:

```
tests/data/
├── txt/
│   └── andrew_ng.txt
├── pdf/
│   └── Andrew Ng - Wikipedia.pdf
├── img/
│   └── elon_musk_AI_opinion.jpeg
├── audio/
│   └── elon-musk-ai-opinion.mp3
└── video/
    └── elon_ai_danger.mp4
```

## Running Tests

### Quick Start

Run all tests:
```bash
python scripts/run_media_tests.py
```

### Run Specific Test Types

**Library availability tests (fast):**
```bash
python scripts/run_media_tests.py --type library
```

**Text extraction tests:**
```bash
python scripts/run_media_tests.py --type text
```

**Image captioning tests:**
```bash
python scripts/run_media_tests.py --type image
```

**Audio transcription tests:**
```bash
python scripts/run_media_tests.py --type audio
```

**Video processing tests:**
```bash
python scripts/run_media_tests.py --type video
```

**Scene detection tests:**
```bash
python scripts/run_media_tests.py --type scene
```

### Using pytest directly

```bash
# Run all media extraction tests
pytest tests/test_media_extraction.py -v -s

# Run only unit tests (exclude slow tests)
pytest tests/test_media_extraction.py -v -s -m "unit and not slow"

# Run only library availability tests
pytest tests/test_media_extraction.py -v -s -k "TestLibraryAvailability"

# Run only text extraction tests
pytest tests/test_media_extraction.py -v -s -k "TestTextExtraction"
```

## Test Categories

### 1. Library Availability Tests (`TestLibraryAvailability`)

**Fast tests** that verify all required libraries are installed:

- ✅ `pypdf` - PDF text extraction
- ✅ `Pillow` - Image loading
- ✅ `transformers` - BLIP image captioning
- ✅ `whisper` - Audio transcription
- ✅ `moviepy` - Video processing
- ✅ `scenedetect` - Scene detection
- ✅ `FFmpeg` - Audio/video codec (system dependency)

### 2. Text Extraction Tests (`TestTextExtraction`)

- ✅ Extract text from `.txt` files
- ✅ Extract text from `.pdf` files using `pypdf`

### 3. Image Extraction Tests (`TestImageExtraction`)

- ✅ Generate captions from images using BLIP model
- ⚠️ **Slow test** - downloads model on first run

### 4. Audio Extraction Tests (`TestAudioExtraction`)

- ✅ Transcribe audio files using Whisper
- ⚠️ **Slow test** - downloads model on first run

### 5. Video Extraction Tests (`TestVideoExtraction`)

- ✅ Load video files with MoviePy
- ✅ Extract audio from video
- ✅ Extract frames from video
- ✅ Full pipeline: extract audio + transcribe
- ⚠️ **Slow tests** - require video processing

### 6. Scene Detection Tests (`TestSceneDetection`)

- ✅ Detect scene changes in videos
- ⚠️ **Slow test** - requires video analysis

## Expected Output

### Successful Test Run

```
tests/test_media_extraction.py::TestLibraryAvailability::test_text_libraries PASSED
✅ pypdf available

tests/test_media_extraction.py::TestLibraryAvailability::test_image_libraries PASSED
✅ PIL/Pillow available
✅ transformers (BLIP) available

tests/test_media_extraction.py::TestTextExtraction::test_txt_file_extraction PASSED
✅ TXT extraction successful: 1234 characters

tests/test_media_extraction.py::TestTextExtraction::test_pdf_file_extraction PASSED
✅ PDF extraction successful: 5678 characters from 3 pages

tests/test_media_extraction.py::TestImageExtraction::test_image_captioning PASSED
✅ Image captioning successful: 'a man in a suit and tie'

tests/test_media_extraction.py::TestAudioExtraction::test_audio_transcription PASSED
✅ Audio transcription successful: 234 characters
   Transcript preview: This is a sample audio transcription...

tests/test_media_extraction.py::TestVideoExtraction::test_video_audio_extraction PASSED
✅ Video loaded successfully:
   Duration: 15.23 seconds
   Size: (1920, 1080)
   FPS: 30.0
   Has audio: True
```

## Troubleshooting

### FFmpeg Not Found

```
FileNotFoundError: FFmpeg not installed
```

**Solution:** Install FFmpeg
```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt-get install ffmpeg

# Windows
# Download from https://ffmpeg.org/download.html
```

### MoviePy Import Error

```
ModuleNotFoundError: No module named 'moviepy.editor'
```

**Solution:** You have MoviePy 2.x which has a different API. The code has been updated to use:
```python
from moviepy import VideoFileClip  # v2.x
```

### Model Download Issues

If BLIP or Whisper models fail to download:

```bash
# Set HuggingFace cache directory
export HF_HOME=/path/to/cache

# Or use offline mode if models are already cached
export TRANSFORMERS_OFFLINE=1
```

## CI/CD Integration

Add to your CI pipeline:

```yaml
# .github/workflows/test.yml
- name: Run media extraction tests
  run: |
    python scripts/run_media_tests.py --type library
    python scripts/run_media_tests.py --type text
```

## Notes

- **Slow tests** are marked with `@pytest.mark.slow` and can be skipped with `-m "not slow"`
- **Model downloads** happen on first run and are cached
- **FFmpeg** must be installed separately (system dependency)
- **Test data** should be committed to the repository for reproducibility

