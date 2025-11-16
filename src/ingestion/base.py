"""Base ingester interface for multimodal data."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Optional
from uuid import uuid4

from loguru import logger

from ..models import Document, Metadata, ModalityType


class BaseIngester(ABC):
    """Abstract base class for data ingesters."""
    
    def __init__(self, modality: ModalityType):
        """Initialize ingester.
        
        Args:
            modality: Type of modality this ingester handles
        """
        self.modality = modality
    
    @abstractmethod
    def validate_file(self, file_path: Path) -> bool:
        """Validate if file can be processed.
        
        Args:
            file_path: Path to file
            
        Returns:
            True if file is valid
        """
        pass
    
    @abstractmethod
    def ingest(self, file_path: Path, **kwargs) -> Document:
        """Ingest file and create document.
        
        Args:
            file_path: Path to file
            **kwargs: Additional ingestion parameters
            
        Returns:
            Document object
        """
        pass
    
    def create_metadata(
        self,
        file_path: Path,
        **kwargs
    ) -> Metadata:
        """Create metadata for document.

        Args:
            file_path: Path to file
            **kwargs: Additional metadata fields (can include original_filename, upload_source, speaker_name)

        Returns:
            Metadata object
        """
        stat = file_path.stat()

        # Extract original_filename from kwargs or use file_path.name
        original_filename = kwargs.pop('original_filename', file_path.name)
        upload_source = kwargs.pop('upload_source', None)
        speaker_name = kwargs.pop('speaker_name', None)

        return Metadata(
            source=str(file_path),
            modality=self.modality,
            file_path=str(file_path),
            file_size=stat.st_size,
            mime_type=self._get_mime_type(file_path),
            original_filename=original_filename,
            upload_source=upload_source,
            speaker_name=speaker_name,
            **kwargs
        )
    
    def _get_mime_type(self, file_path: Path) -> str:
        """Get MIME type from file extension.
        
        Args:
            file_path: Path to file
            
        Returns:
            MIME type string
        """
        import mimetypes
        mime_type, _ = mimetypes.guess_type(str(file_path))
        return mime_type or "application/octet-stream"
    
    def _validate_file_size(
        self,
        file_path: Path,
        max_size_mb: int = 100
    ) -> bool:
        """Validate file size.
        
        Args:
            file_path: Path to file
            max_size_mb: Maximum file size in MB
            
        Returns:
            True if file size is acceptable
        """
        size_mb = file_path.stat().st_size / (1024 * 1024)
        
        if size_mb > max_size_mb:
            logger.warning(
                f"File {file_path} size {size_mb:.2f}MB exceeds limit {max_size_mb}MB"
            )
            return False
        
        return True
    
    def _validate_file_exists(self, file_path: Path) -> bool:
        """Validate file exists.
        
        Args:
            file_path: Path to file
            
        Returns:
            True if file exists
        """
        if not file_path.exists():
            logger.error(f"File not found: {file_path}")
            return False
        
        if not file_path.is_file():
            logger.error(f"Path is not a file: {file_path}")
            return False
        
        return True

