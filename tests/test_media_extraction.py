"""Unit tests for media extraction from all content types.

This test suite verifies that all required libraries can successfully extract
text/content from different media types before ingestion.
"""

import pytest
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class TestTextExtraction:
    """Test text extraction from text files."""
    
    @pytest.mark.unit
    def test_txt_file_extraction(self):
        """Test extracting text from .txt file."""
        test_file = Path("tests/data/txt/andrew_ng.txt")
        
        if not test_file.exists():
            pytest.skip(f"Test file not found: {test_file}")
        
        # Read text file
        with open(test_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Verify content was extracted
        assert content is not None
        assert len(content) > 0
        assert isinstance(content, str)
        
        # Verify it contains expected content
        assert "Andrew" in content or "Ng" in content
        
        print(f"✅ TXT extraction successful: {len(content)} characters")
    
    @pytest.mark.unit
    def test_pdf_file_extraction(self):
        """Test extracting text from PDF file using pypdf."""
        test_file = Path("tests/data/pdf/Andrew Ng - Wikipedia.pdf")
        
        if not test_file.exists():
            pytest.skip(f"Test file not found: {test_file}")
        
        try:
            from pypdf import PdfReader
        except ImportError:
            pytest.fail("pypdf library not installed - required for PDF extraction")
        
        # Extract text from PDF
        reader = PdfReader(test_file)
        content = ""
        for page in reader.pages:
            content += page.extract_text()
        
        # Verify content was extracted
        assert content is not None
        assert len(content) > 0
        assert isinstance(content, str)
        
        # Verify it contains expected content
        assert "Andrew" in content or "Ng" in content
        
        print(f"✅ PDF extraction successful: {len(content)} characters from {len(reader.pages)} pages")


class TestImageExtraction:
    """Test image captioning/OCR extraction."""
    
    @pytest.mark.unit
    @pytest.mark.slow
    def test_image_captioning(self):
        """Test generating captions from images using BLIP."""
        test_file = Path("tests/data/img/elon_musk_AI_opinion.jpeg")
        
        if not test_file.exists():
            pytest.skip(f"Test file not found: {test_file}")
        
        try:
            from PIL import Image
            from transformers import BlipProcessor, BlipForConditionalGeneration
        except ImportError as e:
            pytest.fail(f"Required library not installed: {e}")
        
        # Load image
        image = Image.open(test_file)
        assert image is not None
        assert image.size[0] > 0 and image.size[1] > 0
        
        # Load BLIP model
        processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
        model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")
        
        # Generate caption
        inputs = processor(image, return_tensors="pt")
        outputs = model.generate(**inputs, max_new_tokens=50)
        caption = processor.decode(outputs[0], skip_special_tokens=True)
        
        # Verify caption was generated
        assert caption is not None
        assert len(caption) > 0
        assert isinstance(caption, str)
        
        print(f"✅ Image captioning successful: '{caption}'")


class TestAudioExtraction:
    """Test audio transcription."""
    
    @pytest.mark.unit
    @pytest.mark.slow
    def test_audio_transcription(self):
        """Test transcribing audio using Whisper."""
        test_file = Path("tests/data/audio/elon-musk-ai-opinion.mp3")
        
        if not test_file.exists():
            pytest.skip(f"Test file not found: {test_file}")
        
        try:
            import whisper
        except ImportError:
            pytest.fail("whisper library not installed - required for audio transcription")
        
        # Load Whisper model (using tiny for speed)
        model = whisper.load_model("tiny")
        
        # Transcribe audio
        result = model.transcribe(str(test_file))
        transcript = result["text"]
        
        # Verify transcript was generated
        assert transcript is not None
        assert len(transcript) > 0
        assert isinstance(transcript, str)
        
        print(f"✅ Audio transcription successful: {len(transcript)} characters")
        print(f"   Transcript preview: {transcript[:100]}...")


class TestVideoExtraction:
    """Test video processing (audio + frames)."""
    
    @pytest.mark.unit
    @pytest.mark.slow
    def test_video_audio_extraction(self):
        """Test extracting audio from video using MoviePy."""
        test_file = Path("tests/data/video/elon_musk_ai_danger.mp4")
        
        if not test_file.exists():
            pytest.skip(f"Test file not found: {test_file}")
        
        try:
            from moviepy import VideoFileClip
        except ImportError:
            pytest.fail("moviepy library not installed - required for video processing")
        
        # Load video
        video = VideoFileClip(str(test_file))
        
        # Verify video loaded
        assert video is not None
        assert video.duration > 0
        
        # Check if audio track exists
        has_audio = video.audio is not None
        
        print(f"✅ Video loaded successfully:")
        print(f"   Duration: {video.duration:.2f} seconds")
        print(f"   Size: {video.size}")
        print(f"   FPS: {video.fps}")
        print(f"   Has audio: {has_audio}")

        video.close()

    @pytest.mark.unit
    @pytest.mark.slow
    def test_video_frame_extraction(self):
        """Test extracting frames from video."""
        test_file = Path("tests/data/video/elon_musk_ai_danger.mp4")

        if not test_file.exists():
            pytest.skip(f"Test file not found: {test_file}")

        try:
            from moviepy import VideoFileClip
            import numpy as np
        except ImportError as e:
            pytest.fail(f"Required library not installed: {e}")

        # Load video
        video = VideoFileClip(str(test_file))

        # Extract a frame at 1 second
        if video.duration >= 1.0:
            frame = video.get_frame(1.0)

            # Verify frame was extracted
            assert frame is not None
            assert isinstance(frame, np.ndarray)
            assert len(frame.shape) == 3  # Height x Width x Channels
            assert frame.shape[2] == 3  # RGB channels

            print(f"✅ Frame extraction successful:")
            print(f"   Frame shape: {frame.shape}")
            print(f"   Frame dtype: {frame.dtype}")
        else:
            print(f"⚠️  Video too short ({video.duration:.2f}s) to extract frame at 1s")

        video.close()

    @pytest.mark.unit
    @pytest.mark.slow
    def test_video_audio_transcription(self):
        """Test full pipeline: extract audio from video and transcribe."""
        test_file = Path("tests/data/video/elon_musk_ai_danger.mp4")

        if not test_file.exists():
            pytest.skip(f"Test file not found: {test_file}")

        try:
            from moviepy import VideoFileClip
            import whisper
            import tempfile
        except ImportError as e:
            pytest.fail(f"Required library not installed: {e}")

        # Load video
        video = VideoFileClip(str(test_file))

        if video.audio is None:
            pytest.skip("Video has no audio track")

        # Extract audio to temporary file
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
            tmp_path = Path(tmp.name)
            video.audio.write_audiofile(str(tmp_path))

        video.close()

        # Transcribe audio
        model = whisper.load_model("tiny")
        result = model.transcribe(str(tmp_path))
        transcript = result["text"]

        # Clean up
        tmp_path.unlink()

        # Verify transcript
        assert transcript is not None
        assert len(transcript) > 0

        print(f"✅ Video audio transcription successful:")
        print(f"   Transcript length: {len(transcript)} characters")
        print(f"   Preview: {transcript[:100]}...")


class TestSceneDetection:
    """Test scene detection for videos."""

    @pytest.mark.unit
    @pytest.mark.slow
    def test_scene_detection(self):
        """Test detecting scenes in video using scenedetect."""
        test_file = Path("tests/data/video/elon_musk_ai_danger.mp4")

        if not test_file.exists():
            pytest.skip(f"Test file not found: {test_file}")

        try:
            from scenedetect import detect, ContentDetector
        except ImportError:
            pytest.fail("scenedetect library not installed - required for scene detection")

        # Detect scenes
        scene_list = detect(str(test_file), ContentDetector(threshold=27.0))

        # Verify scenes were detected
        assert scene_list is not None
        assert isinstance(scene_list, list)

        print(f"✅ Scene detection successful:")
        print(f"   Detected {len(scene_list)} scenes")

        if len(scene_list) > 0:
            for i, scene in enumerate(scene_list[:3], 1):  # Show first 3 scenes
                start_time = scene[0].get_seconds()
                end_time = scene[1].get_seconds()
                print(f"   Scene {i}: {start_time:.2f}s - {end_time:.2f}s")


class TestLibraryAvailability:
    """Test that all required libraries are available."""

    @pytest.mark.unit
    def test_text_libraries(self):
        """Test text processing libraries are available."""
        try:
            import pypdf
            print("✅ pypdf available")
        except ImportError:
            pytest.fail("pypdf not installed")

    @pytest.mark.unit
    def test_image_libraries(self):
        """Test image processing libraries are available."""
        try:
            from PIL import Image
            print("✅ PIL/Pillow available")
        except ImportError:
            pytest.fail("Pillow not installed")

        try:
            from transformers import BlipProcessor, BlipForConditionalGeneration
            print("✅ transformers (BLIP) available")
        except ImportError:
            pytest.fail("transformers not installed")

    @pytest.mark.unit
    def test_audio_libraries(self):
        """Test audio processing libraries are available."""
        try:
            import whisper
            print("✅ whisper available")
        except ImportError:
            pytest.fail("whisper not installed")

    @pytest.mark.unit
    def test_video_libraries(self):
        """Test video processing libraries are available."""
        try:
            from moviepy import VideoFileClip
            print("✅ moviepy available")
        except ImportError:
            pytest.fail("moviepy not installed")

        try:
            from scenedetect import detect, ContentDetector
            print("✅ scenedetect available")
        except ImportError:
            pytest.fail("scenedetect not installed")

    @pytest.mark.unit
    def test_ffmpeg_availability(self):
        """Test FFmpeg is available (required for audio/video processing)."""
        import subprocess

        try:
            result = subprocess.run(
                ['ffmpeg', '-version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            assert result.returncode == 0
            print("✅ FFmpeg available")
            print(f"   Version: {result.stdout.split('\\n')[0]}")
        except FileNotFoundError:
            pytest.fail("FFmpeg not installed - required for audio/video processing")
        except subprocess.TimeoutExpired:
            pytest.fail("FFmpeg command timed out")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])


