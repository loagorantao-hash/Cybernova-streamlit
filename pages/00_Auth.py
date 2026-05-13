"""
FR5–FR8: Authentication Page — Login & Registration
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
import textwrap

import streamlit as st
from frontend.components.layout import set_page_config, load_css
from backend.auth.auth_manager import AuthManager
from backend.auth.rbac import get_home_page
from backend.database.connection import init_db

set_page_config("Sign In")
load_css()
init_db()

# Redirect if already logged in
if AuthManager.is_authenticated():
    user = AuthManager.get_current_user()
    st.switch_page(get_home_page(user.get("role", "website_user")))
    st.stop()


# ── Centered Auth Card ─────────────────────────────────────────────────────────
st.html("""
<div style="display:flex;justify-content:center;padding:20px 0 10px;">
    <div style="
        width:72px;height:72px;
        background:linear-gradient(135deg,#2563eb,#06b6d4);
        border-radius:20px;display:flex;align-items:center;justify-content:center;
        font-size:28px;font-weight:900;color:white;
        box-shadow:0 8px 32px rgba(37,99,235,0.5);
    ">CN</div>
</div>
<h2 style="text-align:center;font-size:24px;font-weight:800;color:#f1f5f9;
           letter-spacing:-0.02em;margin:8px 0 4px;">CyberNova Analytics</h2>
<p style="text-align:center;font-size:13px;color:#64748b;margin:0 0 24px;">
    Enterprise Web Log Intelligence
</p>
""")

_, center, _ = st.columns([1, 2, 1])

with center:
    tab_login, tab_register = st.tabs(["Sign In", "Create Account"])

    # ── LOGIN TAB ──────────────────────────────────────────────────────────────
    with tab_login:
        st.html("<div style='height:8px'></div>")
        with st.form("login_form", clear_on_submit=False):
            email = st.text_input("Email Address", placeholder="you@example.com", key="login_email", autocomplete="username")
            password = st.text_input("Password", type="password", placeholder="••••••••", key="login_pass", autocomplete="current-password")

            st.html("<div style='height:4px'></div>")
            submitted = st.form_submit_button("Sign In", use_container_width=True)

            if submitted:
                if not email or not password:
                    st.error("Please enter both email and password.")
                else:
                    result = AuthManager.login(email, password)
                    if result["success"]:
                        st.session_state["authenticated"] = True
                        st.session_state["user"] = result["user"]
                        role = result["user"]["role"]
                        st.success(f"Welcome back, {result['user']['username']}!")
                        st.switch_page(get_home_page(role))
                    else:
                        st.error(result["error"])

        # Demo credentials hint
        st.html(textwrap.dedent("""
        <div style="margin-top:16px;padding:12px;background:rgba(37,99,235,0.08);
                    border-radius:10px;border:1px solid rgba(37,99,235,0.15);">
            <div style="font-size:11px;font-weight:700;color:#60a5fa;margin-bottom:6px;
                        text-transform:uppercase;letter-spacing:0.5px;">Demo Credentials</div>
            <div style="font-size:12px;color:#94a3b8;line-height:1.8;">
                <strong style="color:#f59e0b;">Admin:</strong> admin@cybernova.com / Admin@2026!<br>
                <strong style="color:#34d399;">Analyst:</strong> analyst@cybernova.com / Analyst@2026!<br>
                <strong style="color:#22d3ee;">User:</strong> user@cybernova.com / User@2026!
            </div>
        </div>
        """))

    # ── REGISTER TAB ──────────────────────────────────────────────────────────
    with tab_register:
        st.html("<div style='height:8px'></div>")
        with st.form("register_form", clear_on_submit=True):
            r_username = st.text_input("Username", placeholder="johndoe", key="reg_user", autocomplete="username")
            r_email = st.text_input("Email Address", placeholder="you@example.com", key="reg_email", autocomplete="email")
            r_pass = st.text_input("Password", type="password", placeholder="Min 8 characters", key="reg_pass", autocomplete="new-password")
            r_pass2 = st.text_input("Confirm Password", type="password", placeholder="Repeat password", key="reg_pass2", autocomplete="new-password")

            st.html("<div style='height:4px'></div>")
            reg_submitted = st.form_submit_button("Create Account", use_container_width=True)

            if reg_submitted:
                errors = []
                if not all([r_username, r_email, r_pass, r_pass2]):
                    errors.append("All fields are required.")
                if r_pass != r_pass2:
                    errors.append("Passwords do not match.")
                if len(r_pass) < 8:
                    errors.append("Password must be at least 8 characters.")
                if "@" not in r_email:
                    errors.append("Please enter a valid email address.")

                if errors:
                    for e in errors:
                        st.error(e)
                else:
                    result = AuthManager.register(r_username, r_email, r_pass, role="website_user")
                    if result["success"]:
                        st.success("Account created! You can now sign in.")
                    else:
                        st.error(result["error"])
