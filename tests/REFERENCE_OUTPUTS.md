# Reference Output Files

This document explains the reference output files generated from test media files.

## Purpose

Reference output files serve as:
1. **Ground truth** for comparison in tests
2. **Documentation** of expected extraction results
3. **Debugging aid** to verify extraction is working correctly
4. **Regression testing** to ensure extraction quality doesn't degrade

## Generating Reference Files

### Generate All Reference Files

```bash
python scripts/extract_test_data.py
```

### Generate Specific Types

```bash
# Text files only (fast)
python scripts/extract_test_data.py --type text

# Image files (downloads BLIP model on first run)
python scripts/extract_test_data.py --type image

# Audio files (downloads Whisper model on first run)
python scripts/extract_test_data.py --type audio

# Video files (slow - processes video)
python scripts/extract_test_data.py --type video
```

## Reference File Structure

### Text Files

**Input:** `tests/data/txt/andrew_ng.txt`
**Output:** `tests/data/txt/andrew_ng_extracted.txt`

- Plain text copy of the input file
- Used to verify text reading works correctly

**Input:** `tests/data/pdf/Andrew Ng - Wikipedia.pdf`
**Output:** `tests/data/pdf/Andrew Ng - Wikipedia_extracted.txt`

- Extracted text from PDF using pypdf
- Contains all text from all pages
- Used to verify PDF extraction works correctly

### Image Files

**Input:** `tests/data/img/elon_musk_AI_opinion.jpeg`
**Outputs:**
- `tests/data/img/elon_musk_AI_opinion_caption.txt` - Human-readable caption
- `tests/data/img/elon_musk_AI_opinion_caption.json` - Structured data

**JSON Structure:**
```json
{
  "image": "elon_musk_AI_opinion.jpeg",
  "caption": "a man in a suit and tie",
  "image_size": [1920, 1080],
  "image_mode": "RGB",
  "generated_at": "2024-01-01T12:00:00"
}
```

### Audio Files

**Input:** `tests/data/audio/elon-musk-ai-opinion.mp3`
**Outputs:**
- `tests/data/audio/elon-musk-ai-opinion_transcript.txt` - Human-readable transcript
- `tests/data/audio/elon-musk-ai-opinion_transcript.json` - Structured data with segments

**JSON Structure:**
```json
{
  "audio": "elon-musk-ai-opinion.mp3",
  "transcript": "Full transcript text here...",
  "language": "en",
  "segments": [
    {
      "start": 0.0,
      "end": 5.2,
      "text": "First segment..."
    }
  ],
  "generated_at": "2024-01-01T12:00:00"
}
```

### Video Files

**Input:** `tests/data/video/elon_ai_danger.mp4`
**Outputs:**
- `tests/data/video/elon_ai_danger_extracted.txt` - Human-readable summary
- `tests/data/video/elon_ai_danger_extracted.json` - Structured metadata
- `tests/data/video/frames/` - Directory with extracted key frames

**JSON Structure:**
```json
{
  "video": "elon_ai_danger.mp4",
  "duration": 15.23,
  "size": [1920, 1080],
  "fps": 30.0,
  "has_audio": true,
  "transcript": "Audio transcript if available...",
  "language": "en",
  "scenes": [
    {
      "start": 0.0,
      "end": 5.12,
      "duration": 5.12
    }
  ],
  "frames": [
    {
      "frame_number": 1,
      "time": 2.56,
      "filename": "elon_ai_danger_frame_001_t2.56s.jpg",
      "size": [1080, 1920]
    }
  ],
  "generated_at": "2024-01-01T12:00:00"
}
```

## Using Reference Files in Tests

### Basic Comparison Test

```python
def test_extraction_matches_reference():
    # Extract content
    extracted = extract_content("tests/data/txt/andrew_ng.txt")
    
    # Load reference
    with open("tests/data/txt/andrew_ng_extracted.txt") as f:
        reference = f.read()
    
    # Compare
    assert extracted == reference
```

### JSON Comparison Test

```python
def test_metadata_matches_reference():
    import json
    
    # Extract metadata
    metadata = extract_metadata("tests/data/video/elon_ai_danger.mp4")
    
    # Load reference
    with open("tests/data/video/elon_ai_danger_extracted.json") as f:
        reference = json.load(f)
    
    # Compare specific fields
    assert metadata["duration"] == reference["duration"]
    assert metadata["size"] == reference["size"]
```

## Running Tests with Reference Comparison

```bash
# Run tests that compare against reference files
pytest tests/test_media_extraction_with_reference.py -v -s

# Run only text comparison tests
pytest tests/test_media_extraction_with_reference.py::TestTextExtractionWithReference -v -s
```

## When to Regenerate Reference Files

Regenerate reference files when:

1. **Test data changes** - New or updated test files
2. **Library upgrades** - New version of pypdf, BLIP, Whisper, etc.
3. **Model changes** - Different BLIP or Whisper model
4. **Extraction logic changes** - Updates to extraction code
5. **Reference files missing** - First time setup

## File Locations

```
tests/data/
├── txt/
│   ├── andrew_ng.txt                          # Input
│   └── andrew_ng_extracted.txt                # Reference output
├── pdf/
│   ├── Andrew Ng - Wikipedia.pdf              # Input
│   └── Andrew Ng - Wikipedia_extracted.txt    # Reference output
├── img/
│   ├── elon_musk_AI_opinion.jpeg              # Input
│   ├── elon_musk_AI_opinion_caption.txt       # Reference output
│   └── elon_musk_AI_opinion_caption.json      # Reference output (JSON)
├── audio/
│   ├── elon-musk-ai-opinion.mp3               # Input
│   ├── elon-musk-ai-opinion_transcript.txt    # Reference output
│   └── elon-musk-ai-opinion_transcript.json   # Reference output (JSON)
└── video/
    ├── elon_ai_danger.mp4                     # Input
    ├── elon_ai_danger_extracted.txt           # Reference output
    ├── elon_ai_danger_extracted.json          # Reference output (JSON)
    └── frames/                                # Reference frames
        ├── elon_ai_danger_frame_001_t2.56s.jpg
        ├── elon_ai_danger_frame_002_t7.61s.jpg
        └── ...
```

## Notes

- Reference files are **committed to git** for reproducibility
- JSON files include **timestamps** for tracking when generated
- Video frames are **limited to 5** to save space
- Transcripts may **vary slightly** between runs (model randomness)
- Image captions may **vary slightly** between runs (model randomness)

---

**To generate all reference files:** `python scripts/extract_test_data.py`

