import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from backend.live_engine import LiveEngine
from frontend.components.alert_card import render_alert_panel
from backend.alert_engine import AlertEngine
from frontend.components.sidebar import render_sidebar
from frontend.components.layout import set_page_config, load_css
from backend.auth.auth_manager import AuthManager
from backend.data_ingestion.dataset_loader import load_dataset

# Page config
set_page_config("Live Log Stream")
load_css()

# Auth check (admin only)
user = AuthManager.require_auth(allowed_roles=["admin"])
render_sidebar("pages/95_Live_Log_Stream.py")

dataset = load_dataset()

# Initialize engines
if 'live_engine' not in st.session_state:
    st.session_state.live_engine = LiveEngine(dataset, refresh_interval=st.session_state.get('refresh_interval', 5))

if 'alert_engine' not in st.session_state:
    st.session_state.alert_engine = AlertEngine(dataset)

# Page header
st.html("""
<h1 style="color: #f8fafc; font-size: 32px; margin-bottom: 8px;">
<span class="material-symbols-rounded" style="vertical-align: middle;">sensors</span> Live Log Stream
</h1>
<p style="color: #94a3b8; font-size: 16px; margin-bottom: 24px;">
Real-time monitoring and log analysis
</p>
""")

# Top controls
col1, col2, col3, col4 = st.columns([2, 2, 2, 1])

with col1:
    severity_filter = st.multiselect(
        "Filter by Severity",
        options=['INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        default=['WARNING', 'ERROR', 'CRITICAL']
    )

with col2:
    user_filter = st.text_input("Filter by User ID", placeholder="Enter user ID...")

with col3:
    time_range = st.selectbox(
        "Time Range",
        options=['Last 5 minutes', 'Last 15 minutes', 'Last hour', 'Last 24 hours'],
        index=1
    )

with col4:
    st.html("<br>")
    auto_refresh = st.checkbox("Auto-refresh", value=st.session_state.get('live_mode', False))

st.markdown("---")

# Active alerts section
alerts = st.session_state.alert_engine.run_all_checks()
if alerts:
    with st.expander("Active Alerts", expanded=True):
        render_alert_panel(alerts)

st.markdown("---")

# Live log stream
st.markdown("### Live Event Stream")

refresh_int = st.session_state.get('refresh_interval', 5) if (auto_refresh and st.session_state.get('live_mode', False)) else None

@st.fragment(run_every=refresh_int)
def render_log_stream():
    from backend.database.connection import get_engine
    engine = get_engine()
    
    time_deltas = {
        'Last 5 minutes': 5,
        'Last 15 minutes': 15,
        'Last hour': 60,
        'Last 24 hours': 1440
    }
    
    mins = time_deltas.get(time_range, 60)
    cutoff = (datetime.now() - timedelta(minutes=mins)).strftime('%Y-%m-%d %H:%M:%S')
    
    query = f"SELECT * FROM web_logs WHERE timestamp >= '{cutoff}'"
    # Note: user_id is not natively in our web_logs schema, so we skip exact filtering by user_id for now 
    # unless it's present in the dataframe
    
    filtered_logs = pd.read_sql(query, con=engine)
    
    if not filtered_logs.empty:
        filtered_logs['timestamp'] = pd.to_datetime(filtered_logs['timestamp'])
        filtered_logs = filtered_logs.sort_values('timestamp', ascending=False)
        
        # In case user_filter is numeric and there happens to be a user_id or we want to filter session_id
        if user_filter and 'user_id' in filtered_logs.columns and user_filter.isdigit():
            filtered_logs = filtered_logs[filtered_logs['user_id'] == int(user_filter)]

    st.markdown(f"**Showing {len(filtered_logs):,} events from {time_range.lower()}**")

    if not filtered_logs.empty:
        display_columns = [c for c in [
            'timestamp', 'ip_address', 'location', 'service_name',
            'activity_type', 'http_status', 'revenue_value', 'conversion_flag'
        ] if c in filtered_logs.columns]
        
        st.dataframe(
            filtered_logs[display_columns].head(100),
            use_container_width=True,
            height=600
        )

        col1, col2 = st.columns([6, 1])
        with col2:
            csv = filtered_logs[display_columns].to_csv(index=False)
            st.download_button(
                label="Export CSV",
                data=csv,
                file_name=f"logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )

render_log_stream()
