import streamlit as st
from datetime import datetime

def render_live_mode_toggle():
    """
    Render global live analytics toggle in sidebar
    """
    st.sidebar.markdown("---")
    st.sidebar.markdown("### Live Analytics")
    
    if 'live_mode' not in st.session_state:
        st.session_state.live_mode = False
    if 'refresh_interval' not in st.session_state:
        st.session_state.refresh_interval = 5
    if 'last_refresh' not in st.session_state:
        st.session_state.last_refresh = datetime.now()
    
    col1, col2 = st.sidebar.columns([3, 1])
    
    with col1:
        live_enabled = st.checkbox(
            "Enable Live Mode",
            value=st.session_state.live_mode,
            key="live_mode_checkbox",
            help="Auto-refresh dashboards every 5-10 seconds"
        )
        st.session_state.live_mode = live_enabled
    
    with col2:
        if st.session_state.live_mode:
            st.html("""
            <div style="
                width: 12px;
                height: 12px;
                background: #10b981;
                border-radius: 50%;
                animation: pulse 2s infinite;
                margin-top: 8px;
            "></div>
            <style>
            @keyframes pulse {
                0%, 100% { opacity: 1; box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7); }
                50% { opacity: 0.7; box-shadow: 0 0 0 10px rgba(16, 185, 129, 0); }
            }
            </style>
            """)
    
    if st.session_state.live_mode:
        interval = st.sidebar.slider(
            "Refresh Interval (seconds)",
            min_value=5,
            max_value=30,
            value=st.session_state.refresh_interval,
            step=5,
            key="refresh_interval_slider"
        )
        st.session_state.refresh_interval = interval
        time_ago = (datetime.now() - st.session_state.last_refresh).seconds
        st.sidebar.caption(f"🕐 Last refresh: {time_ago}s ago")
    
    st.sidebar.markdown("---")
