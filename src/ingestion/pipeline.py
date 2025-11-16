"""Orchestration pipeline for multimodal ingestion."""

from pathlib import Path
from typing import Dict, List, Optional, Type
from concurrent.futures import ThreadPoolExecutor, as_completed

from loguru import logger
from tqdm import tqdm

from ..models import Document, ModalityType
from .base import BaseIngester
from .text_ingester import TextIngester
from .image_ingester import ImageIngester
from .audio_ingester import AudioIngester
from .video_ingester import VideoIngester


class IngestionPipeline:
    """Pipeline for ingesting multimodal documents."""
    
    def __init__(self, max_workers: int = 4):
        """Initialize ingestion pipeline.
        
        Args:
            max_workers: Maximum number of parallel workers
        """
        self.max_workers = max_workers
        
        # Initialize ingesters
        self.ingesters: Dict[ModalityType, BaseIngester] = {
            ModalityType.TEXT: TextIngester(),
            ModalityType.IMAGE: ImageIngester(),
            ModalityType.AUDIO: AudioIngester(),
            ModalityType.VIDEO: VideoIngester(),
        }
        
        # Extension to modality mapping
        self.extension_map = self._build_extension_map()
    
    def _build_extension_map(self) -> Dict[str, ModalityType]:
        """Build mapping from file extensions to modalities."""
        ext_map = {}
        
        for modality, ingester in self.ingesters.items():
            if hasattr(ingester, 'SUPPORTED_EXTENSIONS'):
                for ext in ingester.SUPPORTED_EXTENSIONS:
                    ext_map[ext] = modality
        
        return ext_map
    
    def ingest_file(self, file_path: Path, **kwargs) -> Optional[Document]:
        """Ingest a single file.

        Args:
            file_path: Path to file
            **kwargs: Additional parameters to pass to ingester (original_filename, upload_source, speaker_name)

        Returns:
            Document object or None if ingestion failed
        """
        # Determine modality from extension
        modality = self.extension_map.get(file_path.suffix.lower())

        if modality is None:
            logger.warning(f"Unsupported file type: {file_path.suffix}")
            return None

        # Get appropriate ingester
        ingester = self.ingesters.get(modality)

        if ingester is None:
            logger.error(f"No ingester available for modality: {modality}")
            return None

        # Ingest file with kwargs
        try:
            document = ingester.ingest(file_path, **kwargs)
            logger.info(f"Successfully ingested: {file_path}")
            return document

        except Exception as e:
            logger.error(f"Failed to ingest {file_path}: {e}")
            return None
    
    def ingest_directory(
        self,
        directory: Path,
        recursive: bool = True,
        parallel: bool = True,
        **kwargs
    ) -> List[Document]:
        """Ingest all supported files in a directory.

        Args:
            directory: Path to directory
            recursive: Recursively process subdirectories
            parallel: Use parallel processing
            **kwargs: Additional parameters to pass to ingesters (upload_source)

        Returns:
            List of ingested documents
        """
        if not directory.exists() or not directory.is_dir():
            raise ValueError(f"Invalid directory: {directory}")

        # Find all supported files
        files = self._find_supported_files(directory, recursive)

        logger.info(f"Found {len(files)} supported files in {directory}")

        if not files:
            return []

        # Ingest files
        if parallel and len(files) > 1:
            documents = self._ingest_parallel(files, **kwargs)
        else:
            documents = self._ingest_sequential(files, **kwargs)

        successful = len([d for d in documents if d is not None])
        logger.info(f"Successfully ingested {successful}/{len(files)} files")

        return [d for d in documents if d is not None]
    
    def _find_supported_files(
        self,
        directory: Path,
        recursive: bool
    ) -> List[Path]:
        """Find all supported files in directory.
        
        Args:
            directory: Directory to search
            recursive: Search recursively
            
        Returns:
            List of file paths
        """
        files = []
        
        pattern = "**/*" if recursive else "*"
        
        for path in directory.glob(pattern):
            if path.is_file() and path.suffix.lower() in self.extension_map:
                files.append(path)
        
        return sorted(files)
    
    def _ingest_sequential(self, files: List[Path], **kwargs) -> List[Optional[Document]]:
        """Ingest files sequentially.

        Args:
            files: List of file paths
            **kwargs: Additional parameters to pass to ingesters

        Returns:
            List of documents
        """
        documents = []

        for file_path in tqdm(files, desc="Ingesting files"):
            doc = self.ingest_file(file_path, **kwargs)
            documents.append(doc)

        return documents

    def _ingest_parallel(self, files: List[Path], **kwargs) -> List[Optional[Document]]:
        """Ingest files in parallel.

        Args:
            files: List of file paths
            **kwargs: Additional parameters to pass to ingesters

        Returns:
            List of documents
        """
        documents = [None] * len(files)

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tasks
            future_to_idx = {
                executor.submit(self.ingest_file, file_path, **kwargs): idx
                for idx, file_path in enumerate(files)
            }

            # Collect results with progress bar
            with tqdm(total=len(files), desc="Ingesting files") as pbar:
                for future in as_completed(future_to_idx):
                    idx = future_to_idx[future]
                    try:
                        documents[idx] = future.result()
                    except Exception as e:
                        logger.error(f"Error processing file: {e}")
                        documents[idx] = None
                    pbar.update(1)

        return documents
    
    def get_supported_extensions(self) -> List[str]:
        """Get list of all supported file extensions."""
        return sorted(self.extension_map.keys())
    
    def get_modality_for_file(self, file_path: Path) -> Optional[ModalityType]:
        """Get modality type for a file.
        
        Args:
            file_path: Path to file
            
        Returns:
            ModalityType or None
        """
        return self.extension_map.get(file_path.suffix.lower())

