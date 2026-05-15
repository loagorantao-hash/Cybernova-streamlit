"""
FR1, FR11, FR17, FR20 — Website User Dashboard (Hybrid Intelligence)
Combines classic business KPIs with new personal AI functions.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
import pandas as pd
from frontend.components.layout import set_page_config, load_css, page_header, section_header
from frontend.components.sidebar import render_sidebar
from frontend.components.charts import bar_chart, donut_chart, line_chart, show
from frontend.components.data_tables import render_data_table
from frontend.components.filters import render_filter_panel
from backend.auth.auth_manager import AuthManager
from backend.database.queries import get_dataframe
from backend.analytics.kpi_engine import KPIEngine
from backend.analytics.ai_assistant_engine import AIAssistantEngine
from frontend.components.live_kpi_card import render_live_kpi_card
from datetime import datetime

set_page_config("My Dashboard")
load_css()

# Auth guard
user = AuthManager.require_auth(allowed_roles=["website_user", "analyst", "admin"])
render_sidebar("pages/01_User_Dashboard.py")

user_id = user.get('id', 0)
page_header("My CyberNova Dashboard", f"Gaborone HQ Activity Hub — Welcome, {user['username']}", "")

# ── Engines Initialization ───────────────────────────────────────────────────
engine = KPIEngine(user_id=user_id)
ai_engine = AIAssistantEngine(user_id=user_id)

# ── SECTION 1: Personal KPIs (Reverted to Original Style) ─────────────────────
st.markdown("### Personal Metrics")
kpis = engine.summary_kpis()

l_col1, l_col2, l_col3 = st.columns(3)

with l_col1:
    render_live_kpi_card(
        label="Total Visits",
        value=f"{kpis.get('total_records', 0):,}",
        delta="Lifetime activity",
        delta_positive=True,
        icon="activity",
        status="normal"
    )

with l_col2:
    render_live_kpi_card(
        label="Conversions",
        value=str(kpis.get('conversions', 0)),
        delta="Actions taken",
        delta_positive=True,
        icon="check-circle",
        status="optimal" if kpis.get('conversions', 0) > 0 else "normal",
    )

with l_col3:
    render_live_kpi_card(
        label="Errors Encountered",
        value=str(kpis.get('errors', 0)),
        delta="Failed requests",
        delta_positive=kpis.get('errors', 0) == 0,
        icon="alert-triangle",
        status="warning" if kpis.get('errors', 0) > 0 else "optimal",
    )

st.html("<div style='height:24px'></div>")

# ── Main Tabs (Original + New Functions) ──────────────────────────────────────
tab1, tab2, tab3, tab_journey, tab_ai = st.tabs([
    "Overview Charts", "Log Viewer", "Activity Types", "👣 My Journey", "🤖 AI Assistant"
])

# ── Tab 1: Charts (Original) ──────────────────────────────────────────────────
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
        section_header("Top Job Types Used")
        svc_usage = engine.service_usage_frequency(5)
        if not svc_usage.empty:
            show(bar_chart(svc_usage.rename(columns={"service_name": "job_type"}), 
                           "job_type", "visit_count", "Job Type Popularity",
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

# ── Tab 2: Log Viewer (Original) ──────────────────────────────────────────────
with tab2:
    st.info("Showing your detailed activity log records.")
    user_logs_df = get_dataframe(
        f"SELECT timestamp, ip_address, activity_type, service_name as job_type, page_url, "
        f"http_status, response_time_ms, location "
        f"FROM web_logs WHERE user_id = 'USER_{user_id}' ORDER BY timestamp DESC LIMIT 1000"
    )
    if not user_logs_df.empty:
        filtered_df = render_filter_panel(user_logs_df, key_prefix="user")
        render_data_table(filtered_df, title="Personal Activity Record", height=450, key="user_table")
    else:
        st.info("No logs found for your account yet.")

# ── Tab 3: Activity Classification (Original) ─────────────────────────────────
with tab3:
    section_header("Job Classification Metrics")
    svc_breakdown = engine.jobs_analysis()
    if not svc_breakdown.empty:
        col_c1, col_c2 = st.columns([1.5, 1])
        with col_c1:
            show(bar_chart(svc_breakdown, "job_type", "request_count", "Job Type Popularity", color="#8b5cf6"), key="u_svc_pop")
        with col_c2:
            show(donut_chart(svc_breakdown, "request_count", "job_type", "Job Share %"), key="u_svc_pie")
        st.dataframe(svc_breakdown, use_container_width=True, hide_index=True)

# ── Tab 4: My Journey (New Intelligence Function) ─────────────────────────────
with tab_journey:
    section_header("Engagement & Journey Tracking")
    engagement_score = engine.user_engagement_score()
    st.metric("My Engagement Score", f"{engagement_score}/100", delta="Live Activity Level")
    
    st.divider()
    section_header("Recent Activity Timeline")
    timeline = engine.user_activity_timeline(15)
    if not timeline.empty:
        for idx, row in timeline.iterrows():
            st.markdown(f"""
            <div style="border-left: 2px solid #2563eb; padding-left: 20px; margin-bottom: 15px; position: relative;">
                <div style="position: absolute; left: -7px; top: 0; width: 12px; height: 12px; border-radius: 50%; background: #2563eb;"></div>
                <small style="color: #94a3b8;">{row['timestamp']}</small><br>
                <b style="color: #f8fafc;">{row['activity_type'].replace('_', ' ')}</b> — <span style="color: #38bdf8;">{row['job_type']}</span>
            </div>
            """, unsafe_allow_html=True)

# ── Tab 5: AI Assistant (New Intelligence Function) ───────────────────────────
with tab_ai:
    section_header("AI Personal Insights")
    insights = ai_engine.get_quick_insights()
    if insights:
        for ins in insights:
            st.info(f"🤖 **{ins['text']}** \n\n *Suggestion: {ins['suggestion']}*")
    
    st.divider()
    st.markdown("#### Ask your Assistant")
    q = st.text_input("Query your data...", placeholder="e.g., 'What is my most used service?'")
    if q:
        st.write(f"🤖 **Assistant:** {ai_engine.answer_question(q)}")
