"""Tests for ingestion pipeline."""

import pytest
from pathlib import Path
from uuid import UUID

from src.ingestion import TextIngester, IngestionPipeline
from src.models import ModalityType


class TestTextIngester:
    """Test text ingestion."""
    
    def test_text_ingester_initialization(self):
        """Test text ingester can be initialized."""
        ingester = TextIngester()
        assert ingester.modality == ModalityType.TEXT
        assert ingester.chunk_size > 0
    
    def test_supported_extensions(self):
        """Test supported file extensions."""
        ingester = TextIngester()
        assert '.txt' in ingester.SUPPORTED_EXTENSIONS
        assert '.pdf' in ingester.SUPPORTED_EXTENSIONS
        assert '.docx' in ingester.SUPPORTED_EXTENSIONS


class TestIngestionPipeline:
    """Test ingestion pipeline."""
    
    def test_pipeline_initialization(self):
        """Test pipeline can be initialized."""
        pipeline = IngestionPipeline()
        assert pipeline.max_workers > 0
        assert len(pipeline.ingesters) > 0
    
    def test_extension_mapping(self):
        """Test file extension to modality mapping."""
        pipeline = IngestionPipeline()
        
        assert pipeline.get_modality_for_file(Path("test.txt")) == ModalityType.TEXT
        assert pipeline.get_modality_for_file(Path("test.pdf")) == ModalityType.TEXT
        assert pipeline.get_modality_for_file(Path("test.jpg")) == ModalityType.IMAGE
        assert pipeline.get_modality_for_file(Path("test.mp3")) == ModalityType.AUDIO
        assert pipeline.get_modality_for_file(Path("test.mp4")) == ModalityType.VIDEO
    
    def test_get_supported_extensions(self):
        """Test getting all supported extensions."""
        pipeline = IngestionPipeline()
        extensions = pipeline.get_supported_extensions()
        
        assert len(extensions) > 0
        assert '.txt' in extensions
        assert '.pdf' in extensions
        assert '.jpg' in extensions


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

