"""Tests for data models."""

import pytest
from datetime import datetime
from uuid import UUID

from src.models import (
    Chunk,
    Entity,
    Relationship,
    Query,
    ModalityType,
    EntityType,
    RelationshipType,
    Metadata
)


class TestChunk:
    """Test Chunk model."""
    
    def test_chunk_creation(self):
        """Test creating a chunk."""
        metadata = Metadata(
            source="test.txt",
            modality=ModalityType.TEXT
        )
        
        chunk = Chunk(
            content="This is a test chunk.",
            metadata=metadata
        )
        
        assert isinstance(chunk.id, UUID)
        assert chunk.content == "This is a test chunk."
        assert chunk.modality == ModalityType.TEXT
    
    def test_chunk_validation_empty_content(self):
        """Test chunk validation fails for empty content."""
        metadata = Metadata(
            source="test.txt",
            modality=ModalityType.TEXT
        )
        
        with pytest.raises(ValueError):
            Chunk(content="", metadata=metadata)


class TestEntity:
    """Test Entity model."""
    
    def test_entity_creation(self):
        """Test creating an entity."""
        entity = Entity(
            name="John Doe",
            entity_type=EntityType.PERSON,
            source_modality=ModalityType.TEXT,
            source_id=UUID("12345678-1234-5678-1234-567812345678")
        )
        
        assert entity.name == "John Doe"
        assert entity.entity_type == EntityType.PERSON
        assert entity.confidence == 1.0
    
    def test_entity_name_validation(self):
        """Test entity name validation."""
        with pytest.raises(ValueError):
            Entity(
                name="",
                entity_type=EntityType.PERSON,
                source_modality=ModalityType.TEXT,
                source_id=UUID("12345678-1234-5678-1234-567812345678")
            )


class TestQuery:
    """Test Query model."""
    
    def test_query_creation(self):
        """Test creating a query."""
        query = Query(text="What is the capital of France?")
        
        assert isinstance(query.id, UUID)
        assert query.text == "What is the capital of France?"
        assert isinstance(query.timestamp, datetime)
    
    def test_query_validation_too_short(self):
        """Test query validation for short queries."""
        with pytest.raises(ValueError):
            Query(text="Hi")
    
    def test_query_validation_too_long(self):
        """Test query validation for long queries."""
        long_text = "a" * 501
        with pytest.raises(ValueError):
            Query(text=long_text)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

