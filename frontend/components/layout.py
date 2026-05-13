import streamlit as st
from pathlib import Path
import textwrap


def load_css():
    """Inject the global stylesheet into Streamlit."""
    css_path = Path(__file__).parent.parent / "styles" / "main.css"
    if css_path.exists():
        css = css_path.read_text(encoding="utf-8")
        st.html(f"""
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/lucide-static@0.321.0/font/lucide.min.css">
<style>
{css}
</style>
""")


def set_page_config(title: str = "CyberNova Analytics"):
    """Call this at the top of every page before any other st. calls."""
    st.set_page_config(
        page_title=f"{title} | CyberNova",
        page_icon="🔷",
        layout="wide",
        initial_sidebar_state="expanded",
    )


def page_header(title: str, subtitle: str = "", icon: str = ""):
    """Render a styled page header."""
    icon_html = f'<span style="margin-right:10px;font-size:24px;">{icon}</span>' if icon else ""
    st.html(textwrap.dedent(f"""
    <div class="page-header animate-in">
        <h1>{icon_html}{title}</h1>
        {f'<p>{subtitle}</p>' if subtitle else ''}
    </div>
    """))


def section_header(title: str):
    """Render a styled section sub-header."""
    st.html(f'<div class="section-header">{title}</div>')


def glass_container(content_fn, *args, **kwargs):
    """Wrap content in a glassmorphic card via st.container."""
    st.html('<div class="glass-card animate-in">')
    content_fn(*args, **kwargs)
    st.html('</div>')


def brand_logo():
    """Render the CyberNova brand logo for the sidebar."""
    st.html(textwrap.dedent("""
    <div class="brand-logo">
        <div class="brand-logo-icon">CN</div>
        <div>
            <div class="brand-logo-text">CyberNova</div>
            <div class="brand-logo-sub">Analytics</div>
        </div>
    </div>
    """))


def role_badge(role: str):
    """Render a colored role badge."""
    role_styles = {
        "admin": ("badge-amber", "System Admin"),
        "analyst": ("badge-green", "Business Analyst"),
        "website_user": ("badge-cyan", "Website User"),
    }
    cls, label = role_styles.get(role, ("badge-blue", role.title()))
    return f'<span class="badge {cls}">{label}</span>'


def info_metric_row(metrics: list):
    """
    Render a row of simple inline metrics.
    metrics: list of (label, value) tuples
    """
    parts = []
    for label, value in metrics:
        parts.append(textwrap.dedent(f"""
        <div style="text-align:center;padding:0 16px;border-right:1px solid rgba(255,255,255,0.06);">
            <div style="font-size:11px;color:#64748b;text-transform:uppercase;letter-spacing:0.5px;">{label}</div>
            <div style="font-size:18px;font-weight:700;color:#f1f5f9;">{value}</div>
        </div>"""))
    st.html(
        f'<div style="display:flex;align-items:center;flex-wrap:wrap;gap:4px;padding:12px 0;">'
        + "".join(parts) + "</div>"
    )
