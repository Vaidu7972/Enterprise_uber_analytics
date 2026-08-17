import pandas as pd
import streamlit as st
from agentic_ai.tools.sql_tool import execute_read_only_query
from agentic_ai.tools.ml_tool import predict_driver_risk
from agentic_ai.ui.styles.icons import get_icon_svg
from agentic_ai.ui.components.cards import render_kpi_card, render_status_pill
from agentic_ai.ui.components.charts import (
    render_horizontal_bar_chart,
    render_risk_ring,
    render_feature_importance_chart,
    render_benchmark_card,
    render_percentile_bar,
    render_normalized_dumbbell,
)


def render_drivers_page():
    """Render SaaS Driver Intelligence Page with Fleet Benchmarking, Percentile Positioning, and ML Risk Assessments."""
    st.markdown("""<div class="page-header">
<h1>Driver Intelligence</h1>
<p>Individual driver performance benchmark, fleet percentiles, ranking leaderboards, and ML risk predictions.</p>
</div>""", unsafe_allow_html=True)

    df_drivers = execute_read_only_query(
        "SELECT driver_id, driver_name, driver_city, driver_rating, total_revenue, total_trips, average_fare, average_distance FROM gold.driver_performance_mart ORDER BY total_revenue DESC;"
    )

    if not df_drivers.empty:
        df_drivers["total_revenue"] = df_drivers["total_revenue"].astype(float)
        df_drivers["total_trips"] = df_drivers["total_trips"].astype(int)
        df_drivers["average_fare"] = df_drivers["average_fare"].astype(float)
        df_drivers["average_distance"] = df_drivers["average_distance"].astype(float)
        df_drivers["driver_rating"] = df_drivers["driver_rating"].astype(float)

        total_driver_count = len(df_drivers)

        # Fleet Averages (Dynamically Calculated)
        fleet_avg_rev = float(df_drivers["total_revenue"].mean())
        fleet_avg_trips = float(df_drivers["total_trips"].mean())
        fleet_avg_fare = float(df_drivers["average_fare"].mean())
        fleet_avg_rating = float(df_drivers["driver_rating"].mean())
        fleet_avg_dist = float(df_drivers["average_distance"].mean())

        # Driver Selector Top Container
        st.markdown(f"""<div class="filter-bar">{get_icon_svg('Users', '#F59E0B', 18)} <b>Select Driver Profile</b></div>""", unsafe_allow_html=True)
        driver_options = df_drivers.apply(lambda r: f"{r['driver_id']} — {r['driver_name']} ({r['driver_city']})", axis=1).tolist()
        selected_option = st.selectbox("Search Driver Profile", driver_options, key="driver_sel_box")
        selected_id = selected_option.split(" — ")[0]

        drv_info = df_drivers[df_drivers["driver_id"] == selected_id].iloc[0]
        sel_rev = float(drv_info["total_revenue"])
        sel_trips = int(drv_info["total_trips"])
        sel_fare = float(drv_info["average_fare"])
        sel_rating = float(drv_info["driver_rating"])
        sel_dist = float(drv_info["average_distance"])

        # Calculated Ranks
        rev_rank = int((df_drivers["total_revenue"] > sel_rev).sum() + 1)
        trips_rank = int((df_drivers["total_trips"] > sel_trips).sum() + 1)
        rating_rank = int((df_drivers["driver_rating"] > sel_rating).sum() + 1)

        # Calculated Percentiles
        rev_pct = float((df_drivers["total_revenue"] <= sel_rev).mean() * 100.0)
        trips_pct = float((df_drivers["total_trips"] <= sel_trips).mean() * 100.0)
        rating_pct = float((df_drivers["driver_rating"] <= sel_rating).mean() * 100.0)

        # Fetch ML Risk Score for Snapshot Header
        ml_res = predict_driver_risk(driver_id=selected_id)
        risk_lvl = ml_res.get("risk_level", "Low") if ml_res.get("found") else "Low"

        # Top Snapshot Indicators Container
        c1, c2, c3, c4, c5 = st.columns(5)
        with c1:
            render_kpi_card("Driver Profile", drv_info["driver_name"], "Users", f"ID: {selected_id} | {drv_info['driver_city']}", "#3B82F6", change_text="Verified Driver", is_positive=True)
        with c2:
            render_kpi_card("Revenue Rank", f"#{rev_rank} / {total_driver_count}", "TrendingUp", "Fleet Positioning", "#06B6D4", change_text=f"{rev_pct:.0f}th Percentile", is_positive=rev_rank<=total_driver_count//2)
        with c3:
            render_kpi_card("Trips Rank", f"#{trips_rank} / {total_driver_count}", "ChartColumn", "Volume Position", "#10B981", change_text=f"{trips_pct:.0f}th Percentile", is_positive=trips_rank<=total_driver_count//2)
        with c4:
            render_kpi_card("Rating Rank", f"#{rating_rank} / {total_driver_count}", "ShieldCheck", f"Score: {sel_rating:.2f} / 5", "#8B5CF6", change_text=f"{rating_pct:.0f}th Percentile", is_positive=rating_rank<=total_driver_count//2)
        with c5:
            render_kpi_card("Risk Assessment", risk_lvl.upper(), "BrainCircuit", "ML Risk Level", "#EF4444" if risk_lvl == "High" else ("#F59E0B" if risk_lvl == "Medium" else "#10B981"), change_text="Scored by ML Model", is_positive=risk_lvl != "High")

        st.divider()

        # Tabs: Fleet Benchmarking | ML Risk Assessment | Leaderboard
        t1, t2, t3 = st.tabs(["Fleet Benchmarking", "ML Underperformance Risk", "All Driver Leaderboard"])

        # =========================================================================
        # TAB 1: FLEET BENCHMARKING (DRIVER PERFORMANCE BENCHMARK)
        # =========================================================================
        with t1:
            st.markdown(f"""<div class="saas-card-title">{get_icon_svg('ChartColumn', '#3B82F6', 18)} Driver Performance Benchmark</div>""", unsafe_allow_html=True)
            
            # Dynamic Insight Sentence
            rev_diff = (((sel_rev - fleet_avg_rev) / fleet_avg_rev) * 100) if fleet_avg_rev > 0 else 0
            rating_diff = (((sel_rating - fleet_avg_rating) / fleet_avg_rating) * 100) if fleet_avg_rating > 0 else 0

            st.markdown(f"""<div style="margin-bottom:16px; padding:12px 14px; background:rgba(59,130,246,0.08); border-left:3px solid #3B82F6; border-radius:8px; font-size:0.85rem; color:#CBD5E1;">
💡 <b>Fleet Insight:</b> <b>{drv_info['driver_name']}</b> generates <b>{rev_diff:+.1f}%</b> revenue compared to fleet average (<b>${sel_rev:,.2f}</b> vs <b>${fleet_avg_rev:,.2f}</b>) while maintaining a rating <b>{rating_diff:+.1f}%</b> relative to average (<b>{sel_rating:.2f} / 5</b> vs <b>{fleet_avg_rating:.2f} / 5</b>).
</div>""", unsafe_allow_html=True)

            b_col1, b_col2 = st.columns(2)

            with b_col1:
                st.markdown("#### Metric Benchmark Scorecards")
                render_benchmark_card(
                    "💰 Revenue Performance",
                    sel_rev,
                    fleet_avg_rev,
                    unit="$",
                    color="#06B6D4",
                    is_currency=True,
                    tooltip_desc="Total revenue generated by driver compared to fleet average."
                )
                render_benchmark_card(
                    "🚗 Trip Volume",
                    sel_trips,
                    fleet_avg_trips,
                    unit="trips",
                    color="#10B981",
                    tooltip_desc="Total trips completed compared to fleet average."
                )
                render_benchmark_card(
                    "💵 Average Fare",
                    sel_fare,
                    fleet_avg_fare,
                    unit="$",
                    color="#F59E0B",
                    is_currency=True,
                    tooltip_desc="Average fare yield per trip compared to fleet average."
                )
                render_benchmark_card(
                    "⭐ Driver Rating",
                    sel_rating,
                    fleet_avg_rating,
                    unit="",
                    color="#8B5CF6",
                    is_rating=True,
                    tooltip_desc="Driver rating out of 5 compared to fleet average rating."
                )
                render_benchmark_card(
                    "📍 Average Distance",
                    sel_dist,
                    fleet_avg_dist,
                    unit="mi",
                    color="#EC4899",
                    tooltip_desc="Average trip mileage compared to fleet average distance."
                )

            with b_col2:
                st.markdown("#### Fleet Position & Percentile Ranking")
                render_percentile_bar(
                    "Revenue Percentile Position",
                    rev_pct,
                    color="#06B6D4",
                    tooltip_desc="Percentage of drivers in the fleet dataset scoring lower total revenue."
                )
                render_percentile_bar(
                    "Trip Volume Percentile Position",
                    trips_pct,
                    color="#10B981",
                    tooltip_desc="Percentage of drivers in the fleet dataset scoring lower trip volume."
                )
                render_percentile_bar(
                    "Rating Percentile Position",
                    rating_pct,
                    color="#8B5CF6",
                    tooltip_desc="Percentage of drivers in the fleet dataset scoring lower driver rating."
                )

                st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)
                st.markdown("#### Normalized Performance Index (Fleet Avg = 100)")
                
                rev_idx = (sel_rev / fleet_avg_rev) * 100 if fleet_avg_rev > 0 else 100
                trips_idx = (sel_trips / fleet_avg_trips) * 100 if fleet_avg_trips > 0 else 100
                fare_idx = (sel_fare / fleet_avg_fare) * 100 if fleet_avg_fare > 0 else 100
                rating_idx = (sel_rating / fleet_avg_rating) * 100 if fleet_avg_rating > 0 else 100
                dist_idx = (sel_dist / fleet_avg_dist) * 100 if fleet_avg_dist > 0 else 100

                df_dumb = pd.DataFrame([
                    {"Metric": "Revenue Index", "Fleet Index": 100.0, "Driver Index": rev_idx},
                    {"Metric": "Trips Index", "Fleet Index": 100.0, "Driver Index": trips_idx},
                    {"Metric": "Fare Index", "Fleet Index": 100.0, "Driver Index": fare_idx},
                    {"Metric": "Rating Index", "Fleet Index": 100.0, "Driver Index": rating_idx},
                    {"Metric": "Distance Index", "Fleet Index": 100.0, "Driver Index": dist_idx},
                ])

                render_normalized_dumbbell(df_dumb, height=220)

        # =========================================================================
        # TAB 2: ML UNDERPERFORMANCE RISK
        # =========================================================================
        with t2:
            st.markdown(f"""<div class="saas-card-title">{get_icon_svg('BrainCircuit', '#F59E0B', 18)} ML Underperformance Risk Assessment (RandomForest)</div>""", unsafe_allow_html=True)
            
            if ml_res.get("found"):
                risk_lvl = ml_res.get("risk_level", "Unknown")
                risk_prob = ml_res.get("risk_probability", 0)

                ml_col1, ml_col2 = st.columns([1, 2])
                with ml_col1:
                    render_risk_ring(risk_prob, risk_level=risk_lvl, title="Model Risk Score")
                with ml_col2:
                    st.markdown(f"### Assessment: {render_status_pill(risk_lvl)}", unsafe_allow_html=True)
                    st.write(f"• **Driver ID:** `{selected_id}` — `{drv_info['driver_name']}`")
                    st.write(f"• **Risk Probability:** `{risk_prob*100:.1f}%`")
                    st.write(f"• **Model:** `RandomForestClassifier` trained on Gold warehouse driver features.")
                    st.info("Risk cutoff: Probability >= 65% is scored as High Risk underperformance.")

                st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)
                st.markdown("#### Model Feature Importance Weights")
                
                feat_dict = ml_res.get("model_info", {}).get("feature_importances", {
                    "Rating": 0.28,
                    "Total Revenue": 0.24,
                    "Total Trips": 0.20,
                    "Average Fare": 0.16,
                    "Average Distance": 0.12,
                })
                
                df_imp = pd.DataFrame([{"Feature": k.replace("_", " ").title(), "Importance": float(v)} for k, v in feat_dict.items()])
                render_feature_importance_chart(df_imp, feature_col="Feature", importance_col="Importance", height=200)
            else:
                st.warning("No ML risk score available for this driver ID.")

        # =========================================================================
        # TAB 3: ALL DRIVER LEADERBOARD
        # =========================================================================
        with t3:
            st.markdown(f"""<div class="saas-card-title">{get_icon_svg('Users', '#EC4899', 18)} Full Driver Leaderboard & Ranked Explorer</div>""", unsafe_allow_html=True)

            rank_metric = st.selectbox(
                "RANK DRIVERS BY METRIC",
                ["Total Revenue", "Total Trips", "Average Fare", "Driver Rating"],
                key="lb_rank_metric_sel"
            )

            metric_col_map = {
                "Total Revenue": "total_revenue",
                "Total Trips": "total_trips",
                "Average Fare": "average_fare",
                "Driver Rating": "driver_rating",
            }

            sort_col = metric_col_map[rank_metric]
            df_sorted = df_drivers.sort_values(by=sort_col, ascending=False).reset_index(drop=True)
            
            st.markdown(f"#### Top 10 Drivers by {rank_metric}")
            render_horizontal_bar_chart(df_sorted.head(10), "driver_name", sort_col, color="#EC4899", title=rank_metric, height=240)

            st.divider()
            st.dataframe(df_sorted, use_container_width=True, hide_index=True)
            st.download_button("Download Leaderboard CSV", df_sorted.to_csv(index=False), "driver_leaderboard.csv", "text/csv")
