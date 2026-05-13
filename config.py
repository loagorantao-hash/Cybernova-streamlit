import os
from pathlib import Path

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
EXPORTS_DIR = DATA_DIR / "exports"
DB_PATH = DATA_DIR / "cybernova.db"

# Ensure directories exist
for _d in [DATA_DIR, RAW_DATA_DIR, PROCESSED_DATA_DIR, EXPORTS_DIR]:
    _d.mkdir(parents=True, exist_ok=True)

APP_NAME = "CyberNova Analytics"
APP_VERSION = "1.0.0"
APP_TAGLINE = "Enterprise Web Log Intelligence Platform"
SECRET_KEY = os.getenv("SECRET_KEY", "cybernova-secret-2026-xK9!mP3@nQ7")

PARQUET_FILE = RAW_DATA_DIR / "web_logs.parquet"

ROLES = {
    "website_user": "Website User",
    "analyst": "Business Analyst",
    "admin": "System Administrator",
}

ROLE_COLORS = {
    "website_user": "#06b6d4",
    "analyst": "#10b981",
    "admin": "#f59e0b",
}

CACHE_TTL = 300  # 5 minutes

DEFAULT_PAGE_SIZE = 50
MAX_EXPORT_ROWS = 100_000

CHART_COLORS = [
    "#2563eb", "#06b6d4", "#10b981", "#f59e0b",
    "#8b5cf6", "#ec4899", "#ef4444", "#14b8a6",
    "#f97316", "#a78bfa",
]

PLOTLY_LAYOUT = dict(
    template="plotly_dark",
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#f8fafc", family="Inter, sans-serif", size=12),
    margin=dict(l=20, r=20, t=40, b=20),
    legend=dict(bgcolor="rgba(0,0,0,0)", bordercolor="rgba(255,255,255,0.1)"),
    xaxis=dict(showgrid=False, color="#94a3b8"),
    yaxis=dict(gridcolor="rgba(255,255,255,0.08)", color="#94a3b8"),
)
