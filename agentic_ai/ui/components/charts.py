import datetime
import altair as alt
import pandas as pd
import streamlit as st


def get_theme_colors():
    """Return theme color palette based on active light/dark mode."""
    is_dark = st.session_state.get("theme_mode", "dark") == "dark"
    if is_dark:
        return {
            "bg": "#151D2F",
            "card_bg": "#151D2F",
            "text": "#F8FAFC",
            "axis_label": "#94A3B8",
            "grid": "rgba(148, 163, 184, 0.12)",
            "primary": "#3B82F6",
            "secondary": "#10B981",
            "purple": "#8B5CF6",
            "amber": "#F59E0B",
            "pink": "#EC4899",
            "cyan": "#0EA5E9",
            "tooltip_bg": "#1E293B",
        }
    else:
        return {
            "bg": "#FFFFFF",
            "card_bg": "#FFFFFF",
            "text": "#0F172A",
            "axis_label": "#475569",
            "grid": "#F1F5F9",
            "primary": "#2563EB",
            "secondary": "#059669",
            "purple": "#7C3AED",
            "amber": "#D97706",
            "pink": "#DB2777",
            "cyan": "#0284C7",
            "tooltip_bg": "#FFFFFF",
        }


def format_chart_data(df: pd.DataFrame, x_col: str) -> pd.DataFrame:
    """Format date/timestamp columns into human-readable YYYY-MM-DD string labels."""
    if df.empty or x_col not in df.columns:
        return df

    df_copy = df.copy()
    first_val = df_copy[x_col].iloc[0]

    if isinstance(first_val, (datetime.date, datetime.datetime)) or pd.api.types.is_datetime64_any_dtype(df_copy[x_col]):
        df_copy[x_col] = pd.to_datetime(df_copy[x_col]).dt.strftime("%Y-%m-%d")
    elif isinstance(first_val, (int, float)) and x_col.lower() in ("date_key", "date", "dt"):
        str_val = str(int(first_val))
        if len(str_val) == 8 and str_val.startswith("20"):
            try:
                df_copy[x_col] = pd.to_datetime(df_copy[x_col].astype(str), format="%Y%m%d").dt.strftime("%Y-%m-%d")
            except Exception:
                df_copy[x_col] = df_copy[x_col].astype(str)
        else:
            df_copy[x_col] = df_copy[x_col].astype(str)
    else:
        df_copy[x_col] = df_copy[x_col].astype(str)

    return df_copy


def render_area_chart(
    df: pd.DataFrame,
    x_col: str,
    y_col: str,
    color: str = None,
    height: int = 260,
    title: str = None,
):
    """Render smooth curved area chart with vibrant styling."""
    if df.empty:
        st.info("No data available to display chart.")
        return

    df = format_chart_data(df, x_col)
    theme = get_theme_colors()
    chart_color = color or theme["primary"]

    # Smooth Line
    line = (
        alt.Chart(df)
        .mark_line(
            interpolate="monotone",
            color=chart_color,
            size=3.5,
        )
        .encode(
            x=alt.X(
                f"{x_col}:O",
                axis=alt.Axis(
                    title=None,
                    labelColor=theme["axis_label"],
                    gridColor=theme["grid"],
                    tickColor=theme["grid"],
                    domainColor=theme["grid"],
                    labelAngle=-30,
                ),
            ),
            y=alt.Y(
                f"{y_col}:Q",
                axis=alt.Axis(
                    title=title or y_col.replace("_", " ").title(),
                    titleColor=theme["axis_label"],
                    labelColor=theme["axis_label"],
                    gridColor=theme["grid"],
                    domainColor=theme["grid"],
                ),
            ),
            tooltip=[
                alt.Tooltip(x_col, title="Date"),
                alt.Tooltip(y_col, format="$,.2f" if "revenue" in y_col or "fare" in y_col else ",.2f", title=y_col.replace("_", " ").title()),
            ],
        )
    )

    # Gradient Area Fill
    area = (
        alt.Chart(df)
        .mark_area(
            interpolate="monotone",
            opacity=0.22,
            color=chart_color,
        )
        .encode(
            x=alt.X(f"{x_col}:O"),
            y=alt.Y(f"{y_col}:Q"),
        )
    )

    chart = (
        (area + line)
        .properties(height=height)
        .configure_view(strokeWidth=0, fill=theme["bg"])
        .configure_axis(labelFontSize=11, titleFontSize=12)
    )

    st.altair_chart(chart, use_container_width=True)


