import textwrap
"""
FR1-FR4, FR11-FR13, FR18-FR20 — Business Analyst Dashboard
Full analytics: KPI grid, filters, charts, geo map, stats, conversion funnel.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
import pandas as pd
from frontend.components.layout import set_page_config, load_css, page_header, section_header
from frontend.components.sidebar import render_sidebar
from frontend.components import render_kpi_card_enhanced
from frontend.components.charts import (
    bar_chart, donut_chart, line_chart, funnel_chart,
    choropleth_map, scatter_chart, grouped_bar_chart, show
)
from frontend.components.data_tables import render_data_table
from frontend.components.filters import render_filter_panel
from backend.auth.auth_manager import AuthManager
from backend.data_ingestion.dataset_loader import load_dataset
from backend.analytics.kpi_engine import KPIEngine
from backend.analytics.geo_analyzer import prepare_choropleth_data, top_countries
from backend.analytics.statistics import descriptive_stats, correlation_matrix, revenue_statistics

set_page_config("Analyst Dashboard")
load_css()

user = AuthManager.require_auth(allowed_roles=["analyst", "admin"])
render_sidebar("pages/02_Analyst_Dashboard.py")

from frontend.components.kpi_cards import render_kpi_grid_live

# ── Data ──────────────────────────────────────────────────────────────────────
df_full = load_dataset()
page_header("Analyst Dashboard",
            f"Full analytics view — {len(df_full):,} records loaded", "")

# ── Filter Panel (FR11-FR13) ──────────────────────────────────────────────────
df = render_filter_panel(df_full, key_prefix="analyst")

# ── KPI Summary Section (v2.0 Enhanced Live) ──────────────────────────────────
engine = KPIEngine(df)
render_kpi_grid_live(df)

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
        ts = engine.visits_over_time("D")
        if not ts.empty:
            show(line_chart(ts, "date", "visits", "Visits Over Time", "#2563eb"), key="an_ts")

    with col2:
        section_header("Revenue Over Time (FR3)")
        rev_ts = engine.revenue_over_time("D")
        if not rev_ts.empty:
            show(line_chart(rev_ts, "date", "revenue", "Daily Revenue", "#10b981"), key="an_rev_ts")

    col3, col4 = st.columns(2)
    with col3:
        section_header("Top Services by Visits (FR1)")
        svc = engine.service_usage_frequency(10)
        if not svc.empty:
            show(bar_chart(svc, "service_type", "visit_count", horizontal=True,
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
            show(bar_chart(svc_rev, "service_type", "total_revenue",
                           horizontal=True, color="#f59e0b"), key="an_svc_rev")

# ─── TAB 2: Sales & Conversion (FR2, FR4) ────────────────────────────────────
with tab_sales:
    col1, col2 = st.columns([2, 1])

    with col1:
        section_header("Conversion Funnel (FR2 / FR4)")
        funnel_df = engine.sales_funnel()
        show(funnel_chart(funnel_df, "stage", "count", "Visit → Conversion Funnel"), key="an_funnel")

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
    if "service_type" in df.columns and "conversion_flag" in df.columns:
        conv_by_svc = df.groupby("service_type").agg(
            visits=("service_type", "count"),
            conversions=("conversion_flag", "sum"),
        ).reset_index()
        conv_by_svc["conv_rate"] = (conv_by_svc["conversions"] / conv_by_svc["visits"] * 100).round(2)
        show(bar_chart(conv_by_svc.sort_values("conv_rate", ascending=False),
                       "service_type", "conv_rate", "Conversion Rate % by Service",
                       color="#10b981"), key="an_conv_svc")

# ─── TAB 3: Marketing Effectiveness (FR3) ────────────────────────────────────
with tab_marketing:
    section_header("Campaign Performance (FR3)")
    camp = engine.campaign_performance()
    if not camp.empty:
        col1, col2 = st.columns(2)
        with col1:
            show(bar_chart(camp, "campaign_id", "visits", "Visits per Campaign",
                           color="#2563eb"), key="an_camp_visits")
        with col2:
            show(bar_chart(camp, "campaign_id", "revenue", "Revenue per Campaign",
                           color="#f59e0b"), key="an_camp_rev")

        section_header("Campaign Conversion Rates (FR3)")
        show(bar_chart(camp.sort_values("conversion_rate", ascending=False),
                       "campaign_id", "conversion_rate",
                       "Conversion Rate % by Campaign", color="#10b981"), key="an_camp_conv")

        st.dataframe(camp, use_container_width=True, hide_index=True)

# ─── TAB 4: Geographic Analysis (FR18) ───────────────────────────────────────
with tab_geo:
    section_header("Global Visit Distribution (FR18)")
    geo_df = prepare_choropleth_data(df, metric="visits")
    if not geo_df.empty:
        metric_choice = st.radio("Map Metric", ["visits", "conversions", "revenue"],
                                 horizontal=True, key="geo_metric")
        show(choropleth_map(geo_df, "country", "iso_alpha", metric_choice,
                            f"World {metric_choice.title()} Map"), key="an_map")

        col1, col2 = st.columns(2)
        with col1:
            section_header("Top 15 Countries by Visits")
            top_c = top_countries(df, 15)
            show(bar_chart(top_c, "country", "visits", horizontal=True,
                           color="#2563eb"), key="an_top_countries")
        with col2:
            section_header("Country Revenue Leaders")
            show(bar_chart(top_c.sort_values("revenue", ascending=False).head(10),
                           "country", "revenue", horizontal=True,
                           color="#f59e0b"), key="an_country_rev")

        st.dataframe(top_c, use_container_width=True, hide_index=True)

# ─── TAB 5: Statistical Analysis (FR19) ──────────────────────────────────────
with tab_stats:
    section_header("Descriptive Statistics (FR19)")
    stats_df = descriptive_stats(df, ["bytes_sent", "revenue", "status_code"])
    if not stats_df.empty:
        st.dataframe(stats_df, use_container_width=True, hide_index=True)

    section_header("Revenue Statistics")
    rev_stats = revenue_statistics(df)
    if rev_stats:
        r_cols = st.columns(4)
        rev_items = [
            ("Total Revenue", f"${rev_stats.get('total_revenue', 0):,.2f}"),
            ("Mean Revenue", f"${rev_stats.get('mean_revenue', 0):,.2f}"),
            ("Median Revenue", f"${rev_stats.get('median_revenue', 0):,.2f}"),
            ("Std Deviation", f"${rev_stats.get('std_revenue', 0):,.2f}"),
        ]
        for col, (lbl, val) in zip(r_cols, rev_items):
            col.metric(lbl, val)

    section_header("Correlation Matrix")
    corr = correlation_matrix(df)
    if not corr.empty:
        num_cols = corr.columns.tolist()
        import plotly.figure_factory as ff
        import plotly.graph_objects as go
        fig_corr = go.Figure(go.Heatmap(
            z=corr.values, x=num_cols, y=num_cols,
            colorscale=[[0, "#ef4444"], [0.5, "#1e293b"], [1.0, "#10b981"]],
            zmin=-1, zmax=1,
            text=corr.round(2).values, texttemplate="%{text}",
        ))
        fig_corr.update_layout(
            template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)", font=dict(color="#f1f5f9"),
            margin=dict(l=10, r=10, t=30, b=10),
            title=dict(text="Pearson Correlation Matrix", font=dict(size=13, color="#cbd5e1")),
        )
        show(fig_corr, key="an_corr")

    section_header("Bytes Sent Distribution")
    if "bytes_sent" in df.columns:
        import plotly.express as px
        hist_fig = px.histogram(
            df.sample(min(5000, len(df))), x="bytes_sent",
            nbins=50, color_discrete_sequence=["#2563eb"],
        )
        hist_fig.update_layout(
            template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)", font=dict(color="#f1f5f9"),
            xaxis_title="Bytes Sent", yaxis_title="Frequency",
        )
        show(hist_fig, key="an_bytes_hist")

# ─── TAB 6: Log Viewer (FR11-FR13) ───────────────────────────────────────────
with tab_logs:
    display_cols = ["timestamp", "ip_address", "method", "uri", "status_code",
                    "bytes_sent", "country", "service_type", "campaign_id",
                    "conversion_flag", "revenue"]
    display_cols = [c for c in display_cols if c in df.columns]
    render_data_table(df[display_cols], title="Filtered Web Log Records",
                      height=500, enable_export=True, key="an_table")
