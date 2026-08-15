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
        if "theme_mode" not in st.session_state:
            st.session_state.theme_mode = "dark"

        is_dark = (st.session_state.theme_mode == "dark")
        title_color = "#F8FAFC" if is_dark else "#0F172A"
        sub_color = "#94A3B8" if is_dark else "#64748B"
        group_color = "#64748B" if is_dark else "#475569"

        # Branding Top with Theme Toggle
        c_brand, c_toggle = st.columns([7, 4])
        with c_brand:
            brand_html = (
                f'<div style="display:flex; align-items:center; gap:8px; padding:2px 0;">'
                f'{get_icon_svg("Bot", "#3B82F6", 26)}'
                f'<div>'
                f'<div style="font-size:1.05rem; font-weight:800; color:{title_color}; line-height:1.1;">UberOps AI</div>'
                f'<div style="font-size:0.72rem; color:{sub_color};">Mobility Intelligence</div>'
                f'</div>'
                f'</div>'
            )
            st.markdown(brand_html, unsafe_allow_html=True)
        with c_toggle:
            toggle_label = "🌙 Dark" if is_dark else "☀️ Light"
            if st.button(toggle_label, key="theme_toggle_btn", use_container_width=True):
                st.session_state.theme_mode = "light" if is_dark else "dark"
                st.rerun()

        st.markdown("<div style='border-bottom:1px solid rgba(148,163,184,0.14); margin: 8px 0 12px 0;'></div>", unsafe_allow_html=True)

        if "current_page" not in st.session_state:
            st.session_state.current_page = "Overview"

        selected_page = st.session_state.current_page

        for group_label, items in NAV_STRUCTURE:
            st.markdown(f'<div style="font-size:0.7rem; font-weight:700; color:{group_color}; letter-spacing:1px; margin:14px 0 6px 4px; text-transform:uppercase;">{group_label}</div>', unsafe_allow_html=True)
            for page_name, icon_name in items:
                is_selected = (selected_page == page_name)
                icon_color = "#3B82F6" if is_selected else ("#94A3B8" if is_dark else "#64748B")
                button_style = "primary" if is_selected else "secondary"
                
                col1, col2 = st.columns([1, 6])
                with col1:
                    st.markdown(f'<div style="padding-top:6px;">{get_icon_svg(icon_name, icon_color, 18)}</div>', unsafe_allow_html=True)
                with col2:
                    if st.button(page_name, key=f"nav_{page_name}", use_container_width=True, type=button_style):
                        st.session_state.current_page = page_name
                        st.rerun()

        st.divider()

    return st.session_state.current_page
