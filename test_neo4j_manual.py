"""Manual test script to validate all Neo4j edge cases."""

from uuid import uuid4
from src.graph.neo4j_client import Neo4jClient
from src.models import Entity, Relationship, EntityType, RelationshipType, ModalityType

def test_all_scenarios():
    """Run all test scenarios and report results."""
    client = Neo4jClient()
    results = []

    print("=" * 80)
    print("COMPREHENSIVE NEO4J CLIENT TESTS")
    print("=" * 80)

    # Test 1: Entity with empty properties
    print("\n[1/15] Testing entity with empty properties...")
    try:
        entity = Entity(
            name="Test Empty Props",
            entity_type=EntityType.PERSON,
            source_modality=ModalityType.TEXT,
            source_id=uuid4(),
            properties={}
        )
        client.add_entity(entity)
        print("✅ PASS")
        results.append(("Entity with empty properties", True, None))
    except Exception as e:
        print(f"❌ FAIL: {e}")
        results.append(("Entity with empty properties", False, str(e)))

    # Test 2: Entity with primitive properties
    print("\n[2/15] Testing entity with primitive properties...")
    try:
        entity = Entity(
            name="Test Primitive Props",
            entity_type=EntityType.PERSON,
            source_modality=ModalityType.TEXT,
            source_id=uuid4(),
            properties={'age': 30, 'name': 'John', 'active': True, 'score': 95.5}
        )
        client.add_entity(entity)
        print("✅ PASS")
        results.append(("Entity with primitive properties", True, None))
    except Exception as e:
        print(f"❌ FAIL: {e}")
        results.append(("Entity with primitive properties", False, str(e)))

    # Test 3: Entity with nested dict
    print("\n[3/15] Testing entity with nested dict properties...")
    try:
        entity = Entity(
            name="Test Nested Props",
            entity_type=EntityType.PERSON,
            source_modality=ModalityType.TEXT,
            source_id=uuid4(),
            properties={'metadata': {'page': 1, 'section': 'Intro'}}
        )
        client.add_entity(entity)
        print("✅ PASS")
        results.append(("Entity with nested dict", True, None))
    except Exception as e:
        print(f"❌ FAIL: {e}")
        results.append(("Entity with nested dict", False, str(e)))

    # Test 4: Entity with list properties
    print("\n[4/15] Testing entity with list properties...")
    try:
        entity = Entity(
            name="Test List Props",
            entity_type=EntityType.PERSON,
            source_modality=ModalityType.TEXT,
            source_id=uuid4(),
            properties={'tags': ['tag1', 'tag2'], 'scores': [1, 2, 3]}
        )
        client.add_entity(entity)
        print("✅ PASS")
        results.append(("Entity with list properties", True, None))
    except Exception as e:
        print(f"❌ FAIL: {e}")
        results.append(("Entity with list properties", False, str(e)))

    # Test 5: Entity with None values
    print("\n[5/15] Testing entity with None values in properties...")
    try:
        entity = Entity(
            name="Test None Props",
            entity_type=EntityType.PERSON,
            source_modality=ModalityType.TEXT,
            source_id=uuid4(),
            properties={'field1': 'value', 'field2': None, 'field3': 123}
        )
        client.add_entity(entity)
        print("✅ PASS")
        results.append(("Entity with None values", True, None))
    except Exception as e:
        print(f"❌ FAIL: {e}")
        results.append(("Entity with None values", False, str(e)))

    # Test 6: Batch entities with mixed properties
    print("\n[6/15] Testing batch entities with mixed properties...")
    try:
        entities = [
            Entity(name="E1", entity_type=EntityType.PERSON, source_modality=ModalityType.TEXT,
                   source_id=uuid4(), properties={}),
            Entity(name="E2", entity_type=EntityType.PERSON, source_modality=ModalityType.TEXT,
                   source_id=uuid4(), properties={'age': 25}),
            Entity(name="E3", entity_type=EntityType.PERSON, source_modality=ModalityType.TEXT,
                   source_id=uuid4(), properties={'city': 'NYC', 'country': 'USA'})
        ]
        client.add_entities_batch(entities)
        print("✅ PASS")
        results.append(("Batch entities mixed properties", True, None))
    except Exception as e:
        print(f"❌ FAIL: {e}")
        results.append(("Batch entities mixed properties", False, str(e)))

    # Test 7: Relationship with empty properties
    print("\n[7/15] Testing relationship with empty properties...")
    try:
        e1 = Entity(name="P1", entity_type=EntityType.PERSON, source_modality=ModalityType.TEXT, source_id=uuid4())
        e2 = Entity(name="P2", entity_type=EntityType.PERSON, source_modality=ModalityType.TEXT, source_id=uuid4())
        client.add_entity(e1)
        client.add_entity(e2)
        rel = Relationship(source_entity_id=e1.id, target_entity_id=e2.id,
                          relationship_type=RelationshipType.KNOWS, properties={})
        client.add_relationship(rel)
        print("✅ PASS")
        results.append(("Relationship with empty properties", True, None))
    except Exception as e:
        print(f"❌ FAIL: {e}")
        results.append(("Relationship with empty properties", False, str(e)))




    # Test 8: Relationship with primitive properties
    print("\n[8/15] Testing relationship with primitive properties...")
    try:
        e1 = Entity(name="P3", entity_type=EntityType.PERSON, source_modality=ModalityType.TEXT, source_id=uuid4())
        e2 = Entity(name="P4", entity_type=EntityType.PERSON, source_modality=ModalityType.TEXT, source_id=uuid4())
        client.add_entity(e1)
        client.add_entity(e2)
        rel = Relationship(source_entity_id=e1.id, target_entity_id=e2.id,
                          relationship_type=RelationshipType.KNOWS,
                          properties={'since': 2020, 'strength': 'strong'})
        client.add_relationship(rel)
        print("✅ PASS")
        results.append(("Relationship with primitive properties", True, None))
    except Exception as e:
        print(f"❌ FAIL: {e}")
        results.append(("Relationship with primitive properties", False, str(e)))

    # Test 9: Relationship with nested properties
    print("\n[9/15] Testing relationship with nested properties...")
    try:
        e1 = Entity(name="P5", entity_type=EntityType.PERSON, source_modality=ModalityType.TEXT, source_id=uuid4())
        e2 = Entity(name="O1", entity_type=EntityType.ORGANIZATION, source_modality=ModalityType.TEXT, source_id=uuid4())
        client.add_entity(e1)
        client.add_entity(e2)
        rel = Relationship(source_entity_id=e1.id, target_entity_id=e2.id,
                          relationship_type=RelationshipType.WORKS_FOR,
                          properties={'employment': {'start': '2020-01-01', 'position': 'Engineer'}})
        client.add_relationship(rel)
        print("✅ PASS")
        results.append(("Relationship with nested properties", True, None))
    except Exception as e:
        print(f"❌ FAIL: {e}")
        results.append(("Relationship with nested properties", False, str(e)))

    # Test 10: Batch relationships with mixed properties
    print("\n[10/15] Testing batch relationships with mixed properties...")
    try:
        entities = [Entity(name=f"E{i}", entity_type=EntityType.PERSON,
                          source_modality=ModalityType.TEXT, source_id=uuid4())
                   for i in range(10, 15)]
        client.add_entities_batch(entities)

        rels = [
            Relationship(source_entity_id=entities[0].id, target_entity_id=entities[1].id,
                        relationship_type=RelationshipType.KNOWS, properties={}),
            Relationship(source_entity_id=entities[1].id, target_entity_id=entities[2].id,
                        relationship_type=RelationshipType.KNOWS, properties={'since': 2020}),
            Relationship(source_entity_id=entities[2].id, target_entity_id=entities[3].id,
                        relationship_type=RelationshipType.RELATED_TO, properties={}),
            Relationship(source_entity_id=entities[3].id, target_entity_id=entities[4].id,
                        relationship_type=RelationshipType.RELATED_TO, properties={'type': 'family'})
        ]
        client.add_relationships_batch(rels)
        print("✅ PASS")
        results.append(("Batch relationships mixed properties", True, None))
    except Exception as e:
        print(f"❌ FAIL: {e}")
        results.append(("Batch relationships mixed properties", False, str(e)))

    # Test 11-15 and summary
    print("\n[11/15] Testing empty batch entities...")
    try:
        client.add_entities_batch([])
        print("✅ PASS")
        results.append(("Empty batch entities", True, None))
    except Exception as e:
        print(f"❌ FAIL: {e}")
        results.append(("Empty batch entities", False, str(e)))

    print("\n[12/15] Testing empty batch relationships...")
    try:
        client.add_relationships_batch([])
        print("✅ PASS")
        results.append(("Empty batch relationships", True, None))
    except Exception as e:
        print(f"❌ FAIL: {e}")
        results.append(("Empty batch relationships", False, str(e)))

    print("\n[13/15] Testing special characters...")
    try:
        entity = Entity(name="Special", entity_type=EntityType.PERSON, source_modality=ModalityType.TEXT,
                       source_id=uuid4(), properties={'quote': 'He said: "Hello"', 'unicode': 'Hello 世界'})
        client.add_entity(entity)
        print("✅ PASS")
        results.append(("Special characters", True, None))
    except Exception as e:
        print(f"❌ FAIL: {e}")
        results.append(("Special characters", False, str(e)))

    print("\n[14/15] Testing all relationship types...")
    try:
        e1 = Entity(name="AllRel1", entity_type=EntityType.PERSON, source_modality=ModalityType.TEXT, source_id=uuid4())
        e2 = Entity(name="AllRel2", entity_type=EntityType.ORGANIZATION, source_modality=ModalityType.TEXT, source_id=uuid4())
        client.add_entity(e1)
        client.add_entity(e2)
        for rel_type in RelationshipType:
            rel = Relationship(source_entity_id=e1.id, target_entity_id=e2.id,
                              relationship_type=rel_type, properties={'test': True})
            client.add_relationship(rel)
        print("✅ PASS")
        results.append(("All relationship types", True, None))
    except Exception as e:
        print(f"❌ FAIL: {e}")
        results.append(("All relationship types", False, str(e)))

    print("\n[15/15] Testing large batch...")
    try:
        entities = [Entity(name=f"Large{i}", entity_type=EntityType.PERSON,
                          source_modality=ModalityType.TEXT, source_id=uuid4(),
                          properties={'index': i}) for i in range(50)]
        client.add_entities_batch(entities)
        print("✅ PASS")
        results.append(("Large batch", True, None))
    except Exception as e:
        print(f"❌ FAIL: {e}")
        results.append(("Large batch", False, str(e)))

    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    passed = sum(1 for _, success, _ in results if success)
    failed = sum(1 for _, success, _ in results if not success)
    print(f"\nTotal: {len(results)} | ✅ Passed: {passed} | ❌ Failed: {failed}")

    if failed > 0:
        print("\n" + "=" * 80)
        print("FAILED TESTS:")
        for name, success, error in results:
            if not success:
                print(f"\n❌ {name}\n   {error}")

    # Cleanup
    print("\n" + "=" * 80)
    with client.driver.session() as session:
        session.run("MATCH (n) DETACH DELETE n")
    client.close()
    print("✅ Cleanup complete\n")
    return failed == 0

if __name__ == "__main__":
    success = test_all_scenarios()
    exit(0 if success else 1)
