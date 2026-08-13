import streamlit as st
from agentic_ai.ui.styles.icons import get_icon_svg


NAV_STRUCTURE = [
    ("COMMAND CENTER", [
        ("Overview", "LayoutDashboard"),
        ("AI Assistant", "MessageSquare"),
    ]),
    ("ANALYTICS", [
        ("Revenue Intelligence", "TrendingUp"),
        ("Driver Intelligence", "Users"),
        ("Operations Analytics", "ChartColumn"),
    ]),
    ("AI INTELLIGENCE", [
        ("Knowledge Center", "BookOpen"),
        ("Predictive Intelligence", "BrainCircuit"),
        ("Action Center", "ListChecks"),
    ]),
    ("DATA PLATFORM", [
        ("Pipeline Health", "Workflow"),
        ("Data Quality", "ShieldCheck"),
        ("Warehouse Explorer", "Database"),
    ]),
    ("OUTPUT", [
        ("Reports", "FileText"),
    ]),
    ("SYSTEM", [
        ("Agent Activity", "Activity"),
        ("Audit Logs", "ClipboardList"),
        ("Settings", "Settings"),
    ]),
]


def render_saas_sidebar() -> str:
    """Render grouped SaaS navigation sidebar and return selected page name."""
    with st.sidebar:
        # Branding Top
        st.markdown(f"""
            <div style="display:flex; align-items:center; gap:10px; padding:6px 0 16px 0; border-bottom:1px solid rgba(148,163,184,0.12); margin-bottom:16px;">
                {get_icon_svg('Bot', '#3B82F6', 26)}
                <div>
                    <div style="font-size:1.1rem; font-weight:800; color:#F8FAFC; line-height:1.2;">UberOps AI</div>
                    <div style="font-size:0.75rem; color:#94A3B8;">Mobility Intelligence</div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        if "current_page" not in st.session_state:
            st.session_state.current_page = "Overview"

        selected_page = st.session_state.current_page

        for group_label, items in NAV_STRUCTURE:
            st.markdown(f"""<div style="font-size:0.7rem; font-weight:700; color:#64748B; letter-spacing:1px; margin:14px 0 6px 4px; text-transform:uppercase;">{group_label}</div>""", unsafe_allow_html=True)
            for page_name, icon_name in items:
                is_selected = (selected_page == page_name)
                icon_color = "#3B82F6" if is_selected else "#94A3B8"
                button_style = "primary" if is_selected else "secondary"
                
                col1, col2 = st.columns([1, 6])
                with col1:
                    st.markdown(f"""<div style="padding-top:6px;">{get_icon_svg(icon_name, icon_color, 18)}</div>""", unsafe_allow_html=True)
                with col2:
                    if st.button(page_name, key=f"nav_{page_name}", use_container_width=True, type=button_style):
                        st.session_state.current_page = page_name
                        st.rerun()

        st.divider()

    return st.session_state.current_page
