import streamlit as st
from backend.alert_engine import Alert, AlertSeverity
from typing import List

def render_alert_card(alert: Alert):
    """
    Render individual alert card
    """
    severity_config = {
        AlertSeverity.CRITICAL: {
            'color': '#ef4444',
            'bg': 'rgba(239, 68, 68, 0.1)',
            'border': 'rgba(239, 68, 68, 0.3)',
            'icon': 'alert-circle'
        },
        AlertSeverity.WARNING: {
            'color': '#f59e0b',
            'bg': 'rgba(245, 158, 11, 0.1)',
            'border': 'rgba(245, 158, 11, 0.3)',
            'icon': 'alert-triangle'
        },
        AlertSeverity.INFO: {
            'color': '#3b82f6',
            'bg': 'rgba(59, 130, 246, 0.1)',
            'border': 'rgba(59, 130, 246, 0.3)',
            'icon': 'info'
        }
    }
    
    config = severity_config[alert.severity]
    
    html = f'''
    <div style="
        padding: 16px 20px;
        background: {config['bg']};
        border-left: 4px solid {config['color']};
        border-radius: 12px;
        margin-bottom: 12px;
        animation: slideIn 0.3s ease-out;
    ">
        <div style="display: flex; justify-content: space-between; align-items: start;">
            <div style="flex: 1;">
                <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px;">
                    <i data-lucide="{config['icon']}" style="width: 20px; height: 20px; color: {config['color']};"></i>
                    <span style="
                        color: {config['color']};
                        font-weight: 700;
                        font-size: 14px;
                        text-transform: uppercase;
                    ">
                        {alert.severity.value}
                    </span>
                    <span style="color: #64748b; font-size: 12px;">
                        • {alert.timestamp.strftime('%H:%M:%S')}
                    </span>
                </div>
                
                <div style="color: #f8fafc; font-weight: 600; font-size: 15px; margin-bottom: 4px;">
                    {alert.title}
                </div>
                
                <div style="color: #cbd5e1; font-size: 13px;">
                    {alert.message}
                </div>
                
                <div style="margin-top: 8px; font-size: 11px; color: #94a3b8;">
                    Metric: {alert.metric_value:.1f} | Threshold: {alert.threshold}
                </div>
            </div>
        </div>
    </div>
    
    <style>
    @keyframes slideIn {{
        from {{ opacity: 0; transform: translateX(-20px); }}
        to {{ opacity: 1; transform: translateX(0); }}
    }}
    </style>
    
    <script src="https://unpkg.com/lucide@latest"></script>
    <script>lucide.createIcons();</script>
    '''
    
    st.html(html)

def render_alert_panel(alerts: List[Alert], max_display: int = 5):
    """
    Render alert panel with multiple alerts
    """
    if not alerts:
        st.info("No active alerts. System operating normally.")
        return
    
    st.markdown(f"### Active Alerts ({len(alerts)})")
    
    severity_order = {
        AlertSeverity.CRITICAL: 0,
        AlertSeverity.WARNING: 1,
        AlertSeverity.INFO: 2
    }
    sorted_alerts = sorted(alerts, key=lambda a: severity_order[a.severity])
    
    for alert in sorted_alerts[:max_display]:
        render_alert_card(alert)
    
    if len(alerts) > max_display:
        st.caption(f"+ {len(alerts) - max_display} more alerts")
