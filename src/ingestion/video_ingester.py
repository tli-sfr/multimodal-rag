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
            **kwargs: Additional parameters
            
        Returns:
            Document with video data
        """
        if not self.validate_file(file_path):
            raise ValueError(f"Invalid video file: {file_path}")
        
        logger.info(f"Ingesting video: {file_path}")
        
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
        
        # Create metadata
        metadata = self.create_metadata(
            file_path,
            duration_seconds=video_info.get('duration'),
            fps=video_info.get('fps'),
            width=video_info.get('width'),
            height=video_info.get('height'),
            num_frames=video_info.get('frame_count'),
            num_scenes=len(scenes),
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
            import moviepy.editor as mp
            
            video = mp.VideoFileClip(str(file_path))
            
            if video.audio is None:
                logger.info(f"No audio track in video: {file_path}")
                return ""
            
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
                tmp_path = Path(tmp.name)
                video.audio.write_audiofile(str(tmp_path), verbose=False, logger=None)
            
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
        """Extract key frames from video."""
        # Implementation continues...
        return []
    
    def _describe_frames(self, frames: List) -> str:
        """Generate descriptions for extracted frames."""
        # Implementation continues...
        return ""
    
    def _create_chunks(
        self,
        transcription: str,
        descriptions: str,
        scenes: List,
        parent_id: uuid4,
        metadata
    ) -> List[Chunk]:
        """Create chunks from video content."""
        # Implementation continues...
        return []

