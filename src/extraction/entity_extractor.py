"""Entity extraction using LLMs."""

import json
from typing import List, Dict, Any
from uuid import uuid4

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from loguru import logger

from ..models import Entity, EntityType, Chunk, ModalityType
from ..config import get_settings


ENTITY_EXTRACTION_PROMPT = """You are an expert at extracting entities from text. 
Extract all relevant entities from the following text and classify them.

Text:
{text}

Extract entities of the following types:
- Person: Names of people
- Organization: Companies, institutions, groups
- Location: Places, cities, countries, addresses
- Concept: Abstract ideas, theories, methodologies
- Event: Specific events, meetings, occurrences

Return a JSON array of entities with the following structure:
[
  {{
    "name": "entity name",
    "type": "Person|Organization|Location|Concept|Event",
    "description": "brief description of the entity",
    "confidence": 0.0-1.0
  }}
]

Only return the JSON array, no additional text.
"""


class EntityExtractor:
    """Extract entities from text using LLMs."""
    
    def __init__(
        self,
        model: str = "gpt-4-turbo-preview",
        temperature: float = 0.1,
    ):
        """Initialize entity extractor.
        
        Args:
            model: LLM model name
            temperature: Temperature for generation
        """
        settings = get_settings()
        
        self.llm = ChatOpenAI(
            model=model,
            temperature=temperature,
            api_key=settings.openai_api_key
        )
        
        self.prompt = ChatPromptTemplate.from_template(ENTITY_EXTRACTION_PROMPT)
    
    def extract_from_chunk(self, chunk: Chunk) -> List[Entity]:
        """Extract entities from a single chunk.

        Args:
            chunk: Text chunk

        Returns:
            List of extracted entities
        """
        if not chunk.content or len(chunk.content.strip()) < 10:
            return []

        # Check if speaker_name is in metadata - if so, add as a Person entity
        speaker_entities = []
        if chunk.metadata.speaker_name:
            logger.info(f"Adding speaker entity from metadata: {chunk.metadata.speaker_name}")
            speaker_entity = Entity(
                name=chunk.metadata.speaker_name,
                entity_type=EntityType.PERSON,
                description=f"Speaker identified from filename: {chunk.metadata.original_filename or chunk.metadata.source}",
                confidence=1.0,  # High confidence since it's from filename
                source_modality=chunk.modality,
                source_id=chunk.id,
                properties={
                    'chunk_index': chunk.chunk_index,
                    'parent_id': str(chunk.parent_id),
                    'from_filename': True
                }
            )
            speaker_entities.append(speaker_entity)

        try:
            # Generate prompt
            messages = self.prompt.format_messages(text=chunk.content)

            # Call LLM
            response = self.llm.invoke(messages)

            # Parse response
            entities_data = self._parse_response(response.content)

            # Create Entity objects
            entities = []
            for entity_dict in entities_data:
                try:
                    entity = Entity(
                        name=entity_dict['name'],
                        entity_type=EntityType[entity_dict['type'].upper()],
                        description=entity_dict.get('description'),
                        confidence=entity_dict.get('confidence', 0.8),
                        source_modality=chunk.modality,
                        source_id=chunk.id,
                        properties={
                            'chunk_index': chunk.chunk_index,
                            'parent_id': str(chunk.parent_id)
                        }
                    )
                    entities.append(entity)

                except (KeyError, ValueError) as e:
                    logger.warning(f"Failed to create entity from {entity_dict}: {e}")
                    continue

            # Combine speaker entities with extracted entities
            all_entities = speaker_entities + entities

            logger.debug(f"Extracted {len(all_entities)} entities from chunk {chunk.id} ({len(speaker_entities)} from metadata, {len(entities)} from content)")
            return all_entities

        except Exception as e:
            logger.error(f"Entity extraction failed for chunk {chunk.id}: {e}")
            # Still return speaker entities even if LLM extraction fails
            return speaker_entities
    
    def extract_from_chunks(
        self,
        chunks: List[Chunk],
        batch_size: int = 10
    ) -> List[Entity]:
        """Extract entities from multiple chunks.
        
        Args:
            chunks: List of chunks
            batch_size: Number of chunks to process at once
            
        Returns:
            List of all extracted entities
        """
        all_entities = []
        
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i + batch_size]
            
            for chunk in batch:
                entities = self.extract_from_chunk(chunk)
                all_entities.extend(entities)
        
        logger.info(f"Extracted {len(all_entities)} entities from {len(chunks)} chunks")
        return all_entities
    
    def _parse_response(self, response: str) -> List[Dict[str, Any]]:
        """Parse LLM response to extract entities.
        
        Args:
            response: LLM response text
            
        Returns:
            List of entity dictionaries
        """
        try:
            # Try to find JSON array in response
            start_idx = response.find('[')
            end_idx = response.rfind(']') + 1
            
            if start_idx == -1 or end_idx == 0:
                logger.warning("No JSON array found in response")
                return []
            
            json_str = response[start_idx:end_idx]
            entities = json.loads(json_str)
            
            if not isinstance(entities, list):
                logger.warning("Response is not a list")
                return []
            
            return entities
        
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            logger.debug(f"Response: {response}")
            return []
    
    def deduplicate_entities(
        self,
        entities: List[Entity],
        similarity_threshold: float = 0.9
    ) -> List[Entity]:
        """Deduplicate entities based on name similarity.
        
        Args:
            entities: List of entities
            similarity_threshold: Threshold for considering entities as duplicates
            
        Returns:
            Deduplicated list of entities
        """
        if not entities:
            return []
        
        # Simple deduplication based on exact name match and type
        seen = {}
        deduplicated = []
        
        for entity in entities:
            key = (entity.name.lower(), entity.entity_type)
            
            if key not in seen:
                seen[key] = entity
                deduplicated.append(entity)
            else:
                # Merge properties and update confidence
                existing = seen[key]
                existing.confidence = max(existing.confidence, entity.confidence)
                existing.properties.update(entity.properties)
        
        logger.info(f"Deduplicated {len(entities)} entities to {len(deduplicated)}")
        return deduplicated

