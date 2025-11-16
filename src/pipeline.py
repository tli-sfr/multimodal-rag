"""Main RAG pipeline orchestrating all components."""

from pathlib import Path
from typing import List, Optional
from uuid import UUID

from loguru import logger

from .models import Document, Query, Answer, SearchResult
from .ingestion import IngestionPipeline
from .extraction import EntityExtractor, RelationshipExtractor, CrossModalLinker
from .vector_store import QdrantVectorStore, EmbeddingGenerator
from .graph import Neo4jClient
from .search import HybridSearchEngine
from .config import get_settings, get_config


class MultimodalRAGPipeline:
    """End-to-end multimodal RAG pipeline."""
    
    def __init__(self):
        """Initialize RAG pipeline."""
        logger.info("Initializing Multimodal RAG Pipeline")
        
        self.settings = get_settings()
        self.config = get_config()
        
        # Initialize components
        self.ingestion_pipeline = IngestionPipeline(
            max_workers=self.settings.max_workers
        )
        
        self.entity_extractor = EntityExtractor()
        self.relationship_extractor = RelationshipExtractor()
        self.cross_modal_linker = CrossModalLinker()
        
        self.embedding_generator = EmbeddingGenerator()
        
        self.vector_store = QdrantVectorStore()
        self.vector_store.create_collection()
        
        self.graph_client = Neo4jClient()
        self.graph_client.create_constraints()
        self.graph_client.create_indexes()
        
        self.search_engine = HybridSearchEngine(
            vector_store=self.vector_store,
            graph_client=self.graph_client,
            embedding_generator=self.embedding_generator,
            entity_extractor=self.entity_extractor,
            use_graph_filter=True  # Enable graph-based filtering to exclude unconnected content
        )
        
        logger.info("Pipeline initialized successfully")
    
    def ingest_documents(
        self,
        input_path: Path,
        recursive: bool = True,
        **kwargs
    ) -> List[Document]:
        """Ingest documents from path.

        Args:
            input_path: Path to file or directory
            recursive: Process directories recursively
            **kwargs: Additional parameters to pass to ingesters (original_filename, upload_source)

        Returns:
            List of ingested documents
        """
        logger.info(f"Starting ingestion from: {input_path}")

        # Ingest files
        if input_path.is_file():
            doc = self.ingestion_pipeline.ingest_file(input_path, **kwargs)
            documents = [doc] if doc else []
        else:
            # For directory ingestion, mark as script source if not specified
            if 'upload_source' not in kwargs:
                kwargs['upload_source'] = 'script'
            documents = self.ingestion_pipeline.ingest_directory(
                input_path,
                recursive=recursive,
                **kwargs
            )
        
        if not documents:
            logger.warning("No documents ingested")
            return []
        
        logger.info(f"Ingested {len(documents)} documents")
        
        # Process each document
        for doc in documents:
            self._process_document(doc)
        
        return documents
    
    def _process_document(self, document: Document) -> None:
        """Process a single document through the pipeline.
        
        Args:
            document: Document to process
        """
        logger.info(f"Processing document: {document.title}")
        
        try:
            # 1. Extract entities
            entities = self.entity_extractor.extract_from_chunks(document.chunks)
            entities = self.entity_extractor.deduplicate_entities(entities)
            document.entities = entities
            
            # 2. Extract relationships
            relationships = []
            for chunk in document.chunks:
                chunk_entities = [e for e in entities if e.source_id == chunk.id]
                chunk_rels = self.relationship_extractor.extract_from_chunk(
                    chunk,
                    chunk_entities
                )
                relationships.extend(chunk_rels)
            
            document.relationships = relationships
            
            # 3. Generate embeddings
            embeddings = self.embedding_generator.generate_for_chunks(document.chunks)
            
            # Update chunks with embeddings
            for chunk, embedding in zip(document.chunks, embeddings):
                chunk.embedding = embedding
            
            # 4. Store in vector database
            self.vector_store.add_chunks_batch(document.chunks, embeddings)
            
            # 5. Store in graph database
            if entities:
                self.graph_client.add_entities_batch(entities)
            
            if relationships:
                self.graph_client.add_relationships_batch(relationships)
            
            document.processed = True
            logger.info(f"Successfully processed document: {document.title}")
        
        except Exception as e:
            logger.error(f"Failed to process document {document.title}: {e}")
            document.processing_errors.append(str(e))
    
    def query(
        self,
        query_text: str,
        top_k: int = 10
    ) -> Answer:
        """Query the RAG system.
        
        Args:
            query_text: Query text
            top_k: Number of results to return
            
        Returns:
            Answer object
        """
        import time
        start_time = time.time()
        
        logger.info(f"Processing query: {query_text}")
        
        # Create query object
        query = Query(text=query_text)
        
        # Search for relevant context
        search_results = self.search_engine.search(
            query=query,
            top_k=top_k
        )
        
        # Generate answer
        answer_text = self._generate_answer(query, search_results)

        # Calculate latency
        latency_ms = (time.time() - start_time) * 1000

        # Calculate confidence based on search results
        if not search_results or len(search_results) == 0:
            confidence = 0.0  # No results found
        elif len(search_results) < 3:
            confidence = 0.5  # Few results found
        else:
            confidence = 0.8  # Good number of results

        # Create answer object
        answer = Answer(
            query_id=query.id,
            text=answer_text,
            sources=search_results,
            confidence=confidence,
            latency_ms=latency_ms
        )
        
        logger.info(f"Generated answer in {latency_ms:.0f}ms")
        
        return answer
    
    def _generate_answer(
        self,
        query: Query,
        search_results: List[SearchResult]
    ) -> str:
        """Generate answer from search results.

        Args:
            query: User query
            search_results: Retrieved context

        Returns:
            Generated answer
        """
        # Check if any results were found
        if not search_results or len(search_results) == 0:
            logger.info("No search results found, skipping LLM call")
            return (
                "I apologize, but I couldn't find any relevant information in the knowledge base "
                f"to answer your query: \"{query.text}\". "
                "This could mean:\n\n"
                "• The information hasn't been ingested into the system yet\n"
                "• The query terms don't match any indexed content\n"
                "• The similarity threshold is too strict\n\n"
                "Please try:\n"
                "• Rephrasing your query with different keywords\n"
                "• Using broader or more general terms\n"
                "• Checking if the relevant documents have been uploaded"
            )

        from langchain_openai import ChatOpenAI
        from langchain_core.prompts import ChatPromptTemplate

        logger.info(f"Found {len(search_results)} results, generating answer with LLM")

        # Build context from search results
        context_parts = []
        for i, result in enumerate(search_results[:5], 1):
            # Include speaker name if available
            speaker_info = ""
            if hasattr(result, 'metadata') and result.metadata:
                speaker_name = result.metadata.get('speaker_name')
                logger.info(f"Result {i}: has metadata, speaker_name={speaker_name}")
                if speaker_name:
                    speaker_info = f" - Speaker: {speaker_name}"
            else:
                logger.info(f"Result {i}: No metadata attribute or empty metadata")

            context_parts.append(
                f"[{i}] ({result.modality.value}{speaker_info}): {result.content}"
            )

        context = "\n\n".join(context_parts)

        # Generate answer using LLM
        prompt = ChatPromptTemplate.from_template(
            """Answer the question based on the following context.
            Be concise and cite sources using [1], [2], etc.

            Context:
            {context}

            Question: {question}

            Answer:"""
        )

        llm = ChatOpenAI(
            model=self.settings.openai_model,
            temperature=0.2,
            api_key=self.settings.openai_api_key
        )

        messages = prompt.format_messages(
            context=context,
            question=query.text
        )

        response = llm.invoke(messages)

        return response.content
    
    def close(self) -> None:
        """Close all connections."""
        self.graph_client.close()
        logger.info("Pipeline closed")

