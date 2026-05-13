import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path
import logging
import sys, os

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from config import PARQUET_FILE, CACHE_TTL

logger = logging.getLogger(__name__)

# Column aliases: maps common IIS/web-log names → standard internal names
COLUMN_ALIASES = {
    "timestamp": ["timestamp", "datetime", "date_time", "date", "time", "log_time", "created_at", "cs-date", "cs-time"],
    "ip_address": ["ip_address", "ip", "client_ip", "source_ip", "remote_addr", "c-ip"],
    "method": ["method", "http_method", "request_method", "cs-method"],
    "uri": ["uri", "url", "path", "request_uri", "endpoint", "cs-uri-stem", "cs-uri"],
    "status_code": ["status_code", "status", "http_status", "sc-status", "response_code", "http_status"],
    "bytes_sent": ["bytes_sent", "bytes", "content_length", "size", "sc-bytes", "response_time_ms"],
    "country": ["country", "country_code", "geo_country", "location", "c-country", "location"],
    "service_type": ["service_type", "service", "product", "category", "page_type", "service_name", "activity_type"],
    "session_id": ["session_id", "session", "sid", "cs-session"],
    "conversion_flag": ["conversion_flag", "converted", "conversion", "is_converted", "lead_flag"],
    "campaign_id": ["campaign_id", "campaign", "utm_campaign"],
    "revenue": ["revenue", "amount", "sales", "value", "revenue_value"],
    "referrer": ["referrer", "referer", "http_referer", "cs-referer"],
    "user_agent": ["user_agent", "useragent", "ua", "cs-user-agent"],
    "uri": ["uri", "url", "path", "request_uri", "endpoint", "cs-uri-stem", "cs-uri", "page_url"],
}


def _normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    cols_lower = {c.lower(): c for c in df.columns}
    renames = {}
    for standard, aliases in COLUMN_ALIASES.items():
        if standard in df.columns:
            continue
        for alias in aliases:
            if alias.lower() in cols_lower:
                renames[cols_lower[alias.lower()]] = standard
                break
    return df.rename(columns=renames) if renames else df


def _ensure_columns(df: pd.DataFrame) -> pd.DataFrame:
    # Timestamp
    if "timestamp" in df.columns:
        # User's format is DD/MM/YYYY, ensure it's parsed correctly
        df["timestamp"] = pd.to_datetime(df["timestamp"], dayfirst=True, errors="coerce")
    else:
        df["timestamp"] = pd.Timestamp.now()

    # Numeric
    for col, default in [("bytes_sent", 0.0), ("revenue", 0.0)]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(default)
        else:
            df[col] = default

    if "status_code" in df.columns:
        df["status_code"] = pd.to_numeric(df["status_code"], errors="coerce").fillna(200).astype(int)
    else:
        df["status_code"] = 200

    if "conversion_flag" in df.columns:
        df["conversion_flag"] = pd.to_numeric(df["conversion_flag"], errors="coerce").fillna(0).astype(int)
    else:
        df["conversion_flag"] = 0

    # String defaults
    for col in ["country", "service_type", "method", "uri", "ip_address", "campaign_id", "session_id"]:
        if col not in df.columns:
            df[col] = "Unknown"

    # Derived columns
    ts = df["timestamp"]
    df["date"] = ts.dt.date
    df["hour"] = ts.dt.hour
    df["day_of_week"] = ts.dt.day_name()
    df["month"] = ts.dt.to_period("M").astype(str)
    df["year"] = ts.dt.year
    df["status_category"] = df["status_code"].apply(_categorize_status)
    return df


def _categorize_status(code: int) -> str:
    if 200 <= code < 300:
        return "2xx Success"
    elif 300 <= code < 400:
        return "3xx Redirect"
    elif 400 <= code < 500:
        return "4xx Client Error"
    elif code >= 500:
        return "5xx Server Error"
    return "Unknown"


@st.cache_data(ttl=CACHE_TTL, show_spinner="Loading dataset...")
def load_dataset(file_path: str = None) -> pd.DataFrame:
    path = Path(file_path) if file_path else PARQUET_FILE
    if not path.exists():
        logger.warning(f"Dataset not found at {path}. Generating sample data.")
        return _generate_sample_data(5000)
    try:
        df = pd.read_parquet(path)
        df = _normalize_columns(df)
        df = _ensure_columns(df)
        logger.info(f"Loaded {len(df):,} records from {path}")
        return df
    except Exception as e:
        logger.error(f"Dataset load error: {e}")
        st.error(f"Error loading dataset: {e}")
        return _generate_sample_data(5000)


def _generate_sample_data(n: int = 5000) -> pd.DataFrame:
    """Fallback synthetic data when no Parquet is found."""
    import random
    from datetime import datetime, timedelta

    rng = np.random.default_rng(42)
    base = datetime(2024, 1, 1)
    timestamps = [base + timedelta(seconds=int(x)) for x in rng.integers(0, 365 * 86400, n)]
    countries = ["United States", "United Kingdom", "Germany", "France", "Canada",
                 "Australia", "Japan", "Brazil", "India", "South Africa", "Nigeria", "Kenya"]
    services = ["Product Demo", "Support Portal", "Documentation", "Pricing Page",
                "Blog", "Case Studies", "Webinar", "Free Trial", "API Docs", "Dashboard"]
    campaigns = ["CAMP_001", "CAMP_002", "CAMP_003", "CAMP_004", "CAMP_005", "ORGANIC"]
    methods = ["GET", "POST", "PUT", "DELETE"]
    statuses = [200, 200, 200, 200, 301, 404, 500]

    df = pd.DataFrame({
        "timestamp": timestamps,
        "ip_address": [f"{rng.integers(1,255)}.{rng.integers(0,255)}.{rng.integers(0,255)}.{rng.integers(1,255)}" for _ in range(n)],
        "method": rng.choice(methods, n, p=[0.7, 0.2, 0.07, 0.03]),
        "uri": rng.choice(["/home", "/product", "/demo", "/pricing", "/support", "/blog", "/api/v1/data"], n),
        "status_code": rng.choice(statuses, n),
        "bytes_sent": rng.integers(500, 50000, n).astype(float),
        "country": rng.choice(countries, n),
        "service_type": rng.choice(services, n),
        "session_id": [f"sess_{rng.integers(100000, 999999)}" for _ in range(n)],
        "conversion_flag": rng.choice([0, 1], n, p=[0.75, 0.25]),
        "campaign_id": rng.choice(campaigns, n),
        "revenue": np.where(rng.random(n) > 0.75, rng.uniform(50, 5000, n), 0.0),
    })
    df = _ensure_columns(df)
    return df


def get_dataset_info(df: pd.DataFrame) -> dict:
    return {
        "total_records": len(df),
        "columns": list(df.columns),
        "date_range": (
            str(df["timestamp"].min().date()) if "timestamp" in df.columns else "N/A",
            str(df["timestamp"].max().date()) if "timestamp" in df.columns else "N/A",
        ),
        "countries": df["country"].nunique() if "country" in df.columns else 0,
        "services": df["service_type"].nunique() if "service_type" in df.columns else 0,
        "memory_mb": round(df.memory_usage(deep=True).sum() / 1024 / 1024, 2),
    }
