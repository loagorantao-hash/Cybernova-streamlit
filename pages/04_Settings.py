import textwrap
"""
Settings Page — Profile update and password change for all roles.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
from frontend.components.layout import set_page_config, load_css, page_header, section_header
from frontend.components.sidebar import render_sidebar
from frontend.components.layout import role_badge
from backend.auth.auth_manager import AuthManager
from backend.services.user_service import UserService

set_page_config("Settings")
load_css()

user = AuthManager.require_auth()
render_sidebar("pages/04_Settings.py")

page_header("Settings", "Manage your account and preferences", "")

tab_profile, tab_security = st.tabs(["Profile", "Security"])

# ── Profile Tab ───────────────────────────────────────────────────────────────
with tab_profile:
    section_header("Account Information")

    _, center, _ = st.columns([1, 2, 1])
    with center:
        st.html(textwrap.dedent(f"""
        <div class="glass-card" style="text-align:center;padding:32px;">
            <div style="width:64px;height:64px;background:linear-gradient(135deg,#2563eb,#06b6d4);
                        border-radius:50%;display:flex;align-items:center;justify-content:center;
                        font-size:24px;font-weight:800;color:white;margin:0 auto 16px;">
                {user.get('username', 'U')[0].upper()}
            </div>
            <div style="font-size:20px;font-weight:700;color:#f1f5f9;margin-bottom:4px;">
                {user.get('username', 'N/A')}
            </div>
            <div style="font-size:13px;color:#64748b;margin-bottom:12px;">{user.get('email', '')}</div>
            {role_badge(user.get('role', 'website_user'))}
            <div style="font-size:11px;color:#475569;margin-top:12px;">
                Member since: {str(user.get('created_at', 'N/A'))[:10]}
            </div>
        </div>
        """))

    section_header("Update Username")
    with st.form("update_profile"):
        new_username = st.text_input("New Username", value=user.get("username", ""))
        if st.form_submit_button("Update Profile", use_container_width=True):
            if new_username and new_username != user.get("username"):
                res = UserService.update_user(user["id"], username=new_username)
                if res["success"]:
                    st.session_state["user"]["username"] = new_username
                    st.success("Username updated successfully.")
                else:
                    st.error(res["error"])

# ── Security Tab ─────────────────────────────────────────────────────────────
with tab_security:
    section_header("Change Password")
    _, center, _ = st.columns([1, 2, 1])
    with center:
        with st.form("change_password"):
            new_pass = st.text_input("New Password", type="password", placeholder="Min 8 characters")
            confirm_pass = st.text_input("Confirm New Password", type="password")
            if st.form_submit_button("Update Password", use_container_width=True):
                if not new_pass or not confirm_pass:
                    st.error("Please fill in both fields.")
                elif new_pass != confirm_pass:
                    st.error("Passwords do not match.")
                elif len(new_pass) < 8:
                    st.error("Password must be at least 8 characters.")
                else:
                    res = UserService.update_user(user["id"], password=new_pass)
                    if res["success"]:
                        st.success("Password updated successfully.")
                    else:
                        st.error(res["error"])

    section_header("Session")
    _, center, _ = st.columns([1, 2, 1])
    with center:
        st.html(textwrap.dedent(f"""
        <div class="glass-card">
            <div style="font-size:12px;color:#94a3b8;margin-bottom:6px;">Active Session</div>
            <div style="font-size:13px;color:#f1f5f9;">Logged in as <strong>{user.get('username')}</strong></div>
            <div style="font-size:11px;color:#64748b;margin-top:4px;">Role: {user.get('role', '').replace('_', ' ').title()}</div>
        </div>
        """))
        if st.button("Sign Out", use_container_width=True):
            AuthManager.logout()
            st.switch_page("pages/00_Auth.py")
