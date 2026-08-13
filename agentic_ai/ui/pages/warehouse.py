import streamlit as st
from agentic_ai.tools.sql_tool import get_gold_schema, execute_read_only_query
from agentic_ai.ui.styles.icons import get_icon_svg


def render_warehouse_page():
    """Render SaaS Warehouse Explorer Page."""
    st.markdown("""
        <div class="page-header">
            <h1>Warehouse Explorer</h1>
            <p>Read-only schema discovery, table structures, and safe Gold query runner.</p>
        </div>
    """, unsafe_allow_html=True)

    schema_str = get_gold_schema()
    with st.expander("📖 Gold Schema Definitions (information_schema)"):
        st.code(schema_str, language="yaml")

    st.markdown(f"""<div class="saas-card-title">{get_icon_svg('Database', '#3B82F6', 18)} Safe Read-Only SQL Query Runner</div>""", unsafe_allow_html=True)
    sql_input = st.text_area("SQL Query (Gold Schema Only)", "SELECT * FROM gold.kpi_summary;", height=100)
    
    if st.button("Execute Query"):
        try:
            df_res = execute_read_only_query(sql_input)
            st.success(f"Query executed successfully! Retreived {len(df_res)} rows.")
            st.dataframe(df_res, use_container_width=True, hide_index=True)
        except Exception as ex:
            st.error(f"SQL Execution Error: {ex}")
