import streamlit as st
import pandas as pd
from datetime import date
from typing import Optional
from backend.analytics.filter_engine import apply_filters, get_filter_options


def render_filter_panel(df: pd.DataFrame, key_prefix: str = "main") -> pd.DataFrame:
    """
    FR11-FR13: Render filter sidebar/expander and return filtered DataFrame.
    """
    opts = get_filter_options(df)

    with st.expander("Filter Data", expanded=False):
        col1, col2, col3 = st.columns(3)

        with col1:
            date_from = st.date_input(
                "Date From",
                value=opts["date_min"],
                min_value=opts["date_min"],
                max_value=opts["date_max"],
                key=f"{key_prefix}_date_from",
            ) if opts["date_min"] else None

            countries = st.multiselect(
                "Countries",
                options=opts["countries"],
                default=[],
                key=f"{key_prefix}_countries",
            )

        with col2:
            date_to = st.date_input(
                "Date To",
                value=opts["date_max"],
                min_value=opts["date_min"],
                max_value=opts["date_max"],
                key=f"{key_prefix}_date_to",
            ) if opts["date_max"] else None

            services = st.multiselect(
                "Service Types",
                options=opts["services"],
                default=[],
                key=f"{key_prefix}_services",
            )

        with col3:
            methods = st.multiselect(
                "HTTP Methods",
                options=opts["methods"],
                default=[],
                key=f"{key_prefix}_methods",
            )
            status_codes = st.multiselect(
                "Status Codes",
                options=opts["status_codes"],
                default=[],
                key=f"{key_prefix}_status",
            )

        col4, col5 = st.columns([3, 1])
        with col4:
            keyword = st.text_input(
                "Keyword Search (URI, IP, Campaign...)",
                value="",
                key=f"{key_prefix}_keyword",
            )
        with col5:
            conversion_only = st.checkbox(
                "Conversions Only",
                value=False,
                key=f"{key_prefix}_conv_only",
            )

    filtered = apply_filters(
        df,
        date_from=date_from,
        date_to=date_to,
        countries=countries if countries else None,
        services=services if services else None,
        methods=methods if methods else None,
        status_codes=status_codes if status_codes else None,
        keyword=keyword or None,
        conversion_only=conversion_only,
    )

    total = len(df)
    filtered_count = len(filtered)
    pct = filtered_count / total * 100 if total else 0
    st.caption(
        f"Showing **{filtered_count:,}** of **{total:,}** records ({pct:.1f}%)"
    )
    return filtered
