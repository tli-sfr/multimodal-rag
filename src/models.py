"""Core data models for the multimodal RAG system."""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, field_validator


class ModalityType(str, Enum):
    """Supported modality types."""
    TEXT = "text"
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"


class QueryType(str, Enum):
    """Query classification types."""
    FACTUAL = "factual"
    LOOKUP = "lookup"
    REASONING = "reasoning"
    SUMMARIZATION = "summarization"
    COMPARISON = "comparison"


class EntityType(str, Enum):
    """Entity types for knowledge graph."""
    PERSON = "Person"
    ORGANIZATION = "Organization"
    LOCATION = "Location"
    CONCEPT = "Concept"
    EVENT = "Event"
    DOCUMENT = "Document"
    IMAGE = "Image"
    AUDIO = "Audio"
    VIDEO = "Video"
    GENERIC = "Entity"


class RelationshipType(str, Enum):
    """Relationship types for knowledge graph."""
    # General relationships
    MENTIONS = "MENTIONS"
    RELATED_TO = "RELATED_TO"
    PART_OF = "PART_OF"

    # Location relationships
    LOCATED_IN = "LOCATED_IN"

    # Work/Organization relationships
    WORKS_FOR = "WORKS_FOR"
    EMPLOYED_BY = "EMPLOYED_BY"
    MEMBER_OF = "MEMBER_OF"

    # Family relationships
    SPOUSE_OF = "SPOUSE_OF"
    CHILD_OF = "CHILD_OF"
    PARENT_OF = "PARENT_OF"
    SIBLING_OF = "SIBLING_OF"

    # Achievement relationships
    AWARDED = "AWARDED"
    RECEIVED = "RECEIVED"
    WON = "WON"

    # Media relationships
    APPEARS_IN = "APPEARS_IN"
    TRANSCRIBED_FROM = "TRANSCRIBED_FROM"
    EXTRACTED_FROM = "EXTRACTED_FROM"

    # Educational relationships
    STUDIED_AT = "STUDIED_AT"
    GRADUATED_FROM = "GRADUATED_FROM"

    # Creation relationships
    CREATED_BY = "CREATED_BY"
    AUTHORED_BY = "AUTHORED_BY"
    FOUNDED_BY = "FOUNDED_BY"
    FOUNDER_OF = "FOUNDER_OF"

    # Expertise relationships
    EXPERT_IN = "EXPERT_IN"
    SPECIALIZES_IN = "SPECIALIZES_IN"


class Metadata(BaseModel):
    """Generic metadata model."""
    source: str
    modality: ModalityType
    created_at: datetime = Field(default_factory=datetime.utcnow)
    file_path: Optional[str] = None
    file_size: Optional[int] = None
    mime_type: Optional[str] = None
    language: Optional[str] = "en"
    tags: List[str] = Field(default_factory=list)
    custom: Dict[str, Any] = Field(default_factory=dict)

    # New fields for tracking upload source and original filename
    original_filename: Optional[str] = None  # Original filename before temp file
    upload_source: Optional[str] = None  # "ui" or "script"
    speaker_name: Optional[str] = None  # Extracted from filename for videos/audio


class Chunk(BaseModel):
    """Text chunk model."""
    id: UUID = Field(default_factory=uuid4)
    content: str
    modality: ModalityType = ModalityType.TEXT
    metadata: Metadata
    embedding: Optional[List[float]] = None
    chunk_index: int = 0
    parent_id: Optional[UUID] = None
    
    @field_validator('content')
    @classmethod
    def validate_content(cls, v: str) -> str:
        if not v or len(v.strip()) == 0:
            raise ValueError("Content cannot be empty")
        return v


class Entity(BaseModel):
    """Entity model for knowledge graph."""
    id: UUID = Field(default_factory=uuid4)
    name: str
    entity_type: EntityType
    description: Optional[str] = None
    properties: Dict[str, Any] = Field(default_factory=dict)
    source_modality: ModalityType
    source_id: UUID
    confidence: float = Field(ge=0.0, le=1.0, default=1.0)
    embedding: Optional[List[float]] = None
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        if not v or len(v.strip()) == 0:
            raise ValueError("Entity name cannot be empty")
        return v.strip()


class Relationship(BaseModel):
    """Relationship model for knowledge graph."""
    id: UUID = Field(default_factory=uuid4)
    source_entity_id: UUID
    target_entity_id: UUID
    relationship_type: RelationshipType
    properties: Dict[str, Any] = Field(default_factory=dict)
    confidence: float = Field(ge=0.0, le=1.0, default=1.0)
    source_modality: ModalityType
    source_id: UUID


class Document(BaseModel):
    """Document model."""
    id: UUID = Field(default_factory=uuid4)
    title: str
    content: Optional[str] = None
    modality: ModalityType
    metadata: Metadata
    chunks: List[Chunk] = Field(default_factory=list)
    entities: List[Entity] = Field(default_factory=list)
    relationships: List[Relationship] = Field(default_factory=list)
    processed: bool = False
    processing_errors: List[str] = Field(default_factory=list)


class Query(BaseModel):
    """Query model."""
    id: UUID = Field(default_factory=uuid4)
    text: str
    query_type: Optional[QueryType] = None
    rewritten_queries: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    @field_validator('text')
    @classmethod
    def validate_text(cls, v: str) -> str:
        if not v or len(v.strip()) < 3:
            raise ValueError("Query must be at least 3 characters")
        if len(v) > 500:
            raise ValueError("Query must be less than 500 characters")
        return v.strip()


class SearchResult(BaseModel):
    """Search result model."""
    id: UUID
    content: str
    score: float = Field(ge=0.0, le=1.0)
    modality: ModalityType
    metadata: Dict[str, Any] = Field(default_factory=dict)
    source: str  # graph, keyword, vector
    entities: List[Entity] = Field(default_factory=list)


class Answer(BaseModel):
    """Answer model."""
    id: UUID = Field(default_factory=uuid4)
    query_id: UUID
    text: str
    sources: List[SearchResult]
    confidence: float = Field(ge=0.0, le=1.0)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    latency_ms: Optional[float] = None
    
    # Evaluation metrics
    faithfulness_score: Optional[float] = None
    relevance_score: Optional[float] = None
    hallucination_detected: bool = False

