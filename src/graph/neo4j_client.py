"""Neo4j client for knowledge graph operations."""

import json
from typing import List, Dict, Any, Optional
from uuid import UUID

from neo4j import GraphDatabase, Driver
from loguru import logger

from ..models import Entity, Relationship, Document
from ..config import get_settings


class Neo4jClient:
    """Client for Neo4j graph database operations."""
    
    def __init__(
        self,
        uri: Optional[str] = None,
        user: Optional[str] = None,
        password: Optional[str] = None
    ):
        """Initialize Neo4j client.
        
        Args:
            uri: Neo4j URI
            user: Username
            password: Password
        """
        settings = get_settings()
        
        self.uri = uri or settings.neo4j_uri
        self.user = user or settings.neo4j_user
        self.password = password or settings.neo4j_password
        
        self.driver: Optional[Driver] = None
        self._connect()
    
    def _connect(self) -> None:
        """Connect to Neo4j database."""
        try:
            self.driver = GraphDatabase.driver(
                self.uri,
                auth=(self.user, self.password)
            )
            # Verify connectivity
            self.driver.verify_connectivity()
            logger.info(f"Connected to Neo4j at {self.uri}")
        
        except Exception as e:
            logger.error(f"Failed to connect to Neo4j: {e}")
            raise
    
    def close(self) -> None:
        """Close database connection."""
        if self.driver:
            self.driver.close()
            logger.info("Closed Neo4j connection")

    @staticmethod
    def _flatten_properties(properties: Dict[str, Any]) -> Dict[str, Any]:
        """Flatten nested properties for Neo4j storage.

        Neo4j only supports primitive types (str, int, float, bool) or arrays thereof.
        This method converts nested dicts/objects to JSON strings.

        Args:
            properties: Dictionary that may contain nested objects

        Returns:
            Flattened dictionary with only primitive types
        """
        flattened = {}
        for key, value in properties.items():
            if value is None:
                continue
            elif isinstance(value, (str, int, float, bool)):
                flattened[key] = value
            elif isinstance(value, (list, tuple)):
                # Check if all items are primitives
                if all(isinstance(item, (str, int, float, bool)) for item in value):
                    flattened[key] = list(value)
                else:
                    # Convert to JSON string
                    flattened[key] = json.dumps(value)
            elif isinstance(value, dict):
                # Convert nested dict to JSON string
                flattened[key] = json.dumps(value)
            else:
                # Convert other types to string
                flattened[key] = str(value)
        return flattened

    def create_constraints(self) -> None:
        """Create database constraints and indexes."""
        constraints = [
            "CREATE CONSTRAINT entity_id IF NOT EXISTS FOR (e:Entity) REQUIRE e.id IS UNIQUE",
            "CREATE CONSTRAINT document_id IF NOT EXISTS FOR (d:Document) REQUIRE d.id IS UNIQUE",
        ]
        
        with self.driver.session() as session:
            for constraint in constraints:
                try:
                    session.run(constraint)
                    logger.debug(f"Created constraint: {constraint}")
                except Exception as e:
                    logger.warning(f"Constraint creation failed: {e}")
    
    def create_indexes(self) -> None:
        """Create database indexes for performance."""
        indexes = [
            "CREATE INDEX entity_name IF NOT EXISTS FOR (e:Entity) ON (e.name)",
            "CREATE INDEX entity_type IF NOT EXISTS FOR (e:Entity) ON (e.type)",
            "CREATE INDEX document_title IF NOT EXISTS FOR (d:Document) ON (d.title)",
        ]
        
        with self.driver.session() as session:
            for index in indexes:
                try:
                    session.run(index)
                    logger.debug(f"Created index: {index}")
                except Exception as e:
                    logger.warning(f"Index creation failed: {e}")
    
    def add_entity(self, entity: Entity) -> None:
        """Add entity to graph.

        Args:
            entity: Entity to add
        """
        # Flatten properties to avoid nested objects
        flattened_props = self._flatten_properties(entity.properties)

        # Build query - only add properties if they exist
        query = """
        MERGE (e:Entity {id: $id})
        SET e.name = $name,
            e.type = $type,
            e.description = $description,
            e.confidence = $confidence,
            e.source_modality = $source_modality,
            e.source_id = $source_id
        """

        if flattened_props:
            query += ",\n            e += $properties"

        params = {
            'id': str(entity.id),
            'name': entity.name,
            'type': entity.entity_type.value,
            'description': entity.description,
            'confidence': entity.confidence,
            'source_modality': entity.source_modality.value,
            'source_id': str(entity.source_id)
        }

        if flattened_props:
            params['properties'] = flattened_props

        with self.driver.session() as session:
            session.run(query, **params)
    
    def add_entities_batch(self, entities: List[Entity]) -> None:
        """Add multiple entities in batch.

        Args:
            entities: List of entities
        """
        if not entities:
            return

        # Separate entities with and without properties
        entities_with_props = []
        entities_without_props = []

        for e in entities:
            flattened = self._flatten_properties(e.properties)
            if flattened:
                entities_with_props.append((e, flattened))
            else:
                entities_without_props.append(e)

        # Use a single session for all operations
        with self.driver.session() as session:
            # Add entities without properties
            if entities_without_props:
                query = """
                UNWIND $entities AS entity
                MERGE (e:Entity {id: entity.id})
                SET e.name = entity.name,
                    e.type = entity.type,
                    e.description = entity.description,
                    e.confidence = entity.confidence,
                    e.source_modality = entity.source_modality,
                    e.source_id = entity.source_id
                """

                entities_data = [
                    {
                        'id': str(e.id),
                        'name': e.name,
                        'type': e.entity_type.value,
                        'description': e.description,
                        'confidence': e.confidence,
                        'source_modality': e.source_modality.value,
                        'source_id': str(e.source_id)
                    }
                    for e in entities_without_props
                ]

                session.run(query, entities=entities_data)

            # Add entities with properties
            if entities_with_props:
                query = """
                UNWIND $entities AS entity
                MERGE (e:Entity {id: entity.id})
                SET e.name = entity.name,
                    e.type = entity.type,
                    e.description = entity.description,
                    e.confidence = entity.confidence,
                    e.source_modality = entity.source_modality,
                    e.source_id = entity.source_id,
                    e += entity.properties
                """

                entities_data = [
                    {
                        'id': str(e.id),
                        'name': e.name,
                        'type': e.entity_type.value,
                        'description': e.description,
                        'confidence': e.confidence,
                        'source_modality': e.source_modality.value,
                        'source_id': str(e.source_id),
                        'properties': props
                    }
                    for e, props in entities_with_props
                ]

                session.run(query, entities=entities_data)

        logger.info(f"Added {len(entities)} entities to graph")
    
    def add_relationship(self, relationship: Relationship) -> None:
        """Add relationship to graph.

        Args:
            relationship: Relationship to add
        """
        query = f"""
        MATCH (source:Entity {{id: $source_id}})
        MATCH (target:Entity {{id: $target_id}})
        MERGE (source)-[r:{relationship.relationship_type.value}]->(target)
        SET r.confidence = $confidence
        """

        # Only add properties if they exist and are not empty
        flattened_props = self._flatten_properties(relationship.properties)
        if flattened_props:
            query += ", r += $properties"

        with self.driver.session() as session:
            params = {
                'source_id': str(relationship.source_entity_id),
                'target_id': str(relationship.target_entity_id),
                'confidence': relationship.confidence
            }
            if flattened_props:
                params['properties'] = flattened_props

            session.run(query, **params)
    
    def add_relationships_batch(self, relationships: List[Relationship]) -> None:
        """Add multiple relationships in batch."""
        if not relationships:
            return

        # Group by relationship type for efficient batch insertion
        by_type = {}
        for rel in relationships:
            rel_type = rel.relationship_type.value
            if rel_type not in by_type:
                by_type[rel_type] = []
            by_type[rel_type].append(rel)

        # Use a single session for all operations
        with self.driver.session() as session:
            for rel_type, rels in by_type.items():
                # Separate relationships with and without properties
                rels_with_props = []
                rels_without_props = []

                for r in rels:
                    flattened = self._flatten_properties(r.properties) if r.properties else {}
                    if flattened:
                        rels_with_props.append((r, flattened))
                    else:
                        rels_without_props.append(r)

                # Add relationships without properties
                if rels_without_props:
                    query = f"""
                    UNWIND $relationships AS rel
                    MATCH (source:Entity {{id: rel.source_id}})
                    MATCH (target:Entity {{id: rel.target_id}})
                    MERGE (source)-[r:{rel_type}]->(target)
                    SET r.confidence = rel.confidence
                    """

                    rels_data = [
                        {
                            'source_id': str(r.source_entity_id),
                            'target_id': str(r.target_entity_id),
                            'confidence': r.confidence
                        }
                        for r in rels_without_props
                    ]

                    session.run(query, relationships=rels_data)

                # Add relationships with properties
                if rels_with_props:
                    query = f"""
                    UNWIND $relationships AS rel
                    MATCH (source:Entity {{id: rel.source_id}})
                    MATCH (target:Entity {{id: rel.target_id}})
                    MERGE (source)-[r:{rel_type}]->(target)
                    SET r.confidence = rel.confidence,
                        r += rel.properties
                    """

                    rels_data = [
                        {
                            'source_id': str(r.source_entity_id),
                            'target_id': str(r.target_entity_id),
                            'confidence': r.confidence,
                            'properties': props
                        }
                        for r, props in rels_with_props
                    ]

                    session.run(query, relationships=rels_data)

        logger.info(f"Added {len(relationships)} relationships to graph")

    def find_entities_by_name(
        self,
        entity_names: List[str],
        fuzzy: bool = True,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Find entities by name.

        Args:
            entity_names: List of entity names to search for
            fuzzy: Whether to use fuzzy matching (case-insensitive contains)
            limit: Maximum number of results per name

        Returns:
            List of entity dictionaries
        """
        if not entity_names:
            return []

        with self.driver.session() as session:
            if fuzzy:
                # Case-insensitive partial match
                query = """
                UNWIND $names AS name
                MATCH (e:Entity)
                WHERE toLower(e.name) CONTAINS toLower(name)
                RETURN e.id AS id, e.name AS name, e.type AS type,
                       e.description AS description, e.confidence AS confidence,
                       e.source_modality AS source_modality, e.properties AS properties
                LIMIT $limit
                """
            else:
                # Exact match (case-insensitive)
                query = """
                UNWIND $names AS name
                MATCH (e:Entity)
                WHERE toLower(e.name) = toLower(name)
                RETURN e.id AS id, e.name AS name, e.type AS type,
                       e.description AS description, e.confidence AS confidence,
                       e.source_modality AS source_modality, e.properties AS properties
                LIMIT $limit
                """

            result = session.run(query, names=entity_names, limit=limit)
            entities = [dict(record) for record in result]

            logger.debug(f"Found {len(entities)} entities matching {entity_names}")
            return entities

    def find_related_chunks(
        self,
        entity_ids: List[str],
        max_depth: int = 2,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Find chunks related to entities through graph traversal.

        Args:
            entity_ids: List of entity IDs to start from
            max_depth: Maximum relationship depth to traverse
            limit: Maximum number of chunks to return

        Returns:
            List of dictionaries with chunk_id and relevance score
        """
        if not entity_ids:
            return []

        with self.driver.session() as session:
            # Traverse relationships and collect related entities
            # Then get their source chunks
            query = f"""
            UNWIND $entity_ids AS start_id
            MATCH (start:Entity {{id: start_id}})

            // Find entities within max_depth relationships
            CALL {{
                WITH start
                MATCH path = (start)-[*1..{max_depth}]-(related:Entity)
                RETURN related, length(path) AS distance
            }}

            // Calculate relevance score (inverse of distance)
            WITH related, distance,
                 CASE distance
                     WHEN 0 THEN 1.0
                     WHEN 1 THEN 0.8
                     WHEN 2 THEN 0.5
                     ELSE 0.3
                 END AS relevance

            // Get source chunk IDs from entities
            WHERE related.source_id IS NOT NULL

            // Return chunk information
            RETURN DISTINCT
                related.source_id AS chunk_id,
                related.name AS entity_name,
                related.type AS entity_type,
                relevance
            ORDER BY relevance DESC
            LIMIT $limit
            """

            result = session.run(query, entity_ids=entity_ids, limit=limit)
            chunks = []

            for record in result:
                chunk_info = {
                    'chunk_id': record['chunk_id'],
                    'entity_name': record['entity_name'],
                    'entity_type': record['entity_type'],
                    'relevance': record['relevance']
                }
                chunks.append(chunk_info)

            logger.debug(f"Found {len(chunks)} related chunks for {len(entity_ids)} entities")
            return chunks

