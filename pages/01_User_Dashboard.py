"""
FR1, FR11, FR17, FR20 — Website User Dashboard
Displays personal usage statistics, filtered log view, and basic charts.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
from frontend.components.layout import set_page_config, load_css, page_header, section_header
from frontend.components.sidebar import render_sidebar
from frontend.components.kpi_cards import kpi_grid
from frontend.components.charts import bar_chart, donut_chart, line_chart, show
from frontend.components.data_tables import render_data_table
from frontend.components.filters import render_filter_panel
from backend.auth.auth_manager import AuthManager
from backend.data_ingestion.dataset_loader import load_dataset
from backend.analytics.kpi_engine import KPIEngine

set_page_config("My Dashboard")
load_css()

# Auth guard
user = AuthManager.require_auth(allowed_roles=["website_user", "analyst", "admin"])
render_sidebar("pages/01_User_Dashboard.py")

# ── Load Data ─────────────────────────────────────────────────────────────────
df = load_dataset()

page_header("My Dashboard", f"Welcome back, {user['username']}. Here's your activity overview.", "")

from frontend.components.kpi_cards import render_kpi_grid_live

# ── KPI Row ───────────────────────────────────────────────────────────────────
engine = KPIEngine(df)
render_kpi_grid_live(df)

st.html("<div style='height:8px'></div>")

# ── Tabs ───────────────────────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["Overview Charts", "Log Viewer", "Activity Types"])

# ── Tab 1: Charts ──────────────────────────────────────────────────────────────
with tab1:
    col1, col2 = st.columns(2)

    with col1:
        section_header("Visits Over Time")
        ts = engine.visits_over_time("D")
        if not ts.empty:
            show(line_chart(ts, "date", "visits", "Daily Visit Trend", "#2563eb"), key="user_ts")
        else:
            st.info("No time series data available.")

    with col2:
        section_header("Top Services")
        svc = engine.service_usage_frequency(8)
        if not svc.empty:
            show(bar_chart(svc, "service_type", "visit_count", "Service Popularity",
                           horizontal=True, color="#06b6d4"), key="user_svc")

    col3, col4 = st.columns(2)

    with col3:
        section_header("HTTP Status Distribution")
        sc = engine.status_code_distribution()
        if not sc.empty:
            show(donut_chart(sc, "count", "status_category", "Status Codes"), key="user_sc")

    with col4:
        section_header("Hourly Traffic Pattern")
        hd = engine.hourly_distribution()
        if not hd.empty:
            show(bar_chart(hd, "hour", "visits", "Traffic by Hour", "#8b5cf6"), key="user_hourly")

# ── Tab 2: Log Viewer ──────────────────────────────────────────────────────────
with tab2:
    filtered_df = render_filter_panel(df, key_prefix="user")
    display_cols = ["timestamp", "ip_address", "method", "uri", "status_code",
                    "bytes_sent", "country", "service_type", "conversion_flag"]
    display_cols = [c for c in display_cols if c in filtered_df.columns]
    render_data_table(filtered_df[display_cols], title="Web Log Records",
                      height=450, enable_export=True, key="user_table")

# ── Tab 3: Activity Classification (FR17) ─────────────────────────────────────
with tab3:
    section_header("Activity Classification by Service Type")
    svc_all = engine.service_usage_frequency(20)
    if not svc_all.empty:
        col1, col2 = st.columns([3, 2])
        with col1:
            show(bar_chart(svc_all, "service_type", "visit_count",
                           "Activity Frequency by Type",
                           color_sequence=["#2563eb", "#06b6d4", "#10b981", "#8b5cf6",
                                           "#f59e0b", "#ec4899", "#ef4444", "#14b8a6"]),
                 key="user_act_bar")
        with col2:
            show(donut_chart(svc_all.head(8), "visit_count", "service_type",
                             "Activity Distribution"), key="user_act_pie")

        render_summary_table = None
        st.dataframe(svc_all, use_container_width=True, hide_index=True)
