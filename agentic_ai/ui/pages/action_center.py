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


def render_action_center_page():
    """Render SaaS Action Center Page with True Human-in-the-Loop Approval Workflow."""
    st.markdown("""
        <div class="page-header">
            <h1>Action Center — Human-in-the-Loop Governance</h1>
            <p>Review, approve, or reject pending operational recommendations formulated by AI agents.</p>
        </div>
    """, unsafe_allow_html=True)

    is_dark = st.session_state.get("theme_mode", "dark") == "dark"
    bg_card = "#151D2F" if is_dark else "#FFFFFF"
    border_card = "rgba(148,163,184,0.15)" if is_dark else "#E2E8F0"
    text_primary = "#F8FAFC" if is_dark else "#0F172A"
    text_secondary = "#94A3B8" if is_dark else "#64748B"

    # SECTION 1: Pending Actions Queue
    st.markdown(f"""<div class="saas-card-title">{get_icon_svg('Clock', '#F59E0B', 20)} Actions Pending Manager Approval</div>""", unsafe_allow_html=True)

    pending = get_pending_actions()

    if pending:
        for act in pending:
            action_id = act["action_id"]
            action_type = act.get("action_type", "UNKNOWN")
            target = act.get("target_entity", "N/A")
            details = act.get("details", "")
            ts = act.get("timestamp", "")

            st.markdown(f"""
                <div style="background:{bg_card}; border:1px solid {border_card}; border-radius:12px; padding:16px; margin-bottom:14px; box-shadow:0 2px 8px rgba(0,0,0,0.04);">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                        <span class="status-pill" style="background:rgba(245,158,11,0.14); color:#F59E0B; border-color:rgba(245,158,11,0.3); font-weight:700;">
                            {get_icon_svg('Clock', '#F59E0B', 14)} PENDING APPROVAL (ID #{action_id})
                        </span>
                        <span style="font-size:0.8rem; color:{text_secondary};">{ts}</span>
                    </div>
                    <h4 style="margin:4px 0; color:{text_primary}; font-size:1.05rem;">Type: <code style="color:#3B82F6;">{action_type}</code> | Target: <code style="color:#10B981;">{target}</code></h4>
                    <p style="margin:6px 0 12px 0; font-size:0.9rem; color:{text_secondary};">{details}</p>
                </div>
            """, unsafe_allow_html=True)

            col_app, col_rej, col_reason = st.columns([1.5, 1.5, 4])
            with col_app:
                if st.button(f"✅ APPROVE #{action_id}", key=f"btn_app_{action_id}", type="primary", use_container_width=True):
                    # Execute underlying action tool upon manager approval
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
                    st.success(f"Action #{action_id} APPROVED and executed successfully!")
                    st.rerun()

            with col_rej:
                if st.button(f"❌ REJECT #{action_id}", key=f"btn_rej_{action_id}", use_container_width=True):
                    reason_val = st.session_state.get(f"reason_{action_id}", "Rejected by operational lead")
                    reject_pending_action(action_id, rejection_reason=reason_val, rejected_by="Manager")
                    st.warning(f"Action #{action_id} REJECTED.")
                    st.rerun()

            with col_reason:
                st.text_input("Rejection Reason (Optional)", key=f"reason_{action_id}", placeholder="e.g. Driver already completed coaching", label_visibility="collapsed")

            st.divider()
    else:
        st.info("No management actions currently pending approval.")

    # SECTION 2: Action History Audit Trail
    st.markdown(f"""<div class="saas-card-title" style="margin-top:1.5rem;">{get_icon_svg('ClipboardList', '#3B82F6', 20)} Action Governance Audit Log</div>""", unsafe_allow_html=True)

    action_logs = get_all_action_logs()
    if action_logs:
        df_logs = pd.DataFrame(action_logs)
        st.dataframe(df_logs, use_container_width=True, hide_index=True)
    else:
        st.info("No action audit records stored in PostgreSQL Gold schema yet.")
