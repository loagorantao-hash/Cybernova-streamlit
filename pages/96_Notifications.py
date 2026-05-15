import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
from backend.auth.auth_manager import AuthManager
from frontend.components.sidebar import render_sidebar
from frontend.components.layout import set_page_config, load_css
from backend.alert_engine import AlertEngine
from frontend.components.alert_card import render_alert_panel
from backend.data_ingestion.dataset_loader import load_dataset

set_page_config("Notifications")
load_css()

user = AuthManager.require_auth(allowed_roles=["admin", "analyst", "website_user"])
render_sidebar("pages/96_Notifications.py")

st.html("""
<h1 style="color: #f8fafc; font-size: 32px; margin-bottom: 8px;">
<span class="material-symbols-rounded" style="vertical-align: middle;">notifications</span> Notifications Center
</h1>
<p style="color: #94a3b8; font-size: 16px; margin-bottom: 24px;">
System alerts and important updates
</p>
""")

if 'alert_engine' not in st.session_state:
    dataset = load_dataset()
    st.session_state.alert_engine = AlertEngine(dataset)

alerts = st.session_state.alert_engine.run_all_checks()

if alerts:
    st.markdown("### Active Alerts")
    render_alert_panel(alerts, max_display=20)
else:
    st.info("No new notifications.")
