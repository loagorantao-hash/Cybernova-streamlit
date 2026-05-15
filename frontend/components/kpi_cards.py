import streamlit as st
import pandas as pd
from typing import Optional
import textwrap


def kpi_card(
    label: str,
    value: str,
    delta: Optional[str] = None,
    positive: bool = True,
    detail: str = "",
    color: str = "#2563eb",
    col=None,
):
    """Render a single glassmorphic KPI card."""
    arrow = "▲" if positive else "▼"
    delta_class = "positive" if positive else "negative"
    delta_html = (
        f'<div class="kpi-delta {delta_class}">{arrow} {delta}</div>' if delta else ""
    )
    detail_html = f'<div class="kpi-detail">{detail}</div>' if detail else ""

    html = f"""
    <div class="kpi-card" style="--accent-color: linear-gradient(90deg, {color}, #06b6d4);">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
        {delta_html}
        {detail_html}
    </div>
    """
    if col:
        col.html(textwrap.dedent(html))
    else:
        st.html(textwrap.dedent(html))


def kpi_grid(metrics: list):
    """
    Render up to 4 KPI cards per row.
    metrics: list of dicts with keys: label, value, delta, positive, detail, color
    """
    per_row = 4
    for i in range(0, len(metrics), per_row):
        chunk = metrics[i:i + per_row]
        cols = st.columns(len(chunk))
        for col, m in zip(cols, chunk):
            kpi_card(
                label=m.get("label", ""),
                value=m.get("value", ""),
                delta=m.get("delta"),
                positive=m.get("positive", True),
                detail=m.get("detail", ""),
                color=m.get("color", "#2563eb"),
                col=col,
            )
        st.html("<div style='margin-bottom:8px'></div>")


def summary_banner(kpis: dict):
    """Convert summary_kpis() dict into a rendered KPI grid."""
    fmt_num = lambda n: f"{n:,.0f}" if isinstance(n, (int, float)) else str(n)
    fmt_pct = lambda n: f"{n:.1f}%"
    fmt_money = lambda n: f"${n:,.2f}"

    metrics = [
        {"label": "Total Visits",      "value": fmt_num(kpis.get("total_records", 0)),
         "detail": "All log records",   "color": "#2563eb"},
        {"label": "Unique Visitors",    "value": fmt_num(kpis.get("unique_users", 0)),
         "detail": "Distinct Users",    "color": "#06b6d4"},
        {"label": "Total Leads",        "value": fmt_num(kpis.get("leads", 0)),
         "detail": "Expressed interest","color": "#f59e0b"},
        {"label": "Total Conversions",  "value": fmt_num(kpis.get("conversions", 0)),
         "detail": "Successful actions","color": "#10b981"},
        {"label": "Conversion Rate",    "value": fmt_pct(kpis.get("conversion_rate", 0)),
         "detail": "Lead → Action",     "color": "#8b5cf6"},
        {"label": "Total Revenue",      "value": fmt_money(kpis.get("revenue", 0)),
         "detail": "Gross revenue",     "color": "#f59e0b"},
        {"label": "Avg Response Time",  "value": f"{kpis.get('avg_response_time', 0):.0f} ms",
         "detail": "System latency",    "color": "#14b8a6"},
        {"label": "Error Rate",         "value": fmt_pct(kpis.get("error_rate", 0)),
         "positive": kpis.get("error_rate", 0) < 5,
         "detail": "4xx/5xx responses", "color": "#ef4444"},
    ]
    kpi_grid(metrics)
@st.fragment(run_every=10 if st.session_state.get("live_mode") else None)
def render_kpi_grid_live(user_id: Optional[str] = None):
    """
    Renders a live-updating KPI grid. 
    Recalculates KPIs from the database every 10 seconds if live mode is on.
    """
    from backend.analytics.kpi_engine import KPIEngine
    engine = KPIEngine(user_id=user_id)
    kpis = engine.summary_kpis()
    
    fmt_num = lambda n: f"{n:,.0f}" if isinstance(n, (int, float)) else str(n)
    fmt_pct = lambda n: f"{n:.1f}%"
    fmt_money = lambda n: f"${n:,.2f}"

    metrics = [
        {"label": "Total Visits",      "value": fmt_num(kpis.get("total_records", 0)),
         "detail": "All log records",   "color": "#2563eb"},
        {"label": "Unique Visitors",    "value": fmt_num(kpis.get("unique_users", 0)),
         "detail": "Distinct Users",    "color": "#06b6d4"},
        {"label": "Total Leads",        "value": fmt_num(kpis.get("leads", 0)),
         "detail": "Expressed interest","color": "#f59e0b"},
        {"label": "Total Conversions",  "value": fmt_num(kpis.get("conversions", 0)),
         "detail": "Successful actions","color": "#10b981"},
        {"label": "Conversion Rate",    "value": fmt_pct(kpis.get("conversion_rate", 0)),
         "detail": "Lead → Action",     "color": "#8b5cf6"},
        {"label": "Total Revenue",      "value": fmt_money(kpis.get("revenue", 0)),
         "detail": "Gross revenue",     "color": "#f59e0b"},
        {"label": "Avg Response Time",  "value": f"{kpis.get('avg_response_time', 0):.0f} ms",
         "detail": "System latency",    "color": "#14b8a6"},
        {"label": "Error Rate",         "value": fmt_pct(kpis.get("error_rate", 0)),
         "positive": kpis.get("error_rate", 0) < 5,
         "detail": "4xx/5xx responses", "color": "#ef4444"},
    ]
    kpi_grid(metrics)
