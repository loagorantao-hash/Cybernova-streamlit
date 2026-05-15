import textwrap
"""
FR1-FR4, FR11-FR13, FR18-FR20 — Business Analyst Dashboard
Full analytics: KPI grid, charts, geo map, stats, conversion funnel.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
import pandas as pd
from frontend.components.layout import set_page_config, load_css, page_header, section_header
from frontend.components.sidebar import render_sidebar
from frontend.components.kpi_cards import render_kpi_grid_live
from frontend.components.charts import (
    bar_chart, donut_chart, line_chart, funnel_chart,
    choropleth_map, show
)
from frontend.components.data_tables import render_data_table
from frontend.components.filters import render_filter_panel
from backend.auth.auth_manager import AuthManager
from backend.database.queries import get_dataframe, run_query
from backend.analytics.kpi_engine import KPIEngine
from backend.analytics.geo_analyzer import prepare_choropleth_data, top_countries
from backend.analytics.statistics import descriptive_stats, correlation_matrix, revenue_statistics
from backend.live_engine import enable_auto_refresh
from frontend.components.live_kpi_card import render_live_kpi_card
from frontend.components.alert_card import render_alert_panel
from datetime import datetime

set_page_config("Analyst Dashboard")
load_css()

user = AuthManager.require_auth(allowed_roles=["analyst", "admin"])
render_sidebar("pages/02_Analyst_Dashboard.py")

# ── Data ──────────────────────────────────────────────────────────────────────
engine = KPIEngine()
summary_kpis = engine.summary_kpis()
total_records = summary_kpis.get("total_records", 0)

page_header("Analyst Dashboard",
            f"Full BI Analytics View — {total_records:,} records in Database", "")

# ── DB Connection Status ──────────────────────────────────────────────────────
if total_records > 0:
    st.success(f"✅ Connected to SQLite database — **{total_records:,}** records | revenue, leads, conversions all live from DB")
else:
    st.error("❌ Database unavailable or empty — check data/cybernova.db")

# ── Engines Initialization ───────────────────────────────────────────────────

# ── KPI Summary Section ───────────────────────────────────
st.markdown("### System-Wide Metrics")
render_kpi_grid_live(user_id=None)

st.html("<div style='height:24px'></div>")

# ── Main Tabs ─────────────────────────────────────────────────────────────────
tab_overview, tab_sales, tab_marketing, tab_geo, tab_stats, tab_logs = st.tabs([
    "Overview", "Sales & Conversion", "Marketing", "Geographic", "Statistics", "Log Viewer"
])

# ─── TAB 1: Overview ─────────────────────────────────────────────────────────
with tab_overview:
    col1, col2 = st.columns(2)

    with col1:
        section_header("Daily Visit Trend (FR1)")
        ts = engine.visits_over_time()
        if not ts.empty:
            show(line_chart(ts, "date", "visits", "Visits Over Time", "#2563eb"), key="an_ts")

    with col2:
        section_header("Revenue Over Time (FR3)")
        rev_ts = engine.revenue_over_time()
        if not rev_ts.empty:
            show(line_chart(rev_ts, "date", "revenue", "Daily Revenue", "#10b981"), key="an_rev_ts")

    col3, col4 = st.columns(2)
    with col3:
        section_header("Top Services by Visits (FR1)")
        svc = engine.service_usage_frequency(10)
        if not svc.empty:
            show(bar_chart(svc, "service_name", "visit_count", horizontal=True,
                           color="#06b6d4"), key="an_svc")

    with col4:
        section_header("HTTP Status Distribution")
        sc = engine.status_code_distribution()
        if not sc.empty:
            show(donut_chart(sc, "count", "status_category", "Status Codes"), key="an_sc")

    col5, col6 = st.columns(2)
    with col5:
        section_header("Hourly Traffic Heatmap")
        hd = engine.hourly_distribution()
        if not hd.empty:
            show(bar_chart(hd, "hour", "visits", "Traffic by Hour", "#8b5cf6"), key="an_hourly")

    with col6:
        section_header("Revenue by Service (FR1)")
        svc_rev = engine.service_revenue(10)
        if not svc_rev.empty:
            show(bar_chart(svc_rev, "service_name", "total_revenue",
                           horizontal=True, color="#f59e0b"), key="an_svc_rev")

# ─── TAB 2: Sales & Conversion (FR2, FR4) ────────────────────────────────────
with tab_sales:
    col1, col2 = st.columns([2, 1])

    with col1:
        section_header("Conversion Funnel (FR2 / FR4)")
        funnel_df = engine.sales_funnel()
        show(funnel_chart(funnel_df, "stage", "count", "Visit → Lead → Conversion Funnel"), key="an_funnel")

    with col2:
        section_header("Demo Conversion Metrics (FR2)")
        demo = engine.demo_conversion_ratio()
        st.html(textwrap.dedent(f"""
        <div class="glass-card">
            <div class="kpi-label">Total Demo Sessions</div>
            <div class="kpi-value">{demo.get('total_demos', 0):,}</div>
            <hr class="cn-divider">
            <div class="kpi-label">Conversions from Demo</div>
            <div class="kpi-value" style="font-size:22px;">{demo.get('conversions', 0):,}</div>
            <hr class="cn-divider">
            <div class="kpi-label">Demo Conversion Rate</div>
            <div class="kpi-value" style="color:#10b981;">{demo.get('conversion_rate', 0):.2f}%</div>
        </div>
        """))

    section_header("Conversion Rate by Service Type")
    conv_by_svc = get_dataframe("""
        SELECT service_name, COUNT(*) as visits, SUM(conversion_flag) as conversions
        FROM web_logs
        GROUP BY service_name
    """)
    if not conv_by_svc.empty:
        conv_by_svc["conv_rate"] = (conv_by_svc["conversions"] / conv_by_svc["visits"] * 100).round(2)
        show(bar_chart(conv_by_svc.sort_values("conv_rate", ascending=False),
                       "service_name", "conv_rate", "Conversion Rate % by Service",
                       color="#10b981"), key="an_conv_svc")

# ─── TAB 3: Marketing Effectiveness (FR3) ────────────────────────────────────
with tab_marketing:
    section_header("Campaign Performance (FR3)")
    camp = engine.campaign_performance()
    if not camp.empty:
        col1, col2 = st.columns(2)
        with col1:
            show(bar_chart(camp, "campaign_type", "visits", "Visits per Campaign Type",
                           color="#2563eb"), key="an_camp_visits")
        with col2:
            show(bar_chart(camp, "campaign_type", "revenue", "Revenue per Campaign Type",
                           color="#f59e0b"), key="an_camp_rev")

        section_header("Campaign Conversion Rates (FR3)")
        show(bar_chart(camp.sort_values("conversion_rate", ascending=False),
                       "campaign_type", "conversion_rate",
                       "Conversion Rate % by Campaign Type", color="#10b981"), key="an_camp_conv")

        st.dataframe(camp, use_container_width=True, hide_index=True)

# ─── TAB 4: Geographic Analysis (FR18) ───────────────────────────────────────
with tab_geo:
    section_header("Global Visit Distribution (FR18)")
    # Uses engine.geo_distribution() which queries 'location' aliased as 'country'
    geo_agg = engine.geo_distribution(top_n=100)

    if not geo_agg.empty:
        # prepare_choropleth_data accepts a df with 'country' column
        geo_df = prepare_choropleth_data(geo_agg, metric="visits")

        if not geo_df.empty:
            metric_choice = st.radio("Map Metric", ["visits", "conversions", "revenue"],
                                     horizontal=True, key="geo_metric")
            show(choropleth_map(geo_df, "country", "iso_alpha", metric_choice,
                                f"World {metric_choice.title()} Map"), key="an_map")

        col1, col2 = st.columns(2)
        with col1:
            section_header("Top 15 Locations by Visits")
            top_c = geo_agg.head(15)
            show(bar_chart(top_c, "country", "visits", horizontal=True,
                           color="#2563eb"), key="an_top_countries")
        with col2:
            section_header("Location Revenue Leaders")
            show(bar_chart(geo_agg.sort_values("revenue", ascending=False).head(10),
                           "country", "revenue", horizontal=True,
                           color="#f59e0b"), key="an_country_rev")

        st.dataframe(geo_agg.head(30), use_container_width=True, hide_index=True)
    else:
        st.info("No geographic data available.")


# ─── TAB 5: Statistical Analysis (FR19) ──────────────────────────────────────
with tab_stats:
    section_header("Descriptive Statistics (FR19)")
    # Fetch a sample using only columns that actually exist in web_logs
    sample_df = get_dataframe(
        "SELECT response_time_ms, revenue_value, http_status "
        "FROM web_logs ORDER BY RANDOM() LIMIT 10000"
    )
    if not sample_df.empty:
        # Rename for display clarity
        sample_df = sample_df.rename(columns={"http_status": "status_code", "revenue_value": "revenue"})
        stats_df = descriptive_stats(sample_df, ["response_time_ms", "revenue", "status_code"])
        if not stats_df.empty:
            st.dataframe(stats_df, use_container_width=True, hide_index=True)

    section_header("Revenue Statistics")
    rev_stats = run_query("""
        SELECT 
            SUM(revenue_value) as total_revenue,
            AVG(revenue_value) as mean_revenue,
            MAX(revenue_value) as max_revenue,
            MIN(revenue_value) as min_revenue
        FROM web_logs WHERE revenue_value > 0
    """)
    if rev_stats:
        r = rev_stats[0]
        r_cols = st.columns(4)
        rev_items = [
            ("Total Revenue", f"${r['total_revenue'] or 0:,.2f}"),
            ("Mean Revenue", f"${r['mean_revenue'] or 0:,.2f}"),
            ("Max Revenue", f"${r['max_revenue'] or 0:,.2f}"),
            ("Min Revenue", f"${r['min_revenue'] or 0:,.2f}"),
        ]
        for col, (lbl, val) in zip(r_cols, rev_items):
            col.metric(lbl, val)

    section_header("Response Time Distribution")
    if not sample_df.empty and "response_time_ms" in sample_df.columns:
        import plotly.express as px
        hist_fig = px.histogram(
            sample_df, x="response_time_ms",
            nbins=50, color_discrete_sequence=["#2563eb"],
        )
        hist_fig.update_layout(
            template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)", font=dict(color="#f1f5f9"),
            xaxis_title="Response Time (ms)", yaxis_title="Frequency",
        )
        show(hist_fig, key="an_bytes_hist")

# ─── TAB 6: Log Viewer (FR11-FR13) ───────────────────────────────────────────
with tab_logs:
    st.info("Loading recent 5,000 records for filtering and review.")
    df_sample = get_dataframe("SELECT * FROM web_logs ORDER BY timestamp DESC LIMIT 5000")
    if not df_sample.empty:
        filtered_df = render_filter_panel(df_sample, key_prefix="analyst")
        # Use only columns that exist in the actual DB schema
        display_cols = ["timestamp", "user_id", "ip_address", "activity_type", "service_name",
                        "page_url", "http_status", "response_time_ms", "location",
                        "campaign_type", "conversion_flag", "revenue_value"]
        display_cols = [c for c in display_cols if c in filtered_df.columns]
        render_data_table(filtered_df[display_cols], title="Filtered Web Log Records",
                          height=500, enable_export=True, key="an_table")
    else:
        st.error("Could not load log records from the database.")
