"""Comprehensive tests for Neo4j client to catch all edge cases."""

import pytest
from uuid import uuid4
from src.graph.neo4j_client import Neo4jClient
from src.models import Entity, Relationship, EntityType, RelationshipType, ModalityType


@pytest.fixture
def neo4j_client():
    """Create Neo4j client for testing."""
    client = Neo4jClient()
    yield client
    # Cleanup after tests
    with client.driver.session() as session:
        session.run("MATCH (n) DETACH DELETE n")
    client.close()


class TestEntityStorage:
    """Test all entity storage scenarios."""

    def test_entity_with_empty_properties(self, neo4j_client):
        """Test entity with empty properties dict."""
        entity = Entity(
            name="Test Entity",
            entity_type=EntityType.PERSON,
            source_modality=ModalityType.TEXT,
            source_id=uuid4(),
            properties={}  # Empty dict
        )
        neo4j_client.add_entity(entity)

    def test_entity_with_none_properties(self, neo4j_client):
        """Test entity without specifying properties - should use default empty dict."""
        entity = Entity(
            name="Test Entity",
            entity_type=EntityType.PERSON,
            source_modality=ModalityType.TEXT,
            source_id=uuid4()
            # properties not specified - will use default_factory=dict
        )
        neo4j_client.add_entity(entity)

    def test_entity_with_primitive_properties(self, neo4j_client):
        """Test entity with primitive type properties."""
        entity = Entity(
            name="Test Entity",
            entity_type=EntityType.PERSON,
            source_modality=ModalityType.TEXT,
            source_id=uuid4(),
            properties={
                'age': 30,
                'name_str': 'John',
                'active': True,
                'score': 95.5
            }
        )
        neo4j_client.add_entity(entity)

    def test_entity_with_nested_dict_properties(self, neo4j_client):
        """Test entity with nested dictionary properties."""
        entity = Entity(
            name="Test Entity",
            entity_type=EntityType.PERSON,
            source_modality=ModalityType.TEXT,
            source_id=uuid4(),
            properties={
                'metadata': {
                    'page': 1,
                    'section': 'Introduction'
                }
            }
        )
        neo4j_client.add_entity(entity)

    def test_entity_with_list_properties(self, neo4j_client):
        """Test entity with list properties."""
        entity = Entity(
            name="Test Entity",
            entity_type=EntityType.PERSON,
            source_modality=ModalityType.TEXT,
            source_id=uuid4(),
            properties={
                'tags': ['tag1', 'tag2', 'tag3'],
                'scores': [1, 2, 3, 4, 5]
            }
        )
        neo4j_client.add_entity(entity)

    def test_entity_with_complex_list_properties(self, neo4j_client):
        """Test entity with list of dicts properties."""
        entity = Entity(
            name="Test Entity",
            entity_type=EntityType.PERSON,
            source_modality=ModalityType.TEXT,
            source_id=uuid4(),
            properties={
                'items': [
                    {'id': 1, 'name': 'Item 1'},
                    {'id': 2, 'name': 'Item 2'}
                ]
            }
        )
        neo4j_client.add_entity(entity)

    def test_entity_with_null_values_in_properties(self, neo4j_client):
        """Test entity with None values in properties."""
        entity = Entity(
            name="Test Entity",
            entity_type=EntityType.PERSON,
            source_modality=ModalityType.TEXT,
            source_id=uuid4(),
            properties={
                'field1': 'value',
                'field2': None,
                'field3': 123
            }
        )
        neo4j_client.add_entity(entity)

    def test_entities_batch_with_mixed_properties(self, neo4j_client):
        """Test batch insert with mix of empty and non-empty properties."""
        entities = [
            Entity(
                name="Entity 1",
                entity_type=EntityType.PERSON,
                source_modality=ModalityType.TEXT,
                source_id=uuid4(),
                properties={}  # Empty
            ),
            Entity(
                name="Entity 2",
                entity_type=EntityType.ORGANIZATION,
                source_modality=ModalityType.TEXT,
                source_id=uuid4(),
                properties={'founded': 2020}  # Non-empty
            ),
            Entity(
                name="Entity 3",
                entity_type=EntityType.LOCATION,
                source_modality=ModalityType.TEXT,
                source_id=uuid4(),
                properties={'country': 'USA', 'population': 1000000}
            )
        ]
        neo4j_client.add_entities_batch(entities)




