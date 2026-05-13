import textwrap
"""
CyberNova Analytics — Main Entry Point
Handles authentication gate and redirects to role-appropriate dashboard.
"""
import streamlit as st
import sys
from pathlib import Path

# Ensure project root is on sys.path
sys.path.insert(0, str(Path(__file__).parent))

from frontend.components.layout import set_page_config, load_css, page_header, brand_logo
from backend.auth.auth_manager import AuthManager
from backend.auth.rbac import get_home_page

set_page_config("Home")
load_css()


def main():
    # If already authenticated, redirect to role dashboard
    if AuthManager.is_authenticated():
        user = AuthManager.get_current_user()
        home = get_home_page(user.get("role", "website_user"))
        st.switch_page(home)
        return

    # Landing / login redirect
    st.html(textwrap.dedent("""
    <div style="
        display:flex; flex-direction:column; align-items:center; justify-content:center;
        min-height:70vh; text-align:center; padding:40px 20px;
    ">
        <div style="
            width:72px; height:72px;
            background: linear-gradient(135deg, #2563eb, #06b6d4);
            border-radius:20px; display:flex; align-items:center; justify-content:center;
            font-size:32px; font-weight:900; color:white;
            box-shadow:0 8px 32px rgba(37,99,235,0.5);
            margin-bottom:24px;
        ">CN</div>
        <h1 style="
            font-size:36px; font-weight:900; color:#f1f5f9;
            letter-spacing:-0.03em; margin:0 0 12px;
            background:linear-gradient(135deg,#f1f5f9,#60a5fa);
            -webkit-background-clip:text; -webkit-text-fill-color:transparent;
        ">CyberNova Analytics</h1>
        <p style="font-size:16px;color:#64748b;max-width:480px;line-height:1.6;margin:0 0 32px;">
            Enterprise Web Log Intelligence Platform.<br>
            Transform 500,000 IIS server logs into actionable business intelligence.
        </p>
        <div style="display:flex;gap:12px;flex-wrap:wrap;justify-content:center;">
            <div style="padding:10px 20px;background:rgba(37,99,235,0.1);border:1px solid rgba(37,99,235,0.3);
                        border-radius:10px;font-size:12px;color:#60a5fa;font-weight:600;">
                3 User Roles
            </div>
            <div style="padding:10px 20px;background:rgba(6,182,212,0.1);border:1px solid rgba(6,182,212,0.3);
                        border-radius:10px;font-size:12px;color:#22d3ee;font-weight:600;">
                500K Records
            </div>
            <div style="padding:10px 20px;background:rgba(16,185,129,0.1);border:1px solid rgba(16,185,129,0.3);
                        border-radius:10px;font-size:12px;color:#34d399;font-weight:600;">
                Real-time Analytics
            </div>
        </div>
    </div>
    """))

    col1, col2, col3 = st.columns([2, 1, 2])
    with col2:
        if st.button("Sign In", use_container_width=True):
            st.switch_page("pages/00_Auth.py")


if __name__ == "__main__":
    main()
