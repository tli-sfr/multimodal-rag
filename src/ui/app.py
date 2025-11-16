"""Streamlit UI for Multimodal RAG System."""

import sys
from pathlib import Path

# Add project root to path for absolute imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import streamlit as st
import tempfile
import os

from loguru import logger

# Configure page
st.set_page_config(
    page_title="Multimodal Enterprise RAG",
    page_icon="🔍",
    layout="wide",
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': None
    }
)

# Hide the Deploy button and Main Menu
st.markdown(
    """
    <style>
    .stAppDeployButton {
        display: none;
    }
    .stMainMenu {
        display: none;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Import pipeline (with caching)
@st.cache_resource(show_spinner=False)
def get_pipeline():
    """Get or create pipeline instance."""
    try:
        from src.pipeline import MultimodalRAGPipeline
        return MultimodalRAGPipeline()
    except Exception as e:
        logger.error(f"Failed to initialize pipeline: {e}")
        raise


def main():
    """Main Streamlit application."""
    
    st.title("🔍 Multimodal Enterprise RAG System")
    st.markdown("---")
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("⚙️ Configuration")

        top_k = st.slider(
            "Number of results",
            min_value=1,
            max_value=50,
            value=10
        )

        st.markdown("---")
        st.header("📊 System Status")

        try:
            with st.spinner("Initializing..."):
                pipeline = get_pipeline()
            st.success("✅ Initialized")
        except Exception as e:
            error_msg = str(e)
            st.error(f"❌ Error: {error_msg}")

            # Provide helpful error messages
            if "Connection refused" in error_msg or "61" in error_msg:
                st.warning("⚠️ **Docker services not running**")
                st.info("""
                **To fix this:**

                1. Start Docker Desktop
                2. Run in terminal:
                   ```bash
                   docker-compose up -d
                   ```
                3. Wait 10-20 seconds for services to start
                4. Refresh this page

                **Services needed:**
                - Qdrant (vector database) - port 6333
                - Neo4j (graph database) - port 7687
                """)
            elif "langchain" in error_msg.lower():
                st.info("""
                **Import error detected.**

                Run in terminal:
                ```bash
                pip install -e .
                ```
                Then restart Streamlit.
                """)

            st.markdown("---")
            st.markdown("**Note:** You can still view the UI, but functionality will be limited until services are running.")
            return

        st.markdown("---")

        # Cache control at bottom
        if st.button("🔄 Clear Cache"):
            st.cache_resource.clear()
            st.success("Cache cleared! Will reload on next query.")
            st.rerun()
    
    # Main content area with tabs
    tab1, tab2, tab3 = st.tabs(["📤 Upload", "🔍 Query", "📊 Browse Data"])
    
    # Tab 1: File Upload
    with tab1:
        st.header("Upload Documents")

        # Initialize session state for uploaded files
        if 'uploaded_files' not in st.session_state:
            st.session_state.uploaded_files = None

        uploaded_files = st.file_uploader(
            "Upload files (PDF, TXT, Images, Audio, Video)",
            accept_multiple_files=True,
            type=['pdf', 'txt', 'docx', 'jpg', 'jpeg', 'png', 'mp3', 'wav', 'mp4', 'avi'],
            key='file_uploader'
        )

        # Update session state when new files are uploaded
        if uploaded_files:
            st.session_state.uploaded_files = uploaded_files

        if st.session_state.uploaded_files:
            if st.button("Process Files"):
                with st.spinner("Processing files..."):
                    for uploaded_file in st.session_state.uploaded_files:
                        try:
                            # Save to temp file
                            with tempfile.NamedTemporaryFile(
                                delete=False,
                                suffix=Path(uploaded_file.name).suffix
                            ) as tmp_file:
                                tmp_file.write(uploaded_file.read())
                                tmp_path = Path(tmp_file.name)

                            # Ingest file with original filename and upload source
                            # Pass metadata through kwargs
                            documents = pipeline.ingest_documents(
                                tmp_path,
                                original_filename=uploaded_file.name,
                                upload_source="ui"
                            )

                            # Clean up
                            os.unlink(tmp_path)

                            if documents:
                                st.success(f"✅ Processed: {uploaded_file.name}")
                            else:
                                st.warning(f"⚠️ Failed: {uploaded_file.name}")

                        except Exception as e:
                            st.error(f"❌ Error processing {uploaded_file.name}: {e}")

                    # Clear uploaded files after processing
                    st.session_state.uploaded_files = None
                    st.rerun()
    
    # Tab 2: Query Interface
    with tab2:
        st.header("Query the Knowledge Base")
        
        query_text = st.text_input(
            "Enter your question:",
            placeholder="What information are you looking for?"
        )
        
        if st.button("Search") and query_text:
            with st.spinner("Searching..."):
                try:
                    # Execute query
                    answer = pipeline.query(query_text, top_k=top_k)
                    
                    # Display answer
                    st.markdown("### 💡 Answer")
                    st.markdown(answer.text)
                    
                    # Display metadata
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Confidence", f"{answer.confidence:.2%}")
                    with col2:
                        st.metric("Latency", f"{answer.latency_ms:.0f}ms")
                    with col3:
                        st.metric("Sources", len(answer.sources))
                    
                    # Display sources
                    st.markdown("### 📚 Sources")
                    for i, source in enumerate(answer.sources, 1):
                        # Get metadata from source
                        upload_source = source.metadata.get('upload_source', None)
                        original_filename = source.metadata.get('original_filename', None)
                        speaker_name = source.metadata.get('speaker_name', None)
                        tags = source.metadata.get('tags', [])
                        source_field = source.metadata.get('source', None)
                        modality = source.modality.value

                        # Determine status label based on upload source
                        if upload_source == 'ui':
                            status_label = "Uploaded"
                        elif upload_source == 'script':
                            status_label = "Pre-loaded"
                        else:
                            # If no upload_source, try to use original_filename or source
                            if original_filename:
                                status_label = original_filename
                            elif source_field:
                                # Check if source looks like a file path
                                if '/' in str(source_field) or '\\' in str(source_field):
                                    # Extract just the filename from the full path
                                    status_label = Path(str(source_field)).name
                                else:
                                    # Use source as-is (e.g., "mock_data_andrew_ng_pdf")
                                    status_label = str(source_field)
                            else:
                                status_label = "Unknown"

                        # Build title with metadata (no icon)
                        title_parts = [f"Source {i}"]
                        if speaker_name:
                            title_parts.append(f"👤 {speaker_name}")
                        if original_filename:
                            title_parts.append(f"📄 {original_filename}")
                        else:
                            title_parts.append(f"📄 {modality}")
                        title_parts.append(f"[{status_label}]")

                        # Check if this is mock data
                        is_mock_data = (isinstance(tags, list) and 'mock_data' in tags) or (isinstance(tags, str) and tags == 'mock_data')

                        # Add mock data tag if present
                        if is_mock_data:
                            title_parts.append("(mock data)")

                        # Add score
                        title_parts.append(f"Score: {source.score:.3f}")

                        title = " - ".join(title_parts)

                        with st.expander(title):
                            st.text(source.content)
                            st.json(source.metadata)
                
                except Exception as e:
                    st.error(f"❌ Query failed: {e}")
                    logger.error(f"Query error: {e}")
    
    # Tab 3: Browse Data
    with tab3:
        st.header("Browse Existing Data")

        try:
            # Get stats from databases
            from src.vector_store.qdrant_client import QdrantVectorStore
            from src.graph.neo4j_client import Neo4jClient

            qdrant_client = QdrantVectorStore()
            neo4j_client = Neo4jClient()

            # Qdrant stats
            st.subheader("📦 Vector Store (Qdrant)")
            try:
                info = qdrant_client.client.get_collection('multimodal_chunks')
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Total Chunks", info.points_count)
                with col2:
                    st.metric("Vector Dimensions", info.config.params.vectors.size)

                # Show uploaded chunks
                if info.points_count > 0:
                    st.markdown("**Uploaded Chunks:**")

                    # DEBUG: Show we're using the new code
                    st.caption("🔧 Debug: Using updated chunk display logic v2")

                    result = qdrant_client.client.scroll(
                        collection_name='multimodal_chunks',
                        limit=50,
                        with_payload=True,
                        with_vectors=False
                    )
                    points, _ = result

                    for i, point in enumerate(points, 1):
                        # Get metadata - check both top level and nested metadata
                        payload = point.payload
                        metadata = payload.get('metadata', {})

                        # Try to get from metadata first, then fall back to top level
                        modality = metadata.get('modality') or payload.get('modality', 'N/A')
                        upload_source = metadata.get('upload_source') or payload.get('upload_source', None)
                        original_filename = metadata.get('original_filename') or payload.get('original_filename', None)
                        source = metadata.get('source') or payload.get('source', None)
                        speaker_name = metadata.get('speaker_name') or payload.get('speaker_name', None)
                        tags = metadata.get('tags') or payload.get('tags', [])

                        # Determine status label based on upload source
                        if upload_source == 'ui':
                            status_label = "Uploaded"
                        elif upload_source == 'script':
                            status_label = "Pre-loaded"
                        else:
                            # If no upload_source, try to use original_filename or source
                            if original_filename:
                                status_label = original_filename
                            elif source:
                                # Check if source looks like a file path
                                if '/' in str(source) or '\\' in str(source):
                                    # Extract just the filename from the full path
                                    status_label = Path(str(source)).name
                                else:
                                    # Use source as-is (e.g., "mock_data_andrew_ng_pdf")
                                    status_label = str(source)
                            else:
                                status_label = "Unknown"

                        # Build title with metadata (no icon)
                        title_parts = [f"Chunk {i}"]
                        if speaker_name:
                            title_parts.append(f"👤 {speaker_name}")
                        if original_filename:
                            title_parts.append(f"📄 {original_filename}")
                        else:
                            title_parts.append(f"📄 {modality}")
                        title_parts.append(f"[{status_label}]")

                        # Check if this is mock data
                        is_mock_data = (isinstance(tags, list) and 'mock_data' in tags) or (isinstance(tags, str) and tags == 'mock_data')

                        # Add mock data tag if present (tags is a list)
                        if is_mock_data:
                            title_parts.append("(mock data)")

                        title = " - ".join(title_parts)

                        with st.expander(title):
                            # DEBUG: Show what we detected
                            st.caption(f"🔍 Debug: source='{source}', upload_source='{upload_source}', tags={tags}, status_label='{status_label}'")

                            # Show content preview
                            st.text(point.payload.get('content', '')[:500])

                            # Show metadata (excluding content)
                            metadata_display = {k: v for k, v in point.payload.items() if k != 'content'}
                            st.json(metadata_display)
                else:
                    st.warning("No chunks in vector store. Upload documents or run mock data script.")
            except Exception as e:
                st.error(f"Error accessing Qdrant: {e}")

            st.markdown("---")

            # Neo4j stats
            st.subheader("🕸️ Knowledge Graph (Neo4j)")
            try:
                with neo4j_client.driver.session() as session:
                    # Count entities
                    result = session.run("MATCH (e:Entity) RETURN count(e) as count")
                    entity_count = result.single()["count"]

                    # Count relationships
                    result = session.run("MATCH ()-[r]->() RETURN count(r) as count")
                    rel_count = result.single()["count"]

                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Total Entities", entity_count)
                    with col2:
                        st.metric("Total Relationships", rel_count)

                    # Show sample entities
                    if entity_count > 0:
                        st.markdown("**Sample Entities:**")
                        result = session.run("""
                            MATCH (e:Entity)
                            RETURN e.name as name, e.type as type, e.source_modality as modality
                            LIMIT 20
                        """)

                        entities_data = []
                        for record in result:
                            entities_data.append({
                                "Name": record["name"],
                                "Type": record["type"],
                                "Modality": record["modality"]
                            })

                        st.dataframe(entities_data, use_container_width=True)

                        st.info("💡 Open Neo4j Browser at http://localhost:7474 to visualize the knowledge graph")
                    else:
                        st.warning("No entities in knowledge graph. Upload documents or run mock data script.")

                neo4j_client.close()
            except Exception as e:
                st.error(f"Error accessing Neo4j: {e}")

        except Exception as e:
            st.error(f"Error loading data: {e}")

     
    
    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center'>
            <p>Multimodal Enterprise RAG System v1.0.0</p>
             
        </div>
        """,
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()

