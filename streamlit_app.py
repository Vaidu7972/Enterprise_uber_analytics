import json
import pandas as pd
import streamlit as st
from datetime import datetime

from agentic_ai.agents.supervisor_agent import handle_question
from agentic_ai.tools.sql_tool import get_gold_schema, execute_read_only_query
from agentic_ai.rag.vector_store import search_support_docs, collection
from agentic_ai.rag.build_index import build_rag_index
from agentic_ai.tools.ml_tool import predict_driver_risk
from agentic_ai.tools.action_tools import create_training_recommendation, save_investigation
from agentic_ai.memory.persistent_memory import get_recent_audit_logs
from agentic_ai.reports.report_generator import generate_pdf_report
from agentic_ai.multimodal.incident_analyzer import analyze_incident_multimodal
from agentic_ai.config.agent_config import MODEL_META_PATH, MODEL_FILE_PATH, BASE_DIR

# =========================================================
# PAGE CONFIGURATION
# =========================================================
st.set_page_config(
    page_title="UberOps AI — Enterprise Data Intelligence",
    page_icon="🚕",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =========================================================
# CUSTOM UI STYLING (DARK ENTERPRISE DESIGN)
# =========================================================
st.markdown("""
    <style>
    .block-container {
        max-width: 1350px;
        padding-top: 1.5rem;
        padding-bottom: 5rem;
    }
    .hero {
        padding: 2rem 2.5rem;
        border-radius: 20px;
        margin-bottom: 1.5rem;
        background: linear-gradient(135deg, rgba(124, 58, 237, 0.25), rgba(37, 99, 235, 0.15));
        border: 1px solid rgba(148, 163, 184, 0.2);
    }
    .hero h1 {
        font-size: 2.5rem;
        font-weight: 800;
        margin-bottom: 0.3rem;
        background: linear-gradient(90deg, #A78BFA, #60A5FA);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .hero p {
        font-size: 1.05rem;
        color: #94A3B8;
        margin-bottom: 0;
    }
    .route-badge {
        display: inline-block;
        padding: 0.35rem 0.85rem;
        border-radius: 999px;
        font-size: 0.82rem;
        font-weight: 700;
        margin-bottom: 0.8rem;
        border: 1px solid rgba(148, 163, 184, 0.3);
        background: rgba(124, 58, 237, 0.18);
        color: #C084FC;
    }
    .status-card {
        border: 1px solid rgba(148, 163, 184, 0.15);
        border-radius: 12px;
        padding: 0.75rem 0.9rem;
        margin-bottom: 0.5rem;
        background: rgba(30, 41, 59, 0.4);
    }
    .small-text {
        font-size: 0.82rem;
        color: #94A3B8;
    }
    .metric-box {
        background: rgba(30, 41, 59, 0.6);
        border: 1px solid rgba(148, 163, 184, 0.2);
        border-radius: 12px;
        padding: 1rem;
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

# =========================================================
# SESSION STATE
# =========================================================
if "messages" not in st.session_state:
    st.session_state.messages = []
if "last_result" not in st.session_state:
    st.session_state.last_result = None

# =========================================================
# ROUTE INFORMATION
# =========================================================
ROUTE_LABELS = {
    "general": "🧠 General AI",
    "data_agent": "📊 Data Agent (PostgreSQL Gold)",
    "support_agent": "📚 Support Agent (RAG)",
    "ml_agent": "🤖 ML Agent (Risk Model)",
    "multi_agent": "🕸️ LangGraph Multi-Agent",
}

def get_route_label(route):
    return ROUTE_LABELS.get(route, route.replace("_", " ").title())

# =========================================================
# SIDEBAR
# =========================================================
with st.sidebar:
    st.title("🚕 UberOps AI")
    st.caption("Enterprise Agentic Data Intelligence & Support Platform")
    st.divider()

    st.subheader("System Status")
    st.markdown("""
        <div class="status-card">
            🧠 <b>Gemini LLM</b>: <span style="color:#4ADE80;">Connected</span>
        </div>
        <div class="status-card">
            📊 <b>PostgreSQL Gold</b>: <span style="color:#4ADE80;">Connected</span>
        </div>
        <div class="status-card">
            📚 <b>ChromaDB Vector Store</b>: <span style="color:#4ADE80;">Indexed</span>
        </div>
        <div class="status-card">
            🤖 <b>Predictive ML Model</b>: <span style="color:#4ADE80;">Trained</span>
        </div>
        <div class="status-card">
            🕸️ <b>LangGraph Orchestrator</b>: <span style="color:#4ADE80;">Active</span>
        </div>
    """, unsafe_allow_html=True)

    st.divider()
    st.subheader("Sample Prompts")
    sample_questions = [
        "What is total revenue in the warehouse?",
        "Show top 5 drivers by revenue.",
        "What documents are required for driver onboarding?",
        "What should a driver do after an accident?",
        "Which drivers are likely to underperform?",
        "Why is driver D101 underperforming, is this likely to continue, and what training should be recommended?",
    ]

    selected_sample = None
    for q in sample_questions:
        if st.button(q, use_container_width=True):
            selected_sample = q

    st.divider()
    if st.button("🔄 Rebuild RAG Index", use_container_width=True):
        with st.spinner("Indexing support documents into ChromaDB..."):
            build_rag_index()
            st.success("RAG Index successfully rebuilt!")

    if st.button("🗑️ Clear Chat History", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# =========================================================
# MAIN HERO HEADER
# =========================================================
st.markdown("""
    <div class="hero">
        <h1>🚕 UberOps AI</h1>
        <p>Enterprise Data Engineering + Warehouse Analytics + RAG Support Knowledge + Predictive ML + LangGraph Multi-Agent System</p>
    </div>
""", unsafe_allow_html=True)

# =========================================================
# ENTERPRISE NAVIGATION TABS
# =========================================================
tab_ai, tab_data, tab_rag, tab_ml, tab_investigations, tab_reports, tab_arch = st.tabs([
    "🤖 AI Assistant",
    "📊 Data Intelligence",
    "📚 Support Knowledge (RAG)",
    "🤖 ML Intelligence",
    "🕵️ Investigations & Actions",
    "📄 Report Generator",
    "⚙️ System Architecture"
])

# =========================================================
# TAB 1: AI ASSISTANT (MAIN CHAT)
# =========================================================
with tab_ai:
    st.caption("Ask questions across historical analytics, driver risk predictions, support policy SOPs, or multi-agent investigations.")
    
    # Display chat history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            if msg["role"] == "user":
                st.markdown(msg["content"])
            else:
                res = msg["result"]
                st.markdown(f'<div class="route-badge">{get_route_label(res["route"])}</div>', unsafe_allow_html=True)
                st.markdown(res["answer"])

                if res.get("sql"):
                    with st.expander("🧾 View Generated SQL"):
                        st.code(res["sql"], language="sql")

                if res.get("data") is not None and isinstance(res["data"], pd.DataFrame) and not res["data"].empty:
                    with st.expander("🗄️ View PostgreSQL Result Dataframe"):
                        st.dataframe(res["data"], use_container_width=True, hide_index=True)

                if res.get("sources"):
                    with st.expander("📚 Grounded Support Sources"):
                        for s in res["sources"]:
                            st.write(f"• **Source:** `{s['source']}` (Page {s['page']})")

    # Input chat
    user_input = st.chat_input("Ask UberOps AI about revenue, drivers, policies, risk predictions...")
    question = selected_sample if selected_sample else user_input

    if question:
        st.session_state.messages.append({"role": "user", "content": question})
        with st.chat_message("user"):
            st.markdown(question)

        with st.chat_message("assistant"):
            with st.spinner("UberOps Multi-Agent System is reasoning and executing tools..."):
                try:
                    result = handle_question(question)
                    st.session_state.last_result = result
                    
                    st.markdown(f'<div class="route-badge">{get_route_label(result["route"])}</div>', unsafe_allow_html=True)
                    st.markdown(result["answer"])

                    if result.get("sql"):
                        with st.expander("🧾 View Generated SQL"):
                            st.code(result["sql"], language="sql")

                    if result.get("data") is not None and isinstance(result["data"], pd.DataFrame) and not result["data"].empty:
                        with st.expander("🗄️ View PostgreSQL Result Dataframe", expanded=True):
                            st.dataframe(result["data"], use_container_width=True, hide_index=True)

                    if result.get("sources"):
                        with st.expander("📚 Grounded Support Sources"):
                            for s in result["sources"]:
                                st.write(f"• **Source:** `{s['source']}` (Page {s['page']})")

                    # Human-In-The-Loop Approval Widget for sensitive actions
                    if result.get("approval_required"):
                        st.warning("⚠️ Manager Action Approval Required")
                        c1, c2 = st.columns(2)
                        if c1.button("✅ Approve Recommended Action", key="approve_btn"):
                            recs = result.get("recommendations", {})
                            action_type = recs.get("action_type", "ASSIGN_TRAINING")
                            target = recs.get("target_entity", "D101")
                            res_action = create_training_recommendation(driver_id=target, driver_name=target, approved_by="Manager")
                            st.success(f"Action Approved & Persisted! Details: {res_action['details']}")
                        if c2.button("❌ Reject Action", key="reject_btn"):
                            st.info("Action Rejected by Manager.")

                    st.session_state.messages.append({"role": "assistant", "result": result})
                except Exception as err:
                    err_str = str(err)
                    if "429" in err_str or "RESOURCE_EXHAUSTED" in err_str:
                        st.error("⏳ **Gemini API Rate Limit Reached** — The free-tier API quota is temporarily busy. Please wait 10 seconds and try your request again.")
                    else:
                        st.error(f"⚠️ UberOps AI Error: {err_str}")


# =========================================================
# TAB 2: DATA INTELLIGENCE (GOLD WAREHOUSE EXPLORER)
# =========================================================
with tab_data:
    st.header("📊 PostgreSQL Gold Data Warehouse")
    st.caption("Direct read-only interface to PostgreSQL Gold Schema tables & analytics marts.")

    try:
        schema_text = get_gold_schema()
        with st.expander("📖 View Live Gold Schema Structure"):
            st.code(schema_text, language="yaml")
    except Exception as e:
        st.error(f"Could not load schema: {e}")

    col_q1, col_q2 = st.columns([3, 1])
    preset_query = col_q1.selectbox("Select Sample Analytics Query", [
        "SELECT * FROM gold.driver_performance_mart ORDER BY total_revenue DESC LIMIT 10;",
        "SELECT * FROM gold.kpi_summary;",
        "SELECT * FROM gold.revenue_mart ORDER BY date_key DESC LIMIT 15;",
        "SELECT rating, COUNT(*) AS driver_count FROM gold.dim_driver GROUP BY rating ORDER BY rating DESC;",
        "SELECT * FROM gold.fact_trip LIMIT 20;"
    ])

    custom_sql = st.text_area("SQL Query (Read-Only Gold Schema)", value=preset_query, height=100)

    if st.button("▶️ Execute Query"):
        try:
            df_res = execute_read_only_query(custom_sql)
            st.success(f"Executed successfully! Retreived {len(df_res)} rows.")
            st.dataframe(df_res, use_container_width=True, hide_index=True)

            # Chart rendering
            num_cols = df_res.select_dtypes(include="number").columns.tolist()
            cat_cols = df_res.select_dtypes(include="object").columns.tolist()
            if num_cols and cat_cols and len(df_res) >= 2:
                st.subheader("📈 Visualization")
                st.bar_chart(df_res.set_index(cat_cols[0])[num_cols[0]])
        except Exception as err:
            st.error(f"SQL Execution Error: {err}")

# =========================================================
# TAB 3: SUPPORT KNOWLEDGE (HYBRID RAG)
# =========================================================
with tab_rag:
    st.header("📚 Support Knowledge & Hybrid RAG Playground")
    st.caption("Search vector store using Gemini Embeddings + Keyword Matching.")

    search_term = st.text_input("Enter Policy / SOP Search Query", value="What should a driver do after an accident?")
    top_k_val = st.slider("Top Chunks (k)", min_value=1, max_value=8, value=4)

    if st.button("🔍 Search RAG Index"):
        try:
            chunks = search_support_docs(search_term, top_k=top_k_val)
            st.success(f"Retrieved {len(chunks)} relevant chunks from ChromaDB vector store.")
            for idx, c in enumerate(chunks, 1):
                with st.expander(f"Chunk #{idx} — Source: {c['source']} (Page {c['page']}) | Hybrid Score: {c.get('hybrid_score', 0):.4f}"):
                    st.write(f"**Distance:** {c['distance']:.4f} | **Semantic Score:** {c.get('semantic_score', 0):.4f} | **Keyword Score:** {c.get('keyword_score', 0):.4f}")
                    st.info(c["text"])
        except Exception as ex:
            st.error(f"RAG Retrieval Error: {ex}")

# =========================================================
# TAB 4: ML INTELLIGENCE (DRIVER RISK PREDICTION)
# =========================================================
with tab_ml:
    st.header("🤖 Predictive Machine Learning Engine")
    st.caption("RandomForest Driver Underperformance Risk Assessment Model.")

    try:
        batch_ml = predict_driver_risk()
        if batch_ml.get("found"):
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Scored Drivers", batch_ml.get("total_drivers_scored"))
            m2.metric("High Risk Drivers", batch_ml.get("high_risk_count"))
            m3.metric("Medium Risk Drivers", batch_ml.get("medium_risk_count"))
            m4.metric("Low Risk Drivers", batch_ml.get("low_risk_count"))

            st.subheader("⚠️ Top High-Risk Drivers")
            df_high = pd.DataFrame(batch_ml.get("top_high_risk_drivers", []))
            st.dataframe(df_high, use_container_width=True, hide_index=True)

            meta = batch_ml.get("model_info", {})
            if meta.get("importances"):
                st.subheader("🎯 Model Feature Importances")
                st.bar_chart(pd.Series(meta["importances"]))

    except Exception as ex_ml:
        st.error(f"ML Model Error: {ex_ml}")

# =========================================================
# TAB 5: INVESTIGATIONS & ACTIONS
# =========================================================
with tab_investigations:
    st.header("🕵️ Saved Multi-Agent Investigations & Action Logs")
    st.caption("Persistent record of multi-agent investigations and manager approval history.")

    try:
        audit_logs = get_recent_audit_logs()
        if audit_logs:
            st.subheader("📜 Recent Agent Audit Log History")
            st.dataframe(pd.DataFrame(audit_logs), use_container_width=True, hide_index=True)
        else:
            st.info("No audit entries logged yet.")
    except Exception as ex_aud:
        st.error(f"Could not load audit logs: {ex_aud}")

# =========================================================
# TAB 6: REPORT GENERATOR
# =========================================================
with tab_reports:
    st.header("📄 Investigation Report Generator")
    st.caption("Export formal executive PDF & CSV reports for management review.")

    if st.session_state.last_result:
        st.success("Last active investigation ready for report compilation!")
        st.json({
            "route": st.session_state.last_result.get("route"),
            "intent": st.session_state.last_result.get("intent"),
            "approval_required": st.session_state.last_result.get("approval_required")
        })

        if st.button("📥 Generate Executive PDF Report"):
            try:
                pdf_path = generate_pdf_report(st.session_state.last_result)
                st.success(f"PDF Report generated successfully: {pdf_path}")
                with open(pdf_path, "rb") as f:
                    st.download_button("⬇️ Download PDF Investigation Report", data=f.read(), file_name="UberOps_Executive_Report.pdf", mime="application/pdf")
            except Exception as ex_pdf:
                st.error(f"PDF Generation Error: {ex_pdf}")
    else:
        st.info("Run an AI investigation in the 'AI Assistant' tab first to generate a report.")

# =========================================================
# TAB 7: SYSTEM ARCHITECTURE
# =========================================================
with tab_arch:
    st.header("⚙️ System Architecture & Workflow")
    st.markdown("""
    ```text
                         USER / MANAGER
                               │
                               ▼
                        STREAMLIT UI
                               │
                               ▼
                   LANGGRAPH SUPERVISOR AGENT
                               │
                      Intent Classification
                               │
         ┌─────────────────────┼─────────────────────┐
         │                     │                     │
         ▼                     ▼                     ▼
    GENERAL AI             DATA AGENT          SUPPORT AGENT
         │                     │                     │
    Gemini 3.6 Flash       SQL Tool              RAG Engine
                               │                     │
                               ▼                     ▼
                        PostgreSQL Gold          ChromaDB
                               │                     │
                               └──────────┬──────────┘
                                          ▼
                                       ML AGENT
                                          │
                                Random Forest Model
                                          │
                                          ▼
                                   INSIGHT ENGINE
                                          │
                                  RECOMMENDATION ENGINE
                                          │
                                HUMAN-IN-THE-LOOP APPROVAL
                                          │
                                          ▼
                               Persisted Audit Log & Reports
    ```
    """)