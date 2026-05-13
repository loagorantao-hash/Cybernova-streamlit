import pandas as pd
import numpy as np


def geo_summary(df: pd.DataFrame) -> pd.DataFrame:
    """FR18: Aggregate visits and revenue by country."""
    if "country" not in df.columns:
        return pd.DataFrame()
    grp = df.groupby("country").agg(
        visits=("country", "count"),
        conversions=("conversion_flag", "sum") if "conversion_flag" in df.columns else ("country", lambda x: 0),
        revenue=("revenue", "sum") if "revenue" in df.columns else ("country", lambda x: 0.0),
    ).reset_index()
    grp["conversion_rate"] = (grp["conversions"] / grp["visits"] * 100).round(2)
    return grp.sort_values("visits", ascending=False)


def top_countries(df: pd.DataFrame, n: int = 15) -> pd.DataFrame:
    return geo_summary(df).head(n)


def country_iso_map() -> dict:
    """Map country names to ISO-3 codes for Plotly choropleth."""
    return {
        "United States": "USA", "United Kingdom": "GBR", "Germany": "DEU",
        "France": "FRA", "Canada": "CAN", "Australia": "AUS", "Japan": "JPN",
        "Brazil": "BRA", "India": "IND", "South Africa": "ZAF", "Nigeria": "NGA",
        "Kenya": "KEN", "China": "CHN", "Mexico": "MEX", "Italy": "ITA",
        "Spain": "ESP", "Netherlands": "NLD", "Sweden": "SWE", "Norway": "NOR",
        "Denmark": "DNK", "Singapore": "SGP", "South Korea": "KOR",
        "New Zealand": "NZL", "Argentina": "ARG", "Chile": "CHL",
        "Colombia": "COL", "Egypt": "EGY", "Ghana": "GHA", "Morocco": "MAR",
        "Saudi Arabia": "SAU", "UAE": "ARE", "Israel": "ISR", "Turkey": "TUR",
        "Poland": "POL", "Czech Republic": "CZE", "Portugal": "PRT",
        "Belgium": "BEL", "Switzerland": "CHE", "Austria": "AUT",
    }


def prepare_choropleth_data(df: pd.DataFrame, metric: str = "visits") -> pd.DataFrame:
    """FR18: Prepare data for choropleth map."""
    geo = geo_summary(df)
    iso_map = country_iso_map()
    geo["iso_alpha"] = geo["country"].map(iso_map)
    geo = geo.dropna(subset=["iso_alpha"])
    return geo
