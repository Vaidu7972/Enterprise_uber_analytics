import streamlit as st
from agentic_ai.multimodal.incident_analyzer import analyze_incident_multimodal
from agentic_ai.memory.persistent_memory import create_pending_action
from agentic_ai.ui.styles.icons import get_icon_svg
from agentic_ai.ui.components.cards import render_status_pill


def render_incident_attachment_panel(is_active: bool = False):
    """Render compact Vehicle Incident Photo Attachment panel when activated by the ＋ trigger button. Occupies ZERO vertical space when inactive."""
    if not is_active:
        return

    is_dark = st.session_state.get("theme_mode", "dark") == "dark"
    bg_color = "#151D2F" if is_dark else "#FFFFFF"
    border_color = "rgba(239,68,68,0.3)" if is_dark else "#E2E8F0"
    text_color = "#F8FAFC" if is_dark else "#0F172A"
    sub_color = "#94A3B8" if is_dark else "#64748B"

    st.markdown(f"""
        <div class="ai-attachment-panel" style="background:{bg_color}; border:1px solid {border_color}; border-radius:12px; padding:14px; margin-bottom:12px; box-shadow:0 4px 16px rgba(0,0,0,0.08);">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
                <div style="font-size:0.92rem; font-weight:800; color:{text_color}; display:flex; align-items:center; gap:8px;">
                    {get_icon_svg('Camera', '#EF4444', 18)} Vehicle Incident Photo Attachment
                </div>
                <div style="font-size:0.72rem; color:#EF4444; background:rgba(239,68,68,0.12); padding:2px 8px; border-radius:6px; font-weight:700;">
                    Max 10 MB
                </div>
            </div>
            <p style="margin:0 0 8px 0; font-size:0.78rem; color:{sub_color};">Upload a vehicle photo for preliminary AI damage analysis and optional operational support ticketing.</p>
        </div>
    """, unsafe_allow_html=True)

    uploaded_file = st.file_uploader(
        "Upload Incident Photo (PNG / JPG / JPEG)",
        type=["png", "jpg", "jpeg"],
        key="assistant_attachment_img_uploader",
        help="Maximum supported image size is 10 MB."
    )

    if uploaded_file:
        if uploaded_file.size > 10 * 1024 * 1024:
            st.error("⚠️ Please upload a valid JPG or PNG image under 10 MB.")
            return

        file_size_mb = uploaded_file.size / (1024 * 1024)
        file_ext = uploaded_file.name.split(".")[-1].upper()

        st.markdown(f"""
            <div style="background:{bg_color}; border:1px solid {border_color}; border-radius:10px; padding:12px; margin-bottom:12px;">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                    <span style="font-size:0.85rem; font-weight:700; color:{text_color};">🚗 Incident Image Preview</span>
                    <span style="font-size:0.72rem; font-weight:800; color:#EF4444; background:rgba(239,68,68,0.12); padding:2px 8px; border-radius:6px;">
                        {uploaded_file.name} ({file_ext} • {file_size_mb:.1f} MB)
                    </span>
                </div>
            </div>
        """, unsafe_allow_html=True)

        img_col1, img_col2 = st.columns([1, 1])
        with img_col1:
            st.image(uploaded_file, caption=f"{uploaded_file.name}", use_container_width=True)

        with img_col2:
            notes = st.text_area(
                "Incident Description & Location Notes",
                placeholder="Describe what happened (e.g. Bumper dent near Downtown Airport corridor)...",
                key="assistant_incident_notes_attachment",
                height=100,
            )

            act_c1, act_c2 = st.columns([1, 1])
            with act_c1:
                analyze_clicked = st.button("🔍 Analyze Incident", key="btn_run_assistant_multimodal_attachment", type="primary", use_container_width=True)
            with act_c2:
                if st.button("🗑️ Remove Image", key="btn_clear_assistant_img_attachment", use_container_width=True):
                    st.session_state.pop("incident_analysis_result", None)
                    st.session_state.pop("ticket_created_id", None)
                    st.session_state.show_attachment_panel = False
                    st.rerun()

        if analyze_clicked:
            with st.spinner("Analyzing damage photo with Gemini Multimodal Vision & cross-referencing SOPs..."):
                img_bytes = uploaded_file.read()
                res = analyze_incident_multimodal(
                    description=notes,
                    image_bytes=img_bytes,
                    image_mime=uploaded_file.type or "image/jpeg"
                )
                st.session_state.incident_analysis_result = res
                st.session_state.incident_notes_used = notes
                st.session_state.pop("ticket_created_id", None)

    # Display Structured Result Card if present
    if "incident_analysis_result" in st.session_state:
        res = st.session_state.incident_analysis_result
        notes_used = st.session_state.get("incident_notes_used", "")
        assessment_text = res.get("assessment", "")

        severity = "MEDIUM"
        if "high" in assessment_text.lower() or "severe" in assessment_text.lower():
            severity = "HIGH"
        elif "low" in assessment_text.lower() or "minor" in assessment_text.lower():
            severity = "LOW"

        st.divider()
        st.markdown(f"""
            <div style="background:{bg_color}; border:1px solid rgba(239,68,68,0.3); border-radius:12px; padding:16px;">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
                    <div style="font-size:0.95rem; font-weight:800; color:{text_color}; display:flex; align-items:center; gap:8px;">
                        {get_icon_svg('ShieldAlert', '#EF4444', 20)} Multimodal Incident Analysis Assessment
                    </div>
                    <div>
                        {render_status_pill(severity)}
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        st.markdown(assessment_text)

        st.caption(f"ℹ️ {res.get('disclaimer', 'Preliminary visual evaluation only. Physical inspection required.')}")

        st.markdown("<div style='height:10px;'></div>", unsafe_allow_html=True)

        if "ticket_created_id" in st.session_state:
            st.success(f"✅ Support ticket request #{st.session_state.ticket_created_id} has been sent to Action Center for manager approval.")
        else:
            if st.button("📋 Create Support Ticket in Action Center", key="btn_create_ticket_from_multimodal_attachment", type="secondary"):
                act_id = create_pending_action(
                    action_type="CREATE_SUPPORT_TICKET",
                    target_entity="VEHICLE_ACCIDENT_SOP",
                    details=f"Multimodal Incident Assessment: {notes_used or 'Damage photo submitted'}. Severity: {severity}."
                )
                st.session_state.ticket_created_id = act_id
                st.rerun()


def render_incident_analysis_card():
    """Legacy wrapper for incident attachment rendering."""
    render_incident_attachment_panel(is_active=st.session_state.get("show_attachment_panel", False))
