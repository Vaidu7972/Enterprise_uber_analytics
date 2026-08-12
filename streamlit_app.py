import pandas as pd
import streamlit as st

from agentic_ai.agents.supervisor_agent import handle_question


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="UberOps AI",
    page_icon="🚕",
    layout="wide",
    initial_sidebar_state="expanded",
)


# =========================================================
# CUSTOM UI STYLING
# =========================================================

st.markdown(
    """
    <style>

    .block-container {
        max-width: 1250px;
        padding-top: 2rem;
        padding-bottom: 5rem;
    }

    .hero {
        padding: 2rem 2.2rem;
        border-radius: 22px;
        margin-bottom: 1.5rem;

        background:
            linear-gradient(
                135deg,
                rgba(124, 58, 237, 0.22),
                rgba(37, 99, 235, 0.14)
            );

        border: 1px solid rgba(148, 163, 184, 0.18);
    }

    .hero h1 {
        font-size: 2.7rem;
        margin-bottom: 0.2rem;
    }

    .hero p {
        font-size: 1.05rem;
        opacity: 0.82;
        margin-bottom: 0;
    }

    .route-badge {
        display: inline-block;
        padding: 0.35rem 0.8rem;
        border-radius: 999px;
        font-size: 0.82rem;
        font-weight: 700;
        margin-bottom: 0.8rem;
        border: 1px solid rgba(148, 163, 184, 0.25);
        background: rgba(124, 58, 237, 0.13);
    }

    .small-text {
        opacity: 0.7;
        font-size: 0.88rem;
    }

    .status-card {
        border: 1px solid rgba(148, 163, 184, 0.18);
        border-radius: 15px;
        padding: 0.8rem 1rem;
        margin-bottom: 0.6rem;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# SESSION STATE
# =========================================================

if "messages" not in st.session_state:
    st.session_state.messages = []


# =========================================================
# ROUTE INFORMATION
# =========================================================

ROUTE_LABELS = {
    "general": "🧠 General AI",
    "data_agent": "📊 Data Agent",
    "support_agent": "📚 Support Agent",
    "ml_agent": "🤖 ML Agent",
    "multi_agent": "🕸️ Multi-Agent",
}


def get_route_label(route):
    return ROUTE_LABELS.get(
        route,
        route.replace("_", " ").title()
    )


# =========================================================
# RESULT DISPLAY FUNCTION
# =========================================================

def display_result(result):

    route = result.get(
        "route",
        "unknown"
    )

    route_label = get_route_label(
        route
    )

    st.markdown(
        f"""
        <div class="route-badge">
            {route_label}
        </div>
        """,
        unsafe_allow_html=True,
    )

    # -----------------------------------------------------
    # MAIN AI ANSWER
    # -----------------------------------------------------

    answer = result.get(
        "answer"
    )

    if answer:

        st.markdown(
            answer
        )

    # -----------------------------------------------------
    # ROUTING INFORMATION
    # -----------------------------------------------------

    with st.expander(
        "🧭 How UberOps routed this question"
    ):

        st.write(
            "**Route:**",
            route_label
        )

        st.write(
            "**Intent:**",
            result.get(
                "intent",
                "Not available"
            )
        )

        st.write(
            "**Routing reason:**",
            result.get(
                "routing_reason",
                "Not available"
            )
        )

        tables_used = result.get(
            "tables_used",
            []
        )

        if tables_used:

            st.write(
                "**Warehouse tables used:**"
            )

            st.code(
                "\n".join(
                    tables_used
                )
            )

    # -----------------------------------------------------
    # GENERATED SQL
    # -----------------------------------------------------

    sql = result.get(
        "sql"
    )

    if sql:

        with st.expander(
            "🧾 View generated SQL"
        ):

            st.code(
                sql,
                language="sql"
            )

    # -----------------------------------------------------
    # DATABASE RESULT
    # -----------------------------------------------------

    dataframe = result.get(
        "data"
    )

    if (
        dataframe is not None
        and isinstance(
            dataframe,
            pd.DataFrame
        )
        and not dataframe.empty
    ):

        with st.expander(
            "🗄️ View PostgreSQL result",
            expanded=True
        ):

            display_database_result(
                dataframe
            )


# =========================================================
# DATABASE RESULT DISPLAY
# =========================================================

def display_database_result(df):

    # ---------------------------------------------
    # Single-row KPI result
    # ---------------------------------------------

    numeric_columns = (
        df.select_dtypes(
            include="number"
        )
        .columns
        .tolist()
    )

    if (
        len(df) == 1
        and numeric_columns
    ):

        columns_to_show = (
            numeric_columns[:4]
        )

        metric_columns = st.columns(
            len(columns_to_show)
        )

        row = df.iloc[0]

        for index, column_name in enumerate(
            columns_to_show
        ):

            metric_columns[index].metric(
                label=column_name
                .replace("_", " ")
                .title(),
                value=row[column_name],
            )

        st.divider()

    # ---------------------------------------------
    # Full DataFrame
    # ---------------------------------------------

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
    )

    # ---------------------------------------------
    # Download CSV
    # ---------------------------------------------

    csv_data = df.to_csv(
        index=False
    ).encode(
        "utf-8"
    )

    st.download_button(
        label="⬇️ Download result as CSV",
        data=csv_data,
        file_name="uberops_query_result.csv",
        mime="text/csv",
        use_container_width=False,
    )

    # ---------------------------------------------
    # Automatic simple visualization
    # ---------------------------------------------

    if len(df) >= 2:

        numeric_columns = (
            df.select_dtypes(
                include="number"
            )
            .columns
            .tolist()
        )

        non_numeric_columns = [
            column
            for column in df.columns
            if column not in numeric_columns
        ]

        if (
            numeric_columns
            and non_numeric_columns
        ):

            category_column = (
                non_numeric_columns[0]
            )

            numeric_column = (
                numeric_columns[0]
            )

            chart_df = (
                df[
                    [
                        category_column,
                        numeric_column,
                    ]
                ]
                .dropna()
                .head(20)
            )

            if not chart_df.empty:

                with st.expander(
                    "📈 Quick visualization"
                ):

                    st.caption(
                        f"{numeric_column} "
                        f"by {category_column}"
                    )

                    st.bar_chart(
                        chart_df.set_index(
                            category_column
                        )
                    )


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.title(
        "🚕 UberOps AI"
    )

    st.caption(
        "Agentic Data Intelligence Platform"
    )

    st.divider()

    st.subheader(
        "System"
    )

    st.markdown(
        """
        <div class="status-card">
            🧠 <b>Gemini LLM</b><br>
            <span class="small-text">
                Implemented
            </span>
        </div>

        <div class="status-card">
            🧭 <b>Supervisor Router</b><br>
            <span class="small-text">
                Implemented
            </span>
        </div>

        <div class="status-card">
            📊 <b>Data Agent</b><br>
            <span class="small-text">
                PostgreSQL connected
            </span>
        </div>

        <div class="status-card">
            📚 <b>Support Agent</b><br>
            <span class="small-text">
                RAG coming next
            </span>
        </div>

        <div class="status-card">
            🤖 <b>ML Agent</b><br>
            <span class="small-text">
                Planned
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.divider()

    st.subheader(
        "Try a question"
    )

    sample_questions = [
        "What is ETL?",
        "What is the total revenue in the warehouse?",
        "Show me the top 5 drivers by revenue.",
        "What documents are required for driver onboarding?",
        "Which drivers are likely to underperform?",
    ]

    selected_question = None

    for sample_question in sample_questions:

        if st.button(
            sample_question,
            use_container_width=True,
        ):

            selected_question = (
                sample_question
            )

    st.divider()

    if st.button(
        "🗑️ Clear conversation",
        use_container_width=True,
    ):

        st.session_state.messages = []

        st.rerun()


# =========================================================
# HERO SECTION
# =========================================================

st.markdown(
    """
    <div class="hero">

        <h1>
            🚕 UberOps AI
        </h1>

        <p>
            Ask questions across enterprise mobility data,
            analytics, business intelligence, support knowledge
            and predictive AI.
        </p>

    </div>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# PLATFORM SUMMARY
# =========================================================

col1, col2, col3, col4 = st.columns(
    4
)

col1.metric(
    "AI Router",
    "Supervisor"
)

col2.metric(
    "Data Source",
    "PostgreSQL Gold"
)

col3.metric(
    "LLM",
    "Gemini"
)

col4.metric(
    "Interface",
    "Streamlit"
)


st.divider()


# =========================================================
# DISPLAY CHAT HISTORY
# =========================================================

for message in st.session_state.messages:

    role = message[
        "role"
    ]

    with st.chat_message(
        role
    ):

        if role == "user":

            st.markdown(
                message[
                    "content"
                ]
            )

        else:

            display_result(
                message[
                    "result"
                ]
            )


# =========================================================
# CHAT INPUT
# =========================================================

typed_question = st.chat_input(
    "Ask UberOps AI about data, drivers, revenue, policies or predictions..."
)


question = (
    selected_question
    if selected_question
    else typed_question
)


# =========================================================
# PROCESS USER QUESTION
# =========================================================

if question:

    # Store user message

    st.session_state.messages.append(
        {
            "role": "user",
            "content": question,
        }
    )

    with st.chat_message(
        "user"
    ):

        st.markdown(
            question
        )

    # Run Supervisor

    with st.chat_message(
        "assistant"
    ):

        with st.spinner(
            "UberOps AI is analyzing your request..."
        ):

            try:

                result = handle_question(
                    question
                )

                display_result(
                    result
                )

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "result": result,
                    }
                )

            except Exception as error:

                st.error(
                    "UberOps AI could not process "
                    "the request."
                )

                st.exception(
                    error
                )