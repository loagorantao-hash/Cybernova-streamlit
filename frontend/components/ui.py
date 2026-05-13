import streamlit as st
import pandas as pd
# Use an alias to avoid conflict with any local 'html' files
import html as python_html
import textwrap

def render_kpi_card_enhanced(
    label: str, value: str, delta: str = None, delta_type: str = "positive",
    icon: str = None, status: str = "normal", trend: str = "up",
    comparison: str = None, details: str = None
):
    """Generates the v2.0 Smart KPI Card with animated borders and depth."""
    
    # Use the alias here
    s_label = python_html.escape(str(label))
    s_value = python_html.escape(str(value))
    s_comp = python_html.escape(str(comparison)) if comparison else ""
    s_det = python_html.escape(str(details)) if details else ""
    
    # Status color mapping
    colors = {
        "normal": "#2563eb",
        "warning": "#f59e0b",
        "critical": "#ef4444",
        "success": "#10b981",
        "info": "#06b6d4"
    }
    accent_color = colors.get(status, "#2563eb")
    
    # Trend arrow
    trend_icon = "↑" if trend == "up" else "↓" if trend == "down" else "→"
    delta_color = "#10b981" if delta_type == "positive" else "#ef4444" if delta_type == "negative" else "#94a3b8"
    
    # HTML/CSS for the enhanced card
    card_html = f"""
    <div class="smart-kpi-card" style="--accent: {accent_color};">
        <div class="card-inner">
            <div class="card-glow"></div>
            <div class="card-content">
                <div class="card-header">
                    <span class="card-label">{s_label}</span>
                    {f'<span class="card-icon"><i class="lucide-{icon}"></i></span>' if icon else ''}
                </div>
                <div class="card-body">
                    <h2 class="card-value">{s_value}</h2>
                    {f'<div class="card-delta" style="color: {delta_color};">{trend_icon} {delta}</div>' if delta else ''}
                </div>
                <div class="card-footer">
                    {f'<div class="card-comp">{s_comp}</div>' if comparison else ''}
                    {f'<div class="card-details">{s_det}</div>' if details else ''}
                </div>
            </div>
            <div class="animated-border"></div>
        </div>
    </div>
    
    <style>
    .smart-kpi-card {{
        position: relative;
        height: 100%;
        min-height: 160px;
        border-radius: 20px;
        padding: 2px;
        background: rgba(255, 255, 255, 0.05);
        overflow: hidden;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
    }}
    
    .smart-kpi-card:hover {{
        transform: translateY(-8px) scale(1.02);
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.4);
    }}
    
    .card-inner {{
        position: relative;
        background: #111827;
        height: 100%;
        border-radius: 18px;
        padding: 24px;
        z-index: 1;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }}
    
    .card-glow {{
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle at center, var(--accent) 0%, transparent 70%);
        opacity: 0.05;
        pointer-events: none;
        transition: opacity 0.3s;
    }}
    
    .smart-kpi-card:hover .card-glow {{
        opacity: 0.15;
    }}
    
    .card-header {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 12px;
    }}
    
    .card-label {{
        font-size: 12px;
        font-weight: 700;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 1.5px;
    }}
    
    .card-value {{
        font-size: 32px;
        font-weight: 800;
        color: #f8fafc;
        margin: 0;
        letter-spacing: -1px;
    }}
    
    .card-delta {{
        font-size: 14px;
        font-weight: 700;
        margin-top: 4px;
    }}
    
    .card-footer {{
        margin-top: 16px;
        border-top: 1px solid rgba(255, 255, 255, 0.05);
        padding-top: 12px;
    }}
    
    .card-comp {{
        font-size: 12px;
        color: #64748b;
        font-weight: 500;
    }}
    
    .card-details {{
        font-size: 11px;
        color: #475569;
        margin-top: 4px;
    }}
    
    .animated-border {{
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        border-radius: 20px;
        padding: 2px;
        background: linear-gradient(90deg, transparent, var(--accent), transparent);
        background-size: 200% 100%;
        animation: border-flow 3s linear infinite;
        opacity: 0.3;
        z-index: -1;
    }}
    
    @keyframes border-flow {{
        0% {{ background-position: 200% 0; }}
        100% {{ background-position: -200% 0; }}
    }}
    
    .smart-kpi-card:hover .animated-border {{
        opacity: 0.8;
        animation-duration: 1.5s;
    }}
    </style>
    """
    st.html(textwrap.dedent(card_html))
