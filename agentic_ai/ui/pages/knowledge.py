import streamlit as st
from agentic_ai.rag.vector_store import search_support_docs, collection
from agentic_ai.rag.build_index import build_rag_index
from agentic_ai.ui.styles.icons import get_icon_svg
from agentic_ai.ui.components.cards import render_kpi_card

def render_knowledge_page():
    """Render SaaS Support Knowledge Center (RAG) Page."""
    st.markdown("""
        <div class="page-header">
            <h1>Knowledge Center (RAG)</h1>
            <p>Search and manage embedded support policies, driver SOPs, and onboarding documentation in ChromaDB.</p>
        </div>
    """, unsafe_allow_html=True)

    chunk_count = collection.count() if collection else 0

    c1, c2, c3 = st.columns(3)
    with c1:
        render_kpi_card("Vector Chunks", f"{chunk_count:,}", "BookOpen", "ChromaDB Collection", "#3B82F6")
    with c2:
        render_kpi_card("Collection Name", "uberops_docs", "Database", "Vector Store Identifier", "#10B981")
    with c3:
        render_kpi_card("Support Path", "data/support_docs", "FileText", "Source Document Root", "#F59E0B")

    st.divider()

    st.markdown(f"""<div class="saas-card-title">{get_icon_svg('Search', '#3B82F6', 18)} Hybrid Vector & Keyword Search Playground</div>""", unsafe_allow_html=True)
    
    q_col, k_col = st.columns([4, 1])
    with q_col:
        search_query = st.text_input("Enter Policy Search Query", "What is the policy for accident response and vehicle damage?", key="rag_search_input")
    with k_col:
        top_k = st.slider("Top Chunks (k)", 1, 8, 4, key="rag_top_k")

    if st.button("Execute Hybrid Search", key="btn_run_rag_search", type="primary"):
        with st.spinner("Searching ChromaDB Vector Store with Hybrid Scoring..."):
            chunks = search_support_docs(search_query, top_k=top_k)
            if chunks:
                st.success(f"Retrieved {len(chunks)} relevant document chunks.")
                for idx, c in enumerate(chunks, 1):
                    source_name = c.get('source', 'Unknown')
                    page_num = c.get('page', 1)
                    hybrid_score = c.get('hybrid_score', 0)
                    sem_score = c.get('semantic_score', 0)
                    kw_score = c.get('keyword_score', 0)
                    dist_val = c.get('distance', 0)

                    with st.expander(f"Chunk #{idx} — Source: {source_name} (Page {page_num}) | Hybrid Score: {hybrid_score:.4f}"):
                        st.markdown(
                            f"**Distance:** `{dist_val:.4f}` | **Semantic Score:** `{sem_score:.4f}` | **Keyword Score:** `{kw_score:.4f}`"
                        )
                        st.info(c.get("text", ""))
            else:
                st.warning("No matching document chunks found for the query.")

    st.divider()

    st.markdown(f"""<div class="saas-card-title">{get_icon_svg('RefreshCw', '#8B5CF6', 18)} Vector Index Management</div>""", unsafe_allow_html=True)
    if st.button("Rebuild RAG Vector Index", key="btn_rebuild_rag"):
        with st.spinner("Rebuilding document embeddings in ChromaDB vector store..."):
            build_rag_index()
            st.success("RAG Index rebuilt successfully!")
