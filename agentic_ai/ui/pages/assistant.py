import streamlit as st
from agentic_ai.agents.supervisor_agent import handle_question
from agentic_ai.agents.report_agent import generate_executive_report
from agentic_ai.ui.styles.icons import get_icon_svg
from agentic_ai.ui.components.cards import render_starter_card
from agentic_ai.ui.components.voice import render_voice_interface
from agentic_ai.ui.components.chat import render_response_card


def render_assistant_page():
    """Render AI Assistant Workspace matching SaaS product standards."""
    st.markdown("""
        <div class="page-header">
            <h1>AI Assistant Workspace</h1>
            <p>Ask questions across enterprise mobility analytics, operational policies and predictive intelligence.</p>
        </div>
    """, unsafe_allow_html=True)

    # Initialize Session State
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Container Max Width (950px - 1100px)
    main_container = st.container()

    with main_container:
        is_dark = st.session_state.get("theme_mode", "dark") == "dark"
        title_color = "#F8FAFC" if is_dark else "#0F172A"
        sub_color = "#94A3B8" if is_dark else "#64748B"

        # Starter Cards Grid (Empty State)
        if not st.session_state.messages:
            st.markdown(f"""
                <div style="text-align:center; padding:2rem 0 1.5rem 0;">
                    {get_icon_svg('Bot', '#3B82F6', 42)}
                    <h2 style="font-size:1.5rem; font-weight:800; color:{title_color}; margin:10px 0 4px 0;">Welcome to UberOps AI</h2>
                    <p style="font-size:0.95rem; color:{sub_color};">Ask questions across revenue, trips, driver performance, support SOPs, or risk predictions.</p>
                </div>
            """, unsafe_allow_html=True)

            sc1, sc2, sc3 = st.columns(3)
            q_selected = None

            with sc1:
                if st.button("📈 Executive KPIs\nRetrieve revenue, trip counts & avg fare.", key="sc_kpi", use_container_width=True):
                    q_selected = "What are the executive KPIs in the Gold warehouse?"

                st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
                if st.button("📅 Weekend Analysis\nCompare weekday vs weekend revenue.", key="sc_wkd", use_container_width=True):
                    q_selected = "Compare weekday vs weekend performance."

            with sc2:
                if st.button("📊 Revenue Trend\nDaily revenue variance & trip patterns.", key="sc_rev", use_container_width=True):
                    q_selected = "Analyse revenue trend over time."

                st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
                if st.button("👥 Driver Analysis\nIndividual driver rating & revenue.", key="sc_drv_an", use_container_width=True):
                    q_selected = "Show driver performance summary."

            with sc3:
                if st.button("🏆 Top Drivers\nHighest revenue generating drivers.", key="sc_top", use_container_width=True):
                    q_selected = "Show top 5 drivers by revenue."

                st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
                if st.button("📄 Generate Report\nCompile PDF, HTML & CSV reports.", key="sc_rep", use_container_width=True):
                    q_selected = "Generate Executive Performance Report"

            st.divider()

        # Voice Assistant Recorder & Player Component
        voice_query = render_voice_interface()

        # Multimodal Incident Upload Expander
        with st.expander("📸 Vehicle Incident & Damage Image Analysis", expanded=False):
            st.markdown("<p style='font-size:0.85rem; color:#64748B;'>Upload vehicle damage photo for preliminary Gemini multimodal severity assessment and SOP guidance.</p>", unsafe_allow_html=True)
            img_file = st.file_uploader("Upload Incident Image (PNG / JPG)", type=["png", "jpg", "jpeg"], key="incident_img_uploader")
            img_desc = st.text_input("Incident Notes / Location", placeholder="e.g. Side bumper dent near Downtown Airport corridor", key="incident_notes_input")
            if st.button("🔍 Analyze Incident Image", key="btn_analyze_incident", type="primary"):
                if img_file:
                    from agentic_ai.multimodal.incident_analyzer import analyze_incident_multimodal
                    from agentic_ai.memory.persistent_memory import create_pending_action
                    img_bytes = img_file.read()
                    res_inc = analyze_incident_multimodal(description=img_desc, image_bytes=img_bytes, image_mime=img_file.type or "image/jpeg")
                    act_id = create_pending_action(
                        action_type="CREATE_SUPPORT_TICKET",
                        target_entity="VEHICLE_ACCIDENT_SOP",
                        details=f"Multimodal Incident Report: {img_desc or 'Vehicle damage photo assessment'}. Preliminary assessment logged."
                    )
                    st.markdown(f"### 🚗 Incident Analysis Result\n{res_inc['assessment']}")
                    st.info(f"📋 Operational support ticket action #{act_id} created as PENDING in Action Center for Manager approval.")
                else:
                    st.warning("Please upload an image file first.")

        # Render Previous Chat Messages
        for idx, msg in enumerate(st.session_state.messages):
            with st.chat_message(msg["role"]):
                if msg["role"] == "user":
                    st.markdown(msg["content"])
                else:
                    render_response_card(msg["result"], index=idx)

        # Input Query Field
        user_input = st.chat_input("Ask UberOps AI about revenue, drivers, policies, predictions...")
        question = voice_query or (q_selected if 'q_selected' in locals() and q_selected else user_input)

        if question:
            st.session_state.messages.append({"role": "user", "content": question})
            with st.chat_message("user"):
                st.markdown(question)

            with st.chat_message("assistant"):
                with st.spinner("UberOps Multi-Agent System is reasoning..."):
                    try:
                        if "report" in question.lower() and "generate" in question.lower():
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
                            result = handle_question(question)

                        render_response_card(result, index=len(st.session_state.messages))
                        st.session_state.messages.append({"role": "assistant", "result": result})
                    except Exception as ex:
                        st.error(f"Execution Error: {ex}")
