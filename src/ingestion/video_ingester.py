"""Video ingestion with frame extraction and scene detection."""

from pathlib import Path
from typing import List, Optional, Tuple
from uuid import uuid4
import tempfile

import cv2
from scenedetect import detect, ContentDetector
from loguru import logger

from ..models import Document, Chunk, ModalityType
from ..config import get_config
from .base import BaseIngester
from .audio_ingester import AudioIngester
from .image_ingester import ImageIngester


class VideoIngester(BaseIngester):
    """Ingester for video files with frame extraction and transcription."""
    
    SUPPORTED_EXTENSIONS = {'.mp4', '.avi', '.mov', '.mkv', '.webm'}
    
    def __init__(
        self,
        fps_extraction: float = 1.0,
        enable_scene_detection: bool = True,
        scene_threshold: float = 27.0,
        max_frames: int = 100,
    ):
        """Initialize video ingester.
        
        Args:
            fps_extraction: Frames per second to extract
            enable_scene_detection: Enable scene detection
            scene_threshold: Threshold for scene detection
            max_frames: Maximum number of frames to extract
        """
        super().__init__(ModalityType.VIDEO)
        
        config = get_config()
        self.fps_extraction = fps_extraction
        self.enable_scene_detection = enable_scene_detection
        self.scene_threshold = scene_threshold
        self.max_frames = max_frames
        
        # Initialize audio and image ingesters for processing
        self.audio_ingester = AudioIngester(model_name="base")
        self.image_ingester = ImageIngester(
            enable_ocr=False,
            enable_captioning=True
        )
    
    def validate_file(self, file_path: Path) -> bool:
        """Validate video file."""
        if not self._validate_file_exists(file_path):
            return False
        
        if file_path.suffix.lower() not in self.SUPPORTED_EXTENSIONS:
            logger.error(f"Unsupported video extension: {file_path.suffix}")
            return False
        
        if not self._validate_file_size(file_path, max_size_mb=500):
            return False
        
        # Try to open video
        try:
            cap = cv2.VideoCapture(str(file_path))
            if not cap.isOpened():
                logger.error(f"Cannot open video: {file_path}")
                return False
            cap.release()
            return True
        except Exception as e:
            logger.error(f"Invalid video file {file_path}: {e}")
            return False
    
    def ingest(self, file_path: Path, **kwargs) -> Document:
        """Ingest video file.

        Args:
            file_path: Path to video file
            **kwargs: Additional parameters (original_filename, upload_source)

        Returns:
            Document with video data
        """
        if not self.validate_file(file_path):
            raise ValueError(f"Invalid video file: {file_path}")

        logger.info(f"Ingesting video: {file_path}")

        # Extract speaker name from filename (original or current)
        # Use original_filename if provided (from UI upload), otherwise use file_path.name
        filename_to_parse = kwargs.get('original_filename', file_path.name)
        speaker_name = self._extract_speaker_name(filename_to_parse)

        if speaker_name:
            logger.info(f"Extracted speaker name from filename: {speaker_name}")
            kwargs['speaker_name'] = speaker_name

        # Get video metadata
        video_info = self._get_video_info(file_path)

        # Extract audio and transcribe
        audio_transcription = self._extract_and_transcribe_audio(file_path)

        # Detect scenes or extract frames
        if self.enable_scene_detection:
            scenes = self._detect_scenes(file_path)
            logger.info(f"Detected {len(scenes)} scenes")
        else:
            scenes = []

        # Extract key frames
        frames = self._extract_frames(file_path, scenes)

        # Generate captions for frames
        frame_descriptions = self._describe_frames(frames)

        # Create metadata (will include speaker_name, original_filename, upload_source from kwargs)
        metadata = self.create_metadata(
            file_path,
            duration_seconds=video_info.get('duration'),
            fps=video_info.get('fps'),
            width=video_info.get('width'),
            height=video_info.get('height'),
            num_frames=video_info.get('frame_count'),
            num_scenes=len(scenes),
            **kwargs  # Pass through original_filename, upload_source, speaker_name
        )
        
        # Combine content
        content_parts = []
        if audio_transcription:
            content_parts.append(f"Audio Transcription:\n{audio_transcription}")
        if frame_descriptions:
            content_parts.append(f"Visual Content:\n{frame_descriptions}")
        
        content = "\n\n".join(content_parts) if content_parts else f"Video: {file_path.name}"
        
        # Create document
        doc_id = uuid4()
        document = Document(
            id=doc_id,
            title=file_path.stem,
            content=content,
            modality=ModalityType.VIDEO,
            metadata=metadata
        )
        
        # Create chunks (one per scene or time segment)
        chunks = self._create_chunks(
            audio_transcription,
            frame_descriptions,
            scenes,
            doc_id,
            metadata
        )
        
        document.chunks = chunks
        
        logger.info(f"Processed video with {len(chunks)} chunks: {file_path}")
        
        return document
    
    def _extract_speaker_name(self, filename: str) -> Optional[str]:
        """Extract speaker name from filename.

        Handles patterns like:
        - elon_musk_ai_opinion.mp4 -> Elon Musk
        - elon-musk-ai-opinion.mp4 -> Elon Musk
        - andrew_ng.mp4 -> Andrew Ng
        - fei-fei_li.mp4 -> Fei-Fei Li
        - elon_ai_danger.mp4 -> Elon (single name before stop word)

        Args:
            filename: Original filename

        Returns:
            Speaker name or None
        """
        import re

        # Remove file extension
        name_part = Path(filename).stem

        # Common patterns to identify person names at the start of filename
        # Split by underscore, hyphen, or space
        parts = re.split(r'[_\-\s]+', name_part)

        # Common non-name words to stop at
        stop_words = {
            'ai', 'opinion', 'video', 'interview', 'talk', 'speech',
            'lecture', 'presentation', 'discussion', 'about', 'on',
            'danger', 'extracted', 'transcript', 'caption', 'recording',
            'audio', 'clip', 'segment', 'part', 'chapter'
        }

        # Collect name parts (stop at first stop word)
        name_parts = []
        for part in parts:
            if part.lower() in stop_words:
                break
            if part and len(part) > 1:  # Skip single characters
                name_parts.append(part)

        # If we found 1+ parts, assume it's a name
        # (Changed from 2+ to 1+ to handle single names like "Elon")
        if len(name_parts) >= 1:
            # Capitalize each part properly
            speaker_name = ' '.join(word.capitalize() for word in name_parts)
            return speaker_name

        return None

    def _get_video_info(self, file_path: Path) -> dict:
        """Get video file information."""
        cap = cv2.VideoCapture(str(file_path))

        info = {
            'fps': cap.get(cv2.CAP_PROP_FPS),
            'frame_count': int(cap.get(cv2.CAP_PROP_FRAME_COUNT)),
            'width': int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
            'height': int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
        }

        if info['fps'] > 0:
            info['duration'] = info['frame_count'] / info['fps']
        else:
            info['duration'] = 0

        cap.release()
        return info
    
    def _extract_and_transcribe_audio(self, file_path: Path) -> str:
        """Extract audio from video and transcribe."""
        try:
            # Extract audio to temporary file
            # MoviePy 2.x has a different API - classes are directly in moviepy module
            from moviepy import VideoFileClip

            video = VideoFileClip(str(file_path))
            
            if video.audio is None:
                logger.info(f"No audio track in video: {file_path}")
                return ""

            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
                tmp_path = Path(tmp.name)
                # MoviePy 2.x: removed 'verbose' and 'logger' parameters
                # Just provide the filename - MoviePy will handle the rest
                video.audio.write_audiofile(str(tmp_path))
            
            # Transcribe audio
            audio_doc = self.audio_ingester.ingest(tmp_path)
            
            # Clean up
            tmp_path.unlink()
            video.close()
            
            return audio_doc.content
        
        except Exception as e:
            logger.warning(f"Failed to extract/transcribe audio: {e}")
            return ""
    
    def _detect_scenes(self, file_path: Path) -> List[Tuple[float, float]]:
        """Detect scenes in video."""
        try:
            scene_list = detect(str(file_path), ContentDetector(threshold=self.scene_threshold))
            return [(scene[0].get_seconds(), scene[1].get_seconds()) for scene in scene_list]
        except Exception as e:
            logger.warning(f"Scene detection failed: {e}")
            return []
    
    def _extract_frames(
        self,
        file_path: Path,
        scenes: List[Tuple[float, float]]
    ) -> List[Tuple[float, any]]:
        """Extract key frames from video.

        Args:
            file_path: Path to video file
            scenes: List of scene boundaries (start_time, end_time)

        Returns:
            List of (timestamp, frame) tuples
        """
        frames = []
        cap = cv2.VideoCapture(str(file_path))

        try:
            fps = cap.get(cv2.CAP_PROP_FPS)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

            if scenes:
                # Extract one frame from the middle of each scene
                for start_time, end_time in scenes[:self.max_frames]:
                    mid_time = (start_time + end_time) / 2
                    frame_number = int(mid_time * fps)

                    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
                    ret, frame = cap.read()

                    if ret:
                        frames.append((mid_time, frame))
            else:
                # Extract frames at regular intervals
                duration = total_frames / fps if fps > 0 else 0
                interval = max(1.0, duration / min(10, self.max_frames))  # Extract ~10 frames

                current_time = 0
                while current_time < duration and len(frames) < self.max_frames:
                    frame_number = int(current_time * fps)
                    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
                    ret, frame = cap.read()

                    if ret:
                        frames.append((current_time, frame))

                    current_time += interval

        finally:
            cap.release()

        logger.info(f"Extracted {len(frames)} frames from video")
        return frames

    def _describe_frames(self, frames: List[Tuple[float, any]]) -> str:
        """Generate descriptions for extracted frames.

        Args:
            frames: List of (timestamp, frame) tuples

        Returns:
            Combined frame descriptions
        """
        if not frames:
            return ""

        descriptions = []

        for timestamp, frame in frames:
            try:
                # Convert BGR to RGB
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                # Convert to PIL Image
                from PIL import Image
                import numpy as np
                pil_image = Image.fromarray(frame_rgb)

                # Generate caption using image ingester
                caption = self.image_ingester._generate_caption(pil_image)

                if caption:
                    descriptions.append(f"[{timestamp:.1f}s] {caption}")

            except Exception as e:
                logger.warning(f"Failed to describe frame at {timestamp}s: {e}")
                continue

        return "\n".join(descriptions) if descriptions else ""

    def _create_chunks(
        self,
        transcription: str,
        descriptions: str,
        scenes: List,
        parent_id: uuid4,
        metadata
    ) -> List[Chunk]:
        """Create chunks from video content.

        Args:
            transcription: Audio transcription text
            descriptions: Frame descriptions
            scenes: List of scene boundaries
            parent_id: Parent document ID
            metadata: Document metadata

        Returns:
            List of chunks
        """
        chunks = []

        # If we have transcription, create chunks from it
        if transcription:
            # Use text splitter to chunk the transcription
            from langchain_text_splitters import RecursiveCharacterTextSplitter

            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=512,
                chunk_overlap=50,
                length_function=len,
                separators=["\n\n", "\n", ". ", " ", ""]
            )

            text_chunks = text_splitter.split_text(transcription)

            for idx, chunk_text in enumerate(text_chunks):
                chunk_metadata = metadata.model_copy()

                chunk = Chunk(
                    content=chunk_text,
                    modality=ModalityType.VIDEO,
                    metadata=chunk_metadata,
                    chunk_index=idx,
                    parent_id=parent_id
                )
                chunks.append(chunk)

        # If we have frame descriptions, add them as additional chunks
        if descriptions and not transcription:
            # If no transcription, use frame descriptions as chunks
            chunk = Chunk(
                content=descriptions,
                modality=ModalityType.VIDEO,
                metadata=metadata,
                chunk_index=0,
                parent_id=parent_id
            )
            chunks.append(chunk)

        # If we have neither, create a single chunk with basic info
        if not chunks:
            chunk = Chunk(
                content=f"Video file: {metadata.source}",
                modality=ModalityType.VIDEO,
                metadata=metadata,
                chunk_index=0,
                parent_id=parent_id
            )
            chunks.append(chunk)

        return chunks

