import datetime
import altair as alt
import pandas as pd
import streamlit as st


def get_theme_colors():
    """Return semantic theme color palette based on active light/dark mode."""
    is_dark = st.session_state.get("theme_mode", "dark") == "dark"
    if is_dark:
        return {
            "bg": "#111827",
            "card_bg": "#151D2F",
            "text": "#F8FAFC",
            "axis_label": "#94A3B8",
            "grid": "rgba(148, 163, 184, 0.12)",
            "primary": "#3B82F6",
            "secondary": "#10B981",
            "purple": "#8B5CF6",
            "amber": "#F59E0B",
            "pink": "#EC4899",
            "cyan": "#06B6D4",
            "red": "#EF4444",
            "indigo": "#6366F1",
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
            "red": "#DC2626",
            "indigo": "#4F46E5",
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


def render_trip_fare_scatter(
    df: pd.DataFrame,
    x_col: str = "trip_distance",
    y_col: str = "fare_amount",
    size_col: str = "trip_duration_minutes",
    category_col: str = "passenger_count",
    height: int = 320,
):
    """Render Fare vs Trip Distance bubble scatter plot with passenger count colors, duration sizing, cyan dashed trend line, and outlier markers."""
    if df.empty:
        st.info("No trip records available for scatter plot.")
        return

    df_sc = df.copy()
    df_sc["trip_distance"] = df_sc["trip_distance"].astype(float)
    df_sc["fare_amount"] = df_sc["fare_amount"].astype(float)
    df_sc["trip_duration_minutes"] = df_sc["trip_duration_minutes"].astype(float)
    
    if "passenger_count" in df_sc.columns:
        p_ints = df_sc["passenger_count"].fillna(1).astype(int)
        df_sc["passenger_cat"] = p_ints.apply(lambda p: f"{p} Passengers" if p > 1 else "1 Passenger")
    else:
        df_sc["passenger_cat"] = "1 Passenger"

    if "fare_per_mile" not in df_sc.columns:
        df_sc["fare_per_mile"] = df_sc.apply(
            lambda r: (r["fare_amount"] / r["trip_distance"]) if r["trip_distance"] > 0 else 0.0, axis=1
        )

    # Statistical IQR Outlier Detection
    q1 = float(df_sc["fare_per_mile"].quantile(0.25))
    q3 = float(df_sc["fare_per_mile"].quantile(0.75))
    iqr = q3 - q1
    upper_thresh = q3 + 1.5 * iqr

    if "is_outlier" not in df_sc.columns:
        df_sc["is_outlier"] = df_sc["fare_per_mile"] > upper_thresh

    df_sc["outlier_label"] = df_sc["is_outlier"].map({True: "Potential Statistical Outlier", False: "Normal"})

    theme = get_theme_colors()

    # Base Circles
    circles = (
        alt.Chart(df_sc)
        .mark_circle(opacity=0.75, stroke="#1E293B", strokeWidth=1.2)
        .encode(
            x=alt.X("trip_distance:Q", axis=alt.Axis(title="Trip Distance (miles)", labelColor=theme["axis_label"], gridColor=theme["grid"])),
            y=alt.Y("fare_amount:Q", axis=alt.Axis(title="Fare Amount ($)", labelColor=theme["axis_label"], gridColor=theme["grid"])),
            size=alt.Size("trip_duration_minutes:Q", legend=alt.Legend(title="Duration (min)", labelColor=theme["axis_label"], titleColor=theme["text"], orient="right"), scale=alt.Scale(range=[70, 320])),
            color=alt.Color(
                "passenger_cat:N",
                scale=alt.Scale(
                    domain=["1 Passenger", "2 Passengers", "3 Passengers", "4 Passengers", "5+ Passengers"],
                    range=["#3B82F6", "#06B6D4", "#10B981", "#F59E0B", "#EC4899"],
                ),
                legend=alt.Legend(title="Passengers", labelColor=theme["text"], titleColor=theme["axis_label"], orient="right"),
            ),
            tooltip=[
                alt.Tooltip("trip_id:N", title="Trip ID") if "trip_id" in df_sc.columns else alt.Tooltip("trip_distance:Q"),
                alt.Tooltip("fare_amount:Q", format="$,.2f", title="Fare Amount"),
                alt.Tooltip("trip_distance:Q", format=",.2f", title="Trip Distance (mi)"),
                alt.Tooltip("trip_duration_minutes:Q", format=",.1f", title="Trip Duration (min)"),
                alt.Tooltip("passenger_cat:N", title="Passengers"),
                alt.Tooltip("fare_per_mile:Q", format="$,.2f", title="Fare / Mile ($/mi)"),
                alt.Tooltip("outlier_label:N", title="Outlier Status"),
            ],
        )
    )

    # Cyan Dashed Trend Line
    trend_line = (
        alt.Chart(df_sc)
        .transform_regression("trip_distance", "fare_amount")
        .mark_line(color="#06B6D4", strokeDash=[4, 4], size=2.5)
    )

    # Statistical Outlier Red Ring Highlights
    outlier_points = (
        alt.Chart(df_sc[df_sc["is_outlier"] == True])
        .mark_point(color="#EF4444", size=180, shape="circle", strokeWidth=2.5)
        .encode(
            x="trip_distance:Q",
            y="fare_amount:Q",
            tooltip=[
                alt.Tooltip("trip_id:N", title="Trip ID") if "trip_id" in df_sc.columns else alt.Tooltip("trip_distance:Q"),
                alt.Tooltip("fare_amount:Q", format="$,.2f", title="Fare Amount"),
                alt.Tooltip("trip_distance:Q", format=",.2f", title="Trip Distance (mi)"),
                alt.Tooltip("fare_per_mile:Q", format="$,.2f", title="Fare / Mile ($/mi)"),
                alt.Tooltip("outlier_label:N", title="Outlier Flag"),
            ],
        )
    )

    chart = (
        (circles + trend_line + outlier_points)
        .properties(height=height)
        .configure_view(strokeWidth=0, fill=theme["bg"])
    )

    st.altair_chart(chart, use_container_width=True)


def render_distance_band_chart(df: pd.DataFrame, height: int = 220):
    """Render horizontal bar chart analyzing trips grouped by distance band."""
    if df.empty:
        st.info("No trip records available for distance band analysis.")
        return

    df_band = df.copy()
    df_band["trip_distance"] = df_band["trip_distance"].astype(float)
    df_band["fare_amount"] = df_band["fare_amount"].astype(float)
    df_band["trip_duration_minutes"] = df_band["trip_duration_minutes"].astype(float)

    def get_band(d):
        if d <= 3.0:
            return "Short (0–3 mi)"
        elif d <= 7.0:
            return "Medium (3–7 mi)"
        elif d <= 15.0:
            return "Long (7–15 mi)"
        else:
            return "Very Long (15+ mi)"

    df_band["distance_band"] = df_band["trip_distance"].apply(get_band)

    grp = (
        df_band.groupby("distance_band")
        .agg(
            avg_fare=("fare_amount", "mean"),
            trip_count=("trip_distance", "count"),
            avg_duration=("trip_duration_minutes", "mean"),
        )
        .reset_index()
    )

    band_order = ["Short (0–3 mi)", "Medium (3–7 mi)", "Long (7–15 mi)", "Very Long (15+ mi)"]
    grp["distance_band"] = pd.Categorical(grp["distance_band"], categories=band_order, ordered=True)
    grp = grp.sort_values("distance_band")

    theme = get_theme_colors()

    bars = (
        alt.Chart(grp)
        .mark_bar(cornerRadiusTopRight=6, cornerRadiusBottomRight=6, height=22)
        .encode(
            y=alt.Y("distance_band:N", sort=band_order, axis=alt.Axis(title=None, labelColor=theme["text"], grid=False)),
            x=alt.X("avg_fare:Q", axis=alt.Axis(title="Average Fare ($)", labelColor=theme["axis_label"], gridColor=theme["grid"])),
            color=alt.Color(
                "distance_band:N",
                scale=alt.Scale(
                    domain=band_order,
                    range=["#06B6D4", "#3B82F6", "#8B5CF6", "#EC4899"],
                ),
                legend=None,
            ),
            tooltip=[
                alt.Tooltip("distance_band:N", title="Distance Band"),
                alt.Tooltip("trip_count:Q", format=",d", title="Total Trips"),
                alt.Tooltip("avg_fare:Q", format="$,.2f", title="Average Fare"),
                alt.Tooltip("avg_duration:Q", format=",.1f", title="Average Duration (min)"),
            ],
        )
        .properties(height=height)
        .configure_view(strokeWidth=0, fill=theme["bg"])
    )

    st.altair_chart(bars, use_container_width=True)


def render_fare_efficiency_histogram(df: pd.DataFrame, height: int = 220):
    """Render fare per mile efficiency distribution histogram."""
    if df.empty:
        st.info("No trip records available for efficiency distribution.")
        return

    df_eff = df.copy()
    df_eff["fare_amount"] = df_eff["fare_amount"].astype(float)
    df_eff["trip_distance"] = df_eff["trip_distance"].astype(float)
    
    if "fare_per_mile" not in df_eff.columns:
        df_eff["fare_per_mile"] = df_eff.apply(
            lambda r: (r["fare_amount"] / r["trip_distance"]) if r["trip_distance"] > 0 else 0.0, axis=1
        )

    df_eff = df_eff[df_eff["fare_per_mile"] > 0]
    if df_eff.empty:
        st.info("No valid non-zero fare per mile data available.")
        return

    theme = get_theme_colors()

    hist = (
        alt.Chart(df_eff)
        .mark_bar(color=theme["cyan"], opacity=0.82, cornerRadiusTopLeft=3, cornerRadiusTopRight=3)
        .encode(
            x=alt.X("fare_per_mile:Q", bin=alt.Bin(maxbins=20), axis=alt.Axis(title="Fare per Mile ($/mi)", labelColor=theme["axis_label"], gridColor=theme["grid"])),
            y=alt.Y("count()", axis=alt.Axis(title="Number of Trips", labelColor=theme["axis_label"], gridColor=theme["grid"])),
            tooltip=[alt.Tooltip("fare_per_mile:Q", bin=True, title="Fare / Mile Range"), alt.Tooltip("count()", title="Trip Count")],
        )
        .properties(height=height)
        .configure_view(strokeWidth=0, fill=theme["bg"])
    )

    st.altair_chart(hist, use_container_width=True)


def render_benchmark_card(
    title: str,
    selected_val: float,
    fleet_avg: float,
    unit: str = "$",
    color: str = "#06B6D4",
    is_currency: bool = False,
    is_rating: bool = False,
    tooltip_desc: str = "Metric comparison against fleet average",
):
    """Render a colorful horizontal benchmark card comparing selected driver to fleet average."""
    diff_pct = (((selected_val - fleet_avg) / fleet_avg) * 100) if fleet_avg > 0 else 0.0

    if diff_pct >= 2.0:
        pill_text = f"↑ {diff_pct:.1f}% ABOVE FLEET"
        pill_bg = "rgba(16,185,129,0.14)"
        pill_color = "#10B981"
        pill_border = "rgba(16,185,129,0.3)"
    elif diff_pct <= -2.0:
        pill_text = f"↓ {abs(diff_pct):.1f}% BELOW FLEET"
        pill_bg = "rgba(239,68,68,0.14)"
        pill_color = "#EF4444"
        pill_border = "rgba(239,68,68,0.3)"
    else:
        pill_text = "NEAR FLEET AVERAGE"
        pill_bg = "rgba(245,158,11,0.14)"
        pill_color = "#F59E0B"
        pill_border = "rgba(245,158,11,0.3)"

    if is_currency:
        sel_str = f"${selected_val:,.2f}"
        flt_str = f"${fleet_avg:,.2f}"
    elif is_rating:
        sel_str = f"{selected_val:.2f} / 5.0"
        flt_str = f"{fleet_avg:.2f} / 5.0"
    elif unit == "mi":
        sel_str = f"{selected_val:,.2f} mi"
        flt_str = f"{fleet_avg:,.2f} mi"
    elif unit == "trips":
        sel_str = f"{int(selected_val):,} trips"
        flt_str = f"{fleet_avg:,.1f} trips"
    else:
        sel_str = f"{selected_val:,.2f}"
        flt_str = f"{fleet_avg:,.2f}"

    max_scale = max(selected_val, fleet_avg) * 1.15 if max(selected_val, fleet_avg) > 0 else 1.0
    sel_width = min(100.0, (selected_val / max_scale) * 100.0) if max_scale > 0 else 0
    flt_width = min(100.0, (fleet_avg / max_scale) * 100.0) if max_scale > 0 else 0

    is_dark = st.session_state.get("theme_mode", "dark") == "dark"
    card_bg = "#151D2F" if is_dark else "#FFFFFF"
    text_color = "#F8FAFC" if is_dark else "#0F172A"
    sub_color = "#94A3B8" if is_dark else "#64748B"
    card_border = "rgba(148,163,184,0.16)" if is_dark else "#E2E8F0"

    html = f"""<div style="background:{card_bg}; border:1px solid {card_border}; border-radius:14px; padding:16px; margin-bottom:14px; box-shadow:0 2px 8px rgba(0,0,0,0.06);" title="{tooltip_desc}">
<div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
<div style="font-size:0.85rem; font-weight:700; color:{text_color}; text-transform:uppercase; letter-spacing:0.5px;">{title}</div>
<div style="font-size:0.72rem; font-weight:800; color:{pill_color}; background:{pill_bg}; border:1px solid {pill_border}; padding:3px 8px; border-radius:6px;">{pill_text}</div>
</div>
<div style="display:flex; align-items:baseline; justify-content:space-between; margin-bottom:10px;">
<div>
<span style="font-size:0.7rem; font-weight:600; color:{sub_color};">SELECTED DRIVER:</span>
<span style="font-size:1.15rem; font-weight:800; color:{color}; margin-left:6px;">{sel_str}</span>
</div>
<div>
<span style="font-size:0.7rem; font-weight:600; color:{sub_color};">FLEET AVG:</span>
<span style="font-size:0.92rem; font-weight:700; color:#64748B; margin-left:6px;">{flt_str}</span>
</div>
</div>
<div style="position:relative; height:20px; background:rgba(148,163,184,0.12); border-radius:6px; padding:2px; overflow:hidden;">
<div style="height:8px; width:{sel_width:.1f}%; background:{color}; border-radius:4px; margin-bottom:2px;" title="Selected Driver: {sel_str}"></div>
<div style="height:6px; width:{flt_width:.1f}%; background:#64748B; border-radius:3px; opacity:0.8;" title="Fleet Average: {flt_str}"></div>
</div>
</div>"""

    st.markdown(html, unsafe_allow_html=True)


def render_percentile_bar(label: str, percentile_val: float, color: str = "#06B6D4", tooltip_desc: str = "Percentage of drivers in the fleet dataset scoring below this value."):
    """Render colorful percentile positioning progress bar."""
    is_dark = st.session_state.get("theme_mode", "dark") == "dark"
    card_bg = "#151D2F" if is_dark else "#FFFFFF"
    text_color = "#F8FAFC" if is_dark else "#0F172A"

    html = f"""<div style="background:{card_bg}; border:1px solid rgba(148,163,184,0.16); border-radius:12px; padding:14px; margin-bottom:10px;" title="{tooltip_desc}">
<div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
<span style="font-size:0.82rem; font-weight:700; color:{text_color};">{label}</span>
<span style="font-size:0.9rem; font-weight:800; color:{color};">{percentile_val:.0f}th Percentile</span>
</div>
<div style="height:10px; border-radius:5px; background:rgba(148,163,184,0.14); overflow:hidden;">
<div style="height:100%; width:{min(100.0, percentile_val):.1f}%; background:{color}; border-radius:5px;"></div>
</div>
</div>"""

    st.markdown(html, unsafe_allow_html=True)


def render_normalized_dumbbell(df_indexes: pd.DataFrame, height: int = 220):
    """Render dumbbell comparison chart comparing Fleet Average Index (100) to Selected Driver Index."""
    if df_indexes.empty:
        st.info("No index data available for dumbbell chart.")
        return

    theme = get_theme_colors()

    lines = (
        alt.Chart(df_indexes)
        .mark_rule(color=theme["axis_label"], size=2.5)
        .encode(
            y=alt.Y("Metric:N", sort=None, axis=alt.Axis(title=None, labelColor=theme["text"], labelFontSize=12)),
            x=alt.X("Fleet Index:Q", axis=alt.Axis(title="Normalized Index (Fleet Average = 100)", labelColor=theme["axis_label"], gridColor=theme["grid"])),
            x2="Driver Index:Q",
        )
    )

    fleet_dots = (
        alt.Chart(df_indexes)
        .mark_point(color="#64748B", size=100, filled=True)
        .encode(
            y=alt.Y("Metric:N"),
            x=alt.X("Fleet Index:Q"),
            tooltip=[alt.Tooltip("Metric:N"), alt.Tooltip("Fleet Index:Q", title="Fleet Baseline (100)")]
        )
    )

    driver_dots = (
        alt.Chart(df_indexes)
        .mark_point(color=theme["primary"], size=130, filled=True)
        .encode(
            y=alt.Y("Metric:N"),
            x=alt.X("Driver Index:Q"),
            tooltip=[alt.Tooltip("Metric:N"), alt.Tooltip("Driver Index:Q", format=",.1f", title="Selected Driver Index")]
        )
    )

    chart = (lines + fleet_dots + driver_dots).properties(height=height).configure_view(strokeWidth=0, fill=theme["bg"])
    st.altair_chart(chart, use_container_width=True)


def render_calendar_heatmap(
    df: pd.DataFrame,
    date_col: str = "date_key",
    value_col: str = "total_revenue",
    height: int = 240,
):
    """Render calendar-style weekday intensity heatmap for daily revenue."""
    if df.empty or date_col not in df.columns:
        st.info("No revenue records are available for this period.")
        return

    df_hm = df.copy()
    df_hm["dt"] = pd.to_datetime(df_hm[date_col])
    df_hm["weekday"] = df_hm["dt"].dt.strftime("%a")
    df_hm["weekday_full"] = df_hm["dt"].dt.strftime("%A")
    df_hm["date_formatted"] = df_hm["dt"].dt.strftime("%B %d, %Y")
    df_hm["day_num"] = df_hm["dt"].dt.day
    df_hm["week_of_month"] = "Week " + (((df_hm["day_num"] - 1) // 7) + 1).astype(str)
    
    if "is_weekend" in df_hm.columns:
        df_hm["day_type"] = df_hm["is_weekend"].map({True: "Weekend", False: "Weekday"})
    else:
        df_hm["day_type"] = df_hm["dt"].dt.dayofweek.apply(lambda w: "Weekend" if w >= 5 else "Weekday")

    min_val = float(df_hm[value_col].min())
    max_val = float(df_hm[value_col].max())
    q25 = float(df_hm[value_col].quantile(0.25))
    q50 = float(df_hm[value_col].quantile(0.50))
    q75 = float(df_hm[value_col].quantile(0.75))

    theme = get_theme_colors()

    heatmap = (
        alt.Chart(df_hm)
        .mark_rect(cornerRadius=4, stroke=theme["bg"], strokeWidth=2)
        .encode(
            x=alt.X(
                "weekday:O",
                sort=["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
                axis=alt.Axis(
                    title=None,
                    labelColor=theme["text"],
                    grid=False,
                    tickColor=None,
                    domainColor=theme["grid"],
                    labelFontSize=11,
                ),
            ),
            y=alt.Y(
                "week_of_month:O",
                sort="ascending",
                axis=alt.Axis(
                    title=None,
                    labelColor=theme["axis_label"],
                    grid=False,
                    labelFontSize=11,
                ),
            ),
            color=alt.Color(
                f"{value_col}:Q",
                scale=alt.Scale(
                    domain=[min_val, q25, q50, q75, max_val],
                    range=["#1E3A8A", "#3B82F6", "#06B6D4", "#10B981", "#F59E0B"],
                ),
                legend=alt.Legend(
                    title="Revenue ($)",
                    orient="bottom",
                    labelColor=theme["axis_label"],
                    titleColor=theme["text"],
                    gradientLength=200,
                ),
            ),
            tooltip=[
                alt.Tooltip("date_formatted:N", title="Date"),
                alt.Tooltip("weekday_full:N", title="Day"),
                alt.Tooltip(f"{value_col}:Q", format="$,.2f", title="Total Revenue"),
                alt.Tooltip("total_trips:Q", format=",d", title="Total Trips") if "total_trips" in df_hm.columns else alt.Tooltip(value_col),
                alt.Tooltip("average_fare:Q", format="$,.2f", title="Average Fare") if "average_fare" in df_hm.columns else alt.Tooltip(value_col),
                alt.Tooltip("day_type:N", title="Day Type"),
            ],
        )
        .properties(height=height)
        .configure_view(strokeWidth=0, fill=theme["bg"])
    )

    st.altair_chart(heatmap, use_container_width=True)


def render_bubble_scatter(
    df: pd.DataFrame,
    x_col: str = "total_trips",
    y_col: str = "total_revenue",
    size_col: str = "average_fare",
    category_col: str = "is_weekend",
    height: int = 280,
):
    """Render Revenue vs Trip Volume bubble scatter plot with cyan dashed trend line."""
    if df.empty:
        st.info("No revenue records are available for this period.")
        return

    df_sc = df.copy()
    if "date_key" in df_sc.columns:
        df_sc["date_formatted"] = pd.to_datetime(df_sc["date_key"]).dt.strftime("%b %d, %Y")
    else:
        df_sc["date_formatted"] = "N/A"

    if category_col in df_sc.columns:
        if df_sc[category_col].dtype == bool:
            df_sc["day_type"] = df_sc[category_col].map({True: "Weekend", False: "Weekday"})
        else:
            df_sc["day_type"] = df_sc[category_col].astype(str)
    else:
        df_sc["day_type"] = "Weekday"

    theme = get_theme_colors()

    enc_kwargs = {
        "x": alt.X(
            f"{x_col}:Q",
            axis=alt.Axis(
                title=x_col.replace("_", " ").title(),
                titleColor=theme["axis_label"],
                labelColor=theme["axis_label"],
                gridColor=theme["grid"],
            ),
        ),
        "y": alt.Y(
            f"{y_col}:Q",
            axis=alt.Axis(
                title=y_col.replace("_", " ").title(),
                titleColor=theme["axis_label"],
                labelColor=theme["axis_label"],
                gridColor=theme["grid"],
            ),
        ),
        "tooltip": [
            alt.Tooltip("date_formatted:N", title="Date") if "date_formatted" in df_sc.columns else alt.Tooltip(f"{x_col}:Q"),
            alt.Tooltip(f"{x_col}:Q", format=",.2f", title=x_col.replace("_", " ").title()),
            alt.Tooltip(f"{y_col}:Q", format="$,.2f", title=y_col.replace("_", " ").title()),
        ],
    }

    if size_col and size_col in df_sc.columns:
        enc_kwargs["size"] = alt.Size(
            f"{size_col}:Q",
            legend=alt.Legend(
                title=size_col.replace("_", " ").title(),
                labelColor=theme["axis_label"],
                titleColor=theme["text"],
                orient="right",
            ),
            scale=alt.Scale(range=[60, 260]),
        )
        enc_kwargs["tooltip"].append(alt.Tooltip(f"{size_col}:Q", format="$,.2f" if "fare" in size_col or "revenue" in size_col else ",.2f", title=size_col.replace("_", " ").title()))

    if "day_type" in df_sc.columns:
        enc_kwargs["color"] = alt.Color(
            "day_type:N",
            scale=alt.Scale(
                domain=["Weekday", "Weekend"],
                range=["#3B82F6", "#EC4899"],
            ),
            legend=alt.Legend(
                title="Category",
                labelColor=theme["text"],
                titleColor=theme["axis_label"],
                orient="right",
            ),
        )
        enc_kwargs["tooltip"].append(alt.Tooltip("day_type:N", title="Category"))

    circles = alt.Chart(df_sc).mark_circle(opacity=0.72, stroke="#1E293B", strokeWidth=1.5).encode(**enc_kwargs)

    trend_line = (
        alt.Chart(df_sc)
        .transform_regression(x_col, y_col)
        .mark_line(
            color="#06B6D4",
            strokeDash=[4, 4],
            size=2.5,
        )
    )

    chart = (
        (circles + trend_line)
        .properties(height=height)
        .configure_view(strokeWidth=0, fill=theme["bg"])
    )

    st.altair_chart(chart, use_container_width=True)


def render_scatter_chart(df: pd.DataFrame, x_col: str, y_col: str, size_col: str = None, color_col: str = None, height: int = 300):
    """Render scatter plot (alias to render_bubble_scatter)."""
    render_bubble_scatter(df, x_col=x_col, y_col=y_col, size_col=size_col, category_col=color_col or "is_weekend", height=height)


def render_trend_line_chart(df: pd.DataFrame, x_col: str, y_col: str, color: str = None, height: int = 260, title: str = None):
    """Render clean time-series line chart."""
    if df.empty:
        st.info("No data available for trend line chart.")
        return
    df = format_chart_data(df, x_col)
    theme = get_theme_colors()
    line = (
        alt.Chart(df)
        .mark_line(interpolate="monotone", color=color or theme["primary"], size=3)
        .encode(
            x=alt.X(f"{x_col}:O", axis=alt.Axis(title=None, labelColor=theme["axis_label"], gridColor=theme["grid"], labelAngle=-30)),
            y=alt.Y(f"{y_col}:Q", axis=alt.Axis(title=title or y_col.replace("_", " ").title(), labelColor=theme["axis_label"], gridColor=theme["grid"])),
            tooltip=[x_col, alt.Tooltip(y_col, format="$,.2f" if "revenue" in y_col or "fare" in y_col else ",.2f")]
        )
        .properties(height=height)
        .configure_view(strokeWidth=0, fill=theme["bg"])
    )
    st.altair_chart(line, use_container_width=True)


def render_gradient_area_chart(df: pd.DataFrame, x_col: str, y_col: str, color: str = None, height: int = 260, title: str = None):
    """Render smooth curved area chart with gradient fill."""
    if df.empty:
        st.info("No data available for gradient area chart.")
        return
    df = format_chart_data(df, x_col)
    theme = get_theme_colors()
    chart_color = color or theme["primary"]

    line = alt.Chart(df).mark_line(interpolate="monotone", color=chart_color, size=3.5).encode(
        x=alt.X(f"{x_col}:O", axis=alt.Axis(title=None, labelColor=theme["axis_label"], gridColor=theme["grid"], labelAngle=-30)),
        y=alt.Y(f"{y_col}:Q", axis=alt.Axis(title=title or y_col.replace("_", " ").title(), labelColor=theme["axis_label"], gridColor=theme["grid"])),
        tooltip=[x_col, alt.Tooltip(y_col, format="$,.2f" if "revenue" in y_col or "fare" in y_col else ",.2f")]
    )
    area = alt.Chart(df).mark_area(interpolate="monotone", opacity=0.22, color=chart_color).encode(
        x=alt.X(f"{x_col}:O"),
        y=alt.Y(f"{y_col}:Q")
    )
    chart = (area + line).properties(height=height).configure_view(strokeWidth=0, fill=theme["bg"])
    st.altair_chart(chart, use_container_width=True)


def render_area_chart(df: pd.DataFrame, x_col: str, y_col: str, color: str = None, height: int = 260, title: str = None):
    render_gradient_area_chart(df, x_col, y_col, color, height, title)


def render_vertical_bar_chart(df: pd.DataFrame, x_col: str, y_col: str, color: str = None, height: int = 260, title: str = None):
    """Render vertical rounded bar chart."""
    if df.empty:
        st.info("No data available for vertical bar chart.")
        return
    df = format_chart_data(df, x_col)
    theme = get_theme_colors()
    bars = (
        alt.Chart(df)
        .mark_bar(color=color or theme["secondary"], cornerRadiusTopLeft=6, cornerRadiusTopRight=6, size=20)
        .encode(
            x=alt.X(f"{x_col}:O", axis=alt.Axis(title=None, labelColor=theme["axis_label"], gridColor=theme["grid"], labelAngle=-30)),
            y=alt.Y(f"{y_col}:Q", axis=alt.Axis(title=title or y_col.replace("_", " ").title(), labelColor=theme["axis_label"], gridColor=theme["grid"])),
            tooltip=[x_col, alt.Tooltip(y_col, format="$,.2f" if "revenue" in y_col or "fare" in y_col else ",.2f")]
        )
        .properties(height=height)
        .configure_view(strokeWidth=0, fill=theme["bg"])
    )
    st.altair_chart(bars, use_container_width=True)


def render_bar_chart(df: pd.DataFrame, x_col: str, y_col: str, color: str = None, height: int = 260, title: str = None):
    render_vertical_bar_chart(df, x_col, y_col, color, height, title)


def render_horizontal_rank_chart(df: pd.DataFrame, y_col: str, x_col: str, color: str = None, height: int = 260, title: str = None):
    """Render horizontal bar chart for rankings and feature importances."""
    if df.empty:
        st.info("No data available for horizontal rank chart.")
        return
    theme = get_theme_colors()
    chart = (
        alt.Chart(df)
        .mark_bar(color=color or theme["purple"], cornerRadiusTopRight=6, cornerRadiusBottomRight=6, height=18)
        .encode(
            y=alt.Y(f"{y_col}:N", sort="-x", axis=alt.Axis(title=None, labelColor=theme["text"], gridColor=None)),
            x=alt.X(f"{x_col}:Q", axis=alt.Axis(title=title or x_col.replace("_", " ").title(), labelColor=theme["axis_label"], gridColor=theme["grid"])),
            tooltip=[y_col, alt.Tooltip(x_col, format="$,.2f" if "revenue" in x_col or "fare" in x_col else ",.2f")]
        )
        .properties(height=height)
        .configure_view(strokeWidth=0, fill=theme["bg"])
    )
    st.altair_chart(chart, use_container_width=True)


def render_horizontal_bar_chart(df: pd.DataFrame, y_col: str, x_col: str, color: str = None, height: int = 260, title: str = None):
    render_horizontal_rank_chart(df, y_col, x_col, color, height, title)


def render_feature_importance_chart(df: pd.DataFrame, feature_col: str = "Feature", importance_col: str = "Importance", height: int = 240):
    render_horizontal_rank_chart(df, y_col=feature_col, x_col=importance_col, color="#8B5CF6", height=height, title="Importance Weight")


def render_grouped_bar_chart(df: pd.DataFrame, x_col: str, y_col: str, group_col: str, height: int = 260):
    """Render grouped bar comparison chart."""
    if df.empty:
        st.info("No data available for grouped bar chart.")
        return
    theme = get_theme_colors()
    chart = (
        alt.Chart(df)
        .mark_bar(cornerRadiusTopLeft=4, cornerRadiusTopRight=4)
        .encode(
            x=alt.X(f"{group_col}:N", axis=None),
            y=alt.Y(f"{y_col}:Q", axis=alt.Axis(title=y_col.replace("_", " ").title(), labelColor=theme["axis_label"], gridColor=theme["grid"])),
            color=alt.Color(f"{group_col}:N", scale=alt.Scale(range=["#3B82F6", "#10B981", "#8B5CF6", "#F59E0B"]), legend=alt.Legend(labelColor=theme["text"])),
            column=alt.Column(f"{x_col}:N", header=alt.Header(labelColor=theme["text"], title=None)),
            tooltip=[x_col, group_col, alt.Tooltip(y_col, format="$,.2f" if "revenue" in y_col or "fare" in y_col else ",.2f")]
        )
        .properties(height=height)
        .configure_view(strokeWidth=0, fill=theme["bg"])
    )
    st.altair_chart(chart, use_container_width=True)


def render_stacked_bar_chart(df: pd.DataFrame, x_col: str, y_col: str, stack_col: str, height: int = 260):
    """Render stacked bar chart."""
    if df.empty:
        st.info("No data available for stacked bar chart.")
        return
    theme = get_theme_colors()
    chart = (
        alt.Chart(df)
        .mark_bar()
        .encode(
            x=alt.X(f"{x_col}:O", axis=alt.Axis(title=None, labelColor=theme["axis_label"], gridColor=theme["grid"])),
            y=alt.Y(f"{y_col}:Q", axis=alt.Axis(title=y_col.replace("_", " ").title(), labelColor=theme["axis_label"], gridColor=theme["grid"])),
            color=alt.Color(f"{stack_col}:N", scale=alt.Scale(range=["#3B82F6", "#10B981", "#8B5CF6", "#F59E0B"]), legend=alt.Legend(labelColor=theme["text"])),
            tooltip=[x_col, stack_col, alt.Tooltip(y_col, format="$,.2f" if "revenue" in y_col or "fare" in y_col else ",.2f")]
        )
        .properties(height=height)
        .configure_view(strokeWidth=0, fill=theme["bg"])
    )
    st.altair_chart(chart, use_container_width=True)


def render_donut_chart(df: pd.DataFrame, category_col: str, value_col: str, height: int = 240, title: str = None):
    """Render modern vibrant Donut chart."""
    if df.empty:
        st.info("No data available for donut chart.")
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
                scale=alt.Scale(range=["#3B82F6", "#10B981", "#8B5CF6", "#F59E0B", "#EC4899", "#06B6D4"]),
                legend=alt.Legend(orient="right", labelColor=theme["text"], titleColor=theme["axis_label"], title=None)
            ),
            tooltip=[category_col, alt.Tooltip(value_col, format="$,.2f" if "revenue" in value_col else ",.2f")]
        )
        .properties(height=height)
        .configure_view(strokeWidth=0, fill=theme["bg"])
    )
    st.altair_chart(chart, use_container_width=True)


def render_histogram(df: pd.DataFrame, col: str, bins: int = 20, color: str = None, height: int = 220, title: str = None):
    """Render distribution histogram."""
    if df.empty or col not in df.columns:
        st.info("No data available for histogram.")
        return
    theme = get_theme_colors()
    hist = (
        alt.Chart(df)
        .mark_bar(color=color or theme["cyan"], opacity=0.8, cornerRadiusTopLeft=3, cornerRadiusTopRight=3)
        .encode(
            x=alt.X(f"{col}:Q", bin=alt.Bin(maxbins=bins), axis=alt.Axis(title=title or col.replace("_", " ").title(), labelColor=theme["axis_label"], gridColor=theme["grid"])),
            y=alt.Y("count()", axis=alt.Axis(title="Count", labelColor=theme["axis_label"], gridColor=theme["grid"])),
            tooltip=[alt.Tooltip(f"{col}:Q", bin=True, title=col), alt.Tooltip("count()", title="Frequency")]
        )
        .properties(height=height)
        .configure_view(strokeWidth=0, fill=theme["bg"])
    )
    st.altair_chart(hist, use_container_width=True)


def render_distribution_chart(df: pd.DataFrame, col: str, bins: int = 20, color: str = None, height: int = 220):
    render_histogram(df, col, bins, color, height)


def render_heatmap(df: pd.DataFrame, x_col: str, y_col: str, value_col: str, height: int = 260):
    """Render 2D intensity heatmap."""
    render_calendar_heatmap(df, date_col=x_col if x_col in df.columns else "date_key", value_col=value_col, height=height)


def render_risk_ring(probability: float, risk_level: str = "Medium", title: str = "Risk Score"):
    """Render circular progress ring indicator for risk probability."""
    prob_percent = round(probability * 100, 1)
    if prob_percent >= 65.0:
        ring_color = "#EF4444"
        bg_glow = "rgba(239,68,68,0.12)"
    elif prob_percent >= 35.0:
        ring_color = "#F59E0B"
        bg_glow = "rgba(245,158,11,0.12)"
    else:
        ring_color = "#10B981"
        bg_glow = "rgba(16,185,129,0.12)"

    html = f"""<div style="background:{bg_glow}; border:2px solid {ring_color}40; border-radius:16px; padding:20px; text-align:center; box-shadow:0 4px 16px rgba(0,0,0,0.15);">
<div style="font-size:0.8rem; font-weight:700; color:#94A3B8; text-transform:uppercase; letter-spacing:0.5px;">{title}</div>
<div style="position:relative; width:110px; height:110px; margin:12px auto; display:flex; align-items:center; justify-content:center; border-radius:50%; background:conic-gradient({ring_color} {prob_percent*3.6}deg, rgba(148,163,184,0.14) 0deg);">
<div style="width:84px; height:84px; border-radius:50%; background:#111827; display:flex; flex-direction:column; align-items:center; justify-content:center;">
<span style="font-size:1.35rem; font-weight:800; color:#F8FAFC;">{prob_percent}%</span>
<span style="font-size:0.68rem; font-weight:700; color:{ring_color}; text-transform:uppercase;">{risk_level}</span>
</div>
</div>
</div>"""
    st.markdown(html, unsafe_allow_html=True)


def render_progress_ring(value: float, max_val: float = 100.0, label: str = "Progress", color: str = "#3B82F6"):
    """Render normalized progress ring."""
    percent = min(100.0, max(0.0, (value / max_val) * 100.0)) if max_val > 0 else 0
    html = f"""<div style="background:#111827; border:1px solid rgba(148,163,184,0.14); border-radius:14px; padding:16px; text-align:center;">
<div style="font-size:0.78rem; font-weight:600; color:#94A3B8;">{label}</div>
<div style="position:relative; width:90px; height:90px; margin:10px auto; display:flex; align-items:center; justify-content:center; border-radius:50%; background:conic-gradient({color} {percent*3.6}deg, rgba(148,163,184,0.14) 0deg);">
<div style="width:68px; height:68px; border-radius:50%; background:#111827; display:flex; align-items:center; justify-content:center;">
<span style="font-size:1.1rem; font-weight:800; color:#F8FAFC;">{percent:.0f}%</span>
</div>
</div>
</div>"""
    st.markdown(html, unsafe_allow_html=True)


def render_bullet_comparison(selected_val: float, fleet_avg: float, label: str = "Metric Comparison", unit: str = "$"):
    """Render bullet comparison bar comparing selected value against fleet average."""
    ratio = (selected_val / fleet_avg) if fleet_avg > 0 else 1.0
    bar_color = "#10B981" if ratio >= 1.0 else "#F59E0B"
    html = f"""<div style="background:#111827; border:1px solid rgba(148,163,184,0.14); border-radius:12px; padding:14px; margin-bottom:10px;">
<div style="display:flex; justify-content:space-between; font-size:0.85rem; font-weight:700; color:#F8FAFC; margin-bottom:6px;">
<span>{label}</span>
<span>{unit}{selected_val:,.2f} <span style="font-size:0.75rem; color:#94A3B8;">(Fleet Avg: {unit}{fleet_avg:,.2f})</span></span>
</div>
<div style="position:relative; height:12px; border-radius:6px; background:rgba(148,163,184,0.16); overflow:hidden;">
<div style="height:100%; width:{min(100.0, ratio*50.0)}%; background:{bar_color}; border-radius:6px;"></div>
<div style="position:absolute; top:0; left:50%; width:2px; height:100%; background:#3B82F6;"></div>
</div>
</div>"""
    st.markdown(html, unsafe_allow_html=True)


def render_anomaly_timeseries(df: pd.DataFrame, date_col: str = "date_key", value_col: str = "total_revenue", anomaly_col: str = "is_anomaly", height: int = 280):
    render_anomaly_chart(df, date_col, value_col, anomaly_col, height)


def render_anomaly_chart(df: pd.DataFrame, date_col: str = "date_key", value_col: str = "total_revenue", anomaly_col: str = "is_anomaly", height: int = 280):
    """Render time series with overlaid anomaly highlight markers."""
    if df.empty:
        st.info("No data available for anomaly chart.")
        return
    df = format_chart_data(df, date_col)
    theme = get_theme_colors()
    line = (
        alt.Chart(df)
        .mark_line(interpolate="monotone", color=theme["cyan"], size=3)
        .encode(
            x=alt.X(f"{date_col}:O", axis=alt.Axis(labelColor=theme["axis_label"], gridColor=theme["grid"], labelAngle=-30)),
            y=alt.Y(f"{value_col}:Q", axis=alt.Axis(title="Revenue ($)", labelColor=theme["axis_label"], gridColor=theme["grid"])),
            tooltip=[date_col, alt.Tooltip(value_col, format="$,.2f")]
        )
    )
    if anomaly_col in df.columns:
        anom_df = df[df[anomaly_col] == True]
        if not anom_df.empty:
            points = (
                alt.Chart(anom_df)
                .mark_point(color=theme["red"], size=110, filled=True)
                .encode(
                    x=alt.X(f"{date_col}:O"),
                    y=alt.Y(f"{value_col}:Q"),
                    tooltip=[date_col, alt.Tooltip(value_col, format="$,.2f"), alt.Tooltip("z_score", format=",.2f", title="Z-Score")]
                )
            )
            chart = alt.layer(line, points)
        else:
            chart = line
    else:
        chart = line

    chart = chart.properties(height=height).configure_view(strokeWidth=0, fill=theme["bg"])
    st.altair_chart(chart, use_container_width=True)


def render_multi_metric_chart(df: pd.DataFrame, x_col: str, metric1: str = "total_revenue", metric2: str = "total_trips", height: int = 280):
    """Render dual-axis chart combining Revenue line/area + Trip Volume bars."""
    if df.empty:
        st.info("No data available for multi metric chart.")
        return
    df = format_chart_data(df, x_col)
    theme = get_theme_colors()
    base = alt.Chart(df).encode(
        x=alt.X(f"{x_col}:O", axis=alt.Axis(title=None, labelColor=theme["axis_label"], gridColor=theme["grid"], labelAngle=-30))
    )
    bars = base.mark_bar(color=theme["secondary"], opacity=0.35, cornerRadiusTopLeft=4, cornerRadiusTopRight=4, size=16).encode(
        y=alt.Y(f"{metric2}:Q", axis=alt.Axis(title="Total Trips", titleColor=theme["secondary"], labelColor=theme["secondary"], gridColor=None)),
        tooltip=[alt.Tooltip(x_col, title="Date"), alt.Tooltip(metric2, format=",d", title="Total Trips")]
    )
    line = base.mark_line(interpolate="monotone", color=theme["primary"], size=3.5).encode(
        y=alt.Y(f"{metric1}:Q", axis=alt.Axis(title="Revenue ($)", titleColor=theme["primary"], labelColor=theme["primary"], gridColor=theme["grid"])),
        tooltip=[alt.Tooltip(x_col, title="Date"), alt.Tooltip(metric1, format="$,.2f", title="Total Revenue")]
    )
    chart = alt.layer(bars, line).resolve_scale(y="independent").properties(height=height).configure_view(strokeWidth=0, fill=theme["bg"])
    st.altair_chart(chart, use_container_width=True)


def render_pipeline_flow():
    """Render visual ETL medallion architecture pipeline flow diagram."""
    html = """<div style="display:flex; align-items:center; justify-content:space-between; background:#111827; border:1px solid rgba(148,163,184,0.14); border-radius:14px; padding:16px; margin-bottom:1.5rem;">
<div style="text-align:center; flex:1;">
<div style="font-size:0.7rem; font-weight:700; color:#94A3B8;">RAW SOURCE</div>
<div style="font-weight:800; color:#3B82F6; margin-top:2px;">INGESTION</div>
</div>
<div style="color:#64748B;">➔</div>
<div style="text-align:center; flex:1;">
<div style="font-size:0.7rem; font-weight:700; color:#CD7F32;">BRONZE</div>
<div style="font-weight:800; color:#F8FAFC; margin-top:2px;">RAW LANDING</div>
</div>
<div style="color:#64748B;">➔</div>
<div style="text-align:center; flex:1;">
<div style="font-size:0.7rem; font-weight:700; color:#C0C0C0;">SILVER</div>
<div style="font-weight:800; color:#10B981; margin-top:2px;">CLEANED & REJECTED</div>
</div>
<div style="color:#64748B;">➔</div>
<div style="text-align:center; flex:1;">
<div style="font-size:0.7rem; font-weight:700; color:#FFD700;">GOLD</div>
<div style="font-weight:800; color:#8B5CF6; margin-top:2px;">STAR-SCHEMA MARTS</div>
</div>
</div>"""
    st.markdown(html, unsafe_allow_html=True)


def render_activity_timeline(events: list):
    """Render activity timeline."""
    if not events:
        st.info("No activity events available.")
        return
    for ev in events:
        st.markdown(f"• `{ev.get('timestamp', '')}` — **{ev.get('task_name', 'Task')}**: status `{ev.get('status', 'OK')}` ({ev.get('rows_inserted', 0)} rows)")


def render_sparkline(values: list, color: str = "#3B82F6", height: int = 40):
    """Render mini sparkline SVG data trend."""
    if not values or len(values) < 2:
        return
    min_v, max_v = min(values), max(values)
    rng = (max_v - min_v) if max_v > min_v else 1.0
    pts = []
    width = 100
    step = width / (len(values) - 1)
    for idx, v in enumerate(values):
        x = idx * step
        y = height - ((v - min_v) / rng * (height - 8) + 4)
        pts.append(f"{x:.1f},{y:.1f}")
    polyline = " ".join(pts)
    html = f"""<svg width="{width}" height="{height}" style="overflow:visible;"><polyline fill="none" stroke="{color}" stroke-width="2" points="{polyline}" /></svg>"""
    st.markdown(html, unsafe_allow_html=True)