class TestRelationshipStorage:
    """Test all relationship storage scenarios."""

    def test_relationship_with_empty_properties(self, neo4j_client):
        """Test relationship with empty properties dict."""
        # Create entities first
        source_id = uuid4()
        entity1 = Entity(
            name="Person 1",
            entity_type=EntityType.PERSON,
            source_modality=ModalityType.TEXT,
            source_id=source_id,
            properties={}
        )
        entity2 = Entity(
            name="Person 2",
            entity_type=EntityType.PERSON,
            source_modality=ModalityType.TEXT,
            source_id=source_id,
            properties={}
        )
        neo4j_client.add_entity(entity1)
        neo4j_client.add_entity(entity2)

        # Create relationship with empty properties
        relationship = Relationship(
            source_entity_id=entity1.id,
            target_entity_id=entity2.id,
            relationship_type=RelationshipType.RELATED_TO,
            source_modality=ModalityType.TEXT,
            source_id=source_id,
            properties={}  # Empty dict
        )
        neo4j_client.add_relationship(relationship)

    def test_relationship_with_primitive_properties(self, neo4j_client):
        """Test relationship with primitive properties."""
        source_id = uuid4()
        entity1 = Entity(
            name="Person 1",
            entity_type=EntityType.PERSON,
            source_modality=ModalityType.TEXT,
            source_id=source_id
        )
        entity2 = Entity(
            name="Person 2",
            entity_type=EntityType.PERSON,
            source_modality=ModalityType.TEXT,
            source_id=source_id
        )
        neo4j_client.add_entity(entity1)
        neo4j_client.add_entity(entity2)

        relationship = Relationship(
            source_entity_id=entity1.id,
            target_entity_id=entity2.id,
            relationship_type=RelationshipType.RELATED_TO,
            source_modality=ModalityType.TEXT,
            source_id=source_id,
            properties={
                'since': 2020,
                'strength': 'strong',
                'verified': True
            }
        )
        neo4j_client.add_relationship(relationship)

    def test_relationship_with_nested_properties(self, neo4j_client):
        """Test relationship with nested dict properties."""
        source_id = uuid4()
        entity1 = Entity(
            name="Person 1",
            entity_type=EntityType.PERSON,
            source_modality=ModalityType.TEXT,
            source_id=source_id
        )
        entity2 = Entity(
            name="Organization 1",
            entity_type=EntityType.ORGANIZATION,
            source_modality=ModalityType.TEXT,
            source_id=source_id
        )
        neo4j_client.add_entity(entity1)
        neo4j_client.add_entity(entity2)

        relationship = Relationship(
            source_entity_id=entity1.id,
            target_entity_id=entity2.id,
            relationship_type=RelationshipType.WORKS_FOR,
            source_modality=ModalityType.TEXT,
            source_id=source_id,
            properties={
                'employment': {
                    'start_date': '2020-01-01',
                    'position': 'Engineer'
                }
            }
        )
        neo4j_client.add_relationship(relationship)

    def test_relationships_batch_with_mixed_properties(self, neo4j_client):
        """Test batch insert of relationships with mixed properties."""
        # Create entities
        source_id = uuid4()
        entities = [
            Entity(
                name=f"Entity {i}",
                entity_type=EntityType.PERSON,
                source_modality=ModalityType.TEXT,
                source_id=source_id
            )
            for i in range(5)
        ]
        neo4j_client.add_entities_batch(entities)

        # Create relationships with mixed properties
        relationships = [
            Relationship(
                source_entity_id=entities[0].id,
                target_entity_id=entities[1].id,
                relationship_type=RelationshipType.RELATED_TO,
                source_modality=ModalityType.TEXT,
                source_id=source_id,
                properties={}  # Empty
            ),
            Relationship(
                source_entity_id=entities[1].id,
                target_entity_id=entities[2].id,
                relationship_type=RelationshipType.RELATED_TO,
                source_modality=ModalityType.TEXT,
                source_id=source_id,
                properties={'since': 2020}  # Non-empty
            ),
            Relationship(
                source_entity_id=entities[2].id,
                target_entity_id=entities[3].id,
                relationship_type=RelationshipType.RELATED_TO,
                source_modality=ModalityType.TEXT,
                source_id=source_id,
                properties={}  # Empty
            ),
            Relationship(
                source_entity_id=entities[3].id,
                target_entity_id=entities[4].id,
                relationship_type=RelationshipType.RELATED_TO,
                source_modality=ModalityType.TEXT,
                source_id=source_id,
                properties={'type': 'family', 'strength': 0.9}  # Non-empty
            )
        ]
        neo4j_client.add_relationships_batch(relationships)

    def test_all_relationship_types(self, neo4j_client):
        """Test all relationship types to ensure they're valid."""
        source_id = uuid4()
        entity1 = Entity(
            name="Entity 1",
            entity_type=EntityType.PERSON,
            source_modality=ModalityType.TEXT,
            source_id=source_id
        )
        entity2 = Entity(
            name="Entity 2",
            entity_type=EntityType.ORGANIZATION,
            source_modality=ModalityType.TEXT,
            source_id=source_id
        )
        neo4j_client.add_entity(entity1)
        neo4j_client.add_entity(entity2)

        # Test each relationship type
        for rel_type in RelationshipType:
            relationship = Relationship(
                source_entity_id=entity1.id,
                target_entity_id=entity2.id,
                relationship_type=rel_type,
                source_modality=ModalityType.TEXT,
                source_id=source_id,
                properties={'test': True}
            )
            neo4j_client.add_relationship(relationship)


