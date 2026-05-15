import pandas as pd
import numpy as np


def country_iso_map() -> dict:
    """Map country/city names to ISO-3 codes for Plotly choropleth."""
    return {
        # Full country names
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
        "Russia": "RUS", "Pakistan": "PAK", "Bangladesh": "BGD",
        "Indonesia": "IDN", "Malaysia": "MYS", "Philippines": "PHL",
        "Vietnam": "VNM", "Thailand": "THA", "Ukraine": "UKR",
        # Cities that appear in location field — map to their country ISO
        "Nairobi": "KEN", "Lagos": "NGA", "Cairo": "EGY", "Gaborone": "BWA",
        "London": "GBR", "Paris": "FRA", "Berlin": "DEU", "New York": "USA",
        "Toronto": "CAN", "Sydney": "AUS", "Tokyo": "JPN", "Mumbai": "IND",
        "Dubai": "ARE", "Johannesburg": "ZAF", "Accra": "GHA",
        "Casablanca": "MAR", "Riyadh": "SAU", "Istanbul": "TUR",
        "Warsaw": "POL", "Prague": "CZE", "Lisbon": "PRT", "Brussels": "BEL",
        "Zurich": "CHE", "Vienna": "AUT", "Stockholm": "SWE", "Oslo": "NOR",
        "Copenhagen": "DNK", "Amsterdam": "NLD", "Madrid": "ESP", "Rome": "ITA",
        "Mexico City": "MEX", "São Paulo": "BRA", "Buenos Aires": "ARG",
        "Santiago": "CHL", "Bogotá": "COL", "Lima": "PER",
        "Beijing": "CHN", "Shanghai": "CHN", "Seoul": "KOR",
        "Bangkok": "THA", "Jakarta": "IDN", "Kuala Lumpur": "MYS",
        "Manila": "PHL", "Ho Chi Minh City": "VNM",
        "Karachi": "PAK", "Dhaka": "BGD", "Kyiv": "UKR",
    }


def geo_summary(df: pd.DataFrame, country_col: str = "country") -> pd.DataFrame:
    """FR18: Aggregate visits, conversions, revenue by country/location."""
    if country_col not in df.columns:
        return pd.DataFrame()

    # Determine which columns exist
    agg_dict: dict = {"visits": (country_col, "count")}
    if "conversions" in df.columns:
        agg_dict["conversions"] = ("conversions", "sum")
    if "revenue" in df.columns:
        agg_dict["revenue"] = ("revenue", "sum")

    grp = df.groupby(country_col).agg(**agg_dict).reset_index()
    grp = grp.rename(columns={country_col: "country"})
    grp["conversion_rate"] = 0.0
    if "conversions" in grp.columns:
        grp["conversion_rate"] = (grp["conversions"] / grp["visits"] * 100).round(2)
    return grp.sort_values("visits", ascending=False)


def top_countries(df: pd.DataFrame, n: int = 15, country_col: str = "country") -> pd.DataFrame:
    return geo_summary(df, country_col=country_col).head(n)


def prepare_choropleth_data(df: pd.DataFrame, metric: str = "visits") -> pd.DataFrame:
    """
    FR18: Prepare data for choropleth map.
    Accepts DataFrames with either a 'country' or 'location' column.
    """
    # Detect the country column name
    if "country" in df.columns:
        country_col = "country"
    elif "location" in df.columns:
        country_col = "location"
    else:
        return pd.DataFrame()

    geo = geo_summary(df, country_col=country_col)
    if geo.empty:
        return pd.DataFrame()

    iso_map = country_iso_map()
    geo["iso_alpha"] = geo["country"].map(iso_map)
    geo = geo.dropna(subset=["iso_alpha"])
    return geo
