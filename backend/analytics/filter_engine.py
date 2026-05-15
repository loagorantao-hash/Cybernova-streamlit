import pandas as pd
from datetime import date, datetime
from typing import Optional


def apply_filters(
    df: pd.DataFrame,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    countries: Optional[list] = None,
    services: Optional[list] = None,
    status_codes: Optional[list] = None,
    methods: Optional[list] = None,
    keyword: Optional[str] = None,
    min_revenue: Optional[float] = None,
    max_revenue: Optional[float] = None,
    conversion_only: bool = False,
) -> pd.DataFrame:
    """FR11–FR13: Apply multi-dimensional filters to the dataset."""
    filtered = df.copy()

    # Date range
    if date_from and "timestamp" in filtered.columns:
        filtered = filtered[filtered["timestamp"].dt.date >= date_from]
    if date_to and "timestamp" in filtered.columns:
        filtered = filtered[filtered["timestamp"].dt.date <= date_to]

    # Country
    if countries:
        filtered = filtered[filtered["country"].isin(countries)]

    # Service type
    if services:
        filtered = filtered[filtered["service_type"].isin(services)]

    # Status codes
    if status_codes:
        filtered = filtered[filtered["status_code"].isin(status_codes)]

    # HTTP method
    if methods:
        filtered = filtered[filtered["method"].isin(methods)]

    # Keyword search across uri, referrer, user_agent
    if keyword and keyword.strip():
        kw = keyword.strip().lower()
        text_mask = pd.Series(False, index=filtered.index)
        for col in ["uri", "referrer", "user_agent", "ip_address", "campaign_id"]:
            if col in filtered.columns:
                text_mask |= filtered[col].astype(str).str.lower().str.contains(kw, na=False)
        filtered = filtered[text_mask]

    # Revenue range
    if min_revenue is not None and "revenue" in filtered.columns:
        filtered = filtered[filtered["revenue"] >= min_revenue]
    if max_revenue is not None and "revenue" in filtered.columns:
        filtered = filtered[filtered["revenue"] <= max_revenue]

    # Conversions only
    if conversion_only and "conversion_flag" in filtered.columns:
        filtered = filtered[filtered["conversion_flag"] == 1]

    return filtered


def get_filter_options(df: pd.DataFrame) -> dict:
    """Return unique values for filter dropdowns."""
    if "timestamp" in df.columns and not pd.api.types.is_datetime64_any_dtype(df["timestamp"]):
        df = df.copy()
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors='coerce')
    
    return {
        "countries": sorted(df["country"].dropna().unique().tolist()) if "country" in df.columns else [],
        "services": sorted(df["service_type"].dropna().unique().tolist()) if "service_type" in df.columns else [],
        "status_codes": sorted(df["status_code"].dropna().unique().tolist()) if "status_code" in df.columns else [],
        "methods": sorted(df["method"].dropna().unique().tolist()) if "method" in df.columns else [],
        "campaigns": sorted(df["campaign_id"].dropna().unique().tolist()) if "campaign_id" in df.columns else [],
        "date_min": df["timestamp"].min().date() if "timestamp" in df.columns and not df["timestamp"].empty else None,
        "date_max": df["timestamp"].max().date() if "timestamp" in df.columns and not df["timestamp"].empty else None,
    }
