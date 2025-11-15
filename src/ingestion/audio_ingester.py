"""Audio ingestion with transcription."""

from pathlib import Path
from typing import List, Optional
from uuid import uuid4

import whisper
from pydub import AudioSegment
from loguru import logger

from ..models import Document, Chunk, ModalityType
from ..config import get_config
from .base import BaseIngester


class AudioIngester(BaseIngester):
    """Ingester for audio files with transcription."""
    
    SUPPORTED_EXTENSIONS = {'.mp3', '.wav', '.m4a', '.flac', '.ogg'}
    
    def __init__(
        self,
        model_name: str = "base",
        language: str = "en",
    ):
        """Initialize audio ingester.
        
        Args:
            model_name: Whisper model name (tiny, base, small, medium, large)
            language: Language code for transcription
        """
        super().__init__(ModalityType.AUDIO)
        
        config = get_config()
        self.model_name = model_name
        self.language = language
        
        # Load Whisper model
        try:
            logger.info(f"Loading Whisper model: {model_name}")
            self.model = whisper.load_model(model_name)
            logger.info("Whisper model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load Whisper model: {e}")
            raise
    
    def validate_file(self, file_path: Path) -> bool:
        """Validate audio file."""
        if not self._validate_file_exists(file_path):
            return False
        
        if file_path.suffix.lower() not in self.SUPPORTED_EXTENSIONS:
            logger.error(f"Unsupported audio extension: {file_path.suffix}")
            return False
        
        if not self._validate_file_size(file_path, max_size_mb=200):
            return False
        
        return True
    
    def ingest(self, file_path: Path, **kwargs) -> Document:
        """Ingest audio file.
        
        Args:
            file_path: Path to audio file
            **kwargs: Additional parameters
            
        Returns:
            Document with transcription
        """
        if not self.validate_file(file_path):
            raise ValueError(f"Invalid audio file: {file_path}")
        
        logger.info(f"Ingesting audio: {file_path}")
        
        # Get audio metadata
        audio_info = self._get_audio_info(file_path)
        
        # Transcribe audio
        transcription = self._transcribe(file_path)
        
        if not transcription or not transcription.get('text'):
            raise ValueError(f"No transcription generated for {file_path}")
        
        # Create metadata
        metadata = self.create_metadata(
            file_path,
            duration_seconds=audio_info.get('duration'),
            sample_rate=audio_info.get('sample_rate'),
            channels=audio_info.get('channels'),
            language=transcription.get('language', self.language),
        )
        
        # Create document
        doc_id = uuid4()
        document = Document(
            id=doc_id,
            title=file_path.stem,
            content=transcription['text'],
            modality=ModalityType.AUDIO,
            metadata=metadata
        )
        
        # Create chunks from segments
        chunks = self._create_chunks_from_segments(
            transcription.get('segments', []),
            doc_id,
            metadata
        )
        
        # If no segments, create single chunk
        if not chunks:
            chunk = Chunk(
                content=transcription['text'],
                modality=ModalityType.AUDIO,
                metadata=metadata,
                chunk_index=0,
                parent_id=doc_id
            )
            chunks = [chunk]
        
        document.chunks = chunks
        
        logger.info(f"Transcribed audio with {len(chunks)} segments: {file_path}")
        
        return document
    
    def _get_audio_info(self, file_path: Path) -> dict:
        """Get audio file information."""
        try:
            audio = AudioSegment.from_file(str(file_path))
            return {
                'duration': len(audio) / 1000.0,  # Convert to seconds
                'sample_rate': audio.frame_rate,
                'channels': audio.channels,
            }
        except Exception as e:
            logger.warning(f"Failed to get audio info: {e}")
            return {}
    
    def _transcribe(self, file_path: Path) -> dict:
        """Transcribe audio file using Whisper.
        
        Args:
            file_path: Path to audio file
            
        Returns:
            Transcription result with text and segments
        """
        try:
            result = self.model.transcribe(
                str(file_path),
                language=self.language,
                verbose=False,
                word_timestamps=True
            )
            return result
        
        except Exception as e:
            logger.error(f"Transcription failed for {file_path}: {e}")
            raise
    
    def _create_chunks_from_segments(
        self,
        segments: List[dict],
        parent_id: uuid4,
        metadata
    ) -> List[Chunk]:
        """Create chunks from transcription segments.
        
        Args:
            segments: Whisper transcription segments
            parent_id: Parent document ID
            metadata: Document metadata
            
        Returns:
            List of chunks
        """
        chunks = []
        
        for idx, segment in enumerate(segments):
            # Create chunk with timestamp information
            chunk_metadata = metadata.model_copy()
            chunk_metadata.custom.update({
                'start_time': segment.get('start'),
                'end_time': segment.get('end'),
                'segment_id': segment.get('id'),
            })
            
            chunk = Chunk(
                content=segment.get('text', '').strip(),
                modality=ModalityType.AUDIO,
                metadata=chunk_metadata,
                chunk_index=idx,
                parent_id=parent_id
            )
            
            if chunk.content:  # Only add non-empty chunks
                chunks.append(chunk)
        
        return chunks

