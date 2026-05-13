from enum import Enum


class Role(str, Enum):
    website_user = "website_user"
    analyst = "analyst"
    admin = "admin"


PERMISSIONS = {
    Role.website_user: {
        "view_own_logs", "view_basic_charts", "view_activity_classification", "export_own_data", "update_profile",
    },
    Role.analyst: {
        "view_all_logs", "view_advanced_charts", "view_kpi_dashboard", "view_geographic_analysis",
        "view_statistical_analysis", "view_conversion_funnel", "filter_logs", "export_all_data", "update_profile",
    },
    Role.admin: {
        "view_all_logs", "view_advanced_charts", "view_kpi_dashboard", "view_geographic_analysis",
        "view_statistical_analysis", "view_conversion_funnel", "filter_logs", "export_all_data",
        "manage_users", "upload_dataset", "clean_data", "delete_records", "view_system_performance", "update_profile",
    },
}

PAGE_ACCESS = {
    Role.website_user: ["pages/01_User_Dashboard.py", "pages/04_Settings.py"],
    Role.analyst: ["pages/02_Analyst_Dashboard.py", "pages/04_Settings.py"],
    Role.admin: ["pages/02_Analyst_Dashboard.py", "pages/03_Admin_Dashboard.py", "pages/04_Settings.py"],
}


def has_permission(role: str, permission: str) -> bool:
    try:
        return permission in PERMISSIONS.get(Role(role), set())
    except ValueError:
        return False


def get_home_page(role: str) -> str:
    mapping = {
        "website_user": "pages/01_User_Dashboard.py",
        "analyst": "pages/02_Analyst_Dashboard.py",
        "admin": "pages/03_Admin_Dashboard.py",
    }
    return mapping.get(role, "pages/01_User_Dashboard.py")
