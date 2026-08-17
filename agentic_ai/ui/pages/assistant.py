import datetime
import streamlit as st
from agentic_ai.agents.supervisor_agent import handle_question
from agentic_ai.agents.report_agent import generate_executive_report
from agentic_ai.ui.styles.icons import get_icon_svg
from agentic_ai.ui.components.voice import render_voice_panel
from agentic_ai.ui.components.multimodal import render_incident_attachment_panel
from agentic_ai.ui.components.chat import render_response_card
from agentic_ai.ui.components.health import (
    check_postgres_connection,
    check_gold_schema,
    check_gemini_configuration,
    check_ml_model,
    check_vector_store,
)


def render_assistant_page():
    """Render SaaS Enterprise Copilot Workspace matching production AI copilot standards."""
    is_dark = st.session_state.get("theme_mode", "dark") == "dark"
    card_bg = "#151D2F" if is_dark else "#FFFFFF"
    card_border = "rgba(148,163,184,0.14)" if is_dark else "#E2E8F0"
    text_color = "#F8FAFC" if is_dark else "#0F172A"
    sub_color = "#94A3B8" if is_dark else "#64748B"

    # Initialize Session State
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "show_voice_panel" not in st.session_state:
        st.session_state.show_voice_panel = False
    if "show_attachment_panel" not in st.session_state:
        st.session_state.show_attachment_panel = False

    q_selected = None

    # Real System Health Status Checks
    db_ok = check_postgres_connection()
    gold_ok = check_gold_schema()
    gemini_ok = check_gemini_configuration()
    ml_ok = check_ml_model()
    rag_ok = check_vector_store()

    # Copilot Header & Live Status Bar
    h_col1, h_col2 = st.columns([3, 1])
    with h_col1:
        st.markdown(f"""
            <div class="page-header" style="margin-bottom:0.4rem;">
                <div style="display:flex; align-items:center; gap:10px;">
                    <h1 style="margin:0; font-size:1.6rem; font-weight:800;">UberOps AI</h1>
                    <span style="font-size:0.78rem; font-weight:700; color:#3B82F6; background:rgba(59,130,246,0.12); padding:3px 10px; border-radius:12px; border:1px solid rgba(59,130,246,0.25);">
                        Enterprise Mobility Copilot
                    </span>
                </div>
                <p style="margin-top:4px; font-size:0.85rem; color:{sub_color};">Ask natural language questions across Gold warehouse analytics, operational SOPs, or ML risk scores.</p>
            </div>
        """, unsafe_allow_html=True)

        # Live Backend System Status Pills
        st.markdown(f"""
            <div style="display:flex; align-items:center; gap:8px; margin-bottom:12px; font-size:0.72rem; font-weight:700;">
                <span style="color:{'#10B981' if db_ok else '#EF4444'}; background:{'rgba(16,185,129,0.12)' if db_ok else 'rgba(239,68,68,0.12)'}; padding:2px 8px; border-radius:6px; border:1px solid {'rgba(16,185,129,0.25)' if db_ok else 'rgba(239,68,68,0.25)'};">
                    ● {'Online' if db_ok else 'Offline'}
                </span>
                <span style="color:{'#3B82F6' if gold_ok else '#EF4444'}; background:{'rgba(59,130,246,0.12)' if gold_ok else 'rgba(239,68,68,0.12)'}; padding:2px 8px; border-radius:6px; border:1px solid {'rgba(59,130,246,0.25)' if gold_ok else 'rgba(239,68,68,0.25)'};">
                    Gold {'Ready' if gold_ok else 'Unchecked'}
                </span>
                <span style="color:{'#06B6D4' if rag_ok else '#F59E0B'}; background:{'rgba(6,182,212,0.12)' if rag_ok else 'rgba(245,158,11,0.12)'}; padding:2px 8px; border-radius:6px; border:1px solid {'rgba(6,182,212,0.25)' if rag_ok else 'rgba(245,158,11,0.25)'};">
                    RAG {'Ready' if rag_ok else 'Offline'}
                </span>
                <span style="color:{'#10B981' if ml_ok else '#F59E0B'}; background:{'rgba(16,185,129,0.12)' if ml_ok else 'rgba(245,158,11,0.12)'}; padding:2px 8px; border-radius:6px; border:1px solid {'rgba(16,185,129,0.25)' if ml_ok else 'rgba(245,158,11,0.25)'};">
                    ML {'Ready' if ml_ok else 'Offline'}
                </span>
                <span style="color:{'#8B5CF6' if gemini_ok else '#F59E0B'}; background:{'rgba(139,92,246,0.12)' if gemini_ok else 'rgba(245,158,11,0.12)'}; padding:2px 8px; border-radius:6px; border:1px solid {'rgba(139,92,246,0.25)' if gemini_ok else 'rgba(245,158,11,0.25)'};">
                    Gemini {'Ready' if gemini_ok else 'Missing Key'}
                </span>
            </div>
        """, unsafe_allow_html=True)

    with h_col2:
        st.markdown("<div style='height:14px;'></div>", unsafe_allow_html=True)
        btn_c1, btn_c2 = st.columns(2)
        with btn_c1:
            if st.button("➕ New", key="btn_copilot_new_chat", help="Start new chat session", use_container_width=True):
                st.session_state.messages = []
                st.session_state.show_voice_panel = False
                st.session_state.show_attachment_panel = False
                st.rerun()
        with btn_c2:
            if st.button("🧹 Clear", key="btn_copilot_clear_chat", help="Clear current conversation stream", use_container_width=True):
                st.session_state.messages = []
                st.session_state.show_voice_panel = False
                st.session_state.show_attachment_panel = False
                st.rerun()

    # Compact Quick-Ask Prompt Cards
    if not st.session_state.messages:
        st.markdown(f"""<div style="font-size:0.8rem; font-weight:700; color:{sub_color}; margin-bottom:8px;">SUGGESTED QUESTIONS:</div>""", unsafe_allow_html=True)
        qp1, qp2, qp3, qp4, qp5, qp6 = st.columns(6)

        with qp1:
            if st.button("📊 Executive KPIs\nRevenue • Trips • Fare", key="qp_kpis", use_container_width=True):
                q_selected = "What are the executive KPIs in the Gold warehouse?"
        with qp2:
            if st.button("📈 Revenue Trend\nDaily Growth Trends", key="qp_rev", use_container_width=True):
                q_selected = "Analyse revenue trend over time."
        with qp3:
            if st.button("🏆 Top Drivers\nRevenue Leaderboard", key="qp_drivers", use_container_width=True):
                q_selected = "Show top 5 drivers by revenue."
        with qp4:
            if st.button("⚠️ Driver Risk\nRandomForest Scorer", key="qp_risk", use_container_width=True):
                q_selected = "Which drivers are high risk?"
        with qp5:
            if st.button("📖 Policy Search\nSupport SOP Guidelines", key="qp_sop", use_container_width=True):
                q_selected = "What is the vehicle accident escalation SOP?"
        with qp6:
            if st.button("📸 Incident Photo\nMultimodal Assessment", key="qp_incident", use_container_width=True):
                st.session_state.show_attachment_panel = not st.session_state.get("show_attachment_panel", False)
                st.rerun()

        st.divider()

    # Empty Conversation Welcome Screen
    if not st.session_state.messages:
        st.markdown(f"""
            <div style="text-align:center; padding:2rem 1rem 1.5rem 1rem; background:{card_bg}; border:1px solid {card_border}; border-radius:16px; margin-bottom:1.5rem;">
                {get_icon_svg('Bot', '#3B82F6', 44)}
                <h2 style="font-size:1.35rem; font-weight:800; color:{text_color}; margin:10px 0 4px 0;">Welcome to UberOps AI Enterprise Copilot</h2>
                <p style="font-size:0.88rem; color:{sub_color}; max-width:640px; margin:0 auto 16px auto;">
                    Ask natural language questions across revenue performance, trip metrics, driver ratings, ML underperformance risk, or support policies.
                </p>
            </div>
        """, unsafe_allow_html=True)

    # Render Active Conversation Message Stream
    followup_clicked_query = None

    for idx, msg in enumerate(st.session_state.messages):
        if msg["role"] == "user":
            ts_str = msg.get("timestamp", datetime.datetime.now().strftime("%I:%M %p"))
            st.markdown(f"""
                <div class="ai-user-message" style="display:flex; justify-content:flex-end; margin-bottom:14px;">
                    <div style="background:#2563EB; border-radius:14px; padding:12px 16px; max-width:62%; color:#FFFFFF; box-shadow:0 2px 8px rgba(37,99,235,0.2);">
                        <div style="font-size:0.7rem; font-weight:700; color:rgba(255,255,255,0.85); margin-bottom:4px; display:flex; justify-content:space-between; align-items:center; gap:12px;">
                            <span>YOU</span>
                            <span style="font-weight:500; font-size:0.65rem;">{ts_str}</span>
                        </div>
                        <div style="font-size:0.92rem; font-weight:600; line-height:1.4;">{msg["content"]}</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
        else:
            clicked_f = render_response_card(msg["result"], index=idx)
            if clicked_f:
                followup_clicked_query = clicked_f

    # Compact Optional Tools Area (Voice / Attachment popovers - Occupy 0 vertical space when inactive)
    st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)

    t_col1, t_col2, t_col3 = st.columns([2, 2, 8])
    with t_col1:
        voice_toggle_label = "🎤 Voice Active" if st.session_state.show_voice_panel else "🎤 Voice Mode"
        if st.button(voice_toggle_label, key="btn_toggle_voice_tool", type="primary" if st.session_state.show_voice_panel else "secondary", use_container_width=True):
            st.session_state.show_voice_panel = not st.session_state.show_voice_panel
            st.rerun()

    with t_col2:
        attach_toggle_label = "📸 Image Active" if st.session_state.show_attachment_panel else "＋ Attach Image"
        if st.button(attach_toggle_label, key="btn_toggle_attach_tool", type="primary" if st.session_state.show_attachment_panel else "secondary", use_container_width=True):
            st.session_state.show_attachment_panel = not st.session_state.show_attachment_panel
            st.rerun()

    # Render Voice Panel (Zero vertical space when inactive)
    voice_query = render_voice_panel(is_active=st.session_state.show_voice_panel)

    # Render Incident Attachment Panel (Zero vertical space when inactive)
    render_incident_attachment_panel(is_active=st.session_state.show_attachment_panel)

    # Chat Composer Input Field
    user_input = st.chat_input("Ask about revenue, drivers, policies, risk or operations...")
    question = followup_clicked_query or voice_query or q_selected or user_input

    st.markdown("""
        <div style="font-size:0.72rem; color:#64748B; margin-top:4px; text-align:center;">
            Enter to send • Use 🎤 for voice • Use ＋ for incident image
        </div>
    """, unsafe_allow_html=True)

    if question:
        now_ts = datetime.datetime.now().strftime("%I:%M %p")
        st.session_state.messages.append({"role": "user", "content": question, "timestamp": now_ts})
        st.rerun()

    # Process Unanswered User Question
    if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
        latest_question = st.session_state.messages[-1]["content"]

        # Route-Aware Spinner Messaging
        if "report" in latest_question.lower() and "generate" in latest_question.lower():
            spinner_msg = "Compiling executive PDF/HTML report..."
        elif any(k in latest_question.lower() for k in ("driver", "risk", "underperform")):
            spinner_msg = "Executing RandomForest driver risk model..."
        elif any(k in latest_question.lower() for k in ("sop", "policy", "accident", "guideline")):
            spinner_msg = "Searching policy knowledge base with ChromaDB RAG..."
        elif any(k in latest_question.lower() for k in ("revenue", "kpi", "trip", "fare", "gold")):
            spinner_msg = "Querying Gold warehouse star-schema marts..."
        else:
            spinner_msg = "UberOps Multi-Agent System is reasoning..."

        with st.spinner(spinner_msg):
            try:
                if "report" in latest_question.lower() and "generate" in latest_question.lower():
                    report_res = generate_executive_report()
                    result = {
                        "route": "report_agent",
                        "intent": "generate_report",
                        "routing_reason": "User requested executive report generation",
                        "answer": f"Executive report generated successfully!\n\n- **PDF Path:** `{report_res['pdf_path']}`\n- **HTML Path:** `{report_res['html_path']}`\n- **CSV Path:** `{report_res['csv_path']}`",
                        "trace_steps": ["✓ Report Agent triggered", "✓ Warehouse metrics compiled", "✓ PDF/HTML/CSV exported"],
                        "execution_time_ms": 115.0,
                    }
                else:
                    result = handle_question(latest_question)

                st.session_state.messages.append({"role": "assistant", "result": result})
                st.rerun()
            except Exception as ex:
                st.error(f"Execution Error: {ex}")
