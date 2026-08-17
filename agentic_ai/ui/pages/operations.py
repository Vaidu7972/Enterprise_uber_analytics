import pandas as pd
import streamlit as st
from agentic_ai.tools.sql_tool import execute_read_only_query
from agentic_ai.ui.styles.icons import get_icon_svg
from agentic_ai.ui.components.cards import render_kpi_card, render_status_pill
from agentic_ai.ui.components.charts import (
    render_histogram,
    render_bar_chart,
    render_trip_fare_scatter,
    render_distance_band_chart,
    render_fare_efficiency_histogram,
)


def render_operations_page():
    """Render SaaS Operations Analytics Page with interactive yield scatter, distance band analysis, and Multimodal Incident Analyzer."""
    st.markdown("""<div class="page-header">
<h1>Operations Analytics</h1>
<p>Trip duration, distance distribution, passenger load efficiency, and multimodal vehicle incident response.</p>
</div>""", unsafe_allow_html=True)

    df_kpi = execute_read_only_query("SELECT * FROM gold.kpi_summary;")
    if not df_kpi.empty:
        k_dict = df_kpi.iloc[0].to_dict()
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            render_kpi_card("Avg Trip Distance", f"{float(k_dict.get('average_distance', 0)):,.2f} mi", "Activity", "Fleet Mileage", "#3B82F6", change_text="Fleet Avg", is_positive=True)
        with c2:
            render_kpi_card("Avg Trip Duration", f"{float(k_dict.get('average_trip_duration', 0)):,.1f} min", "Clock", "Transit Time", "#10B981", change_text="Transit Avg", is_positive=True)
        with c3:
            render_kpi_card("Total Fleet Trips", f"{int(k_dict.get('total_trips', 0)):,}", "ChartColumn", "Total Completed", "#F59E0B", change_text="Completed", is_positive=True)
        with c4:
            render_kpi_card("Total Revenue", f"${float(k_dict.get('total_revenue', 0)):,.2f}", "TrendingUp", "Gross Revenue", "#8B5CF6", change_text="Gross Volume", is_positive=True)

    st.divider()

    # Tabs: Fare vs Distance Scatter | Trip Distributions | Multimodal Incident Analyzer
    t1, t2, t3 = st.tabs(["Fare vs Distance Scatter", "Trip Distributions", "Multimodal Vehicle Incident Analyzer"])

    # =========================================================================
    # TAB 1: FARE vs DISTANCE SCATTER & MOBILITY YIELD DASHBOARD
    # =========================================================================
    with t1:
        df_trips_raw = execute_read_only_query(
            "SELECT trip_id, fare_amount, trip_distance, trip_duration_minutes, passenger_count FROM gold.fact_trip LIMIT 1000;"
        )

        if not df_trips_raw.empty:
            df_trips_raw["fare_amount"] = df_trips_raw["fare_amount"].astype(float)
            df_trips_raw["trip_distance"] = df_trips_raw["trip_distance"].astype(float)
            df_trips_raw["trip_duration_minutes"] = df_trips_raw["trip_duration_minutes"].astype(float)
            df_trips_raw["passenger_count"] = df_trips_raw["passenger_count"].fillna(1).astype(int)
            
            df_trips_raw["fare_per_mile"] = df_trips_raw.apply(
                lambda r: (r["fare_amount"] / r["trip_distance"]) if r["trip_distance"] > 0 else 0.0, axis=1
            )

            # Statistical IQR Outlier Threshold Calculation
            q1 = float(df_trips_raw["fare_per_mile"].quantile(0.25))
            q3 = float(df_trips_raw["fare_per_mile"].quantile(0.75))
            iqr = q3 - q1
            upper_thresh = q3 + 1.5 * iqr
            df_trips_raw["is_outlier"] = df_trips_raw["fare_per_mile"] > upper_thresh

            # Interactive Filter Controls
            st.markdown(f"""<div class="filter-bar">{get_icon_svg('Sliders', '#3B82F6', 18)} <b>Trip Dataset Filter Controls</b></div>""", unsafe_allow_html=True)
            
            f1, f2, f3, f4, f5 = st.columns([3, 3, 3, 3, 2])
            
            min_d_val = float(df_trips_raw["trip_distance"].min())
            max_d_val = float(df_trips_raw["trip_distance"].max())
            min_f_val = float(df_trips_raw["fare_amount"].min())
            max_f_val = float(df_trips_raw["fare_amount"].max())
            min_dur_val = float(df_trips_raw["trip_duration_minutes"].min())
            max_dur_val = float(df_trips_raw["trip_duration_minutes"].max())
            
            pass_options = sorted(df_trips_raw["passenger_count"].unique().tolist())

            with f1:
                sel_dist_range = st.slider("Distance (mi)", min_d_val, max_d_val, (min_d_val, max_d_val), key="ops_dist_slider")
            with f2:
                sel_fare_range = st.slider("Fare ($)", min_f_val, max_f_val, (min_f_val, max_f_val), key="ops_fare_slider")
            with f3:
                sel_dur_range = st.slider("Duration (min)", min_dur_val, max_dur_val, (min_dur_val, max_dur_val), key="ops_dur_slider")
            with f4:
                sel_pass_cnts = st.multiselect("Passengers", pass_options, default=pass_options, key="ops_pass_mselect")
            with f5:
                st.markdown("<div style='height:24px;'></div>", unsafe_allow_html=True)
                if st.button("🔄 Reset", key="btn_reset_ops_filters", use_container_width=True):
                    st.rerun()

            # Apply Filters
            mask = (
                (df_trips_raw["trip_distance"] >= sel_dist_range[0]) &
                (df_trips_raw["trip_distance"] <= sel_dist_range[1]) &
                (df_trips_raw["fare_amount"] >= sel_fare_range[0]) &
                (df_trips_raw["fare_amount"] <= sel_fare_range[1]) &
                (df_trips_raw["trip_duration_minutes"] >= sel_dur_range[0]) &
                (df_trips_raw["trip_duration_minutes"] <= sel_dur_range[1])
            )
            if sel_pass_cnts:
                mask = mask & (df_trips_raw["passenger_count"].isin(sel_pass_cnts))

            df_trips = df_trips_raw[mask].copy()

            if df_trips.empty:
                st.warning("⚠️ No trips match the selected filters. Please adjust filter ranges.")
            else:
                # Top 4 Calculated Metric Scorecards
                avg_fare_val = float(df_trips["fare_amount"].mean())
                avg_dist_val = float(df_trips["trip_distance"].mean())
                avg_dur_val = float(df_trips["trip_duration_minutes"].mean())
                
                df_valid_dist = df_trips[df_trips["trip_distance"] > 0]
                avg_fpm_val = float(df_valid_dist["fare_per_mile"].mean()) if not df_valid_dist.empty else 0.0

                m1, m2, m3, m4 = st.columns(4)
                with m1:
                    render_kpi_card("Average Fare", f"${avg_fare_val:,.2f}", "TrendingUp", "Filtered Subset", "#06B6D4")
                with m2:
                    render_kpi_card("Average Distance", f"{avg_dist_val:,.2f} mi", "Activity", "Filtered Subset", "#8B5CF6")
                with m3:
                    render_kpi_card("Average Duration", f"{avg_dur_val:,.1f} min", "Clock", "Filtered Subset", "#F59E0B")
                with m4:
                    render_kpi_card("Fare Per Mile", f"${avg_fpm_val:,.2f} / mi", "ShieldCheck", "Yield Efficiency", "#10B981")

                st.markdown("<div style='height:14px;'></div>", unsafe_allow_html=True)

                # Primary Graph Container
                st.markdown(f"""
                    <div style="background:#151D2F; border:1px solid rgba(59,130,246,0.3); border-radius:14px; padding:18px;">
                        <div style="margin-bottom:8px;">
                            <div style="font-weight:800; font-size:1.05rem; color:#F8FAFC; display:flex; align-items:center; gap:8px;">
                                {get_icon_svg('ScatterChart', '#06B6D4', 20)} Fare vs Trip Distance
                            </div>
                            <div style="font-size:0.78rem; color:#94A3B8; margin-top:2px;">See how trip distance, fare, duration and passenger count relate to each other.</div>
                        </div>
                """, unsafe_allow_html=True)

                render_trip_fare_scatter(
                    df_trips,
                    x_col="trip_distance",
                    y_col="fare_amount",
                    size_col="trip_duration_minutes",
                    category_col="passenger_count",
                    height=300,
                )

                # Pearson Correlation & Dynamic Insight
                corr_val = float(df_trips["trip_distance"].corr(df_trips["fare_amount"])) if len(df_trips) > 1 else 0.0

                if corr_val >= 0.70:
                    corr_label = "Strong Positive Relationship"
                elif corr_val >= 0.40:
                    corr_label = "Moderate Positive Relationship"
                elif corr_val >= 0.10:
                    corr_label = "Weak Positive Relationship"
                elif corr_val >= -0.09:
                    corr_label = "Little / No Linear Relationship"
                elif corr_val >= -0.39:
                    corr_label = "Weak Negative Relationship"
                elif corr_val >= -0.69:
                    corr_label = "Moderate Negative Relationship"
                else:
                    corr_label = "Strong Negative Relationship"

                outlier_cnt = int(df_trips["is_outlier"].sum())

                s_col1, s_col2 = st.columns([3, 1])
                with s_col1:
                    st.markdown(f"""
                        <div style="padding:10px 12px; background:rgba(6,182,212,0.08); border-left:3px solid #06B6D4; border-radius:6px; font-size:0.8rem; color:#CBD5E1;">
                            💡 <b>Dynamic Insight:</b> Trip distance and fare amount show a <b>{corr_label.lower()}</b> (correlation <b>{corr_val:.2f}</b>). Flagged <b>{outlier_cnt}</b> statistical IQR yield outliers. <i>Note: Correlation describes association and does not prove causation.</i>
                        </div>
                    """, unsafe_allow_html=True)
                with s_col2:
                    st.markdown(f"""
                        <div style="background:rgba(139,92,246,0.1); border:1px solid rgba(139,92,246,0.25); border-radius:8px; padding:6px 10px; text-align:center;">
                            <div style="font-size:0.68rem; font-weight:700; color:#8B5CF6; text-transform:uppercase;">Distance ↔ Fare</div>
                            <div style="font-size:1.05rem; font-weight:800; color:#F8FAFC; margin-top:2px;">{corr_val:.2f}</div>
                            <div style="font-size:0.65rem; color:#94A3B8;">{corr_label}</div>
                        </div>
                    """, unsafe_allow_html=True)

                st.markdown("</div>", unsafe_allow_html=True)
                st.divider()

                # Secondary Row: Distance Band Analysis (Left) vs Fare Efficiency Histogram (Right)
                row2_col1, row2_col2 = st.columns(2)
                with row2_col1:
                    st.markdown(f"""<div class="saas-card-title">{get_icon_svg('ChartColumn', '#06B6D4', 18)} Fare by Distance Band</div>""", unsafe_allow_html=True)
                    render_distance_band_chart(df_trips, height=220)
                with row2_col2:
                    st.markdown(f"""<div class="saas-card-title">{get_icon_svg('Activity', '#10B981', 18)} Fare Efficiency Distribution (Yield / Mile)</div>""", unsafe_allow_html=True)
                    render_fare_efficiency_histogram(df_trips, height=220)

                # Formatted Detailed Data Table (Below Charts)
                st.divider()
                st.markdown(f"""<div class="saas-card-title">{get_icon_svg('Database', '#8B5CF6', 18)} Detailed Trip Dataset Records ({len(df_trips):,} Filtered Records)</div>""", unsafe_allow_html=True)

                df_table = df_trips.copy()
                df_table_disp = pd.DataFrame()
                df_table_disp["Trip ID"] = df_table["trip_id"].astype(str)
                df_table_disp["Fare ($)"] = df_table["fare_amount"].apply(lambda v: f"${v:,.2f}")
                df_table_disp["Distance (mi)"] = df_table["trip_distance"].apply(lambda v: f"{v:,.2f} mi")
                df_table_disp["Duration (min)"] = df_table["trip_duration_minutes"].apply(lambda v: f"{v:,.1f} min")
                df_table_disp["Passengers"] = df_table["passenger_count"]
                df_table_disp["Fare / Mile ($)"] = df_table["fare_per_mile"].apply(lambda v: f"${v:,.2f} / mi")

                st.dataframe(df_table_disp, use_container_width=True, hide_index=True)
                st.download_button("Export Filtered Trips CSV", df_table.to_csv(index=False), "filtered_trips.csv", "text/csv")

    # =========================================================================
    # TAB 2: TRIP DISTRIBUTIONS
    # =========================================================================
    with t2:
        st.markdown(f"""<div class="saas-card-title">{get_icon_svg('ChartColumn', '#10B981', 18)} Distance & Duration Distribution Histograms</div>""", unsafe_allow_html=True)
        df_dist = execute_read_only_query("SELECT trip_distance, trip_duration_minutes, passenger_count FROM gold.fact_trip LIMIT 500;")
        if not df_dist.empty:
            h1, h2 = st.columns(2)
            with h1:
                st.markdown("**Trip Distance Density (Miles)**")
                render_histogram(df_dist, "trip_distance", bins=20, color="#3B82F6", height=220)
            with h2:
                st.markdown("**Trip Duration Density (Minutes)**")
                render_histogram(df_dist, "trip_duration_minutes", bins=20, color="#10B981", height=220)

            st.markdown("**Passenger Count Breakdown**")
            p_counts = df_dist["passenger_count"].value_counts().reset_index()
            p_counts.columns = ["passenger_count", "trip_count"]
            render_bar_chart(p_counts, "passenger_count", "trip_count", color="#8B5CF6", height=200)

    # =========================================================================
    # TAB 3: MULTIMODAL VEHICLE INCIDENT ANALYZER
    # =========================================================================
    with t3:
        st.markdown(f"""<div class="saas-card-title">{get_icon_svg('ShieldAlert', '#EF4444', 20)} Gemini Multimodal Vehicle Damage Assessment</div>""", unsafe_allow_html=True)
        
        inc_col1, inc_col2 = st.columns([1, 1])
        with inc_col1:
            uploaded_file = st.file_uploader("Upload Vehicle Damage Image (PNG / JPG)", type=["png", "jpg", "jpeg"], key="ops_img_uploader")
            if uploaded_file:
                st.image(uploaded_file, caption="Uploaded Incident Photo", use_container_width=True)
        
        with inc_col2:
            inc_desc = st.text_area("Incident Description & Location Notes", placeholder="e.g. Rear bumper collision near airport highway corridor during heavy rain...", key="ops_img_notes")
            run_btn = st.button("🔍 Run Gemini Multimodal Analysis", key="btn_run_multimodal", type="primary", use_container_width=True)

        if run_btn:
            if uploaded_file or inc_desc.strip():
                with st.spinner("Analyzing damage image & cross-referencing Support SOPs..."):
                    from agentic_ai.multimodal.incident_analyzer import analyze_incident_multimodal
                    from agentic_ai.memory.persistent_memory import create_pending_action

                    img_bytes = uploaded_file.read() if uploaded_file else None
                    img_mime = uploaded_file.type if uploaded_file else "image/jpeg"

                    result = analyze_incident_multimodal(description=inc_desc, image_bytes=img_bytes, image_mime=img_mime)

                    act_id = create_pending_action(
                        action_type="CREATE_SUPPORT_TICKET",
                        target_entity="VEHICLE_ACCIDENT_SOP",
                        details=f"Multimodal Incident Assessment: {inc_desc or 'Damage photo submitted'}. Preliminary evaluation completed."
                    )

                    st.markdown("### Assessment Output")
                    st.markdown(result.get("assessment", ""))
                    st.info(f"📋 Action #{act_id} logged as PENDING in Action Center for Manager approval.")
                    st.caption(f"ℹ️ {result.get('disclaimer')}")
            else:
                st.warning("Please upload an image or provide a description first.")