def render_bar_chart(
    df: pd.DataFrame,
    x_col: str,
    y_col: str,
    color: str = None,
    height: int = 260,
    title: str = None,
):
    """Render modern rounded bar chart."""
    if df.empty:
        st.info("No data available to display chart.")
        return

    df = format_chart_data(df, x_col)
    theme = get_theme_colors()
    chart_color = color or theme["secondary"]

    bars = (
        alt.Chart(df)
        .mark_bar(
            color=chart_color,
            cornerRadiusTopLeft=6,
            cornerRadiusTopRight=6,
            size=20,
        )
        .encode(
            x=alt.X(
                f"{x_col}:O",
                axis=alt.Axis(
                    title=None,
                    labelColor=theme["axis_label"],
                    gridColor=theme["grid"],
                    tickColor=theme["grid"],
                    domainColor=theme["grid"],
                    labelAngle=-30,
                ),
            ),
            y=alt.Y(
                f"{y_col}:Q",
                axis=alt.Axis(
                    title=title or y_col.replace("_", " ").title(),
                    titleColor=theme["axis_label"],
                    labelColor=theme["axis_label"],
                    gridColor=theme["grid"],
                    domainColor=theme["grid"],
                ),
            ),
            tooltip=[
                alt.Tooltip(x_col, title="Date"),
                alt.Tooltip(y_col, format=",.2f", title=y_col.replace("_", " ").title()),
            ],
        )
        .properties(height=height)
        .configure_view(strokeWidth=0, fill=theme["bg"])
    )

    st.altair_chart(bars, use_container_width=True)


def render_multi_metric_chart(
    df: pd.DataFrame,
    x_col: str,
    metric1: str = "total_revenue",
    metric2: str = "total_trips",
    height: int = 280,
):
    """Render dual-axis vibrant chart for Revenue & Trip Volume."""
    if df.empty:
        st.info("No data available to display chart.")
        return

    df = format_chart_data(df, x_col)
    theme = get_theme_colors()

    base = alt.Chart(df).encode(
        x=alt.X(
            f"{x_col}:O",
            axis=alt.Axis(
                title=None,
                labelColor=theme["axis_label"],
                gridColor=theme["grid"],
                tickColor=theme["grid"],
                domainColor=theme["grid"],
                labelAngle=-30,
            ),
        )
    )

    # Primary Metric Line (Revenue)
    line1 = base.mark_line(
        interpolate="monotone",
        color=theme["primary"],
        size=3.5,
    ).encode(
        y=alt.Y(
            f"{metric1}:Q",
            axis=alt.Axis(
                title="Revenue ($)",
                titleColor=theme["primary"],
                labelColor=theme["primary"],
                gridColor=theme["grid"],
            ),
        ),
        tooltip=[alt.Tooltip(x_col, title="Date"), alt.Tooltip(metric1, format="$,.2f", title="Total Revenue")],
    )

    area1 = base.mark_area(
        interpolate="monotone",
        opacity=0.18,
        color=theme["primary"],
    ).encode(
        y=alt.Y(f"{metric1}:Q"),
    )

    # Secondary Metric Line (Trips)
    line2 = base.mark_line(
        interpolate="monotone",
        color=theme["secondary"],
        size=3.5,
        strokeDash=[5, 5],
    ).encode(
        y=alt.Y(
            f"{metric2}:Q",
            axis=alt.Axis(
                title="Total Trips",
                titleColor=theme["secondary"],
                labelColor=theme["secondary"],
                gridColor=None,
            ),
        ),
        tooltip=[alt.Tooltip(x_col, title="Date"), alt.Tooltip(metric2, format=",d", title="Total Trips")],
    )

    chart = (
        alt.layer(area1 + line1, line2)
        .resolve_scale(y="independent")
        .properties(height=height)
        .configure_view(strokeWidth=0, fill=theme["bg"])
    )

    st.altair_chart(chart, use_container_width=True)


def render_donut_chart(
    df: pd.DataFrame,
    category_col: str,
    value_col: str,
    height: int = 240,
    title: str = None,
):
    """Render modern vibrant Donut chart matching Behance dashboard UI standards."""
    if df.empty:
        st.info("No data available to display chart.")
        return

    theme = get_theme_colors()

    chart = (
        alt.Chart(df)
        .mark_arc(innerRadius=50, outerRadius=90, cornerRadius=4)
        .encode(
            theta=alt.Theta(field=value_col, type="quantitative"),
            color=alt.Color(
                field=category_col,
                type="nominal",
                scale=alt.Scale(
                    range=["#3B82F6", "#10B981", "#8B5CF6", "#F59E0B", "#EC4899", "#0EA5E9"]
                ),
                legend=alt.Legend(
                    orient="right",
                    labelColor=theme["text"],
                    titleColor=theme["axis_label"],
                    title=None,
                ),
            ),
            tooltip=[category_col, alt.Tooltip(value_col, format=",.2f")],
        )
        .properties(height=height)
        .configure_view(strokeWidth=0, fill=theme["bg"])
    )

    st.altair_chart(chart, use_container_width=True)
