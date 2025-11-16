#!/usr/bin/env python3
"""Extract content from all test media files and save as reference outputs.

This script processes all test files and saves the extracted content to
corresponding output files for reference and comparison in tests.
"""

import sys
from pathlib import Path
import json
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def extract_text_files():
    """Extract content from text files."""
    print("\n" + "=" * 80)
    print("Extracting Text Files")
    print("=" * 80)
    
    # TXT file
    txt_file = project_root / "tests/data/txt/andrew_ng.txt"
    if txt_file.exists():
        with open(txt_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        output_file = txt_file.parent / "andrew_ng_extracted.txt"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ TXT: {txt_file.name}")
        print(f"   Output: {output_file.name}")
        print(f"   Length: {len(content)} characters")
        print(f"   Preview: {content[:100]}...")
    
    # PDF file
    pdf_file = project_root / "tests/data/pdf/Andrew Ng - Wikipedia.pdf"
    if pdf_file.exists():
        try:
            from pypdf import PdfReader
            
            reader = PdfReader(pdf_file)
            content = ""
            for page in reader.pages:
                content += page.extract_text()
            
            output_file = pdf_file.parent / "Andrew Ng - Wikipedia_extracted.txt"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"\n✅ PDF: {pdf_file.name}")
            print(f"   Output: {output_file.name}")
            print(f"   Pages: {len(reader.pages)}")
            print(f"   Length: {len(content)} characters")
            print(f"   Preview: {content[:100]}...")
        except Exception as e:
            print(f"\n❌ PDF extraction failed: {e}")


def extract_image_files():
    """Extract captions from image files."""
    print("\n" + "=" * 80)
    print("Extracting Image Files")
    print("=" * 80)
    
    img_file = project_root / "tests/data/img/elon_musk_AI_opinion.jpeg"
    if not img_file.exists():
        print(f"⚠️  Image file not found: {img_file}")
        return
    
    try:
        from PIL import Image
        from transformers import BlipProcessor, BlipForConditionalGeneration
        
        print("Loading BLIP model (this may take a while on first run)...")
        processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
        model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")
        
        # Load image
        image = Image.open(img_file)
        
        # Generate caption
        inputs = processor(image, return_tensors="pt")
        outputs = model.generate(**inputs, max_new_tokens=50)
        caption = processor.decode(outputs[0], skip_special_tokens=True)
        
        # Save output
        output_file = img_file.parent / "elon_musk_AI_opinion_caption.txt"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"Image: {img_file.name}\n")
            f.write(f"Caption: {caption}\n")
            f.write(f"Generated: {datetime.now().isoformat()}\n")
        
        # Also save as JSON
        output_json = img_file.parent / "elon_musk_AI_opinion_caption.json"
        with open(output_json, 'w', encoding='utf-8') as f:
            json.dump({
                "image": img_file.name,
                "caption": caption,
                "image_size": image.size,
                "image_mode": image.mode,
                "generated_at": datetime.now().isoformat()
            }, f, indent=2)
        
        print(f"✅ Image: {img_file.name}")
        print(f"   Output: {output_file.name}")
        print(f"   Caption: {caption}")
        print(f"   Image size: {image.size}")
        
    except Exception as e:
        print(f"❌ Image extraction failed: {e}")


def extract_audio_files():
    """Extract transcripts from audio files."""
    print("\n" + "=" * 80)
    print("Extracting Audio Files")
    print("=" * 80)
    
    audio_file = project_root / "tests/data/audio/elon-musk-ai-opinion.mp3"
    if not audio_file.exists():
        print(f"⚠️  Audio file not found: {audio_file}")
        return
    
    try:
        import whisper
        
        print("Loading Whisper model (this may take a while on first run)...")
        model = whisper.load_model("base")
        
        print(f"Transcribing {audio_file.name}...")
        result = model.transcribe(str(audio_file))
        transcript = result["text"]
        
        # Save output
        output_file = audio_file.parent / "elon-musk-ai-opinion_transcript.txt"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"Audio: {audio_file.name}\n")
            f.write(f"Transcript:\n{transcript}\n")
            f.write(f"\nGenerated: {datetime.now().isoformat()}\n")
        
        # Also save as JSON with segments
        output_json = audio_file.parent / "elon-musk-ai-opinion_transcript.json"
        with open(output_json, 'w', encoding='utf-8') as f:
            json.dump({
                "audio": audio_file.name,
                "transcript": transcript,
                "language": result.get("language"),
                "segments": result.get("segments", []),
                "generated_at": datetime.now().isoformat()
            }, f, indent=2)
        
        print(f"✅ Audio: {audio_file.name}")
        print(f"   Output: {output_file.name}")
        print(f"   Length: {len(transcript)} characters")
        print(f"   Language: {result.get('language')}")
        print(f"   Preview: {transcript[:100]}...")
        
    except Exception as e:
        print(f"❌ Audio extraction failed: {e}")


