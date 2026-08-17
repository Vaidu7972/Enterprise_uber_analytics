import pandas as pd
import streamlit as st
from agentic_ai.memory.persistent_memory import (
    get_pending_actions,
    get_all_action_logs,
    approve_pending_action,
    reject_pending_action,
)
from agentic_ai.tools.action_tools import (
    create_training_recommendation,
    create_support_ticket,
)
from agentic_ai.ui.styles.icons import get_icon_svg
from agentic_ai.ui.components.cards import render_kpi_card, render_status_pill

def render_action_center_page():
    """Render SaaS Action Center Page with True Human-in-the-Loop Approval Workflow."""
    st.markdown("""
        <div class="page-header">
            <h1>Action Center — Human-in-the-Loop Governance</h1>
            <p>Review, approve, or reject pending operational recommendations formulated by AI agents.</p>
        </div>
    """, unsafe_allow_html=True)

    all_logs = get_all_action_logs()
    pending = get_pending_actions()

    total_actions = len(all_logs) if all_logs else 0
    pending_count = len(pending) if pending else 0
    approved_count = len([l for l in all_logs if l.get("status") in ("APPROVED", "COMPLETED")]) if all_logs else 0
    rejected_count = len([l for l in all_logs if l.get("status") == "REJECTED"]) if all_logs else 0

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_kpi_card("Pending Approval", f"{pending_count}", "Clock", "Requires Manager Action", "#F59E0B", change_text="Pending Queue", is_positive=False)
    with c2:
        render_kpi_card("Approved Actions", f"{approved_count}", "CircleCheck", "Executed via Audit", "#10B981", change_text="Approved", is_positive=True)
    with c3:
        render_kpi_card("Rejected Actions", f"{rejected_count}", "CircleX", "Management Veto", "#EF4444", change_text="Rejected", is_positive=False)
    with c4:
        render_kpi_card("Total Action Audit", f"{total_actions}", "ClipboardList", "PostgreSQL Gold Log", "#3B82F6", change_text="Total Logged", is_positive=True)

    st.divider()

    # SECTION 1: Pending Actions Queue
    st.markdown(f"""<div class="saas-card-title">{get_icon_svg('Clock', '#F59E0B', 20)} Actions Pending Manager Approval</div>""", unsafe_allow_html=True)

    if pending:
        for act in pending:
            action_id = act["action_id"]
            action_type = act.get("action_type", "UNKNOWN")
            target = act.get("target_entity", "N/A")
            details = act.get("details", "")
            ts = act.get("timestamp", "")

            is_dark = st.session_state.get("theme_mode", "dark") == "dark"
            bg_card = "#111827" if is_dark else "#FFFFFF"
            border_card = "rgba(148,163,184,0.14)" if is_dark else "#E2E8F0"
            text_primary = "#F8FAFC" if is_dark else "#0F172A"
            text_secondary = "#94A3B8" if is_dark else "#64748B"

            st.markdown(f"""
                <div style="background:{bg_card}; border:1px solid {border_card}; border-radius:12px; padding:16px; margin-bottom:14px; box-shadow:0 2px 8px rgba(0,0,0,0.04);">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                        <span class="status-pill status-pill-amber">
                            {get_icon_svg('Clock', '#F59E0B', 14)} PENDING APPROVAL (ID #{action_id})
                        </span>
                        <span style="font-size:0.8rem; color:{text_secondary};">{ts}</span>
                    </div>
                    <h4 style="margin:4px 0; color:{text_primary}; font-size:1.05rem;">Type: <code style="color:#3B82F6;">{action_type}</code> | Target Entity: <code style="color:#10B981;">{target}</code></h4>
                    <p style="margin:6px 0 12px 0; font-size:0.9rem; color:{text_secondary};">{details}</p>
                </div>
            """, unsafe_allow_html=True)

            col_app, col_rej, col_reason = st.columns([1.5, 1.5, 4])
            with col_app:
                if st.button(f"✅ APPROVE #{action_id}", key=f"btn_app_{action_id}", type="primary", use_container_width=True):
                    if action_type == "ASSIGN_TRAINING":
                        create_training_recommendation(
                            driver_id=target,
                            driver_name=f"Driver {target}",
                            course_name="Driver Quality & Hospitality Coaching",
                            approved_by="Manager",
                        )
                    elif action_type == "CREATE_SUPPORT_TICKET":
                        create_support_ticket(
                            ticket_title=f"Incident Ticket - {target}",
                            category=target,
                            description=details,
                            priority="HIGH",
                            approved_by="Manager",
                        )

                    approve_pending_action(action_id, approved_by="Manager")
                    st.toast(f"Action #{action_id} APPROVED and executed successfully!", icon="✅")
                    st.rerun()

            with col_rej:
                if st.button(f"❌ REJECT #{action_id}", key=f"btn_rej_{action_id}", use_container_width=True):
                    reason_val = st.session_state.get(f"reason_{action_id}", "Rejected by operational lead")
                    reject_pending_action(action_id, rejection_reason=reason_val, rejected_by="Manager")
                    st.toast(f"Action #{action_id} REJECTED.", icon="⚠️")
                    st.rerun()

            with col_reason:
                st.text_input("Rejection Reason", key=f"reason_{action_id}", placeholder="e.g. Driver already completed coaching course", label_visibility="collapsed")

            st.divider()
    else:
        st.info("No management actions currently pending approval.")

    # SECTION 2: Action Governance Audit Log
    st.markdown(f"""<div class="saas-card-title" style="margin-top:1.5rem;">{get_icon_svg('ClipboardList', '#3B82F6', 20)} Action Governance Audit Log</div>""", unsafe_allow_html=True)

    if all_logs:
        df_logs = pd.DataFrame(all_logs)
        
        # Filter controls for Action History
        flt_status = st.selectbox("Filter Status", ["All Statuses"] + df_logs["status"].unique().tolist(), key="act_status_flt")
        if flt_status != "All Statuses":
            df_logs = df_logs[df_logs["status"] == flt_status]

        if "status" in df_logs.columns:
            df_logs["status_badge"] = df_logs["status"].apply(render_status_pill)

        st.dataframe(df_logs, use_container_width=True, hide_index=True)
        st.download_button("Download Action Audit Log CSV", df_logs.to_csv(index=False), "action_audit_log.csv", "text/csv")
    else:
        st.info("No action audit records stored in PostgreSQL Gold schema yet.")
