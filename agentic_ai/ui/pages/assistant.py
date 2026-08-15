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
        # Starter Cards Grid (Empty State)
        if not st.session_state.messages:
            st.markdown(f"""
                <div style="text-align:center; padding:2rem 0 1.5rem 0;">
                    {get_icon_svg('Bot', '#3B82F6', 42)}
                    <h2 style="font-size:1.5rem; font-weight:800; color:#F8FAFC; margin:10px 0 4px 0;">Welcome to UberOps AI</h2>
                    <p style="font-size:0.95rem; color:#94A3B8;">Ask questions across revenue, trips, driver performance, support SOPs, or risk predictions.</p>
                </div>
            """, unsafe_allow_html=True)

            sc1, sc2, sc3 = st.columns(3)
            q_selected = None

            with sc1:
                if st.button("Executive KPIs", key="sc_kpi", use_container_width=True):
                    q_selected = "What are the executive KPIs in the Gold warehouse?"
                st.markdown(render_starter_card("Executive KPIs", "Retrieve revenue, trip counts & avg fare.", "TrendingUp", "#3B82F6"), unsafe_allow_html=True)

                st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)
                if st.button("Weekend Analysis", key="sc_wkd", use_container_width=True):
                    q_selected = "Compare weekday vs weekend performance."
                st.markdown(render_starter_card("Weekend Analysis", "Compare weekday vs weekend revenue.", "CalendarDays", "#8B5CF6"), unsafe_allow_html=True)

            with sc2:
                if st.button("Revenue Trend", key="sc_rev", use_container_width=True):
                    q_selected = "Analyse revenue trend over time."
                st.markdown(render_starter_card("Revenue Trend", "Daily revenue variance & trip patterns.", "ChartColumn", "#10B981"), unsafe_allow_html=True)

                st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)
                if st.button("Driver Analysis", key="sc_drv_an", use_container_width=True):
                    q_selected = "Show driver performance summary."
                st.markdown(render_starter_card("Driver Analysis", "Individual driver rating & revenue.", "Users", "#EC4899"), unsafe_allow_html=True)

            with sc3:
                if st.button("Top Drivers", key="sc_top", use_container_width=True):
                    q_selected = "Show top 5 drivers by revenue."
                st.markdown(render_starter_card("Top Drivers", "Highest revenue generating drivers.", "Users", "#F59E0B"), unsafe_allow_html=True)

                st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)
                if st.button("Generate Report", key="sc_rep", use_container_width=True):
                    q_selected = "Generate Executive Performance Report"
                st.markdown(render_starter_card("Generate Report", "Compile PDF, HTML & CSV reports.", "FileText", "#60A5FA"), unsafe_allow_html=True)

            st.divider()

        # Voice Assistant Recorder & Player Component
        voice_query = render_voice_interface()

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
