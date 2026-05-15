import streamlit as st
from streamlit_option_menu import option_menu
from frontend.components.layout import brand_logo, role_badge
from frontend.components.live_toggle import render_live_mode_toggle
from backend.auth.auth_manager import AuthManager
import textwrap


ROLE_MENUS = {
    "website_user": {
        "items": ["My Dashboard", "Notifications", "Settings"],
        "icons": ["house-fill", "bell-fill", "gear-fill"],
        "pages": ["pages/01_User_Dashboard.py", "pages/96_Notifications.py", "pages/04_Settings.py"],
    },
    "analyst": {
        "items": ["Analytics", "Notifications", "Settings"],
        "icons": ["bar-chart-fill", "bell-fill", "gear-fill"],
        "pages": ["pages/02_Analyst_Dashboard.py", "pages/96_Notifications.py", "pages/04_Settings.py"],
    },
    "admin": {
        "items": ["Admin Panel", "Analytics", "Live Log Stream", "Notifications", "Settings"],
        "icons": ["shield-lock-fill", "bar-chart-fill", "activity", "bell-fill", "gear-fill"],
        "pages": ["pages/03_Admin_Dashboard.py", "pages/02_Analyst_Dashboard.py", "pages/95_Live_Log_Stream.py", "pages/96_Notifications.py", "pages/04_Settings.py"],
    },
}


def render_sidebar(current_page: str = ""):
    """Render role-aware sidebar navigation."""
    user = AuthManager.get_current_user()
    if not user:
        return

    role = user.get("role", "website_user")
    menu_cfg = ROLE_MENUS.get(role, ROLE_MENUS["website_user"])

    with st.sidebar:
        brand_logo()
        st.html("<hr class='cn-divider'>")

        # User info card
        st.html(textwrap.dedent(f"""
        <div style="padding:12px;background:rgba(37,99,235,0.08);border-radius:12px;
                    border:1px solid rgba(37,99,235,0.15);margin-bottom:16px;">
            <div style="font-size:13px;font-weight:700;color:#f1f5f9;margin-bottom:4px;">
                {user.get('username', 'User')}
            </div>
            <div style="font-size:11px;color:#64748b;margin-bottom:6px;">
                {user.get('email', '')}
            </div>
            {role_badge(role)}
        </div>
        """))

        # Calculate default index
        default_idx = 0
        if current_page:
            try:
                # Match by exact filename
                default_idx = menu_cfg["pages"].index(current_page)
            except ValueError:
                pass

        # Navigation menu
        selected = option_menu(
            menu_title=None,
            options=menu_cfg["items"],
            icons=menu_cfg["icons"],
            default_index=default_idx,
            styles={
                "container": {"padding": "0", "background": "transparent"},
                "icon": {"color": "#60a5fa", "font-size": "14px"},
                "nav-link": {
                    "font-size": "13px",
                    "font-weight": "500",
                    "color": "#94a3b8",
                    "border-radius": "10px",
                    "padding": "9px 14px",
                    "margin": "2px 0",
                    "--hover-color": "rgba(37,99,235,0.12)",
                },
                "nav-link-selected": {
                    "background": "rgba(37,99,235,0.2)",
                    "color": "#60a5fa",
                    "font-weight": "700",
                    "border": "1px solid rgba(37,99,235,0.3)",
                },
            },
        )

        # Navigate on selection
        for i, item in enumerate(menu_cfg["items"]):
            if selected == item:
                target = menu_cfg["pages"][i]
                if target != current_page:
                    st.switch_page(target)
                break

        st.html("<hr class='cn-divider'>")
        
        # Live Mode Toggle
        render_live_mode_toggle()

        # Logout
        if st.button("Logout", use_container_width=True, key="sidebar_logout"):
            AuthManager.logout()
            st.switch_page("pages/00_Auth.py")

        # Footer
        st.html(textwrap.dedent("""
        <div style="padding:12px 0 0;text-align:center;">
            <div style="font-size:10px;color:#475569;">CyberNova Analytics v1.0</div>
            <div style="font-size:10px;color:#334155;">CET333 Product Development</div>
        </div>
        """))
