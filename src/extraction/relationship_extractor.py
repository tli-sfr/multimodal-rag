"""Relationship extraction between entities."""

import json
from typing import List, Dict, Any, Tuple

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from loguru import logger

from ..models import Entity, Relationship, RelationshipType, Chunk
from ..config import get_settings


RELATIONSHIP_EXTRACTION_PROMPT = """You are an expert at extracting relationships between entities.

Given the following text and entities, identify relationships between them.

Text:
{text}

Entities:
{entities}

Extract relationships using these types:
- MENTIONS: Entity is mentioned in context
- RELATED_TO: General relationship
- PART_OF: Entity is part of another
- LOCATED_IN: Entity is located in a place
- WORKS_FOR: Person works for organization
- EMPLOYED_BY: Person employed by organization
- MEMBER_OF: Person is member of organization
- SPOUSE_OF: Married to
- CHILD_OF: Child of person
- PARENT_OF: Parent of person
- SIBLING_OF: Sibling relationship
- AWARDED: Received award/honor
- RECEIVED: Received something
- WON: Won award/competition
- APPEARS_IN: Entity appears in media
- STUDIED_AT: Studied at institution
- GRADUATED_FROM: Graduated from institution
- CREATED_BY: Created by person/organization
- AUTHORED_BY: Authored by person
- FOUNDED_BY: Founded by person
- FOUNDER_OF: Person founded organization
- EXPERT_IN: Expert in topic/field
- SPECIALIZES_IN: Specializes in area

Return a JSON array:
[
  {{
    "source": "entity name",
    "target": "entity name",
    "type": "relationship type (use exact type from list above)",
    "confidence": 0.0-1.0
  }}
]

Only return the JSON array. Use exact relationship types from the list above.
"""


class RelationshipExtractor:
    """Extract relationships between entities."""
    
    def __init__(self, model: str = "gpt-4-turbo-preview"):
        """Initialize relationship extractor."""
        settings = get_settings()
        
        self.llm = ChatOpenAI(
            model=model,
            temperature=0.1,
            api_key=settings.openai_api_key
        )
        
        self.prompt = ChatPromptTemplate.from_template(RELATIONSHIP_EXTRACTION_PROMPT)
    
    def extract_from_chunk(
        self,
        chunk: Chunk,
        entities: List[Entity]
    ) -> List[Relationship]:
        """Extract relationships from chunk with entities.
        
        Args:
            chunk: Text chunk
            entities: Entities found in chunk
            
        Returns:
            List of relationships
        """
        if not entities or len(entities) < 2:
            return []
        
        try:
            # Format entities for prompt
            entities_str = "\n".join([
                f"- {e.name} ({e.entity_type.value})"
                for e in entities
            ])
            
            # Generate prompt
            messages = self.prompt.format_messages(
                text=chunk.content,
                entities=entities_str
            )
            
            # Call LLM
            response = self.llm.invoke(messages)
            
            # Parse response
            relationships_data = self._parse_response(response.content)
            
            # Create entity name to ID mapping
            entity_map = {e.name.lower(): e.id for e in entities}
            
            # Create Relationship objects
            relationships = []
            for rel_dict in relationships_data:
                try:
                    source_name = rel_dict['source'].lower()
                    target_name = rel_dict['target'].lower()

                    if source_name not in entity_map or target_name not in entity_map:
                        continue

                    # Try to get relationship type, fallback to RELATED_TO if not found
                    rel_type_str = rel_dict['type'].upper()
                    try:
                        rel_type = RelationshipType[rel_type_str]
                    except KeyError:
                        logger.debug(f"Unknown relationship type '{rel_type_str}', using RELATED_TO")
                        rel_type = RelationshipType.RELATED_TO

                    relationship = Relationship(
                        source_entity_id=entity_map[source_name],
                        target_entity_id=entity_map[target_name],
                        relationship_type=rel_type,
                        confidence=rel_dict.get('confidence', 0.8),
                        source_modality=chunk.modality,
                        source_id=chunk.id
                    )
                    relationships.append(relationship)

                except (KeyError, ValueError) as e:
                    logger.warning(f"Failed to create relationship: {e}")
                    continue
            
            return relationships
        
        except Exception as e:
            logger.error(f"Relationship extraction failed: {e}")
            return []
    
    def _parse_response(self, response: str) -> List[Dict[str, Any]]:
        """Parse LLM response."""
        try:
            start_idx = response.find('[')
            end_idx = response.rfind(']') + 1
            
            if start_idx == -1 or end_idx == 0:
                return []
            
            json_str = response[start_idx:end_idx]
            return json.loads(json_str)
        
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON: {e}")
            return []