def extract_video_files():
    """Extract content from video files (audio + frames + scenes)."""
    print("\n" + "=" * 80)
    print("Extracting Video Files")
    print("=" * 80)

    video_file = project_root / "tests/data/video/elon_ai_danger.mp4"
    if not video_file.exists():
        print(f"⚠️  Video file not found: {video_file}")
        return

    try:
        from moviepy import VideoFileClip
        import whisper
        import tempfile
        from scenedetect import detect, ContentDetector
        import numpy as np
        from PIL import Image

        print(f"Loading video: {video_file.name}...")
        video = VideoFileClip(str(video_file))

        # Video metadata
        metadata = {
            "video": video_file.name,
            "duration": video.duration,
            "size": video.size,
            "fps": video.fps,
            "has_audio": video.audio is not None,
            "generated_at": datetime.now().isoformat()
        }

        print(f"✅ Video loaded:")
        print(f"   Duration: {video.duration:.2f}s")
        print(f"   Size: {video.size}")
        print(f"   FPS: {video.fps}")
        print(f"   Has audio: {video.audio is not None}")

        # Extract audio and transcribe
        transcript = None
        if video.audio is not None:
            print("\nExtracting and transcribing audio...")
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
                tmp_path = Path(tmp.name)
                video.audio.write_audiofile(str(tmp_path))

            model = whisper.load_model("base")
            result = model.transcribe(str(tmp_path))
            transcript = result["text"]

            tmp_path.unlink()

            metadata["transcript"] = transcript
            metadata["language"] = result.get("language")

            print(f"   Transcript length: {len(transcript)} characters")
            print(f"   Language: {result.get('language')}")

        # Detect scenes
        print("\nDetecting scenes...")
        scene_list = detect(str(video_file), ContentDetector(threshold=27.0))
        scenes = []
        for scene in scene_list:
            scenes.append({
                "start": scene[0].get_seconds(),
                "end": scene[1].get_seconds(),
                "duration": scene[1].get_seconds() - scene[0].get_seconds()
            })

        metadata["scenes"] = scenes
        print(f"   Detected {len(scenes)} scenes")

        # Extract key frames (one per scene or every 2 seconds)
        print("\nExtracting key frames...")
        frames_dir = video_file.parent / "frames"
        frames_dir.mkdir(exist_ok=True)

        frame_times = []
        if len(scenes) > 0:
            # Extract one frame from middle of each scene
            for i, scene in enumerate(scenes[:5]):  # Limit to 5 frames
                frame_time = (scene["start"] + scene["end"]) / 2
                frame_times.append(frame_time)
        else:
            # Extract frames every 2 seconds
            frame_times = [t for t in range(0, int(video.duration), 2)][:5]

        extracted_frames = []
        for i, frame_time in enumerate(frame_times):
            if frame_time < video.duration:
                frame = video.get_frame(frame_time)
                frame_img = Image.fromarray(frame)

                frame_filename = f"elon_ai_danger_frame_{i+1:03d}_t{frame_time:.2f}s.jpg"
                frame_path = frames_dir / frame_filename
                frame_img.save(frame_path)

                extracted_frames.append({
                    "frame_number": i + 1,
                    "time": frame_time,
                    "filename": frame_filename,
                    "size": frame.shape[:2]
                })

        metadata["frames"] = extracted_frames
        print(f"   Extracted {len(extracted_frames)} frames to {frames_dir.name}/")

        video.close()

        # Save metadata and transcript
        output_file = video_file.parent / "elon_ai_danger_extracted.txt"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"Video: {video_file.name}\n")
            f.write(f"Duration: {metadata['duration']:.2f}s\n")
            f.write(f"Size: {metadata['size']}\n")
            f.write(f"FPS: {metadata['fps']}\n")
            f.write(f"Has audio: {metadata['has_audio']}\n")
            f.write(f"\nScenes detected: {len(scenes)}\n")
            for i, scene in enumerate(scenes, 1):
                f.write(f"  Scene {i}: {scene['start']:.2f}s - {scene['end']:.2f}s ({scene['duration']:.2f}s)\n")
            f.write(f"\nFrames extracted: {len(extracted_frames)}\n")
            for frame in extracted_frames:
                f.write(f"  Frame {frame['frame_number']}: {frame['time']:.2f}s -> {frame['filename']}\n")
            if transcript:
                f.write(f"\nTranscript:\n{transcript}\n")
            f.write(f"\nGenerated: {metadata['generated_at']}\n")

        # Save as JSON
        output_json = video_file.parent / "elon_ai_danger_extracted.json"
        with open(output_json, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2)

        print(f"\n✅ Video extraction complete:")
        print(f"   Output: {output_file.name}")
        print(f"   JSON: {output_json.name}")
        print(f"   Frames: {frames_dir.name}/ ({len(extracted_frames)} files)")

    except Exception as e:
        print(f"❌ Video extraction failed: {e}")
        import traceback
        traceback.print_exc()


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Extract content from all test media files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Extract all media types
  python scripts/extract_test_data.py

  # Extract only text files (fast)
  python scripts/extract_test_data.py --type text

  # Extract only images
  python scripts/extract_test_data.py --type image

  # Extract only audio
  python scripts/extract_test_data.py --type audio

  # Extract only video
  python scripts/extract_test_data.py --type video
        """
    )

    parser.add_argument(
        "--type",
        choices=["text", "image", "audio", "video", "all"],
        default="all",
        help="Type of media to extract"
    )

    args = parser.parse_args()

    print("=" * 80)
    print("Media Content Extraction")
    print("=" * 80)
    print(f"Extracting: {args.type}")
    print(f"Output directory: tests/data/")

    if args.type in ["text", "all"]:
        extract_text_files()

    if args.type in ["image", "all"]:
        extract_image_files()

    if args.type in ["audio", "all"]:
        extract_audio_files()

    if args.type in ["video", "all"]:
        extract_video_files()

    print("\n" + "=" * 80)
    print("✅ Extraction complete!")
    print("=" * 80)
    print("\nExtracted files saved to tests/data/ subdirectories")
    print("Use these files as reference for comparison in tests")


if __name__ == "__main__":
    main()


