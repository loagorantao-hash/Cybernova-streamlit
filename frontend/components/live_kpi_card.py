import streamlit as st
from typing import Optional
from datetime import datetime

def render_live_kpi_card(
    label: str,
    value: str,
    delta: Optional[str] = None,
    delta_positive: bool = True,
    icon: Optional[str] = None,
    status: str = "normal",
    live_indicator: bool = True,
    last_updated: Optional[datetime] = None
):
    """
    Render live KPI card with pulsing animation
    """
    is_live = st.session_state.get('live_mode', False)
    
    status_colors = {
        'normal': '#06b6d4',
        'warning': '#f59e0b',
        'critical': '#ef4444',
        'optimal': '#10b981',
    }
    
    border_color = status_colors.get(status, status_colors['normal'])
    delta_color = '#10b981' if delta_positive else '#ef4444'
    delta_arrow = '↑' if delta_positive else '↓'
    
    pulse_animation = """
    @keyframes pulse-border {{
        0%, 100% {{ 
            border-color: {color};
            box-shadow: 0 0 0 0 rgba(37, 99, 235, 0.7);
        }}
        50% {{ 
            border-color: {color_light};
            box-shadow: 0 0 0 8px rgba(37, 99, 235, 0);
        }}
    }}
    .live-card {{
        animation: pulse-border 2s infinite;
    }}
    """.format(color=border_color, color_light='#60a5fa')
    
    live_dot = f'''
    <div style="
        display: flex;
        align-items: center;
        gap: 6px;
        font-size: 10px;
        color: #10b981;
        font-weight: 600;
        text-transform: uppercase;
    ">
        <div style="
            width: 8px;
            height: 8px;
            background: #10b981;
            border-radius: 50%;
            animation: pulse-dot 2s infinite;
        "></div>
        LIVE
    </div>
    ''' if is_live and live_indicator else ''
    
    time_display = ''
    if last_updated:
        seconds_ago = (datetime.now() - last_updated).seconds
        if seconds_ago < 60:
            time_display = f'<span style="font-size: 10px; color: #64748b;">Updated {seconds_ago}s ago</span>'
        else:
            time_display = f'<span style="font-size: 10px; color: #64748b;">Updated {seconds_ago // 60}m ago</span>'
    
    html = f'''
    <style>
    @keyframes pulse-dot {{
        0%, 100% {{ opacity: 1; }}
        50% {{ opacity: 0.5; }}
    }}
    {pulse_animation if is_live else ''}
    </style>
    
    <div class="{'live-card' if is_live else ''}" style="
        position: relative;
        padding: 20px 24px;
        border-radius: 16px;
        background: linear-gradient(135deg, rgba(15, 23, 42, 0.5), rgba(31, 41, 55, 0.3));
        backdrop-filter: blur(10px);
        border: 2px solid {border_color};
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        transition: all 300ms cubic-bezier(0.4, 0, 0.2, 1);
        height: 100%;
    " onmouseover="this.style.transform='translateY(-4px)'; this.style.boxShadow='0 10px 25px rgba(37, 99, 235, 0.2)';" 
       onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 4px 6px rgba(0, 0, 0, 0.1)';">
        
        <!-- Live indicator -->
        {live_dot}
        
        <!-- Content -->
        <div style="margin-top: 8px;">
            <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 12px;">
                <div>
                    <div style="
                        font-size: 12px;
                        font-weight: 600;
                        color: #94a3b8;
                        text-transform: uppercase;
                        letter-spacing: 0.5px;
                        margin-bottom: 8px;
                    ">
                        {label}
                    </div>
                    <div style="
                        font-size: 28px;
                        font-weight: 700;
                        color: #f8fafc;
                        letter-spacing: -0.02em;
                    ">
                        {value}
                    </div>
                </div>
                
                {f'<i data-lucide="{icon}" style="width: 32px; height: 32px; color: {border_color};"></i>' if icon else ''}
            </div>
            
            <!-- Delta & Timestamp -->
            <div style="padding-top: 12px; border-top: 1px solid rgba(255, 255, 255, 0.1);">
                {f'''<div style="
                    font-size: 12px;
                    font-weight: 600;
                    color: {delta_color};
                    margin-bottom: 4px;
                ">
                    {delta_arrow} {delta}
                </div>''' if delta else ''}
                
                {time_display}
            </div>
        </div>
    </div>
    
    <script src="https://unpkg.com/lucide@latest"></script>
    <script>lucide.createIcons();</script>
    '''
    
    st.html(html)
