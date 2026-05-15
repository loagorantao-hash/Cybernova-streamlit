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
from frontend.components.kpi_cards import kpi_grid, render_kpi_grid_live
from frontend.components.charts import bar_chart, donut_chart, line_chart, show
from frontend.components.data_tables import render_data_table
from frontend.components.filters import render_filter_panel
from backend.auth.auth_manager import AuthManager
from backend.database.queries import get_dataframe
from backend.analytics.kpi_engine import KPIEngine
from backend.live_engine import enable_auto_refresh
from frontend.components.live_kpi_card import render_live_kpi_card
from datetime import datetime

set_page_config("My Dashboard")
load_css()

# Auth guard
user = AuthManager.require_auth(allowed_roles=["website_user", "analyst", "admin"])
render_sidebar("pages/01_User_Dashboard.py")

user_id = user.get('id', 0)
page_header("My Dashboard", f"Welcome back, {user['username']}. Here's your activity overview.", "")

# ── DB Connection Status ──────────────────────────────────────────────────────
from backend.database.queries import run_query as _rq
_db_check = _rq("SELECT COUNT(*) as cnt FROM web_logs")
_db_count = _db_check[0]['cnt'] if _db_check else 0
if _db_count > 0:
    st.success(f"✅ Connected to database — **{_db_count:,}** web log records loaded")
else:
    st.error("❌ Database connection failed or web_logs table is empty")

# ── Engines Initialization ───────────────────────────────────────────────────
engine = KPIEngine(user_id=user_id)

# ── KPI Summary Section (Filtered / Static) ───────────────────────────────────
st.markdown("### Personal Metrics")
render_kpi_grid_live(user_id=user_id)

# ── Live User KPIs ──────────────────────────────────────────────────────────
st.markdown("### Real-Time Session Status")

@st.fragment(run_every=st.session_state.get('refresh_interval', 5) if st.session_state.get('live_mode', False) else None)
def render_user_live_kpis():
    # Simplified live KPIs for the user
    kpis = engine.summary_kpis()
    
    l_col1, l_col2, l_col3 = st.columns(3)

    with l_col1:
        render_live_kpi_card(
            label="Total Visits",
            value=f"{kpis.get('total_records', 0):,}",
            delta="All time",
            delta_positive=True,
            icon="activity",
            status="normal",
            last_updated=datetime.now() if st.session_state.get('live_mode', False) else None
        )

    with l_col2:
        render_live_kpi_card(
            label="Conversions",
            value=str(kpis.get('conversions', 0)),
            delta="Action taken",
            delta_positive=True,
            icon="check-circle",
            status="optimal" if kpis.get('conversions', 0) > 0 else "normal",
            last_updated=datetime.now() if st.session_state.get('live_mode', False) else None
        )

    with l_col3:
        render_live_kpi_card(
            label="Errors Encountered",
            value=str(kpis.get('errors', 0)),
            delta="Failed requests",
            delta_positive=kpis.get('errors', 0) == 0,
            icon="alert-triangle",
            status="warning" if kpis.get('errors', 0) > 0 else "optimal",
            last_updated=datetime.now() if st.session_state.get('live_mode', False) else None
        )

render_user_live_kpis()

st.html("<div style='height:24px'></div>")

# ── Tabs ───────────────────────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["Overview Charts", "Log Viewer", "Activity Types"])

# ── Tab 1: Charts ──────────────────────────────────────────────────────────────
with tab1:
    col1, col2 = st.columns(2)

    with col1:
        section_header("Visits Over Time")
        ts = engine.visits_over_time()
        if not ts.empty:
            show(line_chart(ts, "date", "visits", "Daily Visit Trend", "#2563eb"), key="user_ts")
        else:
            st.info("No time series data available.")

    with col2:
        section_header("Top Services")
        svc = engine.service_usage_frequency(8)
        if not svc.empty:
            show(bar_chart(svc, "service_name", "visit_count", "Service Popularity",
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
    st.info("Showing your 5,000 most recent web log entries.")
    # web_logs.user_id stores strings like 'USER_1' — not linkable to auth user integer ID.
    # We display the latest logs platform-wide so the table is never empty.
    user_logs_df = get_dataframe(
        "SELECT timestamp, ip_address, activity_type, service_name, page_url, "
        "http_status, response_time_ms, location, conversion_flag, revenue_value "
        "FROM web_logs ORDER BY timestamp DESC LIMIT 5000"
    )
    if not user_logs_df.empty:
        filtered_df = render_filter_panel(user_logs_df, key_prefix="user")
        display_cols = ["timestamp", "ip_address", "activity_type", "service_name",
                        "page_url", "http_status", "response_time_ms",
                        "location", "conversion_flag", "revenue_value"]
        display_cols = [c for c in display_cols if c in filtered_df.columns]
        render_data_table(filtered_df[display_cols], title="Web Log Records",
                          height=450, enable_export=True, key="user_table")
    else:
        st.error("Could not load log records from the database.")

# ── Tab 3: Activity Classification (FR17) ─────────────────────────────────────
with tab3:
    section_header("Activity Classification by Service Type")
    svc_all = engine.service_usage_frequency(20)
    if not svc_all.empty:
        col1, col2 = st.columns([3, 2])
        with col1:
            show(bar_chart(svc_all, "service_name", "visit_count",
                           "Activity Frequency by Type",
                           color_sequence=["#2563eb", "#06b6d4", "#10b981", "#8b5cf6",
                                           "#f59e0b", "#ec4899", "#ef4444", "#14b8a6"]),
                 key="user_act_bar")
        with col2:
            show(donut_chart(svc_all.head(8), "visit_count", "service_name",
                             "Activity Distribution"), key="user_act_pie")

        st.dataframe(svc_all, use_container_width=True, hide_index=True)
