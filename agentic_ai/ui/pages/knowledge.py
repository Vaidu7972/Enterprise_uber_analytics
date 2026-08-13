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
            <p>Manage and search embedded support policies, driver SOPs, and onboarding documentation in ChromaDB.</p>
        </div>
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        render_kpi_card("Vector Chunks", f"{collection.count()}", "BookOpen", "ChromaDB Collection", "#3B82F6")
    with c2:
        render_kpi_card("Collection Name", "uberops_docs", "Database", "Vector Store Identifier", "#10B981")
    with c3:
        render_kpi_card("Support Path", "data/support_docs", "FileText", "Source Documents", "#F59E0B")

    st.divider()

    st.markdown(f"""<div class="saas-card-title">{get_icon_svg('Search', '#3B82F6', 18)} Hybrid Vector Search Playground</div>""", unsafe_allow_html=True)
    search_query = st.text_input("Enter Search Query", "What is the policy for accident response?")
    top_k = st.slider("Top Chunks (k)", 1, 8, 4)

    if st.button("Execute Hybrid Search"):
        with st.spinner("Searching ChromaDB Vector Collection..."):
            chunks = search_support_docs(search_query, top_k=top_k)
            for idx, c in enumerate(chunks, 1):
                with st.expander(f"Chunk #{idx} — Source: {c['source']} (Page {c['page']}) | Score: {c.get('hybrid_score', 0):.4f}"):
                    st.write(f"**Distance:** {c['distance']:.4f} | **Semantic Score:** {c.get('semantic_score', 0):.4f} | **Keyword Score:** {c.get('keyword_score', 0):.4f}")
                    st.info(c["text"])

    st.divider()

    st.markdown(f"""<div class="saas-card-title">{get_icon_svg('RefreshCw', '#8B5CF6', 18)} Index Management</div>""", unsafe_allow_html=True)
    if st.button("Rebuild RAG Vector Index"):
        with st.spinner("Rebuilding document embeddings in ChromaDB..."):
            build_rag_index()
            st.success("RAG Index rebuilt successfully!")
