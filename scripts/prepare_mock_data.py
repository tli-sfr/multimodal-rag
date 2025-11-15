#!/usr/bin/env python3
"""
Mock Data Preparation Script

Creates realistic mock data for testing the multimodal RAG system:
1. Andrew Ng - Video, Audio, PDF (related content)
2. Fei-Fei Li - Video, Audio, PDF (unrelated content)

Populates both Qdrant (vector store) and Neo4j (knowledge graph).
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from uuid import uuid4
from datetime import datetime
from loguru import logger

from src.models import (
    Document, Chunk, Entity, Relationship,
    ModalityType, EntityType, RelationshipType,
    Metadata
)
from src.graph.neo4j_client import Neo4jClient
from src.vector_store.qdrant_client import QdrantVectorStore
from src.vector_store.embeddings import EmbeddingGenerator


# Mock data for Andrew Ng (RELATED content)
ANDREW_NG_VIDEO = {
    "title": "Andrew Ng - The Future of AI",
    "modality": ModalityType.VIDEO,
    "chunks": [
        {
            "content": "Hello everyone, I'm Andrew Ng. Today I want to talk about the future of artificial intelligence and how it will transform every industry.",
            "metadata": {"timestamp": "00:00:00-00:00:15", "speaker": "Andrew Ng"}
        },
        {
            "content": "Machine learning has made tremendous progress in the last decade. Deep learning, in particular, has revolutionized computer vision, natural language processing, and speech recognition.",
            "metadata": {"timestamp": "00:00:15-00:00:35", "speaker": "Andrew Ng"}
        },
        {
            "content": "At Stanford, we've been working on making AI education accessible to everyone. That's why I founded Coursera and deeplearning.ai to democratize AI education.",
            "metadata": {"timestamp": "00:00:35-00:00:55", "speaker": "Andrew Ng"}
        }
    ],
    "entities": [
        {"name": "Andrew Ng", "type": EntityType.PERSON, "description": "AI researcher, educator, and entrepreneur"},
        {"name": "Stanford University", "type": EntityType.ORGANIZATION, "description": "Research university"},
        {"name": "Coursera", "type": EntityType.ORGANIZATION, "description": "Online learning platform"},
        {"name": "deeplearning.ai", "type": EntityType.ORGANIZATION, "description": "AI education company"},
        {"name": "Artificial Intelligence", "type": EntityType.CONCEPT, "description": "Field of computer science"},
        {"name": "Machine Learning", "type": EntityType.CONCEPT, "description": "Subset of AI"},
        {"name": "Deep Learning", "type": EntityType.CONCEPT, "description": "Subset of machine learning"}
    ],
    "relationships": [
        ("Andrew Ng", "Stanford University", RelationshipType.WORKS_FOR),
        ("Andrew Ng", "Coursera", RelationshipType.FOUNDER_OF),
        ("Andrew Ng", "deeplearning.ai", RelationshipType.FOUNDER_OF),
        ("Andrew Ng", "Artificial Intelligence", RelationshipType.EXPERT_IN),
        ("Andrew Ng", "Machine Learning", RelationshipType.EXPERT_IN),
        ("Deep Learning", "Machine Learning", RelationshipType.PART_OF)
    ]
}

ANDREW_NG_AUDIO = {
    "title": "Andrew Ng - AI Course Introduction",
    "modality": ModalityType.AUDIO,
    "chunks": [
        {
            "content": "Welcome to Machine Learning! I'm Andrew Ng, and I'll be your instructor for this course.",
            "metadata": {"timestamp": "00:00:00-00:00:08", "speaker": "Andrew Ng"}
        },
        {
            "content": "This course will cover supervised learning, unsupervised learning, and best practices in machine learning. We'll use practical examples and you'll implement algorithms yourself.",
            "metadata": {"timestamp": "00:00:08-00:00:25", "speaker": "Andrew Ng"}
        },
        {
            "content": "I've been teaching this course at Stanford for many years, and now through Coursera, millions of students worldwide have learned machine learning.",
            "metadata": {"timestamp": "00:00:25-00:00:40", "speaker": "Andrew Ng"}
        }
    ],
    "entities": [
        {"name": "Andrew Ng", "type": EntityType.PERSON, "description": "AI researcher and educator"},
        {"name": "Machine Learning Course", "type": EntityType.CONCEPT, "description": "Educational course"},
        {"name": "Stanford University", "type": EntityType.ORGANIZATION, "description": "Research university"},
        {"name": "Coursera", "type": EntityType.ORGANIZATION, "description": "Online learning platform"},
        {"name": "Supervised Learning", "type": EntityType.CONCEPT, "description": "ML paradigm"},
        {"name": "Unsupervised Learning", "type": EntityType.CONCEPT, "description": "ML paradigm"}
    ],
    "relationships": [
        ("Andrew Ng", "Machine Learning Course", RelationshipType.CREATED_BY),
        ("Andrew Ng", "Stanford University", RelationshipType.WORKS_FOR),
        ("Andrew Ng", "Coursera", RelationshipType.FOUNDER_OF),
        ("Machine Learning Course", "Supervised Learning", RelationshipType.MENTIONS),
        ("Machine Learning Course", "Unsupervised Learning", RelationshipType.MENTIONS)
    ]
}

ANDREW_NG_PDF = {
    "title": "Andrew Ng - Biography",
    "modality": ModalityType.TEXT,
    "chunks": [
        {
            "content": "Andrew Ng is a British-American computer scientist and technology entrepreneur focusing on machine learning and artificial intelligence.",
            "metadata": {"page": 1, "section": "Introduction"}
        },
        {
            "content": "He is the founder of DeepLearning.AI and co-founder of Coursera. He was also the chief scientist at Baidu and led the Google Brain project.",
            "metadata": {"page": 1, "section": "Career"}
        },
        {
            "content": "Ng received his PhD from the University of California, Berkeley in 2002. He joined Stanford University as a professor in 2002, where he taught machine learning courses.",
            "metadata": {"page": 2, "section": "Education"}
        },
        {
            "content": "His research focuses on deep learning, machine learning, and robotics. He has published over 200 research papers in these areas.",
            "metadata": {"page": 2, "section": "Research"}
        }
    ],
    "entities": [
        {"name": "Andrew Ng", "type": EntityType.PERSON, "description": "Computer scientist and entrepreneur"},
        {"name": "DeepLearning.AI", "type": EntityType.ORGANIZATION, "description": "AI education company"},
        {"name": "Coursera", "type": EntityType.ORGANIZATION, "description": "Online learning platform"},
        {"name": "Baidu", "type": EntityType.ORGANIZATION, "description": "Chinese technology company"},
        {"name": "Google Brain", "type": EntityType.ORGANIZATION, "description": "Google's AI research team"},
        {"name": "UC Berkeley", "type": EntityType.ORGANIZATION, "description": "University"},
        {"name": "Stanford University", "type": EntityType.ORGANIZATION, "description": "Research university"},
        {"name": "Machine Learning", "type": EntityType.CONCEPT, "description": "Field of study"},
        {"name": "Deep Learning", "type": EntityType.CONCEPT, "description": "Field of study"},
        {"name": "Robotics", "type": EntityType.CONCEPT, "description": "Field of study"}
    ],
    "relationships": [
        ("Andrew Ng", "DeepLearning.AI", RelationshipType.FOUNDER_OF),
        ("Andrew Ng", "Coursera", RelationshipType.FOUNDER_OF),
        ("Andrew Ng", "Baidu", RelationshipType.WORKS_FOR),
        ("Andrew Ng", "Google Brain", RelationshipType.MEMBER_OF),
        ("Andrew Ng", "UC Berkeley", RelationshipType.GRADUATED_FROM),
        ("Andrew Ng", "Stanford University", RelationshipType.WORKS_FOR),
        ("Andrew Ng", "Machine Learning", RelationshipType.EXPERT_IN),
        ("Andrew Ng", "Deep Learning", RelationshipType.EXPERT_IN),
        ("Andrew Ng", "Robotics", RelationshipType.EXPERT_IN)
    ]
}




# Mock data for Fei-Fei Li (UNRELATED content)
FEIFEI_LI_VIDEO = {
    "title": "Fei-Fei Li - AI Research at Stanford",
    "modality": ModalityType.VIDEO,
    "chunks": [
        {
            "content": "I'm Fei-Fei Li, and I direct the Stanford Artificial Intelligence Lab. Our research focuses on computer vision and cognitive neuroscience.",
            "metadata": {"timestamp": "00:00:00-00:00:15", "speaker": "Fei-Fei Li"}
        },
        {
            "content": "One of our major contributions is ImageNet, a large-scale visual database that has been instrumental in advancing deep learning for computer vision.",
            "metadata": {"timestamp": "00:00:15-00:00:30", "speaker": "Fei-Fei Li"}
        },
        {
            "content": "We're also working on human-centered AI, ensuring that AI systems are designed with human values and ethics in mind.",
            "metadata": {"timestamp": "00:00:30-00:00:50", "speaker": "Fei-Fei Li"}
        }
    ],
    "entities": [
        {"name": "Fei-Fei Li", "type": EntityType.PERSON, "description": "Computer scientist and AI researcher"},
        {"name": "Stanford AI Lab", "type": EntityType.ORGANIZATION, "description": "Research laboratory"},
        {"name": "Stanford University", "type": EntityType.ORGANIZATION, "description": "Research university"},
        {"name": "ImageNet", "type": EntityType.CONCEPT, "description": "Large-scale visual database"},
        {"name": "Computer Vision", "type": EntityType.CONCEPT, "description": "Field of AI"},
        {"name": "Cognitive Neuroscience", "type": EntityType.CONCEPT, "description": "Field of study"},
        {"name": "Human-Centered AI", "type": EntityType.CONCEPT, "description": "AI design philosophy"}
    ],
    "relationships": [
        ("Fei-Fei Li", "Stanford AI Lab", RelationshipType.MEMBER_OF),
        ("Fei-Fei Li", "Stanford University", RelationshipType.WORKS_FOR),
        ("Fei-Fei Li", "ImageNet", RelationshipType.CREATED_BY),
        ("Fei-Fei Li", "Computer Vision", RelationshipType.EXPERT_IN),
        ("Fei-Fei Li", "Cognitive Neuroscience", RelationshipType.EXPERT_IN),
        ("ImageNet", "Computer Vision", RelationshipType.PART_OF)
    ]
}

FEIFEI_LI_AUDIO = {
    "title": "Fei-Fei Li - ImageNet Talk",
    "modality": ModalityType.AUDIO,
    "chunks": [
        {
            "content": "ImageNet started as a simple idea: what if we could teach computers to see by showing them millions of labeled images?",
            "metadata": {"timestamp": "00:00:00-00:00:12", "speaker": "Fei-Fei Li"}
        },
        {
            "content": "We collected over 14 million images across 20,000 categories. This dataset became the foundation for the ImageNet Large Scale Visual Recognition Challenge.",
            "metadata": {"timestamp": "00:00:12-00:00:28", "speaker": "Fei-Fei Li"}
        },
        {
            "content": "The breakthrough came in 2012 when Alex Krizhevsky's deep neural network won the competition with unprecedented accuracy. This marked the beginning of the deep learning revolution.",
            "metadata": {"timestamp": "00:00:28-00:00:45", "speaker": "Fei-Fei Li"}
        }
    ],
    "entities": [
        {"name": "Fei-Fei Li", "type": EntityType.PERSON, "description": "Computer scientist"},
        {"name": "ImageNet", "type": EntityType.CONCEPT, "description": "Visual database"},
        {"name": "ImageNet Challenge", "type": EntityType.EVENT, "description": "Annual competition"},
        {"name": "Alex Krizhevsky", "type": EntityType.PERSON, "description": "Computer scientist"},
        {"name": "Deep Neural Networks", "type": EntityType.CONCEPT, "description": "ML architecture"},
        {"name": "Computer Vision", "type": EntityType.CONCEPT, "description": "Field of AI"}
    ],
    "relationships": [
        ("Fei-Fei Li", "ImageNet", RelationshipType.CREATED_BY),
        ("ImageNet", "ImageNet Challenge", RelationshipType.PART_OF),
        ("Alex Krizhevsky", "ImageNet Challenge", RelationshipType.AWARDED),
        ("Deep Neural Networks", "Computer Vision", RelationshipType.PART_OF)
    ]
}

FEIFEI_LI_PDF = {
    "title": "Fei-Fei Li - Biography",
    "modality": ModalityType.TEXT,
    "chunks": [
        {
            "content": "Fei-Fei Li is a Chinese-American computer scientist known for her work in computer vision and artificial intelligence.",
            "metadata": {"page": 1, "section": "Introduction"}
        },
        {
            "content": "She is the Sequoia Professor at Stanford University and co-director of the Stanford Human-Centered AI Institute. She also served as Chief Scientist of AI/ML at Google Cloud.",
            "metadata": {"page": 1, "section": "Career"}
        },
        {
            "content": "Li received her PhD from California Institute of Technology in 2005. Her dissertation focused on Bayesian models for 3D object recognition.",
            "metadata": {"page": 2, "section": "Education"}
        },
        {
            "content": "She is best known for creating ImageNet, which catalyzed the deep learning revolution in computer vision. She has received numerous awards including the IAPR J.K. Aggarwal Prize.",
            "metadata": {"page": 2, "section": "Achievements"}
        }
    ],
    "entities": [
        {"name": "Fei-Fei Li", "type": EntityType.PERSON, "description": "Computer scientist"},
        {"name": "Stanford University", "type": EntityType.ORGANIZATION, "description": "Research university"},
        {"name": "Stanford HAI", "type": EntityType.ORGANIZATION, "description": "Human-Centered AI Institute"},
        {"name": "Google Cloud", "type": EntityType.ORGANIZATION, "description": "Cloud computing service"},
        {"name": "Caltech", "type": EntityType.ORGANIZATION, "description": "California Institute of Technology"},
        {"name": "ImageNet", "type": EntityType.CONCEPT, "description": "Visual database"},
        {"name": "Computer Vision", "type": EntityType.CONCEPT, "description": "Field of AI"},
        {"name": "IAPR J.K. Aggarwal Prize", "type": EntityType.EVENT, "description": "Academic award"}
    ],
    "relationships": [
        ("Fei-Fei Li", "Stanford University", RelationshipType.WORKS_FOR),
        ("Fei-Fei Li", "Stanford HAI", RelationshipType.MEMBER_OF),
        ("Fei-Fei Li", "Google Cloud", RelationshipType.WORKS_FOR),
        ("Fei-Fei Li", "Caltech", RelationshipType.GRADUATED_FROM),
        ("Fei-Fei Li", "ImageNet", RelationshipType.CREATED_BY),
        ("Fei-Fei Li", "Computer Vision", RelationshipType.EXPERT_IN),
        ("Fei-Fei Li", "IAPR J.K. Aggarwal Prize", RelationshipType.AWARDED)
    ]
}

ALL_MOCK_DATA = [
    ("andrew_ng_video", ANDREW_NG_VIDEO),
    ("andrew_ng_audio", ANDREW_NG_AUDIO),
    ("andrew_ng_pdf", ANDREW_NG_PDF),
    ("feifei_li_video", FEIFEI_LI_VIDEO),
    ("feifei_li_audio", FEIFEI_LI_AUDIO),
    ("feifei_li_pdf", FEIFEI_LI_PDF)
]


def create_document_from_mock(doc_id: str, mock_data: dict) -> tuple[Document, list[Entity], list[Relationship]]:
    """Create Document, Entities, and Relationships from mock data."""

    # Create document
    doc = Document(
        id=uuid4(),
        title=mock_data["title"],
        modality=mock_data["modality"],
        metadata=Metadata(
            source=f"mock_data_{doc_id}",
            modality=mock_data["modality"],
            file_size=1000,
            mime_type=f"{mock_data['modality'].value}/mock",
            tags=["mock_data", doc_id]
        )
    )

    # Create chunks
    chunks = []
    for i, chunk_data in enumerate(mock_data["chunks"]):
        chunk = Chunk(
            id=uuid4(),
            content=chunk_data["content"],
            chunk_index=i,
            modality=mock_data["modality"],
            source_id=doc.id,
            metadata=Metadata(
                source=f"mock_data_{doc_id}",
                modality=mock_data["modality"],
                tags=["mock_data", doc_id],
                custom=chunk_data["metadata"]
            )
        )
        chunks.append(chunk)

    doc.chunks = chunks

    # Create entities
    # In a real scenario, entities would be extracted from individual chunks
    # For mock data, we'll distribute entities across chunks
    entities = []
    entity_map = {}  # name -> entity
    for idx, entity_data in enumerate(mock_data["entities"]):
        # Distribute entities across chunks (round-robin)
        chunk_idx = idx % len(chunks)
        chunk_id = chunks[chunk_idx].id

        entity = Entity(
            id=uuid4(),
            name=entity_data["name"],
            entity_type=entity_data["type"],
            description=entity_data.get("description"),
            source_modality=mock_data["modality"],
            source_id=chunk_id,  # Use chunk ID instead of doc ID
            properties={"mock_data": True, "source_doc": doc_id, "chunk_index": chunk_idx}
        )
        entities.append(entity)
        entity_map[entity_data["name"]] = entity

    # Create relationships
    relationships = []
    for source_name, target_name, rel_type in mock_data["relationships"]:
        if source_name in entity_map and target_name in entity_map:
            # Use the source entity's chunk ID
            source_entity = entity_map[source_name]

            relationship = Relationship(
                id=uuid4(),
                source_entity_id=source_entity.id,
                target_entity_id=entity_map[target_name].id,
                relationship_type=rel_type,
                source_modality=mock_data["modality"],
                source_id=source_entity.source_id,  # Use source entity's chunk ID
                properties={"mock_data": True, "source_doc": doc_id}
            )
            relationships.append(relationship)

    return doc, entities, relationships


def populate_mock_data():
    """Populate mock data to Qdrant and Neo4j."""
    logger.info("Starting mock data population...")

    # Initialize clients
    neo4j_client = Neo4jClient()
    qdrant_client = QdrantVectorStore()
    embedding_gen = EmbeddingGenerator()

    # Ensure Qdrant collection exists with correct dimensions
    logger.info("Ensuring Qdrant collection exists with correct dimensions...")
    try:
        # Try to delete existing collection if it exists
        qdrant_client.client.delete_collection(collection_name=qdrant_client.collection_name)
        logger.info("Deleted existing collection")
    except Exception:
        pass  # Collection doesn't exist, that's fine

    # Create collection with correct dimensions
    qdrant_client.create_collection(vector_size=3072)  # OpenAI text-embedding-3-large size

    try:
        total_chunks = 0
        total_entities = 0
        total_relationships = 0

        for doc_id, mock_data in ALL_MOCK_DATA:
            logger.info(f"Processing {doc_id}...")

            # Create document, entities, and relationships
            doc, entities, relationships = create_document_from_mock(doc_id, mock_data)

            # Generate embeddings for chunks
            logger.info(f"  Generating embeddings for {len(doc.chunks)} chunks...")
            embeddings = embedding_gen.generate_for_chunks(doc.chunks)

            # Add chunks to Qdrant
            logger.info(f"  Adding {len(doc.chunks)} chunks to Qdrant...")
            qdrant_client.add_chunks_batch(doc.chunks, embeddings)
            total_chunks += len(doc.chunks)

            # Add entities to Neo4j
            logger.info(f"  Adding {len(entities)} entities to Neo4j...")
            neo4j_client.add_entities_batch(entities)
            total_entities += len(entities)

            # Add relationships to Neo4j
            logger.info(f"  Adding {len(relationships)} relationships to Neo4j...")
            neo4j_client.add_relationships_batch(relationships)
            total_relationships += len(relationships)

            logger.success(f"✅ {doc_id} completed!")

        logger.success(f"\n{'='*60}")
        logger.success(f"✅ Mock data population completed!")
        logger.success(f"{'='*60}")
        logger.success(f"Total chunks added to Qdrant: {total_chunks}")
        logger.success(f"Total entities added to Neo4j: {total_entities}")
        logger.success(f"Total relationships added to Neo4j: {total_relationships}")
        logger.success(f"{'='*60}\n")

        # Print summary by person
        logger.info("Summary by person:")
        logger.info("  Andrew Ng: 3 documents (video, audio, PDF)")
        logger.info("  Fei-Fei Li: 3 documents (video, audio, PDF)")
        logger.info("\nYou can now:")
        logger.info("  1. Start Streamlit: streamlit run src/ui/app.py")
        logger.info("  2. Search for 'Andrew Ng' to see related content")
        logger.info("  3. Search for 'Fei-Fei Li' to see unrelated content")
        logger.info("  4. View Neo4j graph: http://localhost:7474")
        logger.info("  5. Clean up: python scripts/cleanup_mock_data.py")

    except Exception as e:
        logger.error(f"Error populating mock data: {e}")
        raise
    finally:
        neo4j_client.close()


if __name__ == "__main__":
    populate_mock_data()