class TestEdgeCases:
    """Test edge cases and special scenarios."""

    def test_empty_batch_entities(self, neo4j_client):
        """Test adding empty list of entities."""
        neo4j_client.add_entities_batch([])

    def test_empty_batch_relationships(self, neo4j_client):
        """Test adding empty list of relationships."""
        neo4j_client.add_relationships_batch([])

    def test_entity_with_very_long_property_values(self, neo4j_client):
        """Test entity with very long string properties."""
        entity = Entity(
            name="Test Entity",
            entity_type=EntityType.DOCUMENT,
            source_modality=ModalityType.TEXT,
            source_id=uuid4(),
            properties={
                'long_text': 'x' * 10000,  # 10k characters
                'normal': 'short'
            }
        )
        neo4j_client.add_entity(entity)

    def test_entity_with_special_characters_in_properties(self, neo4j_client):
        """Test entity with special characters in property values."""
        entity = Entity(
            name="Test Entity",
            entity_type=EntityType.PERSON,
            source_modality=ModalityType.TEXT,
            source_id=uuid4(),
            properties={
                'quote': "He said: \"Hello\"",
                'newline': "Line1\nLine2",
                'unicode': "Hello 世界 🌍",
                'backslash': "C:\\Users\\test"
            }
        )
        neo4j_client.add_entity(entity)

    def test_large_batch_insert(self, neo4j_client):
        """Test inserting large batch of entities."""
        entities = [
            Entity(
                name=f"Entity {i}",
                entity_type=EntityType.PERSON,
                source_modality=ModalityType.TEXT,
                source_id=uuid4(),
                properties={'index': i, 'batch': 'large'}
            )
            for i in range(100)
        ]
        neo4j_client.add_entities_batch(entities)
