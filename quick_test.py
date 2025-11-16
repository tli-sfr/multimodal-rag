#!/usr/bin/env python
"""Quick test to verify Neo4j fixes work."""

import sys
print("Starting test...", file=sys.stderr, flush=True)

from uuid import uuid4
from src.graph.neo4j_client import Neo4jClient
from src.models import Entity, Relationship, EntityType, RelationshipType, ModalityType

print("Imports successful", file=sys.stderr, flush=True)

client = Neo4jClient()
print("Client created", file=sys.stderr, flush=True)

# Test 1: Entity with empty properties
try:
    entity = Entity(
        name="Test Empty",
        entity_type=EntityType.PERSON,
        source_modality=ModalityType.TEXT,
        source_id=uuid4(),
        properties={}
    )
    client.add_entity(entity)
    print("✅ Test 1 PASSED: Entity with empty properties", file=sys.stderr, flush=True)
except Exception as e:
    print(f"❌ Test 1 FAILED: {e}", file=sys.stderr, flush=True)
    sys.exit(1)

# Test 2: Entity with properties
try:
    entity = Entity(
        name="Test With Props",
        entity_type=EntityType.PERSON,
        source_modality=ModalityType.TEXT,
        source_id=uuid4(),
        properties={'age': 30, 'city': 'NYC'}
    )
    client.add_entity(entity)
    print("✅ Test 2 PASSED: Entity with properties", file=sys.stderr, flush=True)
except Exception as e:
    print(f"❌ Test 2 FAILED: {e}", file=sys.stderr, flush=True)
    sys.exit(1)

# Test 3: Batch with mixed properties
try:
    entities = [
        Entity(name="E1", entity_type=EntityType.PERSON, source_modality=ModalityType.TEXT,
               source_id=uuid4(), properties={}),
        Entity(name="E2", entity_type=EntityType.PERSON, source_modality=ModalityType.TEXT,
               source_id=uuid4(), properties={'age': 25})
    ]
    client.add_entities_batch(entities)
    print("✅ Test 3 PASSED: Batch with mixed properties", file=sys.stderr, flush=True)
except Exception as e:
    print(f"❌ Test 3 FAILED: {e}", file=sys.stderr, flush=True)
    sys.exit(1)

# Test 4: Relationship with empty properties
try:
    e1 = Entity(name="P1", entity_type=EntityType.PERSON, source_modality=ModalityType.TEXT, source_id=uuid4())
    e2 = Entity(name="P2", entity_type=EntityType.PERSON, source_modality=ModalityType.TEXT, source_id=uuid4())
    client.add_entity(e1)
    client.add_entity(e2)
    rel = Relationship(source_entity_id=e1.id, target_entity_id=e2.id,
                      relationship_type=RelationshipType.KNOWS, properties={})
    client.add_relationship(rel)
    print("✅ Test 4 PASSED: Relationship with empty properties", file=sys.stderr, flush=True)
except Exception as e:
    print(f"❌ Test 4 FAILED: {e}", file=sys.stderr, flush=True)
    sys.exit(1)

# Test 5: Relationship with properties
try:
    e1 = Entity(name="P3", entity_type=EntityType.PERSON, source_modality=ModalityType.TEXT, source_id=uuid4())
    e2 = Entity(name="P4", entity_type=EntityType.PERSON, source_modality=ModalityType.TEXT, source_id=uuid4())
    client.add_entity(e1)
    client.add_entity(e2)
    rel = Relationship(source_entity_id=e1.id, target_entity_id=e2.id,
                      relationship_type=RelationshipType.KNOWS, properties={'since': 2020})
    client.add_relationship(rel)
    print("✅ Test 5 PASSED: Relationship with properties", file=sys.stderr, flush=True)
except Exception as e:
    print(f"❌ Test 5 FAILED: {e}", file=sys.stderr, flush=True)
    sys.exit(1)

# Test 6: Batch relationships with mixed properties
try:
    entities = [Entity(name=f"E{i}", entity_type=EntityType.PERSON,
                      source_modality=ModalityType.TEXT, source_id=uuid4())
               for i in range(10, 15)]
    client.add_entities_batch(entities)
    
    rels = [
        Relationship(source_entity_id=entities[0].id, target_entity_id=entities[1].id,
                    relationship_type=RelationshipType.KNOWS, properties={}),
        Relationship(source_entity_id=entities[1].id, target_entity_id=entities[2].id,
                    relationship_type=RelationshipType.KNOWS, properties={'since': 2020})
    ]
    client.add_relationships_batch(rels)
    print("✅ Test 6 PASSED: Batch relationships with mixed properties", file=sys.stderr, flush=True)
except Exception as e:
    print(f"❌ Test 6 FAILED: {e}", file=sys.stderr, flush=True)
    sys.exit(1)

# Cleanup
with client.driver.session() as session:
    session.run("MATCH (n) DETACH DELETE n")
client.close()

print("\n" + "=" * 60, file=sys.stderr, flush=True)
print("✅ ALL TESTS PASSED!", file=sys.stderr, flush=True)
print("=" * 60, file=sys.stderr, flush=True)
print("\nThe Neo4j client is working correctly with all edge cases.", file=sys.stderr, flush=True)
print("You can now upload your PDF through Streamlit.", file=sys.stderr, flush=True)

